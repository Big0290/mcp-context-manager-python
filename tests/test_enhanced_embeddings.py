#!/usr/bin/env python3
"""
Comprehensive tests for Enhanced Embedding Service
Tests all advanced features including multi-model support, caching, quality metrics, and ensemble methods.
"""

import asyncio
import pytest
import time
from typing import List

import numpy as np

# Import the enhanced embedding service
from mcp_memory_server.core.enhanced_embedding_service import (
    EnhancedEmbeddingService,
    ContentType,
    EmbeddingQuality,
    EmbeddingResult,
    ModelType
)


class TestEnhancedEmbeddingService:
    """Test suite for enhanced embedding service."""
    
    @pytest.fixture
    async def embedding_service(self):
        """Create an enhanced embedding service instance."""
        service = EnhancedEmbeddingService()
        return service
    
    @pytest.fixture
    def sample_texts(self):
        """Sample texts for testing different content types."""
        return {
            'code': '''
def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
            ''',
            'error_message': 'Error: ModuleNotFoundError: No module named "requests"',
            'documentation': 'This function calculates the Fibonacci sequence using recursion.',
            'commit_message': 'feat: add enhanced embedding service with multi-model support',
            'issue_description': 'Bug: Memory leak in embedding cache causing high memory usage',
            'general_text': 'The quick brown fox jumps over the lazy dog.'
        }
    
    @pytest.mark.asyncio
    async def test_content_type_detection(self, embedding_service, sample_texts):
        """Test automatic content type detection."""
        
        # Test code detection
        content_type = embedding_service._detect_content_type(sample_texts['code'])
        assert content_type == ContentType.CODE
        
        # Test error message detection
        content_type = embedding_service._detect_content_type(sample_texts['error_message'])
        assert content_type == ContentType.ERROR_MESSAGE
        
        # Test documentation detection
        content_type = embedding_service._detect_content_type(sample_texts['documentation'])
        assert content_type == ContentType.DOCUMENTATION
        
        # Test commit message detection
        content_type = embedding_service._detect_content_type(sample_texts['commit_message'])
        assert content_type == ContentType.COMMIT_MESSAGE
        
        # Test issue description detection
        content_type = embedding_service._detect_content_type(sample_texts['issue_description'])
        assert content_type == ContentType.ISSUE_DESCRIPTION
        
        # Test general text detection
        content_type = embedding_service._detect_content_type(sample_texts['general_text'])
        assert content_type == ContentType.TEXT
    
    @pytest.mark.asyncio
    async def test_optimal_model_selection(self, embedding_service):
        """Test optimal model selection based on content type."""
        
        # Test code model selection
        model = embedding_service._select_optimal_model(ContentType.CODE, 100)
        assert 'codebert' in model.lower() or 'all-MiniLM' in model
        
        # Test long text model selection
        model = embedding_service._select_optimal_model(ContentType.TEXT, 1500)
        assert 'large' in model or 'mpnet' in model or 'all-MiniLM' in model
        
        # Test default model selection
        model = embedding_service._select_optimal_model(ContentType.TEXT, 100)
        assert 'all-MiniLM' in model
    
    @pytest.mark.asyncio
    async def test_basic_embedding_generation(self, embedding_service, sample_texts):
        """Test basic embedding generation with different content types."""
        
        # Test code embedding
        result = await embedding_service.generate_embedding(sample_texts['code'])
        assert isinstance(result, EmbeddingResult)
        assert len(result.embedding) > 0
        assert result.content_type == ContentType.CODE
        assert result.model_used != "none"
        assert result.generation_time >= 0
        
        # Test text embedding
        result = await embedding_service.generate_embedding(sample_texts['general_text'])
        assert isinstance(result, EmbeddingResult)
        assert len(result.embedding) > 0
        assert result.content_type == ContentType.TEXT
        
        # Test error message embedding
        result = await embedding_service.generate_embedding(sample_texts['error_message'])
        assert isinstance(result, EmbeddingResult)
        assert result.content_type == ContentType.ERROR_MESSAGE
    
    @pytest.mark.asyncio
    async def test_embedding_caching(self, embedding_service, sample_texts):
        """Test embedding caching functionality."""
        
        text = sample_texts['general_text']
        
        # Generate embedding first time (should not be cached)
        result1 = await embedding_service.generate_embedding(text, use_cache=True)
        assert not result1.cache_hit
        
        # Generate embedding second time (should be cached)
        result2 = await embedding_service.generate_embedding(text, use_cache=True)
        assert result2.cache_hit
        
        # Verify embeddings are identical
        assert result1.embedding == result2.embedding
        
        # Test without cache
        result3 = await embedding_service.generate_embedding(text, use_cache=False)
        assert not result3.cache_hit
    
    @pytest.mark.asyncio
    async def test_quality_metrics(self, embedding_service, sample_texts):
        """Test embedding quality metrics calculation."""
        
        result = await embedding_service.generate_embedding(sample_texts['code'])
        
        assert isinstance(result.quality, EmbeddingQuality)
        assert 0 <= result.quality.confidence <= 1
        assert 0 <= result.quality.coherence <= 1
        assert 0 <= result.quality.diversity <= 1
        assert 0 <= result.quality.semantic_richness <= 1
        assert 0 <= result.quality.model_confidence <= 1
    
    @pytest.mark.asyncio
    async def test_ensemble_embedding(self, embedding_service, sample_texts):
        """Test ensemble embedding generation."""
        
        result = await embedding_service.generate_ensemble_embedding(sample_texts['code'])
        
        assert isinstance(result, EmbeddingResult)
        assert result.model_used == "ensemble"
        assert len(result.embedding) > 0
        assert result.quality.confidence >= 0.8  # Ensemble should have high confidence
    
    @pytest.mark.asyncio
    async def test_batch_embedding_generation(self, embedding_service, sample_texts):
        """Test batch embedding generation."""
        
        texts = list(sample_texts.values())
        results = await embedding_service.batch_generate_embeddings(texts)
        
        assert len(results) == len(texts)
        for result in results:
            assert isinstance(result, EmbeddingResult)
            assert len(result.embedding) > 0
    
    @pytest.mark.asyncio
    async def test_similarity_calculation(self, embedding_service, sample_texts):
        """Test similarity calculation between embeddings."""
        
        # Generate embeddings for similar texts
        text1 = "Python function to calculate fibonacci"
        text2 = "Function that computes fibonacci numbers in Python"
        
        result1 = await embedding_service.generate_embedding(text1)
        result2 = await embedding_service.generate_embedding(text2)
        
        similarity = embedding_service.calculate_similarity(
            result1.embedding, result2.embedding
        )
        
        assert 0 <= similarity <= 1
        # Similar texts should have higher similarity
        assert similarity > 0.5
    
    @pytest.mark.asyncio
    async def test_performance_stats(self, embedding_service, sample_texts):
        """Test performance statistics tracking."""
        
        # Generate some embeddings
        await embedding_service.generate_embedding(sample_texts['code'])
        await embedding_service.generate_embedding(sample_texts['general_text'])
        
        stats = embedding_service.get_performance_stats()
        
        assert 'total_requests' in stats
        assert 'cache_hits' in stats
        assert 'cache_hit_rate' in stats
        assert 'model_usage' in stats
        assert stats['total_requests'] >= 2
    
    @pytest.mark.asyncio
    async def test_available_models(self, embedding_service):
        """Test getting available models."""
        
        models = embedding_service.get_available_models()
        
        assert isinstance(models, dict)
        assert len(models) > 0
        
        # Check that some expected models are available
        expected_models = ['all-MiniLM-L6-v2']
        for model in expected_models:
            if model in models:
                assert 'dimensions' in models[model]
                assert 'type' in models[model]
    
    @pytest.mark.asyncio
    async def test_embedding_dimensions(self, embedding_service):
        """Test getting embedding dimensions for different models."""
        
        # Test default model dimension
        dimension = embedding_service.get_embedding_dimension('all-MiniLM-L6-v2')
        assert dimension == 384
        
        # Test ensemble dimension
        dimension = embedding_service.get_embedding_dimension('ensemble')
        assert dimension == 384
        
        # Test fallback dimension
        dimension = embedding_service.get_embedding_dimension('unknown-model')
        assert dimension == 384
    
    @pytest.mark.asyncio
    async def test_error_handling(self, embedding_service):
        """Test error handling for invalid inputs."""
        
        # Test empty text
        result = await embedding_service.generate_embedding("")
        assert len(result.embedding) == 0
        assert result.model_used == "none"
        
        # Test None text
        result = await embedding_service.generate_embedding(None)
        assert len(result.embedding) == 0
        
        # Test whitespace-only text
        result = await embedding_service.generate_embedding("   \n\t   ")
        assert len(result.embedding) == 0
    
    @pytest.mark.asyncio
    async def test_model_specific_embeddings(self, embedding_service, sample_texts):
        """Test generating embeddings with specific models."""
        
        # Test with specific model
        result = await embedding_service.generate_embedding(
            sample_texts['code'], 
            model_name='all-MiniLM-L6-v2'
        )
        assert result.model_used == 'all-MiniLM-L6-v2'
        
        # Test with content type override
        result = await embedding_service.generate_embedding(
            sample_texts['general_text'],
            content_type=ContentType.CODE
        )
        assert result.content_type == ContentType.CODE
    
    @pytest.mark.asyncio
    async def test_quality_thresholds(self, embedding_service, sample_texts):
        """Test quality threshold validation."""
        
        result = await embedding_service.generate_embedding(sample_texts['code'])
        
        # Test that quality metrics meet minimum thresholds
        assert result.quality.confidence >= 0.0
        assert result.quality.coherence >= 0.0
        assert result.quality.diversity >= 0.0
        assert result.quality.semantic_richness >= 0.0
        assert result.quality.model_confidence >= 0.0


