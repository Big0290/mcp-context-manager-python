# 🚀 Enhanced Embedding Features

## Overview

The Enhanced Embedding Service provides cutting-edge embedding capabilities with multi-model support, intelligent caching, quality metrics, and ensemble methods. This system transforms your MCP Context Manager into a sophisticated embedding powerhouse.

## 🎯 Key Features

### **Multi-Model Support**

- **OpenAI Models**: `text-embedding-3-small`, `text-embedding-3-large`, `text-embedding-ada-002`
- **Sentence Transformers**: `all-MiniLM-L6-v2`, `all-mpnet-base-v2`, `multi-qa-MiniLM-L6-cos-v1`
- **Code-Specific Models**: `microsoft/codebert-base`, `microsoft/graphcodebert-base`, `Salesforce/codet5p-220m`
- **Multilingual Support**: `paraphrase-multilingual-MiniLM-L12-v2`

### **Intelligent Model Selection**

- **Automatic Content Detection**: Code, documentation, error messages, commit messages, issues
- **Optimal Model Selection**: Based on content type and text length
- **Domain-Specific Optimization**: Code models for code, documentation models for docs

### **Advanced Caching**

- **Multi-Level Caching**: Memory cache + Redis cache
- **Intelligent TTL**: Configurable cache expiration
- **Performance Optimization**: Dramatic speed improvements for repeated queries

### **Quality Metrics**

- **Confidence Scoring**: Model confidence in embedding quality
- **Coherence Analysis**: Semantic coherence measurement
- **Diversity Assessment**: Embedding diversity evaluation
- **Semantic Richness**: Content richness measurement

### **Ensemble Methods**

- **Weighted Averaging**: Combine multiple model outputs
- **Improved Accuracy**: Better results than single models
- **Configurable Weights**: Customize model contributions

## 🛠️ Installation

### **Dependencies**

```bash
# Install enhanced embedding dependencies
pip install transformers>=4.30.0 torch>=2.0.0 accelerate>=0.20.0

# Optional: Install Redis for advanced caching
pip install redis>=5.0.0
```

### **Environment Configuration**

```bash
# Enhanced embedding settings
ENABLE_ENHANCED_EMBEDDINGS=true
ENABLE_EMBEDDING_CACHE=true
EMBEDDING_CACHE_TTL=3600
ENABLE_ENSEMBLE_EMBEDDINGS=true
ENABLE_QUALITY_METRICS=true

# Model selection preferences
PREFERRED_CODE_MODEL=microsoft/codebert-base
PREFERRED_TEXT_MODEL=all-MiniLM-L6-v2
PREFERRED_DOCUMENTATION_MODEL=all-mpnet-base-v2

# Performance settings
EMBEDDING_BATCH_SIZE=10
MAX_EMBEDDING_RETRIES=3
EMBEDDING_TIMEOUT=30.0

# Quality thresholds
MIN_EMBEDDING_CONFIDENCE=0.5
MIN_EMBEDDING_COHERENCE=0.3
MIN_EMBEDDING_DIVERSITY=0.2
```

## 🚀 Quick Start

### **Basic Usage**

```python
from mcp_memory_server.core.enhanced_embedding_service import EnhancedEmbeddingService

# Initialize the service
embedding_service = EnhancedEmbeddingService()

# Generate embedding with automatic model selection
result = await embedding_service.generate_embedding("Your text here")

print(f"Model used: {result.model_used}")
print(f"Content type: {result.content_type.value}")
print(f"Quality confidence: {result.quality.confidence}")
print(f"Embedding dimension: {len(result.embedding)}")
```

### **Domain-Specific Embeddings**

```python
# Code embedding (automatically detected)
code_text = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
code_result = await embedding_service.generate_embedding(code_text)
# Uses code-specific model like microsoft/codebert-base

# Documentation embedding
doc_text = "This function calculates the Fibonacci sequence using recursion."
doc_result = await embedding_service.generate_embedding(doc_text)
# Uses documentation-optimized model

# Error message embedding
error_text = "Error: ModuleNotFoundError: No module named 'requests'"
error_result = await embedding_service.generate_embedding(error_text)
# Uses error-specific processing
```

### **Ensemble Embeddings**

```python
# Generate ensemble embedding using multiple models
ensemble_result = await embedding_service.generate_ensemble_embedding("Your text here")
print(f"Ensemble confidence: {ensemble_result.quality.confidence}")
```

### **Batch Processing**

