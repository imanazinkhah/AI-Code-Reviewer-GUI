from reviewer.syntax_checker import check_syntax
from reviewer.quality_checker import check_quality
from reviewer.function_analyzer import analyze_functions
from reviewer.complexity_analyzer import analyze_complexity
from reviewer.security_checker import check_security
from reviewer.report import generate_report
from reviewer.html_report import generate_html_report
from reviewer.ai_reviewer import review_with_ai


def main():

    print("================================")
    print("      AI Code Reviewer")
    print("================================")

    file_path = input("Enter Python file path: ")

    syntax_result = check_syntax(file_path)

    if not syntax_result["valid"]:

        error = syntax_result["error"]

        print("\n❌ Syntax Error")
        print(f"Line: {error['line']}")
        print(f"Column: {error['column']}")
        print(f"Message: {error['message']}")

        return

    quality_issues = check_quality(file_path)

    function_results = analyze_functions(file_path)

    complexity_results = analyze_complexity(file_path)

    security_issues = check_security(file_path)

    print("\n🤖 AI Code Review")

    try:

        ai_review = review_with_ai(file_path)

        print("\n" + str(ai_review))

    except Exception as error:

        print(f"\n❌ AI Review Error: {error}")

        ai_review = None

    score = generate_report(
        file_path,
        syntax_result,
        quality_issues,
        function_results,
        complexity_results,
        security_issues
    )

    generate_html_report(
        file_path,
        syntax_result,
        quality_issues,
        function_results,
        complexity_results,
        security_issues,
        score,
        ai_review
    )


if __name__ == "__main__":
    main()