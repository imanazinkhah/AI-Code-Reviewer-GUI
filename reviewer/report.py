def generate_report(
    file_path,
    syntax_result,
    quality_issues,
    function_results,
    complexity_results,
    security_issues
):

    score = 100

    if not syntax_result["valid"]:
        score -= 30

    score -= len(quality_issues) * 5
    score -= len(security_issues) * 10

    for function in complexity_results:

        if function["complexity"] > 10:
            score -= 10

        elif function["complexity"] > 5:
            score -= 5

    if score < 0:
        score = 0

    print("\n")
    print("=" * 50)
    print("             CODE AUTO REVIEWER")
    print("=" * 50)

    print(f"\n📁 File: {file_path}")

    print("\n📋 Review Summary")
    print("-" * 50)

    # Syntax

    if syntax_result["valid"]:
        print("Syntax       ✅ PASS")
    else:
        print("Syntax       ❌ FAIL")

    # Quality

    if not quality_issues:
        print("Quality      ✅ PASS")
    else:
        print(f"Quality      ⚠️ {len(quality_issues)} Issues")

    # Functions

    print(f"Functions    ✅ {len(function_results)} Found")

    # Complexity

    high_complexity = 0

    for function in complexity_results:
        if function["complexity"] > 5:
            high_complexity += 1

    if high_complexity == 0:
        print("Complexity   ✅ PASS")
    else:
        print(f"Complexity   ⚠️ {high_complexity} Issues")

    # Security

    if not security_issues:
        print("Security     ✅ PASS")
    else:
        print(f"Security     🔴 {len(security_issues)} Issues")

    print("\n" + "-" * 50)

    print(f"⭐ Overall Score: {score}/100")

    if score >= 90:
        print("Excellent Code 🟢")

    elif score >= 75:
        print("Good Code 🟢")

    elif score >= 60:
        print("Needs Improvement 🟡")

    else:
        print("Poor Code 🔴")

    print("=" * 50)

    return score