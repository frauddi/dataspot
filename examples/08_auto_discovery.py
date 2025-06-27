#!/usr/bin/env python3
"""Auto-Discovery Example: Automatically find concentration patterns.

This example demonstrates how to use the discover() method to automatically
find the most interesting concentration patterns in your data without
needing to specify which fields to analyze.

Perfect for:
- Data exploration when you don't know what to look for
- Fraud detection pattern discovery
- Business intelligence insights
- Data quality assessment
"""

import random

import dataspot


def generate_realistic_transaction_data():
    """Generate realistic transaction data with hidden patterns."""
    print("📊 Generating realistic transaction dataset...")

    # Define realistic values
    countries = ["US", "UK", "DE", "FR", "ES", "IT", "CA", "AU", "JP", "BR"]
    cities = {
        "US": ["New York", "Los Angeles", "Chicago", "Houston"],
        "UK": ["London", "Manchester", "Birmingham", "Leeds"],
        "DE": ["Berlin", "Munich", "Hamburg", "Frankfurt"],
        "FR": ["Paris", "Lyon", "Marseille", "Toulouse"],
        "ES": ["Madrid", "Barcelona", "Valencia", "Seville"],
        "IT": ["Rome", "Milan", "Naples", "Turin"],
        "CA": ["Toronto", "Vancouver", "Montreal", "Calgary"],
        "AU": ["Sydney", "Melbourne", "Brisbane", "Perth"],
        "JP": ["Tokyo", "Osaka", "Nagoya", "Sapporo"],
        "BR": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador"],
    }

    payment_methods = [
        "credit_card",
        "debit_card",
        "paypal",
        "bank_transfer",
        "crypto",
        "apple_pay",
        "google_pay",
    ]
    merchants = [
        "Amazon",
        "Walmart",
        "Target",
        "Best Buy",
        "Apple Store",
        "Netflix",
        "Spotify",
        "Uber",
        "Airbnb",
        "Steam",
    ]
    device_types = ["mobile", "desktop", "tablet", "smart_tv", "watch"]
    user_tiers = ["bronze", "silver", "gold", "platinum", "diamond"]

    transactions = []

    for i in range(2000):
        # Create intentional patterns for discovery

        # Pattern 1: High-value fraud pattern (5% of data)
        if random.random() < 0.05:
            transaction = {
                "country": "US",
                "city": "New York",
                "payment_method": "crypto",
                "merchant": "Steam",
                "device": "desktop",
                "user_tier": "bronze",  # Suspicious: new users with high crypto payments
                "amount": random.randint(500, 2000),
                "hour": random.randint(2, 5),  # Late night transactions
                "is_weekend": True,
                "transaction_id": f"txn_{i}",
                "user_id": f"user_{random.randint(1, 100)}",  # Should be filtered out
            }

        # Pattern 2: Premium user concentration (20% of data)
        elif random.random() < 0.25:
            country = "UK"
            transaction = {
                "country": country,
                "city": random.choice(cities[country]),
                "payment_method": "apple_pay",
                "merchant": random.choice(["Apple Store", "Netflix", "Spotify"]),
                "device": "mobile",
                "user_tier": "platinum",
                "amount": random.randint(50, 300),
                "hour": random.randint(18, 22),  # Evening shopping
                "is_weekend": False,
                "transaction_id": f"txn_{i}",
                "user_id": f"user_{random.randint(1, 100)}",
            }

        # Pattern 3: Weekend shopping pattern (15% of data)
        elif random.random() < 0.18:
            country = random.choice(["DE", "FR"])
            transaction = {
                "country": country,
                "city": random.choice(cities[country]),
                "payment_method": "credit_card",
                "merchant": random.choice(["Amazon", "Walmart", "Target"]),
                "device": random.choice(["mobile", "tablet"]),
                "user_tier": random.choice(["silver", "gold"]),
                "amount": random.randint(25, 150),
                "hour": random.randint(10, 16),  # Weekend shopping hours
                "is_weekend": True,
                "transaction_id": f"txn_{i}",
                "user_id": f"user_{random.randint(1, 100)}",
            }

        # Random transactions (remaining ~60%)
        else:
            country = random.choice(countries)
            transaction = {
                "country": country,
                "city": random.choice(cities[country]),
                "payment_method": random.choice(payment_methods),
                "merchant": random.choice(merchants),
                "device": random.choice(device_types),
                "user_tier": random.choice(user_tiers),
                "amount": random.randint(5, 500),
                "hour": random.randint(0, 23),
                "is_weekend": random.choice([True, False]),
                "transaction_id": f"txn_{i}",
                "user_id": f"user_{random.randint(1, 100)}",
            }

        transactions.append(transaction)

    print(f"   ✅ Generated {len(transactions)} transactions with hidden patterns")
    return transactions


