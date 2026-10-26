
from pathlib import Path
from html import escape

import markdown
import bleach


def generate_html_report(
    file_path,
    syntax_result,
    quality_issues,
    function_results,
    complexity_results,
    security_issues,
    score,
    ai_review=None
):
    """
    Generate an HTML report for the Python code review.
    """

    # Prepare file information
    file_name = Path(file_path).name

    # Prepare syntax status
    syntax_status = (
        "Passed"
        if syntax_result.get("valid", False)
        else "Failed"
    )

    syntax_class = (
        "success"
        if syntax_result.get("valid", False)
        else "danger"
    )

    # Convert score to a safe display value
    score_text = escape(str(score))

    # Prepare quality issues
    quality_html = ""

    if quality_issues:
        for issue in quality_issues:
            quality_html += (
                f'<div class="item warning">'
                f'{escape(str(issue))}</div>\n'
            )
    else:
        quality_html = (
            '<div class="item success">'
            'No quality issues found.'
            '</div>'
        )

    # Prepare function analysis
    functions_html = ""

    if function_results:
        functions_html += """
        <table>
            <thead>
                <tr>
                    <th>Function</th>
                    <th>Line</th>
                    <th>Parameters</th>
                    <th>Lines</th>
                </tr>
            </thead>
            <tbody>
        """

        for function in function_results:
            if isinstance(function, dict):
                name = function.get(
                    "name",
                    function.get("function_name", "Unknown")
                )
                line = function.get(
                    "line",
                    function.get("lineno", "-")
                )
                parameters = function.get(
                    "parameters",
                    function.get("args_count", "-")
                )
                lines = function.get(
                    "lines",
                    function.get("line_count", "-")
                )

            else:
                name = getattr(function, "name", "Unknown")
                line = getattr(function, "line", "-")
                parameters = getattr(
                    function,
                    "parameters",
                    "-"
                )
                lines = getattr(function, "lines", "-")

            functions_html += f"""
                <tr>
                    <td>{escape(str(name))}</td>
                    <td>{escape(str(line))}</td>
                    <td>{escape(str(parameters))}</td>
                    <td>{escape(str(lines))}</td>
                </tr>
            """

        functions_html += """
            </tbody>
        </table>
        """
    else:
        functions_html = (
            '<div class="item">'
            'No functions found.'
            '</div>'
        )

    # Prepare complexity analysis
    complexity_html = ""

    if complexity_results:
        if isinstance(complexity_results, dict):
            for name, value in complexity_results.items():
                complexity_html += (
                    '<div class="item">'
                    f'<strong>{escape(str(name))}:</strong> '
                    f'{escape(str(value))}'
                    '</div>\n'
                )
        else:
            for item in complexity_results:
                complexity_html += (
                    f'<div class="item">'
                    f'{escape(str(item))}</div>\n'
                )
    else:
        complexity_html = (
            '<div class="item">'
            'No complexity data available.'
            '</div>'
        )

    # Prepare security issues
    security_html = ""

    if security_issues:
        for issue in security_issues:
            security_html += (
                f'<div class="item danger">'
                f'{escape(str(issue))}</div>\n'
            )
    else:
        security_html = (
            '<div class="item success">'
            'No security issues detected by the basic checker.'
            '</div>'
        )

    # Prepare AI review
    if ai_review:
        ai_review_html = markdown.markdown(
            str(ai_review),
            extensions=[
                "fenced_code",
                "tables",
                "sane_lists"
            ]
        )

        # Allow only safe HTML elements in the AI output
        allowed_tags = set(
            bleach.sanitizer.ALLOWED_TAGS
        ) | {
            "h1", "h2", "h3", "h4",
            "p", "pre", "code",
            "ul", "ol", "li",
            "hr", "br", "blockquote",
            "table", "thead", "tbody",
            "tr", "th", "td",
            "strong", "del", "div"
        }

        ai_review_html = bleach.clean(
            ai_review_html,
            tags=allowed_tags,
            attributes={
                "code": ["class"],
                "th": ["align"],
                "td": ["align"]
            },
            strip=True
        )
    else:
        ai_review_html = """
        <div class="item warning">
            AI review was not available.
            Check your Gemini API configuration and connection.
        </div>
        """

    # Create HTML document
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>AI Code Reviewer Report</title>

    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 30px 16px;
            background: #eef2f7;
            color: #1f2937;
            font-family: Arial, Helvetica, sans-serif;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1050px;
            margin: auto;
        }}

        .header {{
            background: #172033;
            color: white;
            padding: 30px;
            border-radius: 14px;
            margin-bottom: 24px;
        }}

        .header h1 {{
            margin: 0 0 8px;
            font-size: 28px;
        }}

        .header p {{
            margin: 5px 0;
            color: #d1d5db;
            overflow-wrap: anywhere;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(
                auto-fit,
                minmax(190px, 1fr)
            );
            gap: 16px;
            margin-bottom: 24px;
        }}

        .stat {{
            background: white;
            border-radius: 12px;
            padding: 22px;
            box-shadow: 0 3px 12px #0000000a;
        }}

        .stat-label {{
            color: #64748b;
            font-size: 14px;
        }}

        .stat-value {{
            font-size: 25px;
            font-weight: bold;
            margin-top: 8px;
            overflow-wrap: anywhere;
        }}

        .section {{
            background: white;
            padding: 24px;
            margin-bottom: 24px;
            border-radius: 12px;
            box-shadow: 0 3px 12px #0000000a;
        }}

        .section h2 {{
            margin-top: 0;
            padding-bottom: 12px;
            border-bottom: 1px solid #e5e7eb;
            font-size: 21px;
        }}

        .item {{
            padding: 12px 15px;
            margin: 10px 0;
            border-radius: 7px;
            background: #f8fafc;
            overflow-wrap: anywhere;
        }}

        .success {{
            background: #ecfdf5;
            border-left: 4px solid #10b981;
        }}

        .warning {{
            background: #fffbeb;
            border-left: 4px solid #f59e0b;
        }}

        .danger {{
            background: #fef2f2;
            border-left: 4px solid #ef4444;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
        }}

        th, td {{
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
            text-align: left;
            overflow-wrap: anywhere;
        }}

        th {{
            background: #f1f5f9;
        }}

        /* AI review formatting */

        .ai-review {{
            line-height: 1.9;
            padding: 24px;
            background: #f8fafc;
            border-left: 5px solid #2563eb;
            border-radius: 8px;
            overflow-wrap: anywhere;
        }}

        .ai-review h1,
        .ai-review h2,
        .ai-review h3,
        .ai-review h4 {{
            color: #1e40af;
            margin-top: 24px;
            margin-bottom: 12px;
        }}

        .ai-review h1:first-child,
        .ai-review h2:first-child,
        .ai-review h3:first-child {{
            margin-top: 0;
        }}

        .ai-review p {{
            margin: 12px 0;
        }}

        .ai-review ul,
        .ai-review ol {{
            padding-left: 28px;
        }}

        .ai-review li {{
            margin-bottom: 8px;
        }}

        .ai-review pre {{
            background: #172033;
            color: #f8fafc;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            direction: ltr;
            text-align: left;
            white-space: pre;
        }}

        .ai-review pre code {{
            background: transparent;
            color: inherit;
            padding: 0;
        }}

        .ai-review code {{
            font-family: Consolas, monospace;
            background: #e2e8f0;
            color: #9f1239;
            padding: 2px 5px;
            border-radius: 4px;
        }}

        .ai-review blockquote {{
            border-left: 3px solid #94a3b8;
            padding-left: 14px;
            color: #475569;
            margin-left: 0;
        }}

        .footer {{
            text-align: center;
            color: #64748b;
            padding: 10px;
            font-size: 13px;
        }}

        @media (max-width: 600px) {{
            body {{
                padding: 14px 8px;
            }}

            .header,
            .section {{
                padding: 18px;
            }}

            .header h1 {{
                font-size: 23px;
            }}

            .stat-value {{
                font-size: 22px;
            }}

            th, td {{
                padding: 8px;
                font-size: 13px;
            }}

            .ai-review {{
                padding: 15px;
            }}
        }}
    </style>
