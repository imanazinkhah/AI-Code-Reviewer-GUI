
import os
from google import genai


def review_with_ai(file_path):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set."
        )

    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an expert Python code reviewer.

Analyze this Python code and provide a practical review.

Review these areas:
1. Code quality and readability
2. Potential bugs
3. Security issues
4. Performance
5. Maintainability
6. Python best practices

Explain each important issue and suggest improvements.
If the code is good, mention its strengths too.
Write the review in clear English.

Python code:

{code}
"""

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt
    )

    result = response.text

    if not result:
        raise ValueError(
            "Gemini returned an empty response."
        )

    return result
