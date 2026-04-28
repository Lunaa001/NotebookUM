"""Tests for Circuit Breaker Pattern implementation."""

import pytest
import time
from unittest.mock import MagicMock, patch, Mock
from pybreaker import CircuitBreakerError
from app.services.circuit_breaker_service import CircuitBreakerService, CircuitBreakerFactory
from app.services.ai_service import AIService


class TestCircuitBreakerService:
    """Tests for CircuitBreakerService"""
    
    def test_circuit_breaker_initial_state_closed(self):
        """Test that circuit breaker starts in CLOSED state"""
        breaker = CircuitBreakerService("test", fail_max=3, reset_timeout=10)
        assert breaker.is_closed
        assert not breaker.is_open
        assert "closed" in breaker.state
    
    def test_circuit_breaker_successful_call(self):
        """Test successful call increments success counter"""
        breaker = CircuitBreakerService("test", fail_max=3, reset_timeout=10)
        
        def success_func():
            return "success"
        
        result = breaker.call(success_func)
        
        assert result == "success"
        assert breaker.is_closed
        assert breaker._metrics["successful_calls"] == 1
        assert breaker._metrics["total_calls"] == 1
    
    def test_circuit_breaker_opens_after_failures(self):
        """Test that circuit breaker opens after reaching fail_max"""
        breaker = CircuitBreakerService("test_open", fail_max=3, reset_timeout=1)
        
        def failing_func():
            raise ValueError("Test error")
        
        # Fail 3 times (should open after 3rd failure)
        for i in range(3):
            with pytest.raises((ValueError, CircuitBreakerError)):
                breaker.call(failing_func)
        
        # Circuit should be open now
        assert breaker.is_open
        assert breaker._metrics["failed_calls"] >= 1
    
    def test_circuit_breaker_rejects_when_open(self):
        """Test that circuit breaker rejects calls when OPEN"""
        breaker = CircuitBreakerService("test_reject", fail_max=1, reset_timeout=1)
        
        def failing_func():
            raise ValueError("Test error")
        
        # Fail once to open circuit
        with pytest.raises((ValueError, CircuitBreakerError)):
            breaker.call(failing_func)
        
        # Circuit is now open
        assert breaker.is_open
        initial_rejected = breaker._metrics["rejected_calls"]
        
        # Next call should be rejected immediately with CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            breaker.call(failing_func)
        
        # Should have incremented rejected counter or failed counter
        assert (breaker._metrics["rejected_calls"] > initial_rejected or 
                breaker._metrics["failed_calls"] > 1)
    
    def test_circuit_breaker_metrics(self):
        """Test circuit breaker metrics calculation"""
        breaker = CircuitBreakerService("test")
        
        def success_func():
            return "ok"
        
        def fail_func():
            raise ValueError("error")
        
        # Execute 3 successful calls
        for _ in range(3):
            breaker.call(success_func)
        
        metrics = breaker.metrics
        assert metrics["total_calls"] == 3
        assert metrics["successful_calls"] == 3
        assert metrics["failed_calls"] == 0
        assert "success_rate" in metrics
        assert "avg_latency_ms" in metrics
    
    def test_circuit_breaker_reset(self):
        """Test manual reset of circuit breaker"""
        breaker = CircuitBreakerService("test_reset", fail_max=1, reset_timeout=1)
        
        def failing_func():
            raise ValueError("error")
        
        # Fail to open circuit
        with pytest.raises((ValueError, CircuitBreakerError)):
            breaker.call(failing_func)
        
        assert breaker.is_open
        
        # Reset
        breaker.reset()
        
        # Should be closed again
        assert breaker.is_closed
        assert breaker._metrics["total_calls"] == 0


