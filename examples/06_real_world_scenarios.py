"""Real-World Scenarios Examples.

This module demonstrates complete real-world use cases for Dataspot analysis,
showing how different filtering techniques solve actual business problems.
"""
from dataspot import Dataspot


def fraud_detection_analysis():
    """Analyze transaction patterns to identify potential fraud."""
    print("=== FRAUD DETECTION ANALYSIS ===")
    print("Analyzing transaction patterns to identify potential fraud...")

    # Simulate financial transaction data
    fraud_data = []
    import random

    random.seed(42)  # For reproducible results

    countries = ["US", "UK", "FR", "DE", "JP", "CN", "RU", "BR"]
    devices = ["mobile", "desktop", "tablet"]
    payment_methods = ["credit_card", "debit_card", "paypal", "bank_transfer"]
    merchants = ["amazon", "ebay", "local_store", "gas_station", "restaurant"]

    for i in range(1000):
        # Create some suspicious patterns
        is_suspicious = i < 50  # First 50 transactions are suspicious

        fraud_data.append(
            {
                "country": random.choice(["RU", "CN"] if is_suspicious else countries),
                "device": random.choice(devices),
                "payment_method": random.choice(payment_methods),
                "merchant_type": random.choice(merchants),
                "amount_range": "high"
                if (is_suspicious and random.random() > 0.7)
                else random.choice(["low", "medium", "high"]),
                "time_of_day": random.choice(
                    ["night", "morning", "afternoon", "evening"]
                ),
                "is_fraud": "yes" if is_suspicious else "no",
            }
        )

    dataspot = Dataspot()

    # Find patterns in fraudulent transactions
    print("1. Analyzing known fraud patterns...")
    fraud_patterns = dataspot.find(
        fraud_data,
        ["country", "device", "payment_method", "amount_range"],
        query={"is_fraud": "yes"},
        min_percentage=10,
        limit=10,
    )

    print(f"Top fraud patterns ({len(fraud_patterns)} found):")
    for pattern in fraud_patterns:
        print(f"  {pattern.path}")
        print(
            f"    Frequency: {pattern.count} transactions ({pattern.percentage:.1f}%)"
        )

    # Find high-risk country patterns
    print("\n2. High-risk country analysis...")
    risk_patterns = dataspot.find(
        fraud_data,
        ["country", "payment_method", "merchant_type"],
        contains="RU",
        min_count=5,
    )

    print(f"High-risk patterns: {len(risk_patterns)}")
    for pattern in risk_patterns[:5]:
        print(f"  {pattern.path} - {pattern.count} cases")
    print()


def customer_support_optimization():
    """Optimize customer support ticket allocation and efficiency."""
    print("=== CUSTOMER SUPPORT OPTIMIZATION ===")
    print("Analyzing support tickets to optimize team allocation...")

    # Simulate support ticket data
    support_data = []
    categories = ["technical", "billing", "account", "feature_request", "bug_report"]
    priorities = ["low", "medium", "high", "critical"]
    products = ["web_app", "mobile_app", "api", "desktop_app"]
    regions = ["north_america", "europe", "asia_pacific", "other"]

    for i in range(800):
        # Create realistic patterns - technical issues more common, billing urgent
        category = categories[i % 5]
        if category == "billing":
            priority = ["high", "critical"][i % 2]
        elif category == "technical":
            priority = ["low", "medium"][i % 2]
        else:
            priority = priorities[i % 4]

        support_data.append(
            {
                "category": category,
                "priority": priority,
                "product": products[i % 4],
                "region": regions[i % 4],
                "resolution_time": "fast"
                if priority in ["critical", "high"]
                else ["slow", "medium", "fast"][i % 3],
                "satisfaction": ["low", "medium", "high"][i % 3],
                "agent_tier": "senior"
                if priority == "critical"
                else ["junior", "senior"][i % 2],
            }
        )

    dataspot = Dataspot()

    # Find critical ticket patterns
    print("1. Critical ticket analysis...")
    critical_patterns = dataspot.find(
        support_data,
        ["category", "product", "region"],
        query={"priority": "critical"},
        min_percentage=15,
        limit=8,
    )

    print(f"Critical ticket patterns: {len(critical_patterns)}")
    for pattern in critical_patterns:
        print(f"  {pattern.path} - {pattern.count} tickets ({pattern.percentage:.1f}%)")

    # Analyze resolution efficiency
    print("\n2. Resolution efficiency analysis...")
    efficiency_patterns = dataspot.find(
        support_data,
        ["category", "agent_tier", "resolution_time"],
        query={"satisfaction": "high"},
        contains="fast",
        min_count=10,
    )

    print(f"High-efficiency patterns: {len(efficiency_patterns)}")
    for pattern in efficiency_patterns:
        print(f"  {pattern.path} - {pattern.count} satisfied customers")

    # Regional support needs
    print("\n3. Regional support needs...")
    regional_patterns = dataspot.find(
        support_data,
        ["region", "category", "priority"],
        min_percentage=8,
        exclude="low",  # Focus on urgent issues
        limit=12,
    )

    print(f"Regional urgent issue patterns: {len(regional_patterns)}")
    for pattern in regional_patterns[:6]:
        print(f"  {pattern.path} - {pattern.count} tickets")
    print()


