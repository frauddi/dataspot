# Dataspot Examples

This folder contains practical examples that demonstrate the filtering and analysis capabilities of Dataspot. Each file focuses on specific use cases with concise, easy-to-understand code.

## Example Files

### 1. `01_basic_query_filtering.py`

#### Basic Query Filtering

Shows how to filter data before analysis using queries:

- Single field filtering
- Multiple field filtering
- List value filtering
- Tree visualization with queries

**Use cases:** E-commerce analysis, user segmentation by region/type.

```bash
python 01_basic_query_filtering.py
```

### 2. `02_pattern_filtering_basic.py`

#### Pattern Filtering

Demonstrates filtering patterns after analysis using metrics:

- Percentage thresholds
- Record count limits
- Pattern depth filtering
- Combined filters

**Use cases:** Support ticket analysis, finding significant patterns.

```bash
python 02_pattern_filtering_basic.py
```

### 3. `03_text_pattern_filtering.py`

#### Text Pattern Filtering

Shows text-based filtering capabilities:

- `contains` filters (include text)
- `exclude` filters (exclude text)
- Regular expression filtering
- Combined text + metric filters

**Use cases:** Web analytics, browser analysis, category filtering.

```bash
python 03_text_pattern_filtering.py
```

### 4. `04_advanced_filtering.py`

#### Advanced Filtering

Complex scenarios combining multiple filter types:

- Query filters + pattern filters
- Progressive filtering
- Comparative analysis
- Business scenario examples

**Use cases:** Sales analysis, enterprise segmentation, complex business queries.

```bash
python 04_advanced_filtering.py
```

### 5. `05_data_quality_and_edge_cases.py`

#### Data Quality and Edge Cases

Handling problematic data and edge cases:

- None/null values
- Mixed data types
- Missing fields
- Empty datasets
- Special characters

**Use cases:** Data cleaning, validation, real-world data issues.

```bash
python 05_data_quality_and_edge_cases.py
```

### 6. `06_real_world_scenarios.py`

#### Real-World Scenarios

Complete business use cases:

- Financial fraud detection
- Customer support optimization
- Marketing analysis
- Performance monitoring

**Use cases:** End-to-end business applications.

```bash
python 06_real_world_scenarios.py
```

### 7. `07_tree_visualization.py`

#### Tree Visualization

Hierarchical data structures for dashboards:

- Basic tree building
- Tree filtering
- Query + tree combinations
- Dashboard-ready JSON output

**Use cases:** Interactive dashboards, hierarchical visualization, drill-down interfaces.

```bash
python 07_tree_visualization.py
```

### 8. `08_auto_discovery.py` ✨

#### Automatic Pattern Discovery

Intelligent pattern discovery without manual field selection:

- Automatic field detection
- Field importance ranking
- Smart combination testing
- Discovery insights

**Use cases:** Exploratory data analysis, fraud detection, business intelligence.

```bash
python 08_auto_discovery.py
```

### 9. `09_temporal_comparison.py`

#### Temporal Comparison

Compare patterns between time periods:

- Change detection
- Statistical significance testing
- Anomaly identification
- Trend analysis

**Use cases:** Fraud monitoring, performance tracking, A/B testing.

```bash
python 09_temporal_comparison.py
```

### 10. `10_stats.py`

#### Statistical Analysis

Advanced statistical methods and calculations:

- Significance testing
- Effect size calculations
- Confidence intervals
- Business interpretations

**Use cases:** A/B testing, fraud detection confidence, statistical validation.

```bash
python 10_stats.py
```

## Getting Started

### Prerequisites

Install Dataspot:

```bash
pip install dataspot
```

Or for local development:

```bash
pip install -e .
```

### Run Examples

```bash
# Navigate to examples folder
cd examples

# Run individual examples
python 01_basic_query_filtering.py
python 02_pattern_filtering_basic.py
# ... etc

# Or run all examples
for file in *.py; do
    echo "=== Running $file ==="
    python "$file"
    echo ""
done
```

## Key API Patterns

All examples use the new structured API with Input/Options models:

```python
from dataspot import Dataspot
from dataspot.models.finder import FindInput, FindOptions

# Basic usage
dataspot = Dataspot()
result = dataspot.find(
    FindInput(data=data, fields=fields, query=query),
    FindOptions(min_percentage=10.0, limit=5)
)

# Access results
patterns = result.patterns
for pattern in patterns:
    print(f"{pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)")
```

## Available Methods

- **`find()`** - Find concentration patterns
- **`analyze()`** - Comprehensive analysis with insights
- **`tree()`** - Build hierarchical tree structures
- **`discover()`** - Automatic pattern discovery
- **`compare()`** - Compare datasets for changes

## Filtering Options

### Query Filters (pre-analysis)

- Single values: `{"field": "value"}`
- Lists: `{"field": ["value1", "value2"]}`
- Multiple fields: `{"field1": "value1", "field2": "value2"}`

### Pattern Filters (post-analysis)

- `min_percentage` / `max_percentage` - Percentage thresholds
- `min_count` / `max_count` - Record count limits
- `min_depth` / `max_depth` - Pattern complexity
- `contains` - Text that must be present
- `exclude` - Text that must be excluded
- `regex` - Regular expression matching
- `limit` - Maximum number of results

## Use Cases by Industry

### Finance

- Fraud detection (examples 06, 09)
- Risk analysis (examples 04, 10)

### E-commerce

- User behavior (examples 01, 07)
- Conversion analysis (examples 02, 09)

### Support

- Ticket classification (example 02)
- Resource optimization (example 06)

### Marketing

- Campaign analysis (examples 03, 06)
- Audience segmentation (example 04)

## Tips

1. **Start simple** - Begin with basic examples (01-03)
2. **Use your data** - Replace example datasets with your own
3. **Combine techniques** - Mix approaches from different examples
4. **Handle edge cases** - Review example 05 for real-world data
5. **Get inspired** - Check example 06 for business applications

## Troubleshooting

### Common Issues

#### Error: "ModuleNotFoundError: No module named 'dataspot'"

```bash
pip install dataspot
```

#### Examples show no results

- Check data format (list of dictionaries)
- Reduce filtering thresholds (lower `min_percentage`)
- Verify field names match your data

#### Slow performance

- Use `query` filters to reduce dataset size first
- Apply `limit` to restrict results
- Increase `min_count` or `min_percentage` thresholds

All examples are designed to be educational and easily modifiable for your specific use cases!
