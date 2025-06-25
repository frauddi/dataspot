# Dataspot User Guide

> **Complete guide to finding data concentration patterns with Dataspot**

## Table of Contents

- [Getting Started](#getting-started)
- [Core Concepts](#core-concepts)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Performance Optimization](#performance-optimization)
- [Real-World Examples](#real-world-examples)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

```bash
pip install dataspot
```

### Your First Analysis

```python
import dataspot

# Sample data
data = [
    {"country": "US", "device": "mobile", "amount": 150},
    {"country": "US", "device": "mobile", "amount": 200},
    {"country": "EU", "device": "desktop", "amount": 50},
    {"country": "US", "device": "mobile", "amount": 300},
]

# Create analyzer
analyzer = dataspot.Dataspot()

# Find concentration patterns
patterns = analyzer.find(data, fields=["country", "device"])

# View results
for pattern in patterns:
    print(f"{pattern.path} → {pattern.percentage}% ({pattern.count} records)")
```

## Core Concepts

### What is a Dataspot?

A **dataspot** is a point of data concentration - where your data clusters or accumulates in unexpected or significant ways. Unlike traditional clustering, dataspots:

- Focus on **percentage concentrations** rather than distance metrics
- Create **hierarchical patterns** showing data flow
- Identify **business-meaningful insights** automatically

### Pattern Hierarchy

Dataspot creates hierarchical patterns from your data:

```
device=mobile → 67.8% (190 records)
├── device=mobile > country=US → 45.2% (127 records)
├── device=mobile > country=EU → 15.6% (44 records)
└── device=mobile > country=CA → 7.0% (19 records)
```

### Key Metrics

Each pattern includes:

- **Path**: The hierarchical pattern (e.g., `country=US > device=mobile`)
- **Percentage**: How much of your data this pattern represents
- **Count**: Number of records matching this pattern
- **Depth**: Level in the hierarchy (1 = single field, 2 = two fields, etc.)

## Basic Usage

### Simple Pattern Finding

```python
import dataspot

# Basic analysis
analyzer = dataspot.Dataspot()
patterns = analyzer.find(
    data=your_data,
    fields=["field1", "field2", "field3"]
)

# Print top 5 patterns
for pattern in patterns[:5]:
    print(f"{pattern.path} → {pattern.percentage:.1f}%")
```

### Filtering Results

```python
# Only significant patterns
significant_patterns = analyzer.find(
    data,
    fields=["country", "device", "user_type"],
    min_percentage=10,  # Only patterns with >10% concentration
    min_count=50,      # At least 50 records
    max_depth=2        # Limit to 2-field combinations
)
```

### Sorting Options

```python
# Sort by different criteria
patterns = analyzer.find(data, fields, sort_by="percentage")  # Default
patterns = analyzer.find(data, fields, sort_by="count")       # By record count
patterns = analyzer.find(data, fields, sort_by="depth")       # By hierarchy depth
```

## Advanced Features

### Query Builder Pattern

For complex analyses, use the fluent QueryBuilder interface:

```python
from dataspot import QueryBuilder

# Complex filtering with method chaining
results = QueryBuilder(analyzer) \
    .fields(["country", "device", "payment_method"]) \
    .min_percentage(15) \
    .exclude_values(["test", "internal"]) \
    .contains("mobile") \
    .sort_by("percentage") \
    .limit(20) \
    .execute()
```

### Custom Preprocessing

Transform your data before analysis:

```python
# Add custom field transformations
def extract_hour_from_timestamp(timestamp):
    return timestamp.split("T")[1][:2]

def categorize_amount(amount):
    if amount < 100:
        return "low"
    elif amount < 500:
        return "medium"
    else:
        return "high"

# Register preprocessors
analyzer.add_preprocessor("timestamp", extract_hour_from_timestamp)
analyzer.add_preprocessor("amount", categorize_amount)

# Now analyze with transformed fields
patterns = analyzer.find(data, ["country", "timestamp", "amount"])
```

### Text Pattern Analysis

```python
# Analyze text patterns
def extract_domain(email):
    return email.split("@")[1] if "@" in email else "unknown"

analyzer.add_preprocessor("email", extract_domain)

# Find email domain concentrations
email_patterns = analyzer.find(
    user_data,
    ["email", "country", "account_type"]
)
```

### Advanced Filtering

```python
# Multiple filtering criteria
filtered_patterns = analyzer.query(
    data=transaction_data,
    fields=["country", "payment_method", "amount_category"],
    min_percentage=5,
    max_percentage=80,  # Exclude overwhelming concentrations
    contains=["credit", "mobile"],  # Must contain these terms
    excludes=["test", "internal"],  # Exclude these patterns
    regex_filter=r"US|EU",  # Regex pattern matching
    depth_range=(2, 3)  # Only 2-3 field combinations
)
```

## Performance Optimization

### Large Dataset Strategies

**Chunked Processing:**

```python
def analyze_large_dataset(data, chunk_size=50000):
    """Process large datasets in chunks"""
    all_patterns = []

    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        patterns = analyzer.find(chunk, fields, min_percentage=5)
        all_patterns.extend(patterns)

    return all_patterns
```

**Memory-Efficient Analysis:**

```python
# Reduce memory usage
patterns = analyzer.find(
    data,
    fields,
    min_percentage=10,    # Skip low-concentration patterns
    max_depth=3,         # Limit hierarchy depth
    limit=100,           # Cap number of results
    sample_size=10000    # Analyze sample of large dataset
)
```

### Performance Tips

1. **Filter Early**: Use `min_percentage` to skip insignificant patterns
2. **Limit Depth**: Set `max_depth` to control computational complexity
3. **Sample Large Data**: Use `sample_size` for exploratory analysis
4. **Specific Fields**: Only analyze relevant fields
5. **Batch Processing**: Process large datasets in chunks

## Real-World Examples

### Fraud Detection

```python
# Detect suspicious transaction patterns
suspicious_patterns = analyzer.find(
    transactions,
    fields=["country", "payment_method", "time_of_day", "amount_range"],
    min_percentage=20  # Look for high concentrations
)

# Flag unusual concentrations
for pattern in suspicious_patterns:
    if pattern.percentage > 30 and pattern.count > 100:
        print(f"⚠️ Suspicious pattern: {pattern.path}")
        print(f"   {pattern.percentage}% of transactions")
```

### Business Intelligence

```python
# Customer behavior analysis
customer_insights = analyzer.find(
    customer_data,
    fields=["region", "device", "product_category", "subscription_tier"],
    min_percentage=5
)

# Find growth opportunities
growth_patterns = [p for p in customer_insights
                  if 10 <= p.percentage <= 30]  # Sweet spot for growth

print("Growth Opportunities:")
for pattern in growth_patterns[:10]:
    print(f"📈 {pattern.path} → {pattern.percentage}% market share")
```

### Data Quality Analysis

```python
# Find data quality issues
quality_patterns = analyzer.find(
    raw_data,
    fields=["source", "data_type", "validation_status"],
    min_percentage=1
)

# Identify anomalies
anomalies = [p for p in quality_patterns
            if p.percentage > 80 or "error" in p.path.lower()]

for anomaly in anomalies:
    print(f"🚨 Data quality issue: {anomaly.path}")
```

### A/B Testing Analysis

```python
# Analyze A/B test results
test_patterns = analyzer.find(
    experiment_data,
    fields=["variant", "user_segment", "outcome", "device"],
    min_percentage=3
)

# Compare variant performance
for pattern in test_patterns:
    if "variant=A" in pattern.path:
        print(f"Variant A: {pattern.path} → {pattern.percentage}%")
    elif "variant=B" in pattern.path:
        print(f"Variant B: {pattern.path} → {pattern.percentage}%")
```

## Troubleshooting

### Common Issues

**No Patterns Found:**

```python
# Check your data structure
print(f"Data sample: {data[:2]}")
print(f"Available fields: {list(data[0].keys()) if data else 'No data'}")

# Lower the minimum percentage
patterns = analyzer.find(data, fields, min_percentage=1)
```

**Too Many Patterns:**

```python
# Increase filtering
patterns = analyzer.find(
    data,
    fields,
    min_percentage=10,  # Higher threshold
    max_depth=2,       # Limit complexity
    limit=50          # Cap results
)
```

**Memory Issues:**

```python
# Process in smaller chunks
chunk_size = 10000
for i in range(0, len(data), chunk_size):
    chunk = data[i:i + chunk_size]
    patterns = analyzer.find(chunk, fields)
    # Process patterns immediately
```

**Performance Issues:**

```python
# Profile your analysis
import time

start = time.time()
patterns = analyzer.find(data, fields)
duration = time.time() - start

print(f"Analysis took {duration:.2f}s for {len(data)} records")

# Optimize if needed
if duration > 10:  # If taking too long
    patterns = analyzer.find(
        data,
        fields,
        sample_size=min(50000, len(data))
    )
```

### Data Format Requirements

**Supported Data Formats:**

```python
# List of dictionaries (recommended)
data = [
    {"field1": "value1", "field2": "value2"},
    {"field1": "value3", "field2": "value4"}
]

# Pandas DataFrame
import pandas as pd
df = pd.DataFrame(data)
patterns = analyzer.find(df.to_dict('records'), fields)

# CSV files
df = pd.read_csv('data.csv')
patterns = analyzer.find(df.to_dict('records'), fields)
```

**Field Requirements:**

- Fields must exist in all records
- Values should be strings or convertible to strings
- Empty/null values are handled as "unknown"
- Use preprocessors for complex data transformations

### Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/frauddi/dataspot/issues)
- **Discussions**: [Ask questions and share insights](https://github.com/frauddi/dataspot/discussions)
- **Examples**: Check the `/examples` directory for more use cases

---

**Ready to find your dataspots? Start with the basic examples and work your way up to advanced patterns!**
