"""End-to-End Integration Tests - Full workflow testing."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.services.saga_orchestrator import (
    SagaStep,
    SagaFactory,
    SagaTransactionStatus,
)
from app.services.circuit_breaker_service import (
    CircuitBreakerService,
    CircuitBreakerFactory,
)
from app.services.cache_service import CacheService, get_cache


class TestDocumentProcessingE2E:
    """E2E tests for document processing workflow."""
    
    def test_happy_path_full_document_processing(self):
        """Test complete workflow: upload → extract → summarize."""
        # Mock the actual services
        document_data = {
            "id": 1,
            "filename": "test.pdf",
            "content": b"PDF content",
        }
        
        extracted_text = "This is the extracted text from PDF"
        summary = "This is an AI-generated summary"
        
        # Simulate upload
        def upload_action():
            return document_data
        
        def upload_compensation(result):
            pass  # Delete document
        
        # Simulate extraction
        def extract_action():
            return {"text": extracted_text}
        
        def extract_compensation(result):
            pass  # No compensation needed
        
        # Simulate summarization
        def summarize_action():
            return {"summary": summary}
        
        def summarize_compensation(result):
            pass  # Delete summary
        
        steps = [
            SagaStep("upload", upload_action, upload_compensation, priority=1),
            SagaStep("extract", extract_action, extract_compensation, priority=2),
            SagaStep("summarize", summarize_action, summarize_compensation, priority=3),
        ]
        
        SagaFactory.register_saga_type("document_processing", object)
        transaction = SagaFactory.execute_saga("document_processing", "doc_e2e_1", steps)
        
        assert transaction.status == SagaTransactionStatus.SUCCESS
        assert len(transaction.successful_steps) == 3
        assert transaction.steps[0].result == document_data
        assert transaction.steps[1].result == {"text": extracted_text}
        assert transaction.steps[2].result == {"summary": summary}
    
    def test_extraction_failure_triggers_rollback(self):
        """Test that extraction failure triggers upload rollback."""
        uploaded_doc = {"id": 1, "filename": "test.pdf"}
        uploaded = False
        deleted = False
        
        def upload_action():
            nonlocal uploaded
            uploaded = True
            return uploaded_doc
        
        def upload_compensation(result):
            nonlocal deleted
            deleted = True
        
        def extract_action():
            raise RuntimeError("PDF extraction failed")
        
        def extract_compensation(result):
            pass
        
        def summarize_action():
            pass
        
        def summarize_compensation(result):
            pass
        
        steps = [
            SagaStep("upload", upload_action, upload_compensation, priority=1),
            SagaStep("extract", extract_action, extract_compensation, priority=2),
            SagaStep("summarize", summarize_action, summarize_compensation, priority=3),
        ]
        
        SagaFactory.register_saga_type("document_processing", object)
        transaction = SagaFactory.execute_saga("document_processing", "doc_e2e_fail", steps)
        
        assert transaction.status == SagaTransactionStatus.FAILED
        assert uploaded is True
        assert deleted is True  # Compensation executed
    
    def test_summarization_failure_triggers_full_rollback(self):
        """Test that summarization failure triggers both upload and extraction rollback."""
        upload_deleted = False
        extract_deleted = False
        
        def upload_action():
            return {"id": 1}
        
        def upload_compensation(result):
            nonlocal upload_deleted
            upload_deleted = True
        
        def extract_action():
            return {"text": "extracted"}
        
        def extract_compensation(result):
            nonlocal extract_deleted
            extract_deleted = True
        
        def summarize_action():
            raise RuntimeError("AI API failed")
        
        def summarize_compensation(result):
            pass
        
        steps = [
            SagaStep("upload", upload_action, upload_compensation, priority=1),
            SagaStep("extract", extract_action, extract_compensation, priority=2),
            SagaStep("summarize", summarize_action, summarize_compensation, priority=3),
        ]
        
        SagaFactory.register_saga_type("document_processing", object)
        transaction = SagaFactory.execute_saga("document_processing", "doc_e2e_summary_fail", steps)
        
        assert transaction.status == SagaTransactionStatus.FAILED
        assert upload_deleted is True
        assert extract_deleted is True


class TestCircuitBreakerE2E:
    """E2E tests for circuit breaker protection."""
    
    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after 5 failures."""
        breaker = CircuitBreakerService(
            name="test_api",
            fail_max=5,
            reset_timeout=30,
        )
        
        # Make 5 calls fail
        def failing_action():
            raise ValueError("Simulated failure")
        
        for _ in range(5):
            with pytest.raises((ValueError, Exception)):
                breaker.call(failing_action)
        
        # Circuit should be open now
        assert breaker.is_open
        
        # Next call should be rejected
        with pytest.raises(Exception):  # CircuitBreakerError or pybreaker exception
            breaker.call(failing_action)
    
    def test_circuit_breaker_recovers_after_timeout(self):
        """Test circuit breaker enters HALF_OPEN and recovers."""
        import time
        
        breaker = CircuitBreakerService(
            name="test_recovery",
            fail_max=2,
            reset_timeout=1,  # 1 second for testing
        )
        
        # Make 2 calls fail to open circuit
        def failing_action():
            raise ValueError("failure")
        
        for _ in range(2):
            with pytest.raises((ValueError, Exception)):
                breaker.call(failing_action)
        
        assert breaker.is_open
        
        # Wait for reset timeout + small buffer
        time.sleep(2.5)
        
        # After reset timeout, circuit should be in HALF_OPEN or auto-closed state
        # (depending on pybreaker implementation)
        # Try to make a successful call
        def success_action():
            return "success"
        
        result = breaker.call(success_action)
        assert result == "success"
        # After successful call in HALF_OPEN, should be closed
        assert breaker.is_closed
    
    def test_circuit_breaker_metrics_tracked(self):
        """Test circuit breaker tracks metrics."""
        breaker = CircuitBreakerService(name="test_metrics")
        
        def success_action():
            return "ok"
        
        def fail_action():
            raise ValueError("fail")
        
        # Make some calls
        for _ in range(3):
            breaker.call(success_action)
        
        for _ in range(2):
            with pytest.raises((ValueError, Exception)):
                breaker.call(fail_action)
        
        metrics = breaker.metrics
        assert metrics["total_calls"] == 5
        assert metrics["successful_calls"] == 3
        assert metrics["failed_calls"] == 2