class TestEmbeddingCache:
    """Test suite for embedding cache functionality."""
    
    @pytest.fixture
    async def cache(self):
        """Create an embedding cache instance."""
        from mcp_memory_server.core.enhanced_embedding_service import EmbeddingCache
        return EmbeddingCache()
    
    @pytest.mark.asyncio
    async def test_cache_operations(self, cache):
        """Test basic cache operations."""
        
        text = "Test text for caching"
        model = "test-model"
        content_type = ContentType.TEXT
        embedding = [0.1, 0.2, 0.3, 0.4]
        
        # Test cache miss
        cached = await cache.get(text, model, content_type)
        assert cached is None
        
        # Test cache set and get
        await cache.set(text, model, content_type, embedding)
        cached = await cache.get(text, model, content_type)
        assert cached == embedding
        
        # Test cache key uniqueness
        cached = await cache.get(text, "different-model", content_type)
        assert cached is None
    
    @pytest.mark.asyncio
    async def test_cache_ttl(self, cache):
        """Test cache TTL functionality."""
        
        text = "Test text for TTL"
        model = "test-model"
        content_type = ContentType.TEXT
        embedding = [0.1, 0.2, 0.3]
        
        # Set with short TTL
        cache.cache_ttl = 1  # 1 second
        await cache.set(text, model, content_type, embedding)
        
        # Should be available immediately
        cached = await cache.get(text, model, content_type)
        assert cached == embedding
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Should be expired
        cached = await cache.get(text, model, content_type)
        assert cached is None