```python
# Process multiple texts efficiently
texts = ["Text 1", "Text 2", "Text 3", "Text 4"]
results = await embedding_service.batch_generate_embeddings(texts)

for i, result in enumerate(results):
    print(f"Text {i+1}: {result.model_used} - {result.quality.confidence:.3f}")
```

## 📊 Quality Metrics

### **Understanding Quality Scores**

```python
result = await embedding_service.generate_embedding("Your text here")

# Quality metrics breakdown
print(f"Confidence: {result.quality.confidence:.3f}")
# Higher confidence = more reliable embedding

print(f"Coherence: {result.quality.coherence:.3f}")
# Higher coherence = more semantically consistent

print(f"Diversity: {result.quality.diversity:.3f}")
# Higher diversity = more varied semantic content

print(f"Semantic Richness: {result.quality.semantic_richness:.3f}")
# Higher richness = more meaningful content

print(f"Model Confidence: {result.quality.model_confidence:.3f}")
# Model's confidence in its own output
```

### **Quality Thresholds**

```python
# Set quality thresholds for filtering
MIN_CONFIDENCE = 0.7
MIN_COHERENCE = 0.5

result = await embedding_service.generate_embedding("Your text here")

if (result.quality.confidence >= MIN_CONFIDENCE and
    result.quality.coherence >= MIN_COHERENCE):
    print("High quality embedding generated!")
else:
    print("Consider regenerating with different model")
```

## 🔧 Advanced Configuration

### **Model Selection**

```python
# Force specific model
result = await embedding_service.generate_embedding(
    "Your text here",
    model_name="all-MiniLM-L6-v2"
)

# Override content type detection
result = await embedding_service.generate_embedding(
    "Your text here",
    content_type=ContentType.CODE
)
```

### **Caching Configuration**

```python
# Disable caching for fresh embeddings
result = await embedding_service.generate_embedding(
    "Your text here",
    use_cache=False
)

# Custom cache TTL
embedding_service.cache.cache_ttl = 7200  # 2 hours
```

### **Performance Monitoring**

```python
# Get performance statistics
stats = embedding_service.get_performance_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Cache hit rate: {stats['cache_hit_rate']:.1%}")
print(f"Model usage: {stats['model_usage']}")
```

## 🎯 Content Type Detection

### **Automatic Detection**

The service automatically detects content types:

- **Code**: Contains programming keywords, syntax
- **Error Messages**: Contains error indicators, stack traces
- **Documentation**: Contains documentation keywords
- **Commit Messages**: Contains commit action words
- **Issue Descriptions**: Contains issue-related keywords
- **General Text**: Default for other content

### **Detection Examples**

```python
# Code detection
text = "def calculate_fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)"
content_type = embedding_service._detect_content_type(text)
# Returns: ContentType.CODE

# Error detection
text = "Error: ModuleNotFoundError: No module named 'requests'"
content_type = embedding_service._detect_content_type(text)
# Returns: ContentType.ERROR_MESSAGE

# Documentation detection
text = "This function calculates the Fibonacci sequence using recursion."
content_type = embedding_service._detect_content_type(text)
# Returns: ContentType.DOCUMENTATION
```

## 🔗 Similarity Calculations

### **Cosine Similarity**

```python
# Generate embeddings for comparison
result1 = await embedding_service.generate_embedding("Python function")
result2 = await embedding_service.generate_embedding("JavaScript function")

# Calculate similarity
similarity = embedding_service.calculate_similarity(
    result1.embedding,
    result2.embedding
)
print(f"Similarity: {similarity:.3f}")
```

### **Batch Similarity**

```python
# Compare multiple texts
texts = ["Text A", "Text B", "Text C"]
results = await embedding_service.batch_generate_embeddings(texts)

# Calculate similarity matrix
for i, result1 in enumerate(results):
    for j, result2 in enumerate(results):
        if i != j:
            sim = embedding_service.calculate_similarity(
                result1.embedding, result2.embedding
            )
            print(f"Similarity {i}-{j}: {sim:.3f}")
```

## 🚀 Performance Optimization

### **Caching Benefits**

```python
# First call (no cache)
start_time = time.time()
result1 = await embedding_service.generate_embedding("Repeated text")
first_time = time.time() - start_time

# Second call (with cache)
start_time = time.time()
result2 = await embedding_service.generate_embedding("Repeated text")
second_time = time.time() - start_time

improvement = (first_time - second_time) / first_time * 100
print(f"Cache performance improvement: {improvement:.1f}%")
```

### **Batch Processing**

