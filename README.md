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
- 📈 **Production tested** - battle-tested in real fraud detection systems

## 🚀 Quick Start

```bash
pip install dataspot
```

```python
import dataspot

# Sample transaction data
data = [
    {"country": "US", "device": "mobile", "amount": 150, "user_type": "premium"},
    {"country": "US", "device": "mobile", "amount": 200, "user_type": "premium"},
    {"country": "EU", "device": "desktop", "amount": 50, "user_type": "free"},
    {"country": "US", "device": "mobile", "amount": 300, "user_type": "premium"},
    # ... more data
]

# Find concentration dataspots
dataspot = dataspot.Dataspot()
concentrations = dataspot.find(data, fields=["country", "device", "user_type"])

# Results show where data concentrates
for pattern in concentrations[:5]:
    print(f"{pattern.path} → {pattern.percentage}% ({pattern.count} records)")

# Output:
# country=US > device=mobile > user_type=premium → 45.2% (127 records)
# country=US > device=mobile → 52.1% (146 records)
# device=mobile → 67.8% (190 records)
```

## 🎯 Real-World Use Cases

### 🚨 Fraud Detection

```python
# Find suspicious transaction patterns
suspicious = dataspot.find(
    transactions,
    fields=["country", "payment_method", "time_of_day"],
    min_percentage=15  # Only significant concentrations
)

# Spot unusual concentrations that might indicate fraud
for pattern in suspicious:
    if pattern.percentage > 30:
        print(f"⚠️ High concentration: {pattern.path}")
```

### 📊 Business Intelligence

```python
# Discover customer behavior patterns
insights = dataspot.analyze(
    customer_data,
    fields=["region", "device", "product_category", "tier"]
)

print(f"📈 Found {len(insights.patterns)} concentration patterns")
print(f"🎯 Top opportunity: {insights.top_patterns[0].path}")
```

### 🔍 Data Quality Analysis

```python
# Find data quality issues
concentrations = dataspot.find(user_logs, ["source", "event", "status"])

# Look for unusual concentrations that might indicate data issues
anomalies = [p for p in concentrations if p.percentage > 80]
for anomaly in anomalies:
    print(f"⚠️ Possible data quality issue: {anomaly.path}")
```

## 🛠️ Advanced Usage

### Flexible Filtering

```python
# Complex analysis with multiple criteria
results = dataspot.query(
    min_percentage=10,          # Only patterns with >10% concentration
    max_depth=3,               # Limit hierarchy depth
    contains="mobile",         # Must contain "mobile" in pattern
    min_count=50,             # At least 50 records
    sort_by="concentration"   # Sort by concentration strength
)
```

### Builder Pattern for Complex Queries

```python
from dataspot import QueryBuilder

# Fluent interface for complex filtering
high_value_patterns = QueryBuilder(dataspot) \
    .field("country", "US") \
    .min_percentage(20) \
    .exclude(["test", "internal"]) \
    .sort_by("percentage") \
    .limit(10) \
    .execute()
```

### Custom Analysis

```python
# Add custom preprocessing
def extract_hour(timestamp):
    return timestamp.split("T")[1][:2]  # Extract hour from ISO timestamp

dataspot.add_preprocessor("timestamp", extract_hour)

# Now timestamp field will be analyzed by hour
patterns = dataspot.find(events, ["user_type", "timestamp", "action"])
```

## ⚡ Performance

Dataspot is built for speed and scale. Our optimized algorithm delivers exceptional performance across datasets of any size.

### 🚀 Blazing Fast Performance

| Dataset Size | Processing Time | Memory Usage |
|--------------|----------------|--------------|
| 1K records   | ~3ms          | ~2MB         |
| 10K records  | ~30ms         | ~15MB        |
| 100K records | ~300ms        | ~150MB       |
| 1M records   | ~3s           | ~1.5GB       |

### 📊 Algorithm Complexity

- **Time Complexity**: `O(n × f)` where n = records, f = fields
- **Space Complexity**: `O(n × f)` linear memory usage
- **Scalability**: Linear scaling - predictable performance growth

### 🔥 Built for Production

```python
import time
import dataspot

# Large dataset example
data = generate_transactions(100_000)  # 100K records
fields = ["country", "device", "payment_method", "user_tier"]

start = time.time()
patterns = dataspot.find(data, fields, min_percentage=5)
duration = time.time() - start

print(f"Analyzed 100K records in {duration:.2f}s")
# Output: Analyzed 100K records in 0.31s
```

### 💡 Performance Tips

**Optimize for Speed:**

```python
# Use filtering to reduce pattern count
patterns = dataspot.find(
    data,
    fields,
    min_percentage=10,    # Skip low-concentration patterns
    max_depth=3,         # Limit hierarchy depth
    limit=100           # Cap results
)
```

**Memory Efficiency:**

```python
# Process large datasets in chunks
def analyze_large_dataset(data, chunk_size=50000):
    results = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        patterns = dataspot.find(chunk, fields)
        results.extend(patterns)
    return results
```

### 🎯 When to Use Dataspot

**✅ Perfect for:**

- Real-time fraud detection (millisecond response times)
- Large-scale business intelligence
- High-frequency pattern analysis
- Production systems with strict performance requirements

**⚠️ Consider alternatives for:**

- Simple data grouping (use `pandas.groupby()`)
- One-time data exploration (any tool works)
- Very small datasets (<100 records)

---

*Benchmarks run on standard hardware (Intel i7, 16GB RAM). Your results may vary.*

## 📈 What Makes Dataspot Different?

| **Traditional Clustering** | **Dataspot Analysis** |
|---------------------------|---------------------|
| Groups similar data points | **Finds concentration patterns** |
| Equal-sized clusters | **Identifies where data accumulates** |
| Distance-based | **Percentage and count based** |
| Hard to interpret | **Business-friendly hierarchy** |
| Generic approach | **Built for real-world analysis** |

## Dataspot in action

![Dataspot in action - Finding data concentration patterns](dataspot.gif)

See Dataspot in action as it discovers data concentration patterns and dataspots in real-time

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

The project includes a Makefile with useful development commands:

| Command | Description |
|---------|-------------|
| `make lint` | Check code for style and quality issues |
| `make lint-fix` | Automatically fix linting issues where possible |
| `make tests` | Run all tests with coverage reporting |
| `make check` | Run both linting and tests |
| `make clean` | Remove cache files, build artifacts, and temporary files |
| `make venv-clean` | Remove the virtual environment |
| `make venv-create` | Create a new virtual environment with Python 3.9+ |
| `make venv-install` | Install the uv package manager |
| `make install` | Create virtual environment and install the dependencies |

## 📚 Documentation

- 📖 [User Guide](docs/user-guide.md) - Complete usage documentation
- 💡 [Examples](examples/) - Real-world usage examples
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
- **Sponsored by [Frauddi](https://frauddi.com)** - Production testing and open source support
- **Inspired by real fraud detection challenges** - Built to solve actual problems

## 🔗 Links

- 🏠 [Homepage](https://github.com/frauddi/dataspot)
- 📦 [PyPI Package](https://pypi.org/project/dataspot/) *(coming soon)*
- 🐛 [Issue Tracker](https://github.com/frauddi/dataspot/issues)

---

---

**Find your data's dataspots. Discover what others miss.**
Built with ❤️ by [Frauddi](https://frauddi.com)
