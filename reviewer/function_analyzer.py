import ast


def analyze_functions(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()

    tree = ast.parse(code)

    functions = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):

            function_info = {
                "name": node.name,
                "line": node.lineno,
                "parameters": len(node.args.args),
                "lines": node.end_lineno - node.lineno + 1
            }

            functions.append(function_info)

    return functions