</head>

<body>
<div class="container">

    <div class="header">
        <h1>AI Code Reviewer</h1>
        <p>Automated Python Code Analysis Report</p>
        <p>File: {escape(file_name)}</p>
    </div>

    <div class="grid">

        <div class="stat">
            <div class="stat-label">Syntax Status</div>
            <div class="stat-value {syntax_class}">
                {syntax_status}
            </div>
        </div>

        <div class="stat">
            <div class="stat-label">Quality Score</div>
            <div class="stat-value">{score_text}</div>
        </div>

        <div class="stat">
            <div class="stat-label">Quality Issues</div>
            <div class="stat-value">
                {len(quality_issues or [])}
            </div>
        </div>

        <div class="stat">
            <div class="stat-label">Security Warnings</div>
            <div class="stat-value">
                {len(security_issues or [])}
            </div>
        </div>

    </div>

    <div class="section">
        <h2>Syntax Analysis</h2>
        <div class="item {syntax_class}">
            Syntax check: {syntax_status}
        </div>
    </div>

    <div class="section">
        <h2>Code Quality</h2>
        {quality_html}
    </div>

    <div class="section">
        <h2>Function Analysis</h2>
        {functions_html}
    </div>

    <div class="section">
        <h2>Complexity Analysis</h2>
        {complexity_html}
    </div>

    <div class="section">
        <h2>Security Analysis</h2>
        {security_html}
    </div>

    <div class="section">
        <h2>AI Code Review — Gemini</h2>
        <div class="ai-review">
            {ai_review_html}
        </div>
    </div>

    <div class="footer">
        Generated by Code Auto Reviewer
    </div>

</div>
</body>
</html>
"""

    # Save the report beside the current working directory
    output_path = Path.cwd() / "report.html"
    output_path.write_text(
        html_content,
        encoding="utf-8"
    )

    print(f"\nHTML report generated: {output_path}")

    return str(output_path)
