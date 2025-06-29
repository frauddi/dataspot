# Dataspot User Guide

> **Complete guide to finding data concentration patterns with Dataspot**

## Table of Contents

- [Getting Started](#getting-started)
- [Core Concepts](#core-concepts)
- [API Methods](#api-methods)
- [Advanced Usage](#advanced-usage)
- [Real-World Examples](#real-world-examples)
- [Performance Tips](#performance-tips)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

```bash
pip install dataspot
```

### Your First Analysis

```python
from dataspot import Dataspot
from dataspot.models.finder import FindInput, FindOptions

# Sample transaction data
data = [
    {"country": "US", "device": "mobile", "amount": "high"},
    {"country": "US", "device": "mobile", "amount": "medium"},
    {"country": "EU", "device": "desktop", "amount": "low"},
    {"country": "US", "device": "mobile", "amount": "high"},
]

# Initialize analyzer
dataspot = Dataspot()

# Find concentration patterns
result = dataspot.find(
    FindInput(data=data, fields=["country", "device"]),
    FindOptions(min_percentage=10.0, limit=5)
)

# Print results
for pattern in result.patterns:
    print(f"{pattern.path} → {pattern.percentage}% ({pattern.count} records)")
```

Output:
```
country=US > device=mobile → 75.0% (3 records)
country=US → 75.0% (3 records)
device=mobile → 75.0% (3 records)
```

## Core Concepts

### What is a Dataspot?

A **dataspot** is a point of data concentration where your data clusters in unexpected or significant ways. Unlike traditional clustering, dataspots:

- Focus on **percentage concentrations** rather than distance metrics
- Create **hierarchical patterns** showing data relationships
- Identify **business-meaningful insights** through statistical analysis

### Pattern Structure

Each pattern contains:
- **Path**: Hierarchical pattern description (`country=US > device=mobile`)
- **Percentage**: Proportion of total data this pattern represents
- **Count**: Number of records matching the pattern
- **Value**: Actual matched field values

### API Structure

Dataspot v0.4.0 uses typed input/output models for all operations:

- **Input Models**: Define what data to analyze and how to filter it
- **Options Models**: Configure analysis parameters and thresholds
- **Output Models**: Structured results with patterns, statistics, and metadata

## API Methods

### 1. Find Patterns (`find`)

Discover concentration patterns in your data.

```python
from dataspot.models.finder import FindInput, FindOptions

# Basic pattern finding
result = dataspot.find(
    FindInput(
        data=transactions,
        fields=["country", "payment_method", "device"]
    ),
    FindOptions(
        min_percentage=5.0,    # Only patterns with >5% concentration
        limit=10,              # Top 10 patterns
        sort_by="percentage"   # Sort by concentration strength
    )
)

print(f"Found {len(result.patterns)} patterns")
for pattern in result.patterns:
    print(f"{pattern.path} → {pattern.percentage:.1f}% ({pattern.count} records)")
```

**FindOptions parameters:**
- `min_percentage`: Minimum concentration threshold (default: 0.0)
- `max_percentage`: Maximum concentration threshold (default: 100.0)
- `min_count`: Minimum number of records (default: 1)
- `limit`: Maximum number of patterns to return (default: 100)
- `sort_by`: Sort criteria ("percentage", "count", "path")
- `contains`: Filter patterns containing specific text
- `max_depth`: Limit hierarchy depth

### 2. Statistical Analysis (`analyze`)

Get comprehensive statistical insights with additional metrics.

```python
from dataspot.models.analyzer import AnalyzeInput, AnalyzeOptions

result = dataspot.analyze(
    AnalyzeInput(
        data=customer_data,
        fields=["region", "tier", "product"]
    ),
    AnalyzeOptions(
        min_percentage=8.0,
        include_statistics=True,
        confidence_level=0.95
    )
)

print(f"Analysis summary: {result.summary}")
print(f"Statistical insights: {len(result.insights)} found")

# Enhanced pattern information
for pattern in result.patterns:
    print(f"{pattern.path} → {pattern.percentage:.1f}% "
          f"(confidence: {pattern.confidence:.2f})")
```

### 3. Hierarchical Trees (`tree`)

Build hierarchical visualizations of data relationships.

```python
from dataspot.models.tree import TreeInput, TreeOptions

tree = dataspot.tree(
    TreeInput(
        data=sales_data,
        fields=["region", "product", "channel"]
    ),
    TreeOptions(
        min_value=10,     # Minimum records per node
        max_depth=3,      # Maximum tree depth
        sort_by="value"   # Sort children by record count
    )
)

print(f"Root contains {tree.value} records")
print(f"Has {len(tree.children)} main branches")

# Navigate the tree
for child in tree.children:
    print(f"Branch: {child.name} → {child.value} records")
    for grandchild in child.children:
        print(f"  Sub-branch: {grandchild.name} → {grandchild.value} records")
```

### 4. Auto Discovery (`discover`)

Automatically find the most interesting patterns without specifying fields.

```python
from dataspot.models.discovery import DiscoverInput, DiscoverOptions

result = dataspot.discover(
    DiscoverInput(data=transaction_data),
    DiscoverOptions(
        max_fields=3,         # Consider up to 3-field combinations
        min_percentage=15.0,  # Focus on significant patterns
        limit=10             # Top 10 discoveries
    )
)

print(f"📊 Analyzed {result.statistics.total_records} records")
print(f"🔬 Ranked {len(result.field_ranking)} fields")
print(f"🎯 Discovered {len(result.top_patterns)} key patterns")

# Field importance ranking
print("\nField importance:")
for field_rank in result.field_ranking[:5]:
    print(f"  {field_rank.field}: {field_rank.score:.2f}")

# Top patterns
print("\nTop discovered patterns:")
for pattern in result.top_patterns[:3]:
    print(f"  {pattern.path} → {pattern.percentage:.1f}%")
```

### 5. Temporal Comparison (`compare`)

Compare patterns between different time periods or datasets.

```python
from dataspot.models.compare import CompareInput, CompareOptions

result = dataspot.compare(
    CompareInput(
        current_data=this_month_data,
        baseline_data=last_month_data,
        fields=["country", "payment_method"]
    ),
    CompareOptions(
        change_threshold=0.15,           # 15% change threshold
        statistical_significance=True,   # Test significance
        min_percentage=5.0              # Focus on meaningful patterns
    )
)

print(f"Changes detected: {len(result.changes)}")
print(f"New patterns: {len(result.new_patterns)}")
print(f"Disappeared patterns: {len(result.disappeared_patterns)}")

# Significant changes
for change in result.changes:
    if change.is_significant:
        direction = "↗" if change.change > 0 else "↘"
        print(f"{direction} {change.pattern.path}: "
              f"{change.change:+.1f}% change")
```

## Advanced Usage

### Data Preprocessing

Transform data before analysis using custom preprocessors:

```python
# Add preprocessors for data transformation
dataspot.add_preprocessor("email", lambda x: x.split("@")[1] if "@" in x else "unknown")
dataspot.add_preprocessor("amount", lambda x: "high" if x > 1000 else "low" if x < 100 else "medium")

# Now analysis will use transformed values
result = dataspot.find(
    FindInput(data=user_data, fields=["email", "amount"]),
    FindOptions(min_percentage=10.0)
)
```

### Query Filtering

Pre-filter data before analysis:

```python
# Analyze only US customers
result = dataspot.find(
    FindInput(
        data=customer_data,
        fields=["state", "product", "tier"],
        query={"country": "US"}  # Pre-filter
    ),
    FindOptions(min_percentage=5.0)
)

# Multiple filter criteria
result = dataspot.find(
    FindInput(
        data=transaction_data,
        fields=["payment_method", "amount_range"],
        query={
            "country": ["US", "CA"],     # North America only
            "status": "completed"        # Completed transactions only
        }
    ),
    FindOptions(min_percentage=8.0)
)
```

### Advanced Options

```python
# Comprehensive analysis with all options
result = dataspot.analyze(
    AnalyzeInput(
        data=large_dataset,
        fields=["region", "product", "channel", "tier"],
        query={"active": True}
    ),
    AnalyzeOptions(
        min_percentage=5.0,
        max_percentage=85.0,     # Exclude overwhelming patterns
        min_count=50,            # At least 50 records
        limit=25,                # Top 25 patterns
        sort_by="percentage",
        include_statistics=True,
        confidence_level=0.95
    )
)
```

## Real-World Examples

### Fraud Detection

```python
from dataspot.models.discovery import DiscoverInput, DiscoverOptions

# Auto-discover suspicious patterns
fraud_discovery = dataspot.discover(
    DiscoverInput(data=transactions),
    DiscoverOptions(
        min_percentage=25.0,  # High concentrations are suspicious
        max_fields=4
    )
)

# Flag high-risk patterns
for pattern in fraud_discovery.top_patterns:
    if pattern.percentage > 40:
        print(f"🚨 HIGH RISK: {pattern.path} ({pattern.percentage:.1f}%)")
    elif pattern.percentage > 25:
        print(f"⚠️ MEDIUM RISK: {pattern.path} ({pattern.percentage:.1f}%)")
```

### Customer Segmentation

```python
from dataspot.models.tree import TreeInput, TreeOptions

# Build customer hierarchy
customer_tree = dataspot.tree(
    TreeInput(
        data=customers,
        fields=["region", "segment", "product", "tier"]
    ),
    TreeOptions(min_value=25, max_depth=3)
)

# Identify growth opportunities
def find_growth_opportunities(node, level=0):
    indent = "  " * level
    if 100 <= node.value <= 500:  # Sweet spot for growth
        print(f"{indent}💰 Growth opportunity: {node.name} ({node.value} customers)")

    for child in node.children:
        find_growth_opportunities(child, level + 1)

find_growth_opportunities(customer_tree)
```

### A/B Testing Analysis

```python
from dataspot.models.compare import CompareInput, CompareOptions

# Compare test variants
ab_comparison = dataspot.compare(
    CompareInput(
        current_data=variant_a_data,
        baseline_data=variant_b_data,
        fields=["device", "outcome", "user_segment"]
    ),
    CompareOptions(
        change_threshold=0.05,    # 5% significance threshold
        statistical_significance=True
    )
)

# Analyze results
for change in ab_comparison.changes:
    if change.is_significant:
        variant = "A" if change.change > 0 else "B"
        print(f"✅ Variant {variant} wins: {change.pattern.path} "
              f"({change.change:+.1f}% difference)")
```

### Data Quality Monitoring

```python
from dataspot.models.analyzer import AnalyzeInput, AnalyzeOptions

# Monitor data quality patterns
quality_analysis = dataspot.analyze(
    AnalyzeInput(
        data=raw_data,
        fields=["source", "validation_status", "error_type"]
    ),
    AnalyzeOptions(
        min_percentage=1.0,  # Catch even small issues
        include_statistics=True
    )
)

# Alert on quality issues
for pattern in quality_analysis.patterns:
    if "error" in str(pattern.path).lower() and pattern.percentage > 5:
        print(f"🔍 Data quality alert: {pattern.path} ({pattern.percentage:.1f}%)")
```

## Performance Tips

### Large Dataset Optimization

```python
# For datasets > 100K records
result = dataspot.find(
    FindInput(data=large_dataset, fields=selected_fields),
    FindOptions(
        min_percentage=10.0,  # Skip low-concentration patterns
        limit=50,             # Limit results
        max_depth=3          # Control complexity
    )
)
```

### Memory-Efficient Processing

```python
# Process in chunks for very large datasets
def analyze_chunks(data, chunk_size=50000):
    all_patterns = []

    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        result = dataspot.find(
            FindInput(data=chunk, fields=["key", "fields"]),
            FindOptions(min_percentage=15.0)
        )
        all_patterns.extend(result.patterns)

    return all_patterns
```

### Quick Exploration

```python
# Fast discovery for initial exploration
quick_discovery = dataspot.discover(
    DiscoverInput(data=sample_data[:10000]),  # Sample first
    DiscoverOptions(
        max_fields=2,         # Simple patterns only
        min_percentage=20.0,  # High threshold
        limit=10             # Few results
    )
)
```

## Troubleshooting

### Common Issues

**No Patterns Found:**
```python
# Check data structure
print(f"Data sample: {data[:2]}")
print(f"Available fields: {list(data[0].keys()) if data else 'No data'}")

# Lower thresholds
result = dataspot.find(
    FindInput(data=data, fields=fields),
    FindOptions(min_percentage=1.0)  # Very low threshold
)
```

**Too Many Results:**
```python
# Increase filtering
result = dataspot.find(
    FindInput(data=data, fields=fields),
    FindOptions(
        min_percentage=15.0,  # Higher threshold
        limit=20,            # Fewer results
        max_depth=2         # Simpler patterns
    )
)
```

**Performance Issues:**
```python
import time

# Time your analysis
start = time.time()
result = dataspot.find(FindInput(data=data, fields=fields), FindOptions())
duration = time.time() - start

print(f"Analysis took {duration:.2f}s for {len(data)} records")

# If too slow, optimize
if duration > 10:
    # Use sampling
    sample = data[:min(50000, len(data))]
    result = dataspot.find(FindInput(data=sample, fields=fields), FindOptions())
```

### Data Requirements

**Supported Formats:**
- List of dictionaries (recommended)
- Pandas DataFrame (convert with `df.to_dict('records')`)
- JSON records

**Best Practices:**
- Ensure consistent field names across records
- Handle missing values before analysis (or use preprocessors)
- Use meaningful field names for better pattern interpretation
- Preprocess complex data types (dates, emails, etc.)

### Getting Help

- **Documentation**: Full API reference in code docstrings
- **Examples**: Check `/examples` directory for more use cases
- **Issues**: [GitHub Issues](https://github.com/frauddi/dataspot/issues) for bugs and features
- **Discussions**: [GitHub Discussions](https://github.com/frauddi/dataspot/discussions) for questions

---

**Ready to discover your dataspots? Start with `find()` for basic patterns, then explore `discover()` for automatic insights!**
