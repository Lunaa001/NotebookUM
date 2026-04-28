"""Circuit Breaker service for handling latency, errors, and network failures."""

from pybreaker import CircuitBreaker
from typing import Callable, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)


class CircuitBreakerService:
    """
    Service for implementing circuit breaker pattern with multiple failure detection strategies.
    
    States:
    - CLOSED: Circuit is operational, requests pass through normally
    - OPEN: Circuit is broken, requests fail immediately with CircuitBreakerListener
    - HALF_OPEN: Circuit is testing recovery, limited requests allowed
    """
    
    def __init__(
        self,
        name: str,
        fail_max: int = 5,
        reset_timeout: int = 30,
        listeners: Optional[list] = None,
    ):
        """
        Initialize Circuit Breaker
        
        Args:
            name: Identifier for this circuit breaker
            fail_max: Number of failures before opening circuit
            reset_timeout: Seconds to wait before half-open attempt
            listeners: List of CircuitBreakerListener instances
        """
        self.name = name
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self._listeners = listeners or []
        
        # Create pybreaker instance
        self._breaker = CircuitBreaker(
            fail_max=fail_max,
            reset_timeout=reset_timeout,
            listeners=self._listeners,
            name=name,
        )
        
        # Metrics for monitoring
        self._metrics = {
            "total_calls": 0,
            "failed_calls": 0,
            "successful_calls": 0,
            "rejected_calls": 0,  # Rejected while OPEN
            "latency_sum": 0.0,
            "latency_count": 0,
        }
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Result from function
            
        Raises:
            CircuitBreakerListener: If circuit is OPEN
            Exception: If function execution fails
        """
        self._metrics["total_calls"] += 1
        
        try:
            start_time = time.time()
            result = self._breaker.call(func, *args, **kwargs)
            latency = time.time() - start_time
            
            self._metrics["successful_calls"] += 1
            self._metrics["latency_sum"] += latency
            self._metrics["latency_count"] += 1
            
            logger.info(
                f"[{self.name}] ✅ Success - Latency: {latency:.3f}s, State: {self.state}"
            )
            return result
            
        except Exception as e:
            if self.is_open:
                self._metrics["rejected_calls"] += 1
                logger.warning(f"[{self.name}] ⛔ Circuit OPEN - Request rejected")
            else:
                self._metrics["failed_calls"] += 1
                logger.error(f"[{self.name}] ❌ Failed - Error: {str(e)}")
            raise
    
    @property
    def state(self) -> str:
        """Get current circuit breaker state"""
        state_obj = self._breaker.state
        # pybreaker returns state objects, convert to string
        return str(type(state_obj).__name__).lower().replace("circuit", "").replace("state", "")
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is OPEN"""
        return "open" in str(type(self._breaker.state).__name__).lower()
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is CLOSED"""
        return "closed" in str(type(self._breaker.state).__name__).lower()
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit is HALF_OPEN"""
        return "half" in str(type(self._breaker.state).__name__).lower()
    
    @property
    def failure_count(self) -> int:
        """Get current failure count"""
        return self._breaker.fail_counter
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        total = self._metrics["total_calls"]
        if total == 0:
            return 100.0
        return (self._metrics["successful_calls"] / total) * 100
    
    @property
    def avg_latency(self) -> float:
        """Calculate average latency in milliseconds"""
        if self._metrics["latency_count"] == 0:
            return 0.0
        return (self._metrics["latency_sum"] / self._metrics["latency_count"]) * 1000
    
    @property
    def metrics(self) -> dict:
        """Get all circuit breaker metrics"""
        return {
            **self._metrics,
            "state": self.state,
            "failure_count": self.failure_count,
            "success_rate": f"{self.success_rate:.2f}%",
            "avg_latency_ms": f"{self.avg_latency:.2f}ms",
        }
    
    def reset(self):
        """Manually reset the circuit breaker by creating a new one"""
        # pybreaker doesn't have reset(), so we recreate it
        self._breaker = CircuitBreaker(
            fail_max=self.fail_max,
            reset_timeout=self.reset_timeout,
            listeners=self._listeners,
            name=self.name,
        )
        self._metrics = {
            "total_calls": 0,
            "failed_calls": 0,
            "successful_calls": 0,
            "rejected_calls": 0,
            "latency_sum": 0.0,
            "latency_count": 0,
        }
        logger.info(f"[{self.name}] 🔄 Circuit breaker reset")


class CircuitBreakerFactory:
    """Factory for creating and managing circuit breakers"""
    
    _breakers: dict[str, CircuitBreakerService] = {}
    
    @classmethod
    def get_or_create(
        cls,
        name: str,
        fail_max: int = 5,
        reset_timeout: int = 30,
    ) -> CircuitBreakerService:
        """
        Get existing circuit breaker or create new one
        
        Args:
            name: Unique identifier for circuit breaker
            fail_max: Failures before opening
            reset_timeout: Reset timeout in seconds
            
        Returns:
            CircuitBreakerService instance
        """
        if name not in cls._breakers:
            cls._breakers[name] = CircuitBreakerService(
                name=name,
                fail_max=fail_max,
                reset_timeout=reset_timeout,
            )
        return cls._breakers[name]
    
    @classmethod
    def get_all_metrics(cls) -> dict:
        """Get metrics for all circuit breakers"""
        return {
            name: breaker.metrics
            for name, breaker in cls._breakers.items()
        }
    
    @classmethod
    def reset_all(cls):
        """Reset all circuit breakers"""
        for breaker in cls._breakers.values():
            breaker.reset()
