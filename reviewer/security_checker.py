import ast


def check_security(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()

    tree = ast.parse(code)

    issues = []

    for node in ast.walk(tree):

        # بررسی eval
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == "eval":
                    issues.append({
                        "line": node.lineno,
                        "severity": "HIGH",
                        "message": "Use of eval() can be dangerous."
                    })

        # بررسی exec
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == "exec":
                    issues.append({
                        "line": node.lineno,
                        "severity": "HIGH",
                        "message": "Use of exec() can be dangerous."
                    })

        # بررسی password و secret
        if isinstance(node, ast.Assign):

            for target in node.targets:

                if isinstance(target, ast.Name):

                    name = target.id.lower()

                    if "password" in name or "secret" in name:
                        issues.append({
                            "line": node.lineno,
                            "severity": "HIGH",
                            "message": f"Possible hard-coded secret: {target.id}"
                        })

    return issues