def marketing_campaign_analysis():
    """Analyze marketing campaign performance across channels and demographics."""
    print("=== MARKETING CAMPAIGN ANALYSIS ===")
    print("Analyzing campaign performance across channels and demographics...")

    # Simulate marketing campaign data
    campaign_data = []
    channels = ["email", "social_media", "google_ads", "display", "influencer"]
    demographics = ["18-25", "26-35", "36-45", "46-55", "55+"]
    interests = ["tech", "fashion", "fitness", "food", "travel"]
    devices = ["mobile", "desktop", "tablet"]

    for i in range(1500):
        # Create realistic conversion patterns
        channel = channels[i % 5]
        demo = demographics[i % 5]

        # Social media and influencer work better for younger demographics
        if channel in ["social_media", "influencer"] and demo in ["18-25", "26-35"]:
            conversion = ["yes", "no", "no"][i % 3]  # Higher conversion
        else:
            conversion = ["yes", "no", "no", "no"][i % 4]  # Lower conversion

        campaign_data.append(
            {
                "channel": channel,
                "demographic": demo,
                "interest": interests[i % 5],
                "device": devices[i % 3],
                "time_period": ["morning", "afternoon", "evening", "night"][i % 4],
                "conversion": conversion,
                "engagement": ["low", "medium", "high"][i % 3],
            }
        )

    dataspot = Dataspot()

    # Analyze high-converting patterns
    print("1. High-conversion pattern analysis...")
    conversion_patterns = dataspot.find(
        campaign_data,
        ["channel", "demographic", "interest", "device"],
        query={"conversion": "yes"},
        min_percentage=12,
        limit=10,
    )

    print(f"High-conversion patterns: {len(conversion_patterns)}")
    for pattern in conversion_patterns:
        print(f"  {pattern.path}")
        print(f"    Conversions: {pattern.count} ({pattern.percentage:.1f}%)")

    # Channel effectiveness by demographic
    print("\n2. Channel effectiveness by demographic...")
    for demo in ["18-25", "26-35", "36-45"]:
        demo_patterns = dataspot.find(
            campaign_data,
            ["channel", "device"],
            query={"demographic": demo, "conversion": "yes"},
            min_count=5,
            limit=3,
        )
        print(f"   {demo} age group - Top channels:")
        for pattern in demo_patterns:
            print(f"     {pattern.path} - {pattern.count} conversions")

    # Low engagement analysis
    print("\n3. Low engagement pattern analysis...")
    low_engagement = dataspot.find(
        campaign_data,
        ["channel", "demographic", "time_period"],
        query={"engagement": "low"},
        min_percentage=15,
        limit=8,
    )

    print(f"Low engagement patterns to avoid: {len(low_engagement)}")
    for pattern in low_engagement[:5]:
        print(f"  {pattern.path} - {pattern.count} low-engagement cases")
    print()


