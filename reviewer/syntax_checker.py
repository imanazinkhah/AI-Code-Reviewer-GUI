import ast


def check_syntax(file_path):
    """
    بررسی Syntax یک فایل Python
    """

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()

        ast.parse(code)

        return {
            "valid": True,
            "error": None
        }

    except SyntaxError as error:
        return {
            "valid": False,
            "error": {
                "line": error.lineno,
                "column": error.offset,
                "message": error.msg
            }
        }

    except FileNotFoundError:
        return {
            "valid": False,
            "error": {
                "line": None,
                "column": None,
                "message": "File not found."
            }
        }