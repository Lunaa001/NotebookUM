"""Tests for Redis Cache Service."""

import pytest
from datetime import timedelta
from unittest.mock import Mock, patch, MagicMock
import json
from app.services.cache_service import (
    CacheService,
    get_cache,
    cache_result,
    invalidate_cache,
    CACHE_TTL_DOCUMENT_TEXT,
    CACHE_TTL_SUMMARY,
)


@pytest.fixture
def redis_mock():
    """Mock Redis connection for testing."""
    with patch('app.services.cache_service.redis.Redis') as mock:
        yield mock


@pytest.fixture
def cache_service(redis_mock):
    """Create cache service with mocked Redis."""
    redis_instance = MagicMock()
    redis_instance.ping.return_value = True
    redis_instance.get.return_value = None
    redis_mock.return_value = redis_instance
    
    service = CacheService(auto_connect=True)
    service._redis = redis_instance
    service._connected = True
    
    return service


class TestCacheService:
    """Test CacheService basic operations."""
    
    def test_cache_service_initialization(self, redis_mock):
        """Test cache service initializes with correct parameters."""
        redis_instance = MagicMock()
        redis_instance.ping.return_value = True
        redis_mock.return_value = redis_instance
        
        service = CacheService(
            host="localhost",
            port=6379,
            db=0,
            auto_connect=True,
        )
        
        assert service.host == "localhost"
        assert service.port == 6379
        assert service.is_connected()
    
    def test_cache_get_hit(self, cache_service):
        """Test cache get returns value when key exists."""
        cache_service._redis.get.return_value = '{"data": "value"}'
        
        result = cache_service.get("test_key")
        
        assert result == {"data": "value"}
        assert cache_service._metrics["cache_hits"] == 1
        assert cache_service._metrics["total_gets"] == 1
    
    def test_cache_get_miss(self, cache_service):
        """Test cache get returns None when key doesn't exist."""
        cache_service._redis.get.return_value = None
        
        result = cache_service.get("test_key")
        
        assert result is None
        assert cache_service._metrics["cache_misses"] == 1
        assert cache_service._metrics["total_gets"] == 1
    
    def test_cache_set_with_ttl(self, cache_service):
        """Test cache set stores value with TTL."""
        value = {"id": 1, "name": "Test"}
        ttl = timedelta(hours=1)
        
        result = cache_service.set("doc:1", value, ttl=ttl)
        
        assert result is True
        cache_service._redis.setex.assert_called_once()
        call_args = cache_service._redis.setex.call_args
        assert call_args[0][0] == "doc:1"
        assert call_args[0][1] == 3600  # 1 hour in seconds
        assert cache_service._metrics["total_sets"] == 1
    
    def test_cache_set_without_ttl(self, cache_service):
        """Test cache set stores value without TTL."""
        value = "test_value"
        
        result = cache_service.set("key", value)
        
        assert result is True
        cache_service._redis.set.assert_called_once_with("key", "test_value")
    
    def test_cache_delete_single_key(self, cache_service):
        """Test cache delete removes single key."""
        result = cache_service.delete("test_key")
        
        assert result is True
        cache_service._redis.delete.assert_called_once_with("test_key")
        assert cache_service._metrics["total_deletes"] == 1
    
    def test_cache_delete_with_pattern(self, cache_service):
        """Test cache delete with wildcard pattern."""
        cache_service._redis.keys.return_value = ["doc:1", "doc:2", "doc:3"]
        
        result = cache_service.delete("doc:*")
        
        assert result is True
        cache_service._redis.keys.assert_called_once_with("doc:*")
        cache_service._redis.delete.assert_called_once_with("doc:1", "doc:2", "doc:3")
    
    def test_cache_exists(self, cache_service):
        """Test cache exists check."""
        cache_service._redis.exists.return_value = 1
        
        exists = cache_service.exists("test_key")
        
        assert exists is True
        cache_service._redis.exists.assert_called_once_with("test_key")
    
    def test_cache_get_ttl(self, cache_service):
        """Test cache TTL retrieval."""
        cache_service._redis.ttl.return_value = 3600
        
        ttl = cache_service.get_ttl("test_key")
        
        assert ttl == 3600
        cache_service._redis.ttl.assert_called_once_with("test_key")
    
    def test_cache_metrics(self, cache_service):
        """Test cache metrics calculation."""
        cache_service._metrics = {
            "total_gets": 10,
            "cache_hits": 7,
            "cache_misses": 3,
            "total_sets": 5,
            "total_deletes": 2,
            "errors": 0,
        }
        
        metrics = cache_service.get_metrics()
        
        assert metrics["cache_hits"] == 7
        assert metrics["cache_misses"] == 3
        assert metrics["hit_rate_percent"] == pytest.approx(70.0)
        assert metrics["connected"] is True