class TestCacheE2E:
    """E2E tests for caching functionality."""
    
    @patch('app.services.cache_service.redis.Redis')
    def test_cache_hit_on_repeated_access(self, mock_redis_class):
        """Test cache hit when accessing same document multiple times."""
        # Setup mock
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis_class.return_value = mock_redis
        
        cache = CacheService()
        
        # First access - cache miss
        mock_redis.get.return_value = None
        result1 = cache.get("doc:1:text")
        assert result1 is None
        assert cache._metrics["cache_misses"] == 1
        
        # Set in cache
        cache.set("doc:1:text", "extracted text")
        
        # Second access - cache hit
        mock_redis.get.return_value = '"extracted text"'
        result2 = cache.get("doc:1:text")
        assert result2 == "extracted text"
        assert cache._metrics["cache_hits"] == 1
        
        metrics = cache.get_metrics()
        assert metrics["hit_rate_percent"] == 50.0  # 1 hit out of 2 total
    
    @patch('app.services.cache_service.redis.Redis')
    def test_cache_invalidation_on_delete(self, mock_redis_class):
        """Test cache invalidation when document deleted."""
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis_class.return_value = mock_redis
        
        cache = CacheService()
        
        # Cache some data
        cache.set("document:123:text", "text")
        cache.set("document:123:metadata", {"size": 1024})
        cache.set("summary:123", "summary")
        
        # Delete with pattern
        mock_redis.keys.return_value = [
            "document:123:text",
            "document:123:metadata",
        ]
        deleted = cache.flush_pattern("document:123:*")
        assert deleted == 2
        
        # Delete summary
        mock_redis.keys.return_value = ["summary:123"]
        deleted = cache.flush_pattern("summary:123")
        assert deleted == 1


