import ast


def check_quality(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()

    tree = ast.parse(code)

    issues = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Name):

            if node.id in ["x", "y", "z"]:
                issues.append({
                    "line": node.lineno,
                    "message": f"Variable name '{node.id}' is too generic."
                })

    return issues