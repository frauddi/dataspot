# Dataspot 🔥

> **Find data concentration patterns and dataspots in your datasets**

[![PyPI version](https://badge.fury.io/py/dataspot.svg)](https://pypi.org/project/dataspot/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintained by Frauddi](https://img.shields.io/badge/Maintained%20by-Frauddi-blue.svg)](https://frauddi.com)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Dataspot automatically discovers **where your data concentrates**, helping you identify patterns, anomalies, and insights in datasets. Originally developed for fraud detection at Frauddi, now available as open source.

## ✨ Why Dataspot?

- 🎯 **Purpose-built** for finding data concentrations, not just clustering
- 🔍 **Fraud detection ready** - spot suspicious behavior patterns
- ⚡ **Simple API** - get insights in 3 lines of code
- 📊 **Hierarchical analysis** - understand data at multiple levels
- 🔧 **Flexible filtering** - customize analysis with powerful options
- 📈 **Field-tested** - validated in real fraud detection systems

## 🚀 Quick Start

```bash
pip install dataspot
```

```python
from dataspot import Dataspot
from dataspot.models.finder import FindInput, FindOptions

# Sample transaction data
data = [
    {"country": "US", "device": "mobile", "amount": "high", "user_type": "premium"},
    {"country": "US", "device": "mobile", "amount": "medium", "user_type": "premium"},
    {"country": "EU", "device": "desktop", "amount": "low", "user_type": "free"},
    {"country": "US", "device": "mobile", "amount": "high", "user_type": "premium"},
]

# Find concentration patterns
dataspot = Dataspot()
result = dataspot.find(
    FindInput(data=data, fields=["country", "device", "user_type"]),
    FindOptions(min_percentage=10.0, limit=5)
)

# Results show where data concentrates
for pattern in result.patterns:
    print(f"{pattern.path} → {pattern.percentage}% ({pattern.count} records)")

# Output:
# country=US > device=mobile > user_type=premium → 75.0% (3 records)
# country=US > device=mobile → 75.0% (3 records)
# device=mobile → 75.0% (3 records)
```

## 🎯 Real-World Use Cases

### 🚨 Fraud Detection

```python
from dataspot.models.finder import FindInput, FindOptions

# Find suspicious transaction patterns
result = dataspot.find(
    FindInput(
        data=transactions,
        fields=["country", "payment_method", "time_of_day"]
    ),
    FindOptions(min_percentage=15.0, contains="crypto")
)

# Spot unusual concentrations that might indicate fraud
for pattern in result.patterns:
    if pattern.percentage > 30:
        print(f"⚠️ High concentration: {pattern.path}")
```

### 📊 Business Intelligence

```python
from dataspot.models.analyzer import AnalyzeInput, AnalyzeOptions

# Discover customer behavior patterns
insights = dataspot.analyze(
    AnalyzeInput(
        data=customer_data,
        fields=["region", "device", "product_category", "tier"]
    ),
    AnalyzeOptions(min_percentage=10.0)
)

print(f"📈 Found {len(insights.patterns)} concentration patterns")
print(f"🎯 Top opportunity: {insights.patterns[0].path}")
```

### 🔍 Temporal Analysis

```python
from dataspot.models.compare import CompareInput, CompareOptions

# Compare patterns between time periods
comparison = dataspot.compare(
    CompareInput(
        current_data=this_month_data,
        baseline_data=last_month_data,
        fields=["country", "payment_method"]
    ),
    CompareOptions(
        change_threshold=0.20,
        statistical_significance=True
    )
)

print(f"📊 Changes detected: {len(comparison.changes)}")
print(f"🆕 New patterns: {len(comparison.new_patterns)}")
```

### 🤖 Auto Discovery

```python
from dataspot.models.discovery import DiscoverInput, DiscoverOptions

# Automatically discover important patterns
discovery = dataspot.discover(
    DiscoverInput(data=transaction_data),
    DiscoverOptions(max_fields=3, min_percentage=15.0)
)

print(f"🎯 Top patterns discovered: {len(discovery.top_patterns)}")
for field_ranking in discovery.field_ranking[:3]:
    print(f"📈 {field_ranking.field}: {field_ranking.score:.2f}")
```

## 🛠️ Core Methods

| Method | Purpose | Input Model | Options Model | Output Model |
|--------|---------|-------------|---------------|--------------|
| `find()` | Find concentration patterns | `FindInput` | `FindOptions` | `FindOutput` |
| `analyze()` | Statistical analysis | `AnalyzeInput` | `AnalyzeOptions` | `AnalyzeOutput` |
| `compare()` | Temporal comparison | `CompareInput` | `CompareOptions` | `CompareOutput` |
| `discover()` | Auto pattern discovery | `DiscoverInput` | `DiscoverOptions` | `DiscoverOutput` |
| `tree()` | Hierarchical visualization | `TreeInput` | `TreeOptions` | `TreeOutput` |

### Advanced Filtering Options

```python
# Complex analysis with multiple criteria
result = dataspot.find(
    FindInput(
        data=data,
        fields=["country", "device", "payment"],
        query={"country": ["US", "EU"]}  # Pre-filter data
    ),
    FindOptions(
        min_percentage=10.0,      # Only patterns with >10% concentration
        max_depth=3,             # Limit hierarchy depth
        contains="mobile",       # Must contain "mobile" in pattern
        min_count=50,           # At least 50 records
        sort_by="percentage",   # Sort by concentration strength
        limit=20                # Top 20 patterns
    )
)
```

## ⚡ Performance

Dataspot delivers consistent, predictable performance with exceptionally efficient memory usage and linear scaling.

### 🚀 Real-World Performance

| Dataset Size | Processing Time | Memory Usage |
|--------------|----------------|--------------|
| 1K records   | ~4ms          | ~1MB         |
| 10K records  | ~40ms         | ~2MB         |
| 100K records | ~400ms        | ~3MB         |
| 1M records   | ~4s           | ~10MB        |

> **Benchmark Details**: Performance measured on standard hardware with realistic datasets (multiple fields, mixed data types). Memory usage is exceptionally efficient due to optimized algorithms. Times are averages of multiple runs for accuracy.

### 💡 Performance Tips

```python
# Optimize for speed
result = dataspot.find(
    FindInput(data=large_dataset, fields=fields),
    FindOptions(
        min_percentage=10.0,    # Skip low-concentration patterns
        max_depth=3,           # Limit hierarchy depth
        limit=100             # Cap results
    )
)

# Memory efficient processing
from dataspot.models.tree import TreeInput, TreeOptions

tree = dataspot.tree(
    TreeInput(data=data, fields=["country", "device"]),
    TreeOptions(min_value=10, top=5)  # Simplified tree
)
```

## 📈 What Makes Dataspot Different?

| **Traditional Clustering** | **Dataspot Analysis** |
|---------------------------|---------------------|
| Groups similar data points | **Finds concentration patterns** |
| Equal-sized clusters | **Identifies where data accumulates** |
| Distance-based | **Percentage and count based** |
| Hard to interpret | **Business-friendly hierarchy** |
| Generic approach | **Built for real-world analysis** |

## 🎬 Dataspot in Action

![Dataspot in action - Finding data concentration patterns](dataspot.gif)

See Dataspot discover concentration patterns and dataspots in real-time with hierarchical analysis and statistical insights.

## 📊 API Structure

### Input Models

- `FindInput` - Data and fields for pattern finding
- `AnalyzeInput` - Statistical analysis configuration
- `CompareInput` - Current vs baseline data comparison
- `DiscoverInput` - Automatic pattern discovery
- `TreeInput` - Hierarchical tree visualization

### Options Models

- `FindOptions` - Filtering and sorting for patterns
- `AnalyzeOptions` - Statistical analysis parameters
- `CompareOptions` - Change detection thresholds
- `DiscoverOptions` - Auto-discovery constraints
- `TreeOptions` - Tree structure customization

### Response Models

All methods return structured responses with:

- `patterns` - Found concentration patterns
- `statistics` - Analysis metrics
- `metadata` - Processing information

## 🔧 Installation & Requirements

```bash
# Install from PyPI
pip install dataspot

# Development installation
git clone https://github.com/frauddi/dataspot.git
cd dataspot
pip install -e ".[dev]"
```

**Requirements:**

- Python 3.9+
- No heavy dependencies (just standard library + optional speedups)

## 🛠️ Development Commands

| Command | Description |
|---------|-------------|
| `make lint` | Check code for style and quality issues |
| `make lint-fix` | Automatically fix linting issues where possible |
| `make tests` | Run all tests with coverage reporting |
| `make check` | Run both linting and tests |
| `make clean` | Remove cache files, build artifacts, and temporary files |
| `make install` | Create virtual environment and install dependencies |

## 📚 Documentation & Examples

- 📖 [User Guide](docs/user-guide.md) - Complete usage documentation
- 💡 [Examples](examples/) - Real-world usage examples:
  - `01_basic_query_filtering.py` - Query and filtering basics
  - `02_pattern_filtering_basic.py` - Pattern-based filtering
  - `06_real_world_scenarios.py` - Business use cases
  - `08_auto_discovery.py` - Automatic pattern discovery
  - `09_temporal_comparison.py` - A/B testing and change detection
  - `10_stats.py` - Statistical analysis
- 🤝 [Contributing](docs/CONTRIBUTING.md) - How to contribute

## 🌟 Why Open Source?

Dataspot was born from real-world fraud detection needs at Frauddi. We believe powerful pattern analysis shouldn't be locked behind closed doors. By open-sourcing Dataspot, we hope to:

- 🎯 **Advance fraud detection** across the industry
- 🤝 **Enable collaboration** on pattern analysis techniques
- 🔍 **Help companies** spot issues in their data
- 📈 **Improve data quality** everywhere

## 🤝 Contributing

We welcome contributions! Whether you're:

- 🐛 Reporting bugs
- 💡 Suggesting features
- 📝 Improving documentation
- 🔧 Adding new analysis methods

See our [Contributing Guide](docs/CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Created by [@eliosf27](https://github.com/eliosf27)** - Original algorithm and implementation
- **Sponsored by [Frauddi](https://frauddi.com)** - Field testing and open source support
- **Inspired by real fraud detection challenges** - Built to solve actual problems

## 🔗 Links

- 🏠 [Homepage](https://github.com/frauddi/dataspot)
- 📦 [PyPI Package](https://pypi.org/project/dataspot/)
- 🐛 [Issue Tracker](https://github.com/frauddi/dataspot/issues)

---

**Find your data's dataspots. Discover what others miss.**
Built with ❤️ by [Frauddi](https://frauddi.com)
