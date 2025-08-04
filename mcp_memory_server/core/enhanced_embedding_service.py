#!/usr/bin/env python3
"""
Enhanced Embedding Service with Advanced Features
Supports multiple embedding models, domain-specific models, caching, and quality metrics.
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

import numpy as np
from pydantic import BaseModel

# Optional imports for advanced features
try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from mcp_memory_server.config import settings


class ModelType(str, Enum):
    """Types of embedding models supported."""
    OPENAI = "openai"
    SENTENCE_TRANSFORMERS = "sentence-transformers"
    CODE_BERT = "code-bert"
    GRAPHCODE_BERT = "graphcode-bert"
    MULTI_MODAL = "multi-modal"
    ENSEMBLE = "ensemble"
    FALLBACK = "fallback"


class ContentType(str, Enum):
    """Types of content for domain-specific embeddings."""
    CODE = "code"
    TEXT = "text"
    DOCUMENTATION = "documentation"
    ERROR_MESSAGE = "error_message"
    COMMIT_MESSAGE = "commit_message"
    ISSUE_DESCRIPTION = "issue_description"
    MIXED = "mixed"


@dataclass
class EmbeddingQuality:
    """Quality metrics for embeddings."""
    confidence: float = 0.0
    coherence: float = 0.0
    diversity: float = 0.0
    semantic_richness: float = 0.0
    model_confidence: float = 0.0


@dataclass
class EmbeddingResult:
    """Result of embedding generation with metadata."""
    embedding: List[float]
    model_used: str
    content_type: ContentType
    quality: EmbeddingQuality
    generation_time: float
    cache_hit: bool = False
    metadata: Dict[str, Any] = None


class EmbeddingCache:
    """Intelligent caching system for embeddings."""
    
    def __init__(self, cache_ttl: int = 3600):
        self.cache_ttl = cache_ttl
        self.memory_cache = {}
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection if available."""
        if REDIS_AVAILABLE and hasattr(settings, 'redis_url'):
            try:
                self.redis_client = redis.from_url(settings.redis_url)
                self.redis_client.ping()
            except Exception as e:
                logging.warning(f"Redis not available: {e}")
                self.redis_client = None
    
    def _generate_cache_key(self, text: str, model: str, content_type: ContentType) -> str:
        """Generate cache key for embedding."""
        content_hash = hashlib.md5(text.encode()).hexdigest()
        return f"embedding:{model}:{content_type.value}:{content_hash}"
    
    async def get(self, text: str, model: str, content_type: ContentType) -> Optional[List[float]]:
        """Get embedding from cache."""
        cache_key = self._generate_cache_key(text, model, content_type)
        
        # Try Redis first
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logging.warning(f"Redis cache error: {e}")
        
        # Try memory cache
        if cache_key in self.memory_cache:
            cached_data = self.memory_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['embedding']
            else:
                del self.memory_cache[cache_key]
        
        return None
    
    async def set(self, text: str, model: str, content_type: ContentType, embedding: List[float]):
        """Store embedding in cache."""
        cache_key = self._generate_cache_key(text, model, content_type)
        cache_data = {
            'embedding': embedding,
            'timestamp': time.time()
        }
        
        # Store in memory cache
        self.memory_cache[cache_key] = cache_data
        
        # Store in Redis if available
        if self.redis_client:
            try:
                self.redis_client.setex(
                    cache_key, 
                    self.cache_ttl, 
                    json.dumps(embedding)
                )
            except Exception as e:
                logging.warning(f"Redis cache set error: {e}")