class TestContentTypeDetection:
    """Test suite for content type detection."""
    
    @pytest.fixture
    def embedding_service(self):
        """Create embedding service for content type detection."""
        return EnhancedEmbeddingService()
    
    def test_code_detection(self, embedding_service):
        """Test code content type detection."""
        
        code_samples = [
            "def hello_world():",
            "function calculate() {",
            "const x = 5;",
            "import numpy as np",
            "class MyClass:",
            "if (condition) {",
            "for i in range(10):",
            "return value;"
        ]
        
        for code in code_samples:
            content_type = embedding_service._detect_content_type(code)
            assert content_type == ContentType.CODE
    
    def test_error_detection(self, embedding_service):
        """Test error message content type detection."""
        
        error_samples = [
            "Error: Module not found",
            "Exception: Invalid input",
            "Traceback (most recent call last):",
            "Failed to connect to database",
            "Error occurred while processing"
        ]
        
        for error in error_samples:
            content_type = embedding_service._detect_content_type(error)
            assert content_type == ContentType.ERROR_MESSAGE
    
    def test_documentation_detection(self, embedding_service):
        """Test documentation content type detection."""
        
        doc_samples = [
            "This function calculates the fibonacci sequence",
            "API documentation for the user service",
            "Tutorial on how to use the library",
            "Reference guide for developers",
            "Documentation for the new feature"
        ]
        
        for doc in doc_samples:
            content_type = embedding_service._detect_content_type(doc)
            assert content_type == ContentType.DOCUMENTATION


# Performance benchmarks
class TestEmbeddingPerformance:
    """Performance benchmarks for embedding service."""
    
    @pytest.fixture
    async def embedding_service(self):
        """Create embedding service for performance testing."""
        return EnhancedEmbeddingService()
    
    @pytest.mark.asyncio
    async def test_generation_speed(self, embedding_service):
        """Test embedding generation speed."""
        
        text = "This is a test text for performance benchmarking."
        
        start_time = time.time()
        result = await embedding_service.generate_embedding(text)
        generation_time = time.time() - start_time
        
        # Should complete within reasonable time (5 seconds)
        assert generation_time < 5.0
        assert result.generation_time > 0
    
    @pytest.mark.asyncio
    async def test_batch_performance(self, embedding_service):
        """Test batch embedding generation performance."""
        
        texts = [f"Test text {i} for batch processing." for i in range(10)]
        
        start_time = time.time()
        results = await embedding_service.batch_generate_embeddings(texts)
        batch_time = time.time() - start_time
        
        # Batch should be faster than individual calls
        assert len(results) == 10
        assert batch_time < 10.0  # Should complete within 10 seconds
    
    @pytest.mark.asyncio
    async def test_cache_performance(self, embedding_service):
        """Test cache performance benefits."""
        
        text = "Text for cache performance testing"
        
        # First call (no cache)
        start_time = time.time()
        result1 = await embedding_service.generate_embedding(text, use_cache=True)
        first_call_time = time.time() - start_time
        
        # Second call (with cache)
        start_time = time.time()
        result2 = await embedding_service.generate_embedding(text, use_cache=True)
        second_call_time = time.time() - start_time
        
        # Cached call should be much faster
        assert second_call_time < first_call_time
        assert result2.cache_hit


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 