class TestAIServiceWithCircuitBreaker:
    """Tests for AIService with Circuit Breaker integration"""
    
    @patch('app.services.ai_service.requests.post')
    def test_ai_service_uses_circuit_breaker(self, mock_post):
        """Test that AIService uses circuit breaker for API calls"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test summary"}}]
        }
        mock_post.return_value = mock_response
        
        ai_service = AIService(api_key="test-key")
        
        # First call should succeed
        result = ai_service.generate_summary("Test text")
        assert result == "Test summary"
        
        # Circuit breaker should be in CLOSED state
        assert ai_service.circuit_breaker.is_closed
    
    @patch('app.services.ai_service.requests.post')
    def test_ai_service_circuit_breaker_opens_on_failures(self, mock_post):
        """Test that circuit breaker opens after repeated API failures"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        # Use unique name for this test's circuit breaker
        ai_service = AIService(api_key="test-key")
        ai_service.circuit_breaker = CircuitBreakerService("test_ai_fail", fail_max=2, reset_timeout=1)
        
        # Fail 2 times to open circuit
        for i in range(2):
            with pytest.raises((ValueError, CircuitBreakerError)):
                ai_service.generate_summary("Test text")
        
        # Circuit should be open
        assert ai_service.circuit_breaker.is_open
        
        # Next call should fail with CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            ai_service.generate_summary("Test text")
    
    @patch('app.services.ai_service.requests.post')
    def test_ai_service_circuit_breaker_metrics(self, mock_post):
        """Test circuit breaker metrics in AIService"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Summary"}}]
        }
        mock_post.return_value = mock_response
        
        ai_service = AIService(api_key="test-key")
        # Reset circuit breaker for clean test
        CircuitBreakerFactory._breakers.pop("gemma4_api", None)
        ai_service.circuit_breaker = CircuitBreakerService("test_ai_metrics", fail_max=5)
        
        # Make successful calls
        for _ in range(2):
            ai_service.generate_summary("Test text")
        
        metrics = ai_service.circuit_breaker.metrics
        assert metrics["total_calls"] >= 2
        assert metrics["successful_calls"] >= 2


class TestCircuitBreakerFactory:
    """Tests for CircuitBreakerFactory"""
    
    def test_factory_creates_circuit_breaker(self):
        """Test that factory creates circuit breaker"""
        factory = CircuitBreakerFactory
        
        # Clear existing breakers
        factory._breakers.clear()
        
        breaker = factory.get_or_create("test_api")
        
        assert breaker is not None
        assert breaker.name == "test_api"
    
    def test_factory_returns_same_instance(self):
        """Test that factory returns same instance for same name"""
        factory = CircuitBreakerFactory
        factory._breakers.clear()
        
        breaker1 = factory.get_or_create("same_api")
        breaker2 = factory.get_or_create("same_api")
        
        assert breaker1 is breaker2
    
    def test_factory_get_all_metrics(self):
        """Test factory returns metrics for all circuit breakers"""
        factory = CircuitBreakerFactory
        factory._breakers.clear()
        
        breaker1 = factory.get_or_create("api1")
        breaker2 = factory.get_or_create("api2")
        
        all_metrics = factory.get_all_metrics()
        
        assert "api1" in all_metrics
        assert "api2" in all_metrics
        assert "closed" in all_metrics["api1"]["state"]
        assert "closed" in all_metrics["api2"]["state"]
    
    def test_factory_reset_all(self):
        """Test factory resets all circuit breakers"""
        factory = CircuitBreakerFactory
        factory._breakers.clear()
        
        breaker1 = factory.get_or_create("api1", fail_max=1)
        breaker2 = factory.get_or_create("api2", fail_max=1)
        
        # Open both by failing
        def fail_func():
            raise ValueError("error")
        
        with pytest.raises((ValueError, CircuitBreakerError)):
            breaker1.call(fail_func)
        with pytest.raises((ValueError, CircuitBreakerError)):
            breaker2.call(fail_func)
        
        # Both should be open
        assert breaker1.is_open
        assert breaker2.is_open
        
        # Reset all
        factory.reset_all()
        
        # All should be closed
        assert breaker1.is_closed
        assert breaker2.is_closed