class TestCacheServiceDisconnected:
    """Test CacheService behavior when Redis is unavailable."""
    
    def test_cache_gracefully_handles_disconnection(self, redis_mock):
        """Test cache operations gracefully fail when Redis unavailable."""
        redis_instance = MagicMock()
        redis_instance.ping.side_effect = Exception("Connection refused")
        redis_mock.return_value = redis_instance
        
        service = CacheService(auto_connect=True)
        
        assert not service.is_connected()
        assert service.get("key") is None
        assert service.set("key", "value") is False
        assert service.delete("key") is False


class TestCacheDecorators:
    """Test cache decorators."""
    
    @patch('app.services.cache_service.get_cache')
    def test_cache_result_decorator_caches_result(self, mock_get_cache):
        """Test @cache_result decorator caches function result."""
        mock_cache = MagicMock()
        mock_cache.get.return_value = None  # Cache miss
        mock_get_cache.return_value = mock_cache
        
        call_count = 0
        
        @cache_result(ttl=timedelta(hours=1))
        def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call - should execute function and cache
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        mock_cache.set.assert_called_once()
    
    @patch('app.services.cache_service.get_cache')
    def test_cache_result_decorator_returns_cached_value(self, mock_get_cache):
        """Test @cache_result decorator returns cached value."""
        mock_cache = MagicMock()
        mock_cache.get.return_value = 20  # Cache hit
        mock_get_cache.return_value = mock_cache
        
        call_count = 0
        
        @cache_result(ttl=timedelta(hours=1))
        def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Call function
        result = expensive_function(5)
        
        # Should return cached value without calling function
        assert result == 20
        assert call_count == 0
        mock_cache.set.assert_not_called()
    
    @patch('app.services.cache_service.get_cache')
    def test_invalidate_cache_decorator(self, mock_get_cache):
        """Test @invalidate_cache decorator invalidates patterns."""
        mock_cache = MagicMock()
        mock_get_cache.return_value = mock_cache
        
        @invalidate_cache("document:*", "summary:*")
        def delete_document(doc_id: int):
            return f"deleted_{doc_id}"
        
        result = delete_document(123)
        
        assert result == "deleted_123"
        assert mock_cache.flush_pattern.call_count == 2
        mock_cache.flush_pattern.assert_any_call("document:*")
        mock_cache.flush_pattern.assert_any_call("summary:*")


class TestCacheServiceIntegration:
    """Integration tests for cache service."""
    
    def test_cache_flush_pattern(self, cache_service):
        """Test flushing cache by pattern."""
        cache_service._redis.keys.return_value = [
            "document:1:text",
            "document:1:metadata",
            "document:2:text",
        ]
        
        deleted = cache_service.flush_pattern("document:1:*")
        
        assert deleted == 3
        cache_service._redis.keys.assert_called_once_with("document:1:*")
        cache_service._redis.delete.assert_called_once()
    
    def test_cache_clear_all(self, cache_service):
        """Test clearing entire cache."""
        result = cache_service.clear_all()
        
        assert result is True
        cache_service._redis.flushdb.assert_called_once()
    
    def test_cache_reset_metrics(self, cache_service):
        """Test resetting cache metrics."""
        cache_service._metrics = {
            "total_gets": 100,
            "cache_hits": 70,
            "cache_misses": 30,
            "total_sets": 50,
            "total_deletes": 10,
            "errors": 2,
        }
        
        cache_service.reset_metrics()
        
        metrics = cache_service.get_metrics()
        assert metrics["total_gets"] == 0
        assert metrics["cache_hits"] == 0
        assert metrics["total_sets"] == 0
        assert metrics["hit_rate_percent"] == 0


