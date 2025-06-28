"""Real-World Scenarios Examples.

Shows complete business use cases for fraud detection, support optimization, and marketing analysis.
"""

from dataspot import Dataspot
from dataspot.models.finder import FindInput, FindOptions
from dataspot.models.tree import TreeInput, TreeOptions


def main():
    """Real-world business scenario examples."""
    dataspot = Dataspot()

    print("=== 1. Fraud Detection ===")

    # Simple fraud transaction data
    fraud_data = [
        {
            "country": "US",
            "method": "card",
            "amount": "low",
            "time": "day",
            "fraud": "no",
        },
        {
            "country": "US",
            "method": "card",
            "amount": "medium",
            "time": "day",
            "fraud": "no",
        },
        {
            "country": "RU",
            "method": "crypto",
            "amount": "high",
            "time": "night",
            "fraud": "yes",
        },
        {
            "country": "RU",
            "method": "crypto",
            "amount": "high",
            "time": "night",
            "fraud": "yes",
        },
        {
            "country": "CN",
            "method": "wire",
            "amount": "high",
            "time": "night",
            "fraud": "yes",
        },
        {
            "country": "EU",
            "method": "card",
            "amount": "medium",
            "time": "day",
            "fraud": "no",
        },
    ] * 3  # 18 records

    # Find fraud patterns
    fraud_patterns = dataspot.find(
        FindInput(
            data=fraud_data,
            fields=["country", "method", "amount"],
            query={"fraud": "yes"},
        ),
        FindOptions(min_percentage=20.0, limit=5),
    )

    print(f"Fraud patterns found: {len(fraud_patterns.patterns)}")
    for pattern in fraud_patterns.patterns:
        print(
            f"  🚨 {pattern.path} - {pattern.count} cases ({pattern.percentage:.1f}%)"
        )

    print("\n=== 2. Support Optimization ===")

    # Support ticket data
    support_data = [
        {
            "category": "billing",
            "priority": "high",
            "agent": "senior",
            "resolved": "fast",
        },
        {
            "category": "billing",
            "priority": "critical",
            "agent": "senior",
            "resolved": "fast",
        },
        {
            "category": "technical",
            "priority": "medium",
            "agent": "junior",
            "resolved": "slow",
        },
        {
            "category": "technical",
            "priority": "low",
            "agent": "junior",
            "resolved": "medium",
        },
        {
            "category": "account",
            "priority": "medium",
            "agent": "senior",
            "resolved": "fast",
        },
        {
            "category": "feature",
            "priority": "low",
            "agent": "junior",
            "resolved": "slow",
        },
    ] * 4  # 24 records

    # Find efficiency patterns
    efficient_patterns = dataspot.find(
        FindInput(
            data=support_data, fields=["category", "agent"], query={"resolved": "fast"}
        ),
        FindOptions(min_percentage=15.0),
    )

    print(f"Efficient support patterns: {len(efficient_patterns.patterns)}")
    for pattern in efficient_patterns.patterns:
        print(
            f"  ⚡ {pattern.path} - {pattern.count} fast resolutions ({pattern.percentage:.1f}%)"
        )

    print("\n=== 3. Marketing Analysis ===")

    # Marketing campaign data
    marketing_data = [
        {
            "channel": "social",
            "demographic": "18-25",
            "device": "mobile",
            "converted": "yes",
        },
        {
            "channel": "social",
            "demographic": "18-25",
            "device": "mobile",
            "converted": "yes",
        },
        {
            "channel": "email",
            "demographic": "26-35",
            "device": "desktop",
            "converted": "no",
        },
        {
            "channel": "google",
            "demographic": "36-45",
            "device": "desktop",
            "converted": "yes",
        },
        {
            "channel": "social",
            "demographic": "26-35",
            "device": "mobile",
            "converted": "yes",
        },
        {
            "channel": "email",
            "demographic": "36-45",
            "device": "desktop",
            "converted": "no",
        },
    ] * 3  # 18 records

    # Find successful conversion patterns
    conversion_patterns = dataspot.find(
        FindInput(
            data=marketing_data,
            fields=["channel", "demographic"],
            query={"converted": "yes"},
        ),
        FindOptions(min_percentage=20.0, limit=5),
    )

    print(f"High-conversion patterns: {len(conversion_patterns.patterns)}")
    for pattern in conversion_patterns.patterns:
        print(
            f"  📈 {pattern.path} - {pattern.count} conversions ({pattern.percentage:.1f}%)"
        )

    print("\n=== 4. Sales Performance ===")

    # Sales data
    sales_data = [
        {
            "territory": "west",
            "industry": "tech",
            "rep": "senior",
            "size": "large",
            "won": "yes",
        },
        {
            "territory": "west",
            "industry": "tech",
            "rep": "senior",
            "size": "medium",
            "won": "yes",
        },
        {
            "territory": "east",
            "industry": "finance",
            "rep": "junior",
            "size": "small",
            "won": "no",
        },
        {
            "territory": "east",
            "industry": "healthcare",
            "rep": "senior",
            "size": "large",
            "won": "yes",
        },
        {
            "territory": "west",
            "industry": "tech",
            "rep": "senior",
            "size": "large",
            "won": "yes",
        },
        {
            "territory": "east",
            "industry": "finance",
            "rep": "senior",
            "size": "medium",
            "won": "yes",
        },
    ] * 2  # 12 records

    # Find winning patterns
    winning_patterns = dataspot.find(
        FindInput(
            data=sales_data,
            fields=["territory", "industry", "rep"],
            query={"won": "yes"},
        ),
        FindOptions(min_percentage=15.0, contains="senior"),
    )

    print(f"Winning sales patterns: {len(winning_patterns.patterns)}")
    for pattern in winning_patterns.patterns:
        print(f"  💰 {pattern.path} - {pattern.count} wins ({pattern.percentage:.1f}%)")

    print("\n=== 5. Dashboard Tree ===")

    # Dashboard data
    dashboard_data = [
        {"region": "US", "device": "mobile", "user": "premium", "revenue": "high"},
        {"region": "US", "device": "desktop", "user": "free", "revenue": "low"},
        {"region": "EU", "device": "mobile", "user": "premium", "revenue": "high"},
        {"region": "EU", "device": "tablet", "user": "enterprise", "revenue": "high"},
        {"region": "CA", "device": "mobile", "user": "free", "revenue": "medium"},
    ] * 2  # 10 records

    # Build hierarchical tree for dashboard
    tree = dataspot.tree(
        TreeInput(data=dashboard_data, fields=["region", "device", "user"]),
        TreeOptions(min_percentage=10.0, top=3),
    )

    print("Dashboard tree structure:")
    tree_dict = tree.to_dict()
    # Show simplified tree
    print(f"📊 Total: {tree_dict['value']} records")
    print(f"🌍 Regions: {len(tree_dict['children'])}")
    for region in tree_dict["children"]:
        print(
            f"  {region['name']}: {region['value']} records ({region['percentage']:.1f}%)"
        )


if __name__ == "__main__":
    main()