def basic_auto_discovery():
    """Automatic pattern discovery."""
    print("\n" + "=" * 60)
    print("🔍 Example 1: Basic Auto-Discovery")
    print("=" * 60)

    data = generate_realistic_transaction_data()
    dataspot_instance = dataspot.Dataspot()

    # Simple auto-discovery
    print("🤖 Running automatic pattern discovery...")
    results = dataspot_instance.discover(data)

    print("\n📊 Discovery Results:")
    print(f"   📈 Total records analyzed: {results['statistics']['total_records']:,}")
    print(f"   🔬 Fields analyzed: {results['statistics']['fields_analyzed']}")
    print(f"   🧪 Combinations tried: {results['statistics']['combinations_tried']}")
    print(f"   📋 Patterns found: {results['statistics']['patterns_discovered']}")
    print(
        f"   🎯 Best concentration: {results['statistics']['best_concentration']:.1f}%"
    )

    print("\n🏆 Top 5 Discovered Patterns:")
    for i, pattern in enumerate(results["top_patterns"][:5], 1):
        print(f"   {i}. {pattern.path}")
        print(f"      → {pattern.percentage}% ({pattern.count:,} records)")

    print("\n🎯 Field Ranking (most valuable for analysis):")
    for i, (field, score) in enumerate(results["field_ranking"][:5], 1):
        print(f"   {i}. {field}: {score:.1f} points")

    return results


def targeted_fraud_discovery():
    """Fraud detection."""
    print("\n" + "=" * 60)
    print("🚨 Example 2: Fraud Detection Discovery")
    print("=" * 60)

    data = generate_realistic_transaction_data()
    dataspot_instance = dataspot.Dataspot()

    # High-threshold discovery for suspicious patterns
    print("🕵️ Looking for suspicious high-concentration patterns...")
    fraud_results = dataspot_instance.discover(
        data,
        min_concentration=25.0,  # Only strong patterns
        max_fields=3,  # Limit complexity
        max_combinations=15,  # Focus on best combinations
    )

    print("\n🚨 Suspicious Patterns Found:")
    suspicious_patterns = [
        p for p in fraud_results["top_patterns"] if p.percentage > 30
    ]

    if suspicious_patterns:
        for i, pattern in enumerate(suspicious_patterns[:3], 1):
            print(f"\n   🔍 Pattern {i}: {pattern.path}")
            print(
                f"      ⚠️  Concentration: {pattern.percentage}% ({pattern.count} records)"
            )
            print(
                f"      📊 Risk Level: {'HIGH' if pattern.percentage > 50 else 'MEDIUM'}"
            )

            # Show sample records
            if pattern.samples:
                print("      📋 Sample records:")
                for j, sample in enumerate(pattern.samples[:2], 1):
                    relevant_fields = {
                        k: v
                        for k, v in sample.items()
                        if k in pattern.path.replace("=", " ").split()
                    }
                    print(f"         {j}. {relevant_fields}")
    else:
        print("   ✅ No highly suspicious patterns detected")


def business_intelligence_discovery():
    """Generate business intelligence insights."""
    print("\n" + "=" * 60)
    print("📊 Example 3: Business Intelligence Discovery")
    print("=" * 60)

    data = generate_realistic_transaction_data()
    dataspot_instance = dataspot.Dataspot()

    # Discovery for business insights
    print("📈 Discovering business intelligence patterns...")
    bi_results = dataspot_instance.discover(
        data,
        min_concentration=15.0,  # Medium threshold
        max_fields=4,  # Allow more complex patterns
        max_combinations=20,
    )

    print("\n💼 Business Intelligence Insights:")

    # Geographic insights
    geo_patterns = [
        p
        for p in bi_results["top_patterns"]
        if "country" in p.path and p.percentage > 20
    ]
    if geo_patterns:
        print("\n   🌍 Geographic Concentrations:")
        for pattern in geo_patterns[:3]:
            print(f"      • {pattern.path} → {pattern.percentage}% market share")

    # Payment method insights
    payment_patterns = [
        p
        for p in bi_results["top_patterns"]
        if "payment_method" in p.path and p.percentage > 20
    ]
    if payment_patterns:
        print("\n   💳 Payment Method Preferences:")
        for pattern in payment_patterns[:3]:
            print(f"      • {pattern.path} → {pattern.percentage}% of transactions")

    # User tier insights
    tier_patterns = [
        p
        for p in bi_results["top_patterns"]
        if "user_tier" in p.path and p.percentage > 15
    ]
    if tier_patterns:
        print("\n   👑 User Tier Analysis:")
        for pattern in tier_patterns[:3]:
            print(f"      • {pattern.path} → {pattern.percentage}% concentration")