```python
# Process multiple texts efficiently
texts = [f"Text {i}" for i in range(100)]
start_time = time.time()
results = await embedding_service.batch_generate_embeddings(texts)
batch_time = time.time() - start_time

print(f"Processed {len(texts)} texts in {batch_time:.2f}s")
print(f"Average time per text: {batch_time/len(texts):.3f}s")
```

## 🔧 Troubleshooting

### **Common Issues**

#### **Model Loading Errors**

```python
# Check available models
models = embedding_service.get_available_models()
print("Available models:", list(models.keys()))

# Verify model configuration
for model_name, config in models.items():
    print(f"{model_name}: {config['type'].value} - {config['dimensions']}d")
```

#### **Cache Issues**

```python
# Check cache status
stats = embedding_service.get_performance_stats()
print(f"Cache hit rate: {stats['cache_hit_rate']:.1%}")

# Clear cache if needed
embedding_service.cache.memory_cache.clear()
```

#### **Quality Issues**

```python
# Check quality metrics
result = await embedding_service.generate_embedding("Your text")
print(f"Quality metrics: {result.quality}")

# Try different model if quality is low
if result.quality.confidence < 0.5:
    result = await embedding_service.generate_embedding(
        "Your text",
        model_name="all-mpnet-base-v2"
    )
```

### **Performance Tuning**

```python
# Adjust batch size for your use case
embedding_service.batch_size = 20  # Increase for bulk processing

# Set quality thresholds
MIN_CONFIDENCE = 0.6
MIN_COHERENCE = 0.4

# Monitor performance
stats = embedding_service.get_performance_stats()
print(f"Average generation time: {stats['average_generation_time']:.3f}s")
```

## 📈 Monitoring and Analytics

### **Performance Metrics**

```python
# Get comprehensive statistics
stats = embedding_service.get_performance_stats()

print("📊 Performance Overview:")
print(f"   Total requests: {stats['total_requests']}")
print(f"   Cache hits: {stats['cache_hits']}")
print(f"   Cache hit rate: {stats['cache_hit_rate']:.1%}")
print(f"   Average generation time: {stats['average_generation_time']:.3f}s")

print("\n📊 Model Usage:")
for model, count in stats['model_usage'].items():
    percentage = (count / stats['total_requests']) * 100
    print(f"   {model}: {count} requests ({percentage:.1f}%)")
```

### **Quality Analytics**

```python
# Analyze quality distribution
results = []
for text in sample_texts:
    result = await embedding_service.generate_embedding(text)
    results.append(result)

# Calculate quality statistics
confidences = [r.quality.confidence for r in results]
coherences = [r.quality.coherence for r in results]

print(f"Average confidence: {np.mean(confidences):.3f}")
print(f"Average coherence: {np.mean(coherences):.3f}")
print(f"Quality range: {min(confidences):.3f} - {max(confidences):.3f}")
```

## 🎯 Best Practices

### **Model Selection**

1. **Code Content**: Use code-specific models (`microsoft/codebert-base`)
2. **Documentation**: Use documentation models (`all-mpnet-base-v2`)
3. **General Text**: Use general-purpose models (`all-MiniLM-L6-v2`)
4. **Long Content**: Use larger models (`text-embedding-3-large`)

### **Caching Strategy**

1. **Enable caching** for repeated content
2. **Set appropriate TTL** based on content volatility
3. **Monitor cache hit rates** for optimization
4. **Use Redis** for distributed deployments

### **Quality Management**

1. **Set quality thresholds** for your use case
2. **Monitor quality metrics** over time
3. **Use ensemble methods** for critical applications
4. **Retry with different models** for low-quality results

### **Performance Optimization**

1. **Use batch processing** for multiple texts
2. **Monitor performance stats** regularly
3. **Adjust batch sizes** based on your workload
4. **Consider model size** vs. performance trade-offs

## 🔮 Future Enhancements

### **Planned Features**

- **Multi-modal embeddings**: Support for code, images, and structured data
- **Fine-tuning capabilities**: Custom model training
- **Advanced ensemble methods**: More sophisticated model combination
- **Real-time quality monitoring**: Live quality assessment
- **Distributed caching**: Multi-node cache coordination

### **Integration Opportunities**

- **VS Code Extension**: Native IDE integration
- **GitHub Actions**: Automated quality checks
- **CI/CD Pipeline**: Embedding quality gates
- **Monitoring Dashboards**: Real-time performance tracking

---

**Transform your embedding capabilities with the Enhanced Embedding Service!** 🚀✨