class EnhancedEmbeddingService:
    """
    Enhanced embedding service with advanced features:
    - Multiple embedding models
    - Domain-specific model selection
    - Intelligent caching
    - Quality metrics
    - Ensemble methods
    - Performance monitoring
    """
    
    def __init__(self):
        self.models = {}
        self._loaded_models = {}  # Cache for loaded models
        self.cache = EmbeddingCache()
        self.logger = logging.getLogger(__name__)
        self.performance_stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'average_generation_time': 0.0,
            'model_usage': {}
        }
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all available embedding models."""
        self._init_openai_models()
        self._init_sentence_transformer_models()
        self._init_code_specific_models()
        self._init_ensemble_model()
    
    def _init_openai_models(self):
        """Initialize OpenAI embedding models."""
        if not OPENAI_AVAILABLE or not settings.openai_api_key:
            return
        
        # Latest OpenAI models
        openai_models = {
            'text-embedding-3-small': {'dimensions': 1536, 'type': ModelType.OPENAI},
            'text-embedding-3-large': {'dimensions': 3072, 'type': ModelType.OPENAI},
            'text-embedding-ada-002': {'dimensions': 1536, 'type': ModelType.OPENAI}
        }
        
        for model_name, config in openai_models.items():
            self.models[model_name] = config
    
    def _init_sentence_transformer_models(self):
        """Initialize sentence transformer models."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return
        
        # General purpose models
        general_models = {
            'all-MiniLM-L6-v2': {'dimensions': 384, 'type': ModelType.SENTENCE_TRANSFORMERS},
            'all-mpnet-base-v2': {'dimensions': 768, 'type': ModelType.SENTENCE_TRANSFORMERS},
            'multi-qa-MiniLM-L6-cos-v1': {'dimensions': 384, 'type': ModelType.SENTENCE_TRANSFORMERS},
            'paraphrase-multilingual-MiniLM-L12-v2': {'dimensions': 384, 'type': ModelType.SENTENCE_TRANSFORMERS}
        }
        
        # Code-specific models
        code_models = {
            'microsoft/codebert-base': {'dimensions': 768, 'type': ModelType.CODE_BERT},
            'microsoft/graphcodebert-base': {'dimensions': 768, 'type': ModelType.GRAPHCODE_BERT},
            'Salesforce/codet5p-220m': {'dimensions': 768, 'type': ModelType.CODE_BERT}
        }
        
        self.models.update(general_models)
        self.models.update(code_models)
    
    def _init_code_specific_models(self):
        """Initialize code-specific embedding models."""
        # These would be loaded on-demand to save memory
        self.code_models = {
            'code-bert': 'microsoft/codebert-base',
            'graphcode-bert': 'microsoft/graphcodebert-base',
            'codet5p': 'Salesforce/codet5p-220m'
        }
    
    def _init_ensemble_model(self):
        """Initialize ensemble model configuration."""
        self.ensemble_config = {
            'models': ['all-MiniLM-L6-v2', 'text-embedding-3-small'],
            'weights': [0.6, 0.4],
            'type': ModelType.ENSEMBLE
        }
    
    def _detect_content_type(self, text: str) -> ContentType:
        """Detect the type of content for optimal model selection."""
        text_lower = text.lower()
        
        # Code indicators
        code_indicators = ['function', 'class', 'def ', 'import ', 'from ', 'const ', 'let ', 'var ', '{', '}', '(', ')', ';', '//', '/*']
        if any(indicator in text for indicator in code_indicators):
            return ContentType.CODE
        
        # Error message indicators
        error_indicators = ['error:', 'exception:', 'traceback:', 'failed', 'failed to', 'error occurred']
        if any(indicator in text_lower for indicator in error_indicators):
            return ContentType.ERROR_MESSAGE
        
        # Documentation indicators
        doc_indicators = ['documentation', 'guide', 'tutorial', 'api', 'reference', 'docs']
        if any(indicator in text_lower for indicator in doc_indicators):
            return ContentType.DOCUMENTATION
        
        # Commit message indicators
        commit_indicators = ['fix', 'add', 'update', 'remove', 'refactor', 'feat', 'docs']
        if any(indicator in text_lower for indicator in commit_indicators):
            return ContentType.COMMIT_MESSAGE
        
        # Issue description indicators
        issue_indicators = ['bug', 'issue', 'problem', 'feature request', 'enhancement']
        if any(indicator in text_lower for indicator in issue_indicators):
            return ContentType.ISSUE_DESCRIPTION
        
        return ContentType.TEXT
    
    def _select_optimal_model(self, content_type: ContentType, text_length: int) -> str:
        """Select the optimal model based on content type and characteristics."""
        
        if content_type == ContentType.CODE:
            # Prefer code-specific models for code
            if 'microsoft/codebert-base' in self.models:
                return 'microsoft/codebert-base'
            elif 'microsoft/graphcodebert-base' in self.models:
                return 'microsoft/graphcodebert-base'
        
        # For longer texts, prefer larger models
        if text_length > 1000:
            if 'text-embedding-3-large' in self.models:
                return 'text-embedding-3-large'
            elif 'all-mpnet-base-v2' in self.models:
                return 'all-mpnet-base-v2'
        
        # Default to reliable general-purpose model
        return 'all-MiniLM-L6-v2'
    
    async def generate_embedding(
        self, 
        text: str, 
        model_name: Optional[str] = None,
        use_cache: bool = True,
        content_type: Optional[ContentType] = None
    ) -> EmbeddingResult:
        """Generate embedding with advanced features."""
        
        if not text or len(text.strip()) == 0:
            return EmbeddingResult(
                embedding=[],
                model_used="none",
                content_type=ContentType.TEXT,
                quality=EmbeddingQuality(),
                generation_time=0.0
            )
        
        # Detect content type if not provided
        if content_type is None:
            content_type = self._detect_content_type(text)
        
        # Select optimal model if not specified
        if model_name is None:
            model_name = self._select_optimal_model(content_type, len(text))
        
        # Check cache first
        if use_cache:
            cached_embedding = await self.cache.get(text, model_name, content_type)
            if cached_embedding:
                self.performance_stats['cache_hits'] += 1
                return EmbeddingResult(
                    embedding=cached_embedding,
                    model_used=model_name,
                    content_type=content_type,
                    quality=EmbeddingQuality(confidence=0.9),  # High confidence for cached results
                    generation_time=0.0,
                    cache_hit=True
                )
        
        # Generate embedding
        start_time = time.time()
        try:
            embedding = await self._generate_embedding_with_model(text, model_name)
            generation_time = time.time() - start_time
            
            # Calculate quality metrics
            quality = self._calculate_embedding_quality(embedding, text, model_name)
            
            # Cache the result
            if use_cache:
                await self.cache.set(text, model_name, content_type, embedding)
            
            # Update performance stats
            self.performance_stats['total_requests'] += 1
            self.performance_stats['model_usage'][model_name] = self.performance_stats['model_usage'].get(model_name, 0) + 1
            
            return EmbeddingResult(
                embedding=embedding,
                model_used=model_name,
                content_type=content_type,
                quality=quality,
                generation_time=generation_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate embedding with {model_name}: {e}")
            # Fallback to simple embedding
            fallback_embedding = self._generate_simple_embedding(text)
            return EmbeddingResult(
                embedding=fallback_embedding,
                model_used="fallback",
                content_type=content_type,
                quality=EmbeddingQuality(confidence=0.3),
                generation_time=time.time() - start_time
            )
    
    async def _generate_embedding_with_model(self, text: str, model_name: str) -> List[float]:
        """Generate embedding using specific model."""
        
        if model_name.startswith('text-embedding-'):
            return await self._generate_openai_embedding(text, model_name)
        elif model_name in ['microsoft/codebert-base', 'microsoft/graphcodebert-base']:
            return await self._generate_code_bert_embedding(text, model_name)
        else:
            return await self._generate_sentence_transformer_embedding(text, model_name)
    
    async def _generate_openai_embedding(self, text: str, model_name: str) -> List[float]:
        """Generate embedding using OpenAI API."""
        if not OPENAI_AVAILABLE or not settings.openai_api_key:
            raise ValueError("OpenAI not available")
        
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: client.embeddings.create(input=text, model=model_name)
        )
        
        return response.data[0].embedding
    
    async def _generate_sentence_transformer_embedding(self, text: str, model_name: str) -> List[float]:
        """Generate embedding using sentence transformers."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ValueError("Sentence transformers not available")
        
        # Load model if not already loaded
        if model_name not in self._loaded_models:
            self._loaded_models[model_name] = SentenceTransformer(model_name)
        
        model = self._loaded_models[model_name]
        
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(None, lambda: model.encode(text))
        
        return embedding.tolist()
    
    async def _generate_code_bert_embedding(self, text: str, model_name: str) -> List[float]:
        """Generate embedding using code-specific BERT models."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ValueError("Sentence transformers not available")
        
        # Load model if not already loaded
        if model_name not in self._loaded_models:
            self._loaded_models[model_name] = SentenceTransformer(model_name)
        
        model = self._loaded_models[model_name]
        
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(None, lambda: model.encode(text))
        
        return embedding.tolist()
    
    def _generate_simple_embedding(self, text: str) -> List[float]:
        """Generate a simple fallback embedding."""
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i : i + 4]
            if len(chunk) == 4:
                value = int.from_bytes(chunk, byteorder="big")
                embedding.append((value % 1000) / 1000.0)
        
        # Pad or truncate to 384 dimensions
        while len(embedding) < 384:
            embedding.extend(embedding[: min(384 - len(embedding), len(embedding))])
        
        return embedding[:384]
    
    def _calculate_embedding_quality(self, embedding: List[float], text: str, model_name: str) -> EmbeddingQuality:
        """Calculate quality metrics for the embedding."""
        if not embedding:
            return EmbeddingQuality()
        
        # Convert to numpy array
        emb_array = np.array(embedding)
        
        # Calculate various quality metrics
        confidence = min(1.0, len(text) / 1000.0)  # Longer texts get higher confidence
        coherence = np.std(emb_array) / np.mean(np.abs(emb_array)) if np.mean(np.abs(emb_array)) > 0 else 0
        diversity = len(set(np.round(emb_array, 3))) / len(emb_array)
        semantic_richness = np.linalg.norm(emb_array) / len(emb_array)
        
        # Model-specific confidence
        model_confidence = 0.8  # Default
        if 'codebert' in model_name.lower():
            model_confidence = 0.9
        elif 'text-embedding-3' in model_name:
            model_confidence = 0.95
        elif 'all-MiniLM' in model_name:
            model_confidence = 0.85
        
        return EmbeddingQuality(
            confidence=confidence,
            coherence=coherence,
            diversity=diversity,
            semantic_richness=semantic_richness,
            model_confidence=model_confidence
        )
    
    async def generate_ensemble_embedding(self, text: str) -> EmbeddingResult:
        """Generate ensemble embedding using multiple models."""
        if not self.ensemble_config:
            return await self.generate_embedding(text)
        
        # Generate embeddings with different models
        embeddings = []
        weights = []
        
        for model_name, weight in zip(self.ensemble_config['models'], self.ensemble_config['weights']):
            try:
                result = await self.generate_embedding(text, model_name)
                embeddings.append(result.embedding)
                weights.append(weight)
            except Exception as e:
                self.logger.warning(f"Failed to generate embedding with {model_name}: {e}")
        
        if not embeddings:
            return await self.generate_embedding(text)
        
        # Weighted average of embeddings
        weighted_embedding = np.average(embeddings, weights=weights, axis=0)
        
        return EmbeddingResult(
            embedding=weighted_embedding.tolist(),
            model_used="ensemble",
            content_type=self._detect_content_type(text),
            quality=EmbeddingQuality(confidence=0.9),
            generation_time=0.0
        )
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        if not embedding1 or not embedding2:
            return 0.0
        
        try:
            if SKLEARN_AVAILABLE:
                vec1 = np.array(embedding1).reshape(1, -1)
                vec2 = np.array(embedding2).reshape(1, -1)
                similarity = cosine_similarity(vec1, vec2)[0][0]
            else:
                vec1 = np.array(embedding1)
                vec2 = np.array(embedding2)
                
                dot_product = np.dot(vec1, vec2)
                norm1 = np.linalg.norm(vec1)
                norm2 = np.linalg.norm(vec2)
                
                if norm1 == 0 or norm2 == 0:
                    return 0.0
                
                similarity = dot_product / (norm1 * norm2)
            
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    async def batch_generate_embeddings(
        self, 
        texts: List[str], 
        model_name: Optional[str] = None,
        use_cache: bool = True
    ) -> List[EmbeddingResult]:
        """Generate embeddings for multiple texts efficiently."""
        results = []
        
        # Process in batches for efficiency
        batch_size = 10
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.generate_embedding(text, model_name, use_cache) for text in batch]
            )
            results.extend(batch_results)
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = self.performance_stats.copy()
        if stats['total_requests'] > 0:
            stats['cache_hit_rate'] = stats['cache_hits'] / stats['total_requests']
        else:
            stats['cache_hit_rate'] = 0.0
        
        return stats
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get list of available models with their configurations."""
        return self.models.copy()
    
    def get_embedding_dimension(self, model_name: str) -> int:
        """Get the dimension of embeddings for a specific model."""
        if model_name in self.models:
            return self.models[model_name]['dimensions']
        elif model_name == "ensemble":
            return 384  # Default ensemble dimension
        else:
            return 384  # Default fallback dimension


# Initialize the enhanced service
enhanced_embedding_service = EnhancedEmbeddingService() 