def compare_manual_vs_auto():
    """Compare manual analysis vs auto-discovery."""
    print("\n" + "=" * 60)
    print("⚖️  Example 4: Manual vs Auto-Discovery Comparison")
    print("=" * 60)

    data = generate_realistic_transaction_data()
    dataspot_instance = dataspot.Dataspot()

    # Manual analysis (assume we guess some fields)
    print("👤 Manual Analysis (analyst's guess):")
    manual_fields = ["country", "payment_method", "user_tier"]  # Common guess
    manual_patterns = dataspot_instance.find(data, manual_fields, min_percentage=20)

    if manual_patterns:
        print(f"   Best pattern: {manual_patterns[0].path}")
        print(f"   Concentration: {manual_patterns[0].percentage}%")
        print(f"   Total patterns: {len(manual_patterns)}")

    # Auto-discovery
    print("\n🤖 Auto-Discovery (no human bias):")
    auto_results = dataspot_instance.discover(data, min_concentration=20)

    if auto_results["top_patterns"]:
        print(f"   Best pattern: {auto_results['top_patterns'][0].path}")
        print(f"   Concentration: {auto_results['top_patterns'][0].percentage}%")
        print(f"   Total patterns: {len(auto_results['top_patterns'])}")

    # Comparison
    if manual_patterns and auto_results["top_patterns"]:
        manual_best = manual_patterns[0].percentage
        auto_best = auto_results["top_patterns"][0].percentage

        print("\n📊 Comparison Results:")
        print(f"   Manual best: {manual_best}%")
        print(f"   Auto best: {auto_best}%")

        if auto_best > manual_best:
            improvement = ((auto_best - manual_best) / manual_best) * 100
            print(f"   🚀 Auto-discovery found {improvement:.1f}% better patterns!")
        elif auto_best >= manual_best * 0.9:
            print("   ✅ Auto-discovery matched manual analysis quality")
        else:
            print("   📝 Manual analysis was better (domain knowledge helps)")


def performance_demonstration():
    """Demonstrate performance characteristics."""
    print("\n" + "=" * 60)
    print("⚡ Example 5: Performance Demonstration")
    print("=" * 60)

    import time

    # Test different dataset sizes
    sizes = [500, 1000, 2000]

    print("🔬 Testing performance across different dataset sizes:")

    for size in sizes:
        # Generate data
        print(f"\n   📊 Testing {size:,} records...")
        data = []
        for i in range(size):
            data.append(
                {
                    "country": ["US", "EU", "CA", "AU"][i % 4],
                    "device": ["mobile", "desktop", "tablet"][i % 3],
                    "payment": ["card", "bank", "crypto"][i % 3],
                    "tier": ["free", "premium"][i % 2],
                }
            )

        dataspot_instance = dataspot.Dataspot()

        # Measure performance
        start_time = time.time()
        results = dataspot_instance.discover(data, max_fields=3)
        end_time = time.time()

        duration_ms = (end_time - start_time) * 1000
        records_per_sec = int(size / (duration_ms / 1000)) if duration_ms > 0 else 0

        print(f"      ⏱️  Time: {duration_ms:.1f}ms")
        print(f"      🚀 Speed: {records_per_sec:,} records/sec")
        print(f"      📋 Patterns: {len(results['top_patterns'])}")
        print(f"      🧪 Combinations: {results['statistics']['combinations_tried']}")


if __name__ == "__main__":
    print("🚀 Dataspot Auto-Discovery Examples")
    print("=" * 60)
    print("This script demonstrates automatic pattern discovery capabilities.")
    print("No need to specify fields - the algorithm finds patterns automatically!")

    try:
        # Run all examples
        basic_auto_discovery()
        targeted_fraud_discovery()
        business_intelligence_discovery()
        compare_manual_vs_auto()
        performance_demonstration()

        print("\n" + "=" * 60)
        print("✅ All auto-discovery examples completed successfully!")
        print("\n🎯 Key Takeaways:")
        print("   • Auto-discovery finds patterns you might miss")
        print("   • Great for exploratory data analysis")
        print("   • Reduces analyst bias and saves time")
        print("   • Perfect for fraud detection and business intelligence")
        print("   • Performance scales well with dataset size")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()
