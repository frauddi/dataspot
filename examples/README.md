# Dataspot Examples

This folder contains practical examples that demonstrate all the filtering and analysis capabilities of Dataspot. Each file focuses on specific use cases based on the project's tests.

## Example Files

### 1. `01_basic_query_filtering.py`

#### Basic Query Filtering

Demonstrates how to filter data before analysis using queries:

- Single field filtering
- Multiple field filtering
- Queries with value lists
- Mixed query types
- Comparison with and without filters

**Use cases:** E-commerce, transactions, user analysis by region/type.

```bash
python 01_basic_query_filtering.py
```

### 2. `02_pattern_filtering_basic.py`

#### Basic Pattern Filtering

Shows how to filter patterns after analysis using metrics:

- Filtering by minimum/maximum percentage
- Filtering by record count
- Filtering by depth (complexity)
- Result limits
- Combination of metric filters

**Use cases:** Technical support, tickets, volume and significance analysis.

```bash
python 02_pattern_filtering_basic.py
```

### 3. `03_text_pattern_filtering.py`

#### Text Pattern Filtering

Demonstrates filtering based on text content:

- `contains` filters (contains text)
- `exclude` filters (exclude text)
- Regular expression filters (regex)
- Combining text filters with other criteria

**Use cases:** Web analysis, browsers, filtering by specific categories.

```bash
python 03_text_pattern_filtering.py
```

### 4. `04_advanced_filtering.py`

#### Advanced Filtering

Complex cases that combine multiple types of filters:

- Combination of queries + pattern filters
- Multi-stage filtering
- Comparative analysis
- Progressive filtering
- Edge case handling
- Performance optimization

**Use cases:** Sales analysis, advanced segmentation, business analysis.

```bash
python 04_advanced_filtering.py
```

### 5. `05_data_quality_and_edge_cases.py`

#### Data Quality and Edge Cases

Handling problematic data and edge cases:

- `None`/null values
- Data type coercion
- Missing fields
- Empty or very small datasets
- Special characters
- Large datasets

**Use cases:** Data cleaning, validation, real-world data with issues.

```bash
python 05_data_quality_and_edge_cases.py
```

### 6. `06_real_world_scenarios.py`

#### Real-World Scenarios

Complete use cases based on real business problems:

- Financial fraud detection
- Customer support optimization
- Marketing campaign analysis
- Sales performance
- Website optimization
- Dashboard tree visualization

**Use cases:** Complete business applications, business analysis.

```bash
python 06_real_world_scenarios.py
```

## How to Run the Examples

### Prerequisites

Make sure you have Dataspot installed:

```bash
pip install dataspot
```

Or if you're developing locally:

```bash
pip install -e .
```

### Run Individual Examples

```bash
# From the examples folder
cd examples

# Run a specific example
python 01_basic_query_filtering.py

# Or run all examples
python 01_basic_query_filtering.py
python 02_pattern_filtering_basic.py
python 03_text_pattern_filtering.py
python 04_advanced_filtering.py
python 05_data_quality_and_edge_cases.py
python 06_real_world_scenarios.py
python 07_tree_visualization.py
```

### Run All Examples

```bash
# Script to run all examples
for file in *.py; do
    if [ "$file" != "README.md" ]; then
        echo "=== Running $file ==="
        python "$file"
        echo ""
    fi
done
```

## Correspondence with Tests

Each example corresponds to specific test cases:

| Example | Corresponding Tests |
|---------|-------------------|
| `01_basic_query_filtering.py` | `TestQueryFiltering` |
| `02_pattern_filtering_basic.py` | `TestPatternFiltering` (metrics) |
| `03_text_pattern_filtering.py` | `TestPatternFiltering` (text/regex) |
| `04_advanced_filtering.py` | `TestAdvancedFiltering` |
| `05_data_quality_and_edge_cases.py` | Special cases from all tests |
| `06_real_world_scenarios.py` | Practical applications |
| `07_tree_visualization.py` | Tree method functionality |

## Available Filtering Parameters

### Query Filters

- `query`: Dictionary to filter data before analysis
  - Single values: `{"field": "value"}`
  - Lists: `{"field": ["value1", "value2"]}`
  - Multiple fields: `{"field1": "value1", "field2": ["value2", "value3"]}`

### Pattern Filters

- `min_percentage`: Minimum representation percentage
- `max_percentage`: Maximum representation percentage
- `min_count`: Minimum record count
- `max_count`: Maximum record count
- `min_depth`: Minimum pattern depth
- `max_depth`: Maximum pattern depth
- `contains`: Text that the pattern must contain
- `exclude`: Text(s) that the pattern must not contain
- `regex`: Regular expression to filter patterns
- `limit`: Maximum number of results

## Use Cases by Industry

### Finance

- Fraud detection (`06_real_world_scenarios.py`)
- Transaction analysis (`01_basic_query_filtering.py`)

### E-commerce

- User behavior analysis (`01_basic_query_filtering.py`)
- Conversion optimization (`06_real_world_scenarios.py`)

### Technical Support

- Ticket classification (`02_pattern_filtering_basic.py`)
- Resource optimization (`06_real_world_scenarios.py`)

### Marketing

- Campaign analysis (`06_real_world_scenarios.py`)
- Audience segmentation (`04_advanced_filtering.py`)

### Web Development

- Log analysis (`03_text_pattern_filtering.py`)
- Performance metrics (`05_data_quality_and_edge_cases.py`)

## Tips for Using the Examples

1. **Start with basic examples** (`01_` and `02_`) to understand fundamental concepts
2. **Experiment with your own data** by modifying the example datasets
3. **Combine techniques** from different examples according to your needs
4. **Review edge cases** (`05_`) if working with real-world data
5. **Get inspired by real scenarios** (`06_`) for business applications

## Modify and Customize

All examples are designed to be easily modifiable:

1. **Change the data:** Replace simulated datasets with your own data
2. **Adjust filters:** Modify filtering parameters according to your needs
3. **Add fields:** Include additional fields in the analysis
4. **Combine techniques:** Use multiple examples as reference

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'dataspot'"

```bash
pip install dataspot
# or if you're in local development:
pip install -e .
```

### Examples don't show expected results

- Verify that input data is correct
- Adjust filtering parameters (e.g., reduce `min_percentage`)
- Check that field names match your data

### Slow performance with large datasets

- Use query filters (`query`) to reduce the dataset first
- Apply `limit` to restrict the number of results
- Consider using `min_count` or `min_percentage` to filter insignificant patterns

## Contributing

If you have ideas for new examples or improvements:

1. Create a new file following the numbering pattern
2. Include clear documentation in the code
3. Add the example to this README
4. Make sure the examples are executable

Practical examples are the best way to learn Dataspot!