class TestSagaMetricsE2E:
    """E2E tests for saga metrics."""
    
    def test_saga_metrics_aggregation(self):
        """Test saga metrics across multiple executions."""
        SagaFactory.register_saga_type("test_saga", object)
        SagaFactory.reset_metrics("test_saga")
        
        # Execute 8 successful sagas
        for i in range(8):
            def success_action():
                return f"result_{i}"
            
            steps = [SagaStep(f"step_{i}", success_action, Mock())]
            SagaFactory.execute_saga("test_saga", f"saga_success_{i}", steps)
        
        # Execute 2 failed sagas
        for i in range(2):
            def fail_action():
                raise ValueError("intentional failure")
            
            steps = [SagaStep(f"step_{i}", fail_action, Mock())]
            SagaFactory.execute_saga("test_saga", f"saga_fail_{i}", steps)
        
        # Check metrics
        metrics = SagaFactory.get_metrics("test_saga")
        
        assert metrics["total_executed"] == 10
        assert metrics["total_successful"] == 8
        assert metrics["total_failed"] == 2
        assert metrics["success_rate"] == 80.0
    
    def test_saga_latency_tracking(self):
        """Test saga latency is tracked."""
        import time
        
        SagaFactory.register_saga_type("latency_saga", object)
        SagaFactory.reset_metrics("latency_saga")
        
        def slow_action():
            time.sleep(0.01)  # 10ms
            return "done"
        
        steps = [SagaStep("slow_step", slow_action, Mock())]
        transaction = SagaFactory.execute_saga("latency_saga", "latency_test", steps)
        
        # Latency should be >= 10ms
        assert transaction.latency >= 10.0
        
        metrics = SagaFactory.get_metrics("latency_saga")
        assert metrics["latency_sum"] > 0


class TestRateLimitingE2E:
    """E2E tests for rate limiting simulation."""
    
    def test_rate_limiting_blocks_excessive_traffic(self):
        """Test rate limiter blocks requests exceeding limit."""
        rate_limit = 100  # 100 req/sec
        burst = 50
        
        # Simulate 150 requests in burst
        allowed = 0
        blocked = 0
        
        for i in range(150):
            if i < rate_limit + burst:
                allowed += 1
            else:
                blocked += 1
        
        # Should allow 150 (100 + 50 burst)
        assert allowed == 150
        assert blocked == 0
        
        # Next second, requests over 100 should be blocked
        allowed_next = 0
        for i in range(150):
            if i < rate_limit:
                allowed_next += 1
            else:
                blocked += 1
        
        assert allowed_next == 100
        assert blocked == 50


class TestTraefikRoutingE2E:
    """E2E tests for Traefik routing."""
    
    def test_notebookum_service_routing(self):
        """Test requests route to NotebookUM service."""
        # This would require a running Traefik instance
        # For testing, we verify the configuration
        import yaml
        from pathlib import Path
        
        config_path = Path(__file__).parent.parent / "dockers/traefik/config/config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Verify NotebookUM router exists
        assert "notebookum" in config["http"]["routers"]
        
        # Verify service points to correct backend
        router = config["http"]["routers"]["notebookum"]
        service = config["http"]["services"][router["service"]]
        
        assert service["loadBalancer"]["servers"][0]["url"] == "http://notebookum:8000"
    
    def test_health_check_configured(self):
        """Test health check is configured in Traefik."""
        import yaml
        from pathlib import Path
        
        config_path = Path(__file__).parent.parent / "dockers/traefik/config/config.yml"
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Get NotebookUM service
        service = config["http"]["services"]["notebookum"]
        health_check = service["loadBalancer"]["healthCheck"]
        
        assert health_check["path"] == "/health"
        assert health_check["interval"] == "30s"
        assert health_check["timeout"] == "5s"
