import ast


def analyze_complexity(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()

    tree = ast.parse(code)

    functions = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):

            complexity = 1

            for child in ast.walk(node):

                if isinstance(
                    child,
                    (ast.If, ast.For, ast.While, ast.And, ast.Or)
                ):
                    complexity += 1

            functions.append({
                "name": node.name,
                "line": node.lineno,
                "complexity": complexity
            })

    return functions