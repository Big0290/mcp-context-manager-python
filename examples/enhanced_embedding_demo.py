#!/usr/bin/env python3
"""
Enhanced Embedding Service Demonstration
Showcases all advanced features including multi-model support, caching, quality metrics, and ensemble methods.
"""

import asyncio
import json
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


class EnhancedEmbeddingDemo:
    """Demonstration class for enhanced embedding features."""
    
    def __init__(self):
        self.embedding_service = EnhancedEmbeddingService()
        self.demo_texts = self._get_demo_texts()
    
    def _get_demo_texts(self) -> dict:
        """Get sample texts for demonstration."""
        return {
            'python_code': '''
def fibonacci(n):
    """Calculate the nth Fibonacci number using recursion."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def fibonacci_iterative(n):
    """Calculate the nth Fibonacci number using iteration."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
            ''',
            'javascript_code': '''
function calculateFibonacci(n) {
    // Calculate the nth Fibonacci number
    if (n <= 1) {
        return n;
    }
    return calculateFibonacci(n - 1) + calculateFibonacci(n - 2);
}

const fibonacciIterative = (n) => {
    if (n <= 1) return n;
    let a = 0, b = 1;
    for (let i = 2; i <= n; i++) {
        [a, b] = [b, a + b];
    }
    return b;
};
            ''',
            'error_message': '''
Traceback (most recent call last):
  File "main.py", line 15, in <module>
    result = fibonacci(10)
  File "main.py", line 8, in fibonacci
    return fibonacci(n-1) + fibonacci(n-2)
RecursionError: maximum recursion depth exceeded
            ''',
            'documentation': '''
# Fibonacci Sequence Implementation

This module provides two implementations of the Fibonacci sequence:

## Recursive Implementation
The `fibonacci(n)` function uses recursion to calculate the nth Fibonacci number.
Time complexity: O(2^n)
Space complexity: O(n)

## Iterative Implementation  
The `fibonacci_iterative(n)` function uses iteration for better performance.
Time complexity: O(n)
Space complexity: O(1)

## Usage Examples
```python
# Recursive approach
result = fibonacci(10)  # Returns 55

# Iterative approach
result = fibonacci_iterative(10)  # Returns 55
```
            ''',
            'commit_message': 'feat: add enhanced embedding service with multi-model support and caching',
            'issue_description': 'Bug: Memory leak in embedding cache causing high memory usage during batch processing',
            'general_text': 'The quick brown fox jumps over the lazy dog. This is a sample text for testing general embedding capabilities.',
            'long_text': '''
This is a much longer text that demonstrates how the enhanced embedding service handles 
larger content. It includes multiple sentences and paragraphs to test the system's ability 
to process substantial amounts of text while maintaining semantic coherence and quality.

The enhanced embedding service features multiple advanced capabilities including:
- Multi-model support with automatic model selection
- Intelligent caching with Redis and memory-based storage
- Quality metrics calculation for embedding assessment
- Ensemble methods for improved accuracy
- Domain-specific model selection (code, documentation, errors, etc.)
- Performance monitoring and statistics tracking

These features work together to provide a robust and efficient embedding solution that can 
handle various types of content while optimizing for both speed and accuracy.
            '''
        }
    
    async def demo_content_type_detection(self):
        """Demonstrate automatic content type detection."""
        print("🔍 **Content Type Detection Demo**")
        print("=" * 50)
        
        for name, text in self.demo_texts.items():
            content_type = self.embedding_service._detect_content_type(text)
            print(f"📄 {name:20} → {content_type.value}")
        
        print()
    
    async def demo_model_selection(self):
        """Demonstrate optimal model selection."""
        print("🎯 **Optimal Model Selection Demo**")
        print("=" * 50)
        
        for name, text in self.demo_texts.items():
            content_type = self.embedding_service._detect_content_type(text)
            model = self.embedding_service._select_optimal_model(content_type, len(text))
            print(f"📄 {name:20} → {model}")
        
        print()
    
    async def demo_basic_embeddings(self):
        """Demonstrate basic embedding generation."""
        print("🚀 **Basic Embedding Generation Demo**")
        print("=" * 50)
        
        for name, text in list(self.demo_texts.items())[:3]:  # Test first 3
            print(f"📄 Generating embedding for: {name}")
            
            result = await self.embedding_service.generate_embedding(text)
            
            print(f"   Model used: {result.model_used}")
            print(f"   Content type: {result.content_type.value}")
            print(f"   Embedding dimension: {len(result.embedding)}")
            print(f"   Generation time: {result.generation_time:.3f}s")
            print(f"   Cache hit: {result.cache_hit}")
            print(f"   Quality confidence: {result.quality.confidence:.3f}")
            print()
    
    async def demo_caching(self):
        """Demonstrate embedding caching."""
        print("💾 **Embedding Caching Demo**")
        print("=" * 50)
        
        text = self.demo_texts['general_text']
        
        # First call (no cache)
        print("🔄 First call (no cache):")
        start_time = time.time()
        result1 = await self.embedding_service.generate_embedding(text, use_cache=True)
        first_time = time.time() - start_time
        print(f"   Time: {first_time:.3f}s")
        print(f"   Cache hit: {result1.cache_hit}")
        
        # Second call (with cache)
        print("⚡ Second call (with cache):")
        start_time = time.time()
        result2 = await self.embedding_service.generate_embedding(text, use_cache=True)
        second_time = time.time() - start_time
        print(f"   Time: {second_time:.3f}s")
        print(f"   Cache hit: {result2.cache_hit}")
        
        # Performance improvement
        if first_time > 0:
            improvement = (first_time - second_time) / first_time * 100
            print(f"   Performance improvement: {improvement:.1f}%")
        
        print()
    
    async def demo_quality_metrics(self):
        """Demonstrate quality metrics calculation."""
        print("📊 **Quality Metrics Demo**")
        print("=" * 50)
        
        for name, text in list(self.demo_texts.items())[:3]:
            result = await self.embedding_service.generate_embedding(text)
            
            print(f"📄 {name}:")
            print(f"   Confidence: {result.quality.confidence:.3f}")
            print(f"   Coherence: {result.quality.coherence:.3f}")
            print(f"   Diversity: {result.quality.diversity:.3f}")
            print(f"   Semantic Richness: {result.quality.semantic_richness:.3f}")
            print(f"   Model Confidence: {result.quality.model_confidence:.3f}")
            print()
    
    async def demo_ensemble_embeddings(self):
        """Demonstrate ensemble embedding generation."""
        print("🎭 **Ensemble Embedding Demo**")
        print("=" * 50)
        
        text = self.demo_texts['python_code']
        
        # Individual model embeddings
        print("🔍 Individual model results:")
        models = ['all-MiniLM-L6-v2', 'text-embedding-3-small']
        
        for model in models:
            try:
                result = await self.embedding_service.generate_embedding(text, model_name=model)
                print(f"   {model}: confidence={result.quality.confidence:.3f}")
            except Exception as e:
                print(f"   {model}: Error - {e}")
        
        # Ensemble embedding
        print("\n🎭 Ensemble result:")
        ensemble_result = await self.embedding_service.generate_ensemble_embedding(text)
        print(f"   Model: {ensemble_result.model_used}")
        print(f"   Confidence: {ensemble_result.quality.confidence:.3f}")
        print(f"   Dimension: {len(ensemble_result.embedding)}")
        
        print()
    
    async def demo_similarity_comparison(self):
        """Demonstrate similarity comparison between different content types."""
        print("🔗 **Similarity Comparison Demo**")
        print("=" * 50)
        
        # Compare similar content
        text1 = "Python function to calculate fibonacci"
        text2 = "Function that computes fibonacci numbers in Python"
        text3 = "JavaScript function for fibonacci calculation"
        
        results = await asyncio.gather(
            self.embedding_service.generate_embedding(text1),
            self.embedding_service.generate_embedding(text2),
            self.embedding_service.generate_embedding(text3)
        )
        
        print("📊 Similarity Matrix:")
        print("   " + " " * 20 + "Text1" + " " * 10 + "Text2" + " " * 10 + "Text3")
        
        for i, result1 in enumerate(results):
            similarities = []
            for j, result2 in enumerate(results):
                if i == j:
                    similarities.append("1.000")
                else:
                    sim = self.embedding_service.calculate_similarity(
                        result1.embedding, result2.embedding
                    )
                    similarities.append(f"{sim:.3f}")
            
            text_name = f"Text{i+1}"
            print(f"   {text_name:20} {' '.join(similarities)}")
        
        print()
    
    async def demo_batch_processing(self):
        """Demonstrate batch embedding processing."""
        print("📦 **Batch Processing Demo**")
        print("=" * 50)
        
        texts = list(self.demo_texts.values())
        
        print(f"🔄 Processing {len(texts)} texts in batch...")
        
        start_time = time.time()
        results = await self.embedding_service.batch_generate_embeddings(texts)
        batch_time = time.time() - start_time
        
        print(f"✅ Batch completed in {batch_time:.3f}s")
        print(f"📊 Results summary:")
        print(f"   Total texts: {len(results)}")
        print(f"   Average generation time: {batch_time/len(results):.3f}s per text")
        
        # Count content types
        content_types = {}
        for result in results:
            ct = result.content_type.value
            content_types[ct] = content_types.get(ct, 0) + 1
        
        print(f"   Content type distribution:")
        for ct, count in content_types.items():
            print(f"     {ct}: {count}")
        
        print()
    
    async def demo_performance_stats(self):
        """Demonstrate performance statistics."""
        print("📈 **Performance Statistics Demo**")
        print("=" * 50)
        
        # Generate some embeddings to build stats
        for text in list(self.demo_texts.values())[:5]:
            await self.embedding_service.generate_embedding(text)
        
        stats = self.embedding_service.get_performance_stats()
        
        print("📊 Performance Statistics:")
        print(f"   Total requests: {stats['total_requests']}")
        print(f"   Cache hits: {stats['cache_hits']}")
        print(f"   Cache hit rate: {stats['cache_hit_rate']:.1%}")
        print(f"   Average generation time: {stats['average_generation_time']:.3f}s")
        
        print("\n📊 Model Usage:")
        for model, count in stats['model_usage'].items():
            print(f"   {model}: {count} requests")
        
        print()
    
    async def demo_available_models(self):
        """Demonstrate available models listing."""
        print("🔧 **Available Models Demo**")
        print("=" * 50)
        
        models = self.embedding_service.get_available_models()
        
        print(f"📋 Available Models ({len(models)} total):")
        for model_name, config in models.items():
            print(f"   📄 {model_name}")
            print(f"      Type: {config['type'].value}")
            print(f"      Dimensions: {config['dimensions']}")
        
        print()
    
    async def demo_error_handling(self):
        """Demonstrate error handling."""
        print("⚠️ **Error Handling Demo**")
        print("=" * 50)
        
        # Test various edge cases
        edge_cases = [
            ("Empty string", ""),
            ("Whitespace only", "   \n\t   "),
            ("None", None),
            ("Very long text", "A" * 10000),
        ]
        
        for name, text in edge_cases:
            try:
                result = await self.embedding_service.generate_embedding(text)
                print(f"✅ {name}: Success (dimension: {len(result.embedding)})")
            except Exception as e:
                print(f"❌ {name}: Error - {e}")
        
        print()
    
    async def run_full_demo(self):
        """Run the complete demonstration."""
        print("🚀 **Enhanced Embedding Service - Full Demo**")
        print("=" * 60)
        print("This demo showcases all advanced features of the enhanced embedding service.")
        print()
        
        # Run all demos
        await self.demo_content_type_detection()
        await self.demo_model_selection()
        await self.demo_basic_embeddings()
        await self.demo_caching()
        await self.demo_quality_metrics()
        await self.demo_ensemble_embeddings()
        await self.demo_similarity_comparison()
        await self.demo_batch_processing()
        await self.demo_performance_stats()
        await self.demo_available_models()
        await self.demo_error_handling()
        
        print("🎉 **Demo Complete!**")
        print("The enhanced embedding service provides:")
        print("   ✅ Multi-model support with automatic selection")
        print("   ✅ Intelligent caching for performance")
        print("   ✅ Quality metrics for embedding assessment")
        print("   ✅ Ensemble methods for improved accuracy")
        print("   ✅ Domain-specific model optimization")
        print("   ✅ Comprehensive error handling")
        print("   ✅ Performance monitoring and statistics")


async def main():
    """Main demo function."""
    demo = EnhancedEmbeddingDemo()
    await demo.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main()) 