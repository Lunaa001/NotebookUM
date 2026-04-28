"""Saga Pattern orchestrator for distributed transactions with automatic compensation/rollback."""

from dataclasses import dataclass, field
from typing import Callable, Optional, Any, Dict, List
from enum import Enum
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class SagaStepStatus(Enum):
    """Status of a saga step."""
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class SagaTransactionStatus(Enum):
    """Status of the entire saga transaction."""
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


@dataclass
class SagaStep:
    """
    Represents a single step in a saga with forward action and compensating action.
    
    Attributes:
        name: Unique identifier for this step
        action: Callable that performs the forward action
        compensation: Callable that compensates for the forward action (rollback)
        priority: Execution order (lower = earlier)
    """
    name: str
    action: Callable
    compensation: Callable
    priority: int = 0
    
    # Runtime state
    status: SagaStepStatus = field(default=SagaStepStatus.PENDING)
    result: Optional[Any] = field(default=None)
    error: Optional[Exception] = field(default=None)
    start_time: Optional[float] = field(default=None)
    end_time: Optional[float] = field(default=None)
    
    @property
    def latency(self) -> float:
        """Get latency in milliseconds."""
        if self.start_time is None or self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time) * 1000


@dataclass
class SagaTransaction:
    """
    Represents a complete saga transaction with multiple steps and compensation logic.
    
    Attributes:
        transaction_id: Unique identifier for this transaction
        steps: List of SagaStep objects to execute
        status: Current status of the transaction
    """
    transaction_id: str
    steps: List[SagaStep]
    status: SagaTransactionStatus = field(default=SagaTransactionStatus.PENDING)
    created_at: datetime = field(default_factory=datetime.utcnow)
    start_time: Optional[float] = field(default=None)
    end_time: Optional[float] = field(default=None)
    
    def __post_init__(self):
        """Sort steps by priority after initialization."""
        self.steps.sort(key=lambda s: s.priority)
    
    @property
    def latency(self) -> float:
        """Get total latency in milliseconds."""
        if self.start_time is None or self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time) * 1000
    
    @property
    def successful_steps(self) -> List[SagaStep]:
        """Get all successfully executed steps."""
        return [s for s in self.steps if s.status == SagaStepStatus.SUCCESS]
    
    @property
    def failed_steps(self) -> List[SagaStep]:
        """Get all failed steps."""
        return [s for s in self.steps if s.status == SagaStepStatus.FAILED]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary for logging/metrics."""
        return {
            "transaction_id": self.transaction_id,
            "status": self.status.value,
            "total_steps": len(self.steps),
            "successful_steps": len(self.successful_steps),
            "failed_steps": len(self.failed_steps),
            "latency_ms": self.latency,
            "created_at": self.created_at.isoformat(),
            "steps": [
                {
                    "name": s.name,
                    "status": s.status.value,
                    "latency_ms": s.latency,
                    "error": str(s.error) if s.error else None,
                }
                for s in self.steps
            ],
        }


class SagaOrchestrator:
    """
    Orchestrates distributed transactions using the Saga pattern.
    Executes steps sequentially and compensates on failure (LIFO rollback).
    """
    
    def __init__(self, transaction_id: str, steps: List[SagaStep]):
        """
        Initialize saga orchestrator.
        
        Args:
            transaction_id: Unique identifier for this transaction
            steps: List of SagaStep objects to execute
        """
        self.transaction = SagaTransaction(
            transaction_id=transaction_id,
            steps=steps,
        )
        self._compensations_executed: List[str] = []
    
    def execute(self) -> SagaTransaction:
        """
        Execute the saga transaction.
        Runs all steps in priority order.
        On failure, automatically compensates all successful steps (LIFO).
        
        Returns:
            SagaTransaction with final state
        """
        logger.info(f"🔄 Starting saga transaction {self.transaction.transaction_id}")
        self.transaction.status = SagaTransactionStatus.EXECUTING
        self.transaction.start_time = time.time()
        
        try:
            # Execute all steps in order
            for step in self.transaction.steps:
                if not self._execute_step(step):
                    # Step failed - start compensation
                    logger.error(f"❌ Step '{step.name}' failed in saga {self.transaction.transaction_id}")
                    self._compensate()
                    self.transaction.status = SagaTransactionStatus.FAILED
                    self.transaction.end_time = time.time()
                    return self.transaction
            
            # All steps succeeded
            self.transaction.status = SagaTransactionStatus.SUCCESS
            logger.info(f"✅ Saga transaction {self.transaction.transaction_id} completed successfully")
            
        except Exception as e:
            logger.error(f"💥 Unexpected error in saga {self.transaction.transaction_id}: {e}")
            self._compensate()
            self.transaction.status = SagaTransactionStatus.FAILED
        
        finally:
            self.transaction.end_time = time.time()
        
        return self.transaction
    
    def _execute_step(self, step: SagaStep) -> bool:
        """
        Execute a single step.
        
        Args:
            step: SagaStep to execute
            
        Returns:
            True if successful, False if failed
        """
        try:
            step.status = SagaStepStatus.EXECUTING
            step.start_time = time.time()
            
            # Execute the action
            result = step.action()
            
            step.result = result
            step.status = SagaStepStatus.SUCCESS
            step.end_time = time.time()
            
            logger.debug(f"✓ Step '{step.name}' succeeded ({step.latency:.1f}ms)")
            self._compensations_executed.append(step.name)
            
            return True
            
        except Exception as e:
            step.error = e
            step.status = SagaStepStatus.FAILED
            step.end_time = time.time()
            logger.error(f"✗ Step '{step.name}' failed: {e}")
            return False
    
    def _compensate(self):
        """
        Compensate for all successful steps in reverse order (LIFO).
        """
        logger.warning(f"🔄 Starting compensation for saga {self.transaction.transaction_id}")
        self.transaction.status = SagaTransactionStatus.COMPENSATING
        
        # Execute compensation in reverse order
        for step in reversed(self.transaction.steps):
            if step.status == SagaStepStatus.SUCCESS:
                self._execute_compensation(step)
        
        self.transaction.status = SagaTransactionStatus.COMPENSATED
        logger.info(f"✓ Compensation complete for saga {self.transaction.transaction_id}")
    
    def _execute_compensation(self, step: SagaStep):
        """
        Execute compensation for a single step.
        
        Args:
            step: SagaStep to compensate
        """
        try:
            step.status = SagaStepStatus.COMPENSATING
            step.start_time = time.time()
            
            # Execute the compensation action
            step.compensation(step.result)
            
            step.status = SagaStepStatus.COMPENSATED
            step.end_time = time.time()
            
            logger.debug(f"↶ Compensation for '{step.name}' succeeded ({step.latency:.1f}ms)")
            
        except Exception as e:
            logger.error(f"⚠️  Compensation for '{step.name}' failed: {e}")
            # Note: We don't re-raise here - compensation failures are logged but don't stop rollback


class SagaFactory:
    """Factory for creating and managing named saga patterns."""
    
    _sagas: Dict[str, type] = {}
    _metrics: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register_saga_type(cls, name: str, saga_class: type):
        """Register a saga type for creation."""
        cls._sagas[name] = saga_class
        cls._metrics[name] = {
            "total_executed": 0,
            "total_successful": 0,
            "total_failed": 0,
            "latency_sum": 0.0,
        }
    
    @classmethod
    def create_orchestrator(
        cls, 
        saga_name: str, 
        transaction_id: str, 
        steps: List[SagaStep]
    ) -> SagaOrchestrator:
        """Create a saga orchestrator instance."""
        if saga_name not in cls._sagas:
            raise ValueError(f"Unknown saga type: {saga_name}")
        
        return SagaOrchestrator(transaction_id, steps)
    
    @classmethod
    def execute_saga(
        cls,
        saga_name: str,
        transaction_id: str,
        steps: List[SagaStep],
    ) -> SagaTransaction:
        """Create and execute a saga in one call."""
        orchestrator = cls.create_orchestrator(saga_name, transaction_id, steps)
        transaction = orchestrator.execute()
        
        # Update metrics
        if saga_name in cls._metrics:
            metrics = cls._metrics[saga_name]
            metrics["total_executed"] += 1
            if transaction.status == SagaTransactionStatus.SUCCESS:
                metrics["total_successful"] += 1
            else:
                metrics["total_failed"] += 1
            metrics["latency_sum"] += transaction.latency
        
        return transaction
    
    @classmethod
    def get_metrics(cls, saga_name: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for a saga or all sagas."""
        if saga_name:
            if saga_name not in cls._metrics:
                return {}
            
            metrics = cls._metrics[saga_name]
            total = metrics["total_executed"]
            
            return {
                **metrics,
                "avg_latency_ms": metrics["latency_sum"] / total if total > 0 else 0.0,
                "success_rate": (metrics["total_successful"] / total * 100) if total > 0 else 0.0,
            }
        
        # Return all metrics
        result = {}
        for name, metrics in cls._metrics.items():
            total = metrics["total_executed"]
            result[name] = {
                **metrics,
                "avg_latency_ms": metrics["latency_sum"] / total if total > 0 else 0.0,
                "success_rate": (metrics["total_successful"] / total * 100) if total > 0 else 0.0,
            }
        
        return result
    
    @classmethod
    def reset_metrics(cls, saga_name: Optional[str] = None):
        """Reset metrics for a saga or all sagas."""
        if saga_name:
            if saga_name in cls._metrics:
                cls._metrics[saga_name] = {
                    "total_executed": 0,
                    "total_successful": 0,
                    "total_failed": 0,
                    "latency_sum": 0.0,
                }
        else:
            for name in cls._metrics:
                cls._metrics[name] = {
                    "total_executed": 0,
                    "total_successful": 0,
                    "total_failed": 0,
                    "latency_sum": 0.0,
                }