def sales_performance_analysis():
    """Optimize sales performance and territory allocation."""
    print("=== SALES PERFORMANCE ANALYSIS ===")
    print("Analyzing sales patterns for territory optimization...")

    # Simulate sales performance data
    sales_data = []
    territories = ["west_coast", "east_coast", "midwest", "south", "international"]
    industries = ["technology", "healthcare", "finance", "manufacturing", "retail"]
    sales_reps = ["junior", "senior", "veteran"]

    for i in range(1200):
        territory = territories[i % 5]
        industry = industries[i % 5]
        rep_type = sales_reps[i % 3]

        # Veterans perform better on large deals
        if rep_type == "veteran":
            deal_size = ["large", "enterprise", "medium"][i % 3]
            outcome = ["won", "lost"][i % 2]  # 50% win rate
        elif rep_type == "senior":
            deal_size = ["medium", "large", "small"][i % 3]
            outcome = ["won", "lost", "lost"][i % 3]  # 33% win rate
        else:
            deal_size = ["small", "medium"][i % 2]
            outcome = ["won", "lost", "lost", "lost"][i % 4]  # 25% win rate

        sales_data.append(
            {
                "territory": territory,
                "industry": industry,
                "deal_size": deal_size,
                "rep_type": rep_type,
                "quarter": f"Q{(i % 4) + 1}",
                "outcome": outcome,
                "sales_cycle": ["short", "medium", "long"][i % 3],
            }
        )

    dataspot = Dataspot()

    # Winning deal patterns
    print("1. Winning deal pattern analysis...")
    winning_patterns = dataspot.find(
        sales_data,
        ["territory", "industry", "deal_size", "rep_type"],
        query={"outcome": "won"},
        min_percentage=8,
        limit=12,
    )

    print(f"Winning patterns: {len(winning_patterns)}")
    for pattern in winning_patterns:
        print(f"  {pattern.path}")
        print(f"    Wins: {pattern.count} ({pattern.percentage:.1f}%)")

    # Territory performance
    print("\n2. Territory performance analysis...")
    for territory in ["west_coast", "east_coast", "midwest"]:
        territory_patterns = dataspot.find(
            sales_data,
            ["industry", "deal_size", "rep_type"],
            query={"territory": territory, "outcome": "won"},
            min_count=8,
            limit=4,
        )
        print(f"   {territory.title()} - Top patterns:")
        for pattern in territory_patterns:
            print(f"     {pattern.path} - {pattern.count} wins")

    # Large deal analysis
    print("\n3. Large deal success factors...")
    large_deal_patterns = dataspot.find(
        sales_data,
        ["territory", "industry", "rep_type", "sales_cycle"],
        query={"deal_size": "enterprise", "outcome": "won"},
        min_count=3,
    )

    print(f"Enterprise deal success patterns: {len(large_deal_patterns)}")
    for pattern in large_deal_patterns:
        print(f"  {pattern.path} - {pattern.count} enterprise wins")
    print()


def website_analytics_optimization():
    """Analyze website user behavior patterns for conversion optimization."""
    print("=== WEBSITE ANALYTICS OPTIMIZATION ===")
    print("Analyzing user behavior patterns for conversion optimization...")

    # Simulate website analytics data
    web_data = []
    browsers = ["chrome", "safari", "firefox", "edge"]
    traffic_sources = ["organic", "paid_search", "social", "direct", "referral"]
    page_types = ["landing", "product", "category", "blog", "checkout"]
    user_types = ["new", "returning", "premium"]

    for i in range(2000):
        source = traffic_sources[i % 5]
        user_type = user_types[i % 3]

        # Premium users convert better
        if user_type == "premium":
            conversion = ["yes", "no"][i % 2]  # 50% conversion
        elif user_type == "returning":
            conversion = ["yes", "no", "no"][i % 3]  # 33% conversion
        else:
            conversion = ["yes", "no", "no", "no"][i % 4]  # 25% conversion

        web_data.append(
            {
                "browser": browsers[i % 4],
                "traffic_source": source,
                "page_type": page_types[i % 5],
                "user_type": user_type,
                "device": ["mobile", "desktop", "tablet"][i % 3],
                "session_duration": ["short", "medium", "long"][i % 3],
                "conversion": conversion,
            }
        )

    dataspot = Dataspot()

    # High-converting user journeys
    print("1. High-converting user journey analysis...")
    conversion_patterns = dataspot.find(
        web_data,
        ["traffic_source", "page_type", "user_type", "device"],
        query={"conversion": "yes"},
        min_percentage=10,
        limit=10,
    )

    print(f"High-conversion patterns: {len(conversion_patterns)}")
    for pattern in conversion_patterns:
        print(f"  {pattern.path}")
        print(f"    Conversions: {pattern.count} ({pattern.percentage:.1f}%)")

    # Mobile vs Desktop performance
    print("\n2. Device performance comparison...")

    mobile_patterns = dataspot.find(
        web_data,
        ["traffic_source", "user_type"],
        query={"device": "mobile", "conversion": "yes"},
        min_count=10,
        limit=5,
    )

    desktop_patterns = dataspot.find(
        web_data,
        ["traffic_source", "user_type"],
        query={"device": "desktop", "conversion": "yes"},
        min_count=10,
        limit=5,
    )

    print(f"   Mobile conversions: {len(mobile_patterns)} patterns")
    print(f"   Desktop conversions: {len(desktop_patterns)} patterns")

    # Traffic source effectiveness
    print("\n3. Traffic source effectiveness...")
    source_analysis = dataspot.find(
        web_data,
        ["traffic_source", "user_type", "session_duration"],
        query={"conversion": "yes"},
        min_percentage=5,
        contains="organic",
        limit=8,
    )

    print(f"Organic traffic conversion patterns: {len(source_analysis)}")
    for pattern in source_analysis:
        print(f"  {pattern.path} - {pattern.count} conversions")
    print()


if __name__ == "__main__":
    fraud_detection_analysis()
    customer_support_optimization()
    marketing_campaign_analysis()
    sales_performance_analysis()
    website_analytics_optimization()