class TestDocumentCaching:
    """Test caching for document operations."""
    
    def test_cache_document_text(self, cache_service):
        """Test caching extracted document text."""
        doc_id = 123
        text = "This is the extracted document text"
        
        # Mock the redis set and get to work together
        cache_store = {}
        
        def mock_setex(key, ttl, value):
            cache_store[key] = value
        
        def mock_set(key, value):
            cache_store[key] = value
        
        def mock_get(key):
            return cache_store.get(key)
        
        cache_service._redis.setex.side_effect = mock_setex
        cache_service._redis.set.side_effect = mock_set
        cache_service._redis.get.side_effect = mock_get
        
        cache_service.set(
            f"document:{doc_id}:text",
            text,
            ttl=CACHE_TTL_DOCUMENT_TEXT,
        )
        
        cached_text = cache_service.get(f"document:{doc_id}:text")
        assert cached_text == text
    
    def test_cache_document_metadata(self, cache_service):
        """Test caching document metadata."""
        doc_id = 123
        metadata = {
            "filename": "document.pdf",
            "size": 1024,
            "upload_date": "2024-01-01",
        }
        
        # Mock the redis set and get to work together
        cache_store = {}
        
        def mock_setex(key, ttl, value):
            cache_store[key] = value
        
        def mock_set(key, value):
            cache_store[key] = value
        
        def mock_get(key):
            return cache_store.get(key)
        
        cache_service._redis.setex.side_effect = mock_setex
        cache_service._redis.set.side_effect = mock_set
        cache_service._redis.get.side_effect = mock_get
        
        cache_service.set(
            f"document:{doc_id}:metadata",
            metadata,
            ttl=CACHE_TTL_DOCUMENT_TEXT,
        )
        
        cached_metadata = cache_service.get(f"document:{doc_id}:metadata")
        assert cached_metadata == metadata
    
    def test_cache_document_summary(self, cache_service):
        """Test caching document summary."""
        doc_id = 123
        summary = "This is a summary of the document"
        
        # Mock the redis set and get to work together
        cache_store = {}
        
        def mock_setex(key, ttl, value):
            cache_store[key] = value
        
        def mock_set(key, value):
            cache_store[key] = value
        
        def mock_get(key):
            return cache_store.get(key)
        
        cache_service._redis.setex.side_effect = mock_setex
        cache_service._redis.set.side_effect = mock_set
        cache_service._redis.get.side_effect = mock_get
        
        cache_service.set(
            f"summary:{doc_id}",
            summary,
            ttl=CACHE_TTL_SUMMARY,
        )
        
        cached_summary = cache_service.get(f"summary:{doc_id}")
        assert cached_summary == summary
    
    def test_cache_invalidation_on_document_delete(self, cache_service):
        """Test cache invalidation when document is deleted."""
        doc_id = 123
        cache_service._redis.keys.return_value = [
            f"document:{doc_id}:text",
            f"document:{doc_id}:metadata",
        ]
        
        # Simulate document deletion - flush document keys
        deleted = cache_service.flush_pattern(f"document:{doc_id}:*")
        
        # Then flush summary key
        cache_service._redis.keys.return_value = [f"summary:{doc_id}"]
        deleted += cache_service.flush_pattern(f"summary:{doc_id}")
        
        assert deleted == 3


class TestGetCacheGlobal:
    """Test global cache instance."""
    
    @patch('app.services.cache_service.CacheService')
    def test_get_cache_returns_singleton(self, mock_cache_class):
        """Test get_cache() returns same instance."""
        import app.services.cache_service as cache_module
        
        # Reset global instance
        cache_module._cache_instance = None
        
        # First call creates instance
        cache1 = get_cache()
        # Second call returns same instance
        cache2 = get_cache()
        
        assert cache1 is cache2
