"""
Embedding service for generating and managing vector embeddings.
"""

import asyncio
from typing import List, Optional

import numpy as np

# Optional import for scikit-learn
try:
    from sklearn.metrics.pairwise import cosine_similarity

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available, using fallback similarity calculation")

from mcp_memory_server.config import settings


class EmbeddingService:
    """Service for generating and managing vector embeddings."""

    def __init__(self):
        self.model = None
        self.model_name = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the embedding model based on configuration."""
        try:
            if settings.embedding_model == "openai":
                if not settings.openai_api_key:
                    raise ValueError("OpenAI API key is required for OpenAI embeddings")
                self.model_name = "text-embedding-ada-002"
            else:
                # Use sentence-transformers
                try:
                    from sentence_transformers import SentenceTransformer

                    self.model = SentenceTransformer(
                        settings.sentence_transformer_model
                    )
                    self.model_name = settings.sentence_transformer_model
                except ImportError:
                    print(
                        "Warning: sentence-transformers not available, using fallback model"
                    )
                    self.model_name = "simple"
        except Exception as e:
            print(f"Failed to initialize embedding model: {e}")
            # Fallback to a simple model
            self.model_name = "simple"

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text."""
        if not text or len(text.strip()) == 0:
            return []

        try:
            if settings.embedding_model == "openai":
                return await self._generate_openai_embedding(text)
            else:
                return await self._generate_sentence_transformer_embedding(text)
        except Exception as e:
            print(f"Failed to generate embedding: {e}")
            # Return a simple fallback embedding
            return self._generate_simple_embedding(text)

    async def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API."""
        import openai

        client = openai.OpenAI(api_key=settings.openai_api_key)

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: client.embeddings.create(input=text, model=self.model_name)
        )

        return response.data[0].embedding

    async def _generate_sentence_transformer_embedding(self, text: str) -> List[float]:
        """Generate embedding using sentence-transformers."""
        if not self.model:
            raise ValueError("Sentence transformer model not initialized")

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(None, lambda: self.model.encode(text))

        return embedding.tolist()

    def _generate_simple_embedding(self, text: str) -> List[float]:
        """Generate a simple fallback embedding."""
        # Simple hash-based embedding for fallback
        import hashlib

        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to list of floats
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i : i + 4]
            if len(chunk) == 4:
                value = int.from_bytes(chunk, byteorder="big")
                embedding.append((value % 1000) / 1000.0)  # Normalize to 0-1

        # Pad or truncate to 384 dimensions (common embedding size)
        while len(embedding) < 384:
            embedding.extend(embedding[: min(384 - len(embedding), len(embedding))])

        return embedding[:384]

    def calculate_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings."""
        if not embedding1 or not embedding2:
            return 0.0

        try:
            if SKLEARN_AVAILABLE:
                # Use scikit-learn for similarity calculation
                vec1 = np.array(embedding1).reshape(1, -1)
                vec2 = np.array(embedding2).reshape(1, -1)
                similarity = cosine_similarity(vec1, vec2)[0][0]
            else:
                # Fallback similarity calculation
                vec1 = np.array(embedding1)
                vec2 = np.array(embedding2)

                # Manual cosine similarity calculation
                dot_product = np.dot(vec1, vec2)
                norm1 = np.linalg.norm(vec1)
                norm2 = np.linalg.norm(vec2)

                if norm1 == 0 or norm2 == 0:
                    return 0.0

                similarity = dot_product / (norm1 * norm2)

            # Ensure result is between 0 and 1
            return max(0.0, min(1.0, similarity))

        except Exception as e:
            print(f"Failed to calculate similarity: {e}")
            return 0.0

    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently."""
        if settings.embedding_model == "openai":
            return await self._batch_generate_openai_embeddings(texts)
        else:
            return await self._batch_generate_sentence_transformer_embeddings(texts)

    async def _batch_generate_openai_embeddings(
        self, texts: List[str]
    ) -> List[List[float]]:
        """Generate embeddings using OpenAI API in batch."""
        import openai

        client = openai.OpenAI(api_key=settings.openai_api_key)

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: client.embeddings.create(input=texts, model=self.model_name)
        )

        return [data.embedding for data in response.data]

    async def _batch_generate_sentence_transformer_embeddings(
        self, texts: List[str]
    ) -> List[List[float]]:
        """Generate embeddings using sentence-transformers in batch."""
        if not self.model:
            raise ValueError("Sentence transformer model not initialized")

        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, lambda: self.model.encode(texts)
            )

            return embeddings.tolist()
        except Exception as e:
            print(f"Failed to generate sentence transformer embeddings: {e}")
            # Fallback to simple embeddings
            return [self._generate_simple_embedding(text) for text in texts]

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings generated by this service."""
        if settings.embedding_model == "openai":
            return 1536  # OpenAI text-embedding-ada-002 dimension
        elif self.model:
            return self.model.get_sentence_embedding_dimension()
        else:
            return 384  # Default fallback dimension
