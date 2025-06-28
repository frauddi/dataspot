#!/usr/bin/env python3
"""Auto Discovery Examples.

Shows how to automatically discover concentration patterns without specifying fields in advance.
"""

from dataspot import Dataspot
from dataspot.models.discovery import DiscoverInput, DiscoverOptions


def main():
    """Auto discovery examples."""
    dataspot = Dataspot()

    print("=== 1. Basic Auto Discovery ===")

    # Transaction data with hidden patterns
    transaction_data = [
        {
            "country": "US",
            "method": "card",
            "device": "mobile",
            "tier": "premium",
            "amount": "high",
        },
        {
            "country": "US",
            "method": "card",
            "device": "desktop",
            "tier": "premium",
            "amount": "medium",
        },
        {
            "country": "RU",
            "method": "crypto",
            "device": "desktop",
            "tier": "basic",
            "amount": "high",
        },
        {
            "country": "RU",
            "method": "crypto",
            "device": "desktop",
            "tier": "basic",
            "amount": "high",
        },
        {
            "country": "RU",
            "method": "crypto",
            "device": "desktop",
            "tier": "basic",
            "amount": "high",
        },
        {
            "country": "EU",
            "method": "bank",
            "device": "mobile",
            "tier": "premium",
            "amount": "medium",
        },
        {
            "country": "EU",
            "method": "bank",
            "device": "mobile",
            "tier": "premium",
            "amount": "low",
        },
        {
            "country": "CA",
            "method": "paypal",
            "device": "tablet",
            "tier": "basic",
            "amount": "low",
        },
    ] * 3  # 24 records

    # Let the algorithm discover patterns automatically
    discovery_result = dataspot.discover(
        DiscoverInput(data=transaction_data),
        DiscoverOptions(max_fields=3, min_percentage=15.0, limit=8),
    )

    print(f"📊 Records analyzed: {discovery_result.statistics.total_records}")
    print(f"🔬 Fields ranked: {len(discovery_result.field_ranking)}")
    print(f"🎯 Patterns found: {len(discovery_result.top_patterns)}")

    print("\n🏆 Top discovered patterns:")
    for i, pattern in enumerate(discovery_result.top_patterns[:5], 1):
        print(
            f"  {i}. {pattern.path} - {pattern.count} records ({pattern.percentage:.1f}%)"
        )

    print("\n📈 Field importance ranking:")
    for field_ranking in discovery_result.field_ranking[:4]:
        print(f"  {field_ranking.field}: {field_ranking.score:.2f}")

    print("\n=== 2. Fraud Detection Discovery ===")

    # Focus on suspicious high-concentration patterns
    fraud_data = [
        {"country": "US", "payment": "card", "time": "day", "suspicious": "no"},
        {"country": "US", "payment": "card", "time": "day", "suspicious": "no"},
        {
            "country": "UNKNOWN",
            "payment": "crypto",
            "time": "night",
            "suspicious": "yes",
        },
        {
            "country": "UNKNOWN",
            "payment": "crypto",
            "time": "night",
            "suspicious": "yes",
        },
        {
            "country": "UNKNOWN",
            "payment": "crypto",
            "time": "night",
            "suspicious": "yes",
        },
        {
            "country": "UNKNOWN",
            "payment": "crypto",
            "time": "night",
            "suspicious": "yes",
        },
        {"country": "EU", "payment": "bank", "time": "day", "suspicious": "no"},
    ] * 2  # 14 records

    # High-threshold discovery for suspicious patterns
    fraud_discovery = dataspot.discover(
        DiscoverInput(data=fraud_data),  # Don't use suspicious field manually
        DiscoverOptions(min_percentage=30.0, max_fields=3),
    )

    print(f"🚨 Suspicious patterns discovered: {len(fraud_discovery.top_patterns)}")
    for pattern in fraud_discovery.top_patterns[:3]:
        if pattern.percentage > 30:
            risk_level = "HIGH" if pattern.percentage > 50 else "MEDIUM"
            print(
                f"  🔍 {pattern.path} - {pattern.percentage:.1f}% ({risk_level} risk)"
            )

    print("\n=== 3. Business Intelligence Discovery ===")

    # Customer behavior data
    customer_data = [
        {
            "segment": "enterprise",
            "channel": "direct",
            "satisfaction": "high",
            "renewal": "yes",
        },
        {
            "segment": "enterprise",
            "channel": "direct",
            "satisfaction": "high",
            "renewal": "yes",
        },
        {
            "segment": "enterprise",
            "channel": "direct",
            "satisfaction": "medium",
            "renewal": "yes",
        },
        {
            "segment": "small_biz",
            "channel": "online",
            "satisfaction": "medium",
            "renewal": "no",
        },
        {
            "segment": "small_biz",
            "channel": "online",
            "satisfaction": "low",
            "renewal": "no",
        },
        {
            "segment": "startup",
            "channel": "partner",
            "satisfaction": "high",
            "renewal": "yes",
        },
    ] * 2  # 12 records

    # Business insights discovery
    business_discovery = dataspot.discover(
        DiscoverInput(data=customer_data),
        DiscoverOptions(min_percentage=20.0, max_fields=4),
    )

    print(f"💼 Business patterns found: {len(business_discovery.top_patterns)}")

    # Categorize insights
    for pattern in business_discovery.top_patterns[:4]:
        insight_type = "💰" if "enterprise" in str(pattern.path) else "📊"
        print(f"  {insight_type} {pattern.path} - {pattern.percentage:.1f}%")

    print("\n=== 4. Discovery vs Manual Comparison ===")

    # Simple comparison data
    comparison_data = [
        {"region": "west", "product": "premium", "outcome": "success"},
        {"region": "west", "product": "premium", "outcome": "success"},
        {"region": "west", "product": "basic", "outcome": "mixed"},
        {"region": "east", "product": "premium", "outcome": "success"},
        {"region": "east", "product": "basic", "outcome": "failure"},
    ] * 2  # 10 records

    # Manual analysis (common guess)
    from dataspot.models.finder import FindInput, FindOptions

    manual_result = dataspot.find(
        FindInput(data=comparison_data, fields=["region", "product"]),
        FindOptions(min_percentage=20.0),
    )

    # Auto discovery
    auto_result = dataspot.discover(
        DiscoverInput(data=comparison_data), DiscoverOptions(min_percentage=20.0)
    )

    print(f"👤 Manual analysis: {len(manual_result.patterns)} patterns")
    print(f"🤖 Auto discovery: {len(auto_result.top_patterns)} patterns")

    if manual_result.patterns and auto_result.top_patterns:
        manual_best = manual_result.patterns[0].percentage
        auto_best = auto_result.top_patterns[0].percentage

        print(f"📊 Best manual: {manual_best:.1f}%")
        print(f"📊 Best auto: {auto_best:.1f}%")

        if auto_best > manual_best:
            print("🚀 Auto-discovery found better patterns!")
        else:
            print("✅ Comparable results")


if __name__ == "__main__":
    main()
