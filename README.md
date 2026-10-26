# AI Code Reviewer

**An AI-powered Python code review tool built with Google Gemini.**

AI Code Reviewer is a Python application that uses Google's Gemini API to analyze Python source code and generate practical code review feedback in a readable HTML report.

The goal of this project is to help developers identify potential issues, improve code quality, and write more maintainable Python applications.

## Features

- **AI-Powered Code Review:** Analyze Python source code using Google Gemini.
- **Code Quality:** Review readability, structure, and clarity.
- **Potential Bug Detection:** Identify possible logical and runtime issues.
- **Security Analysis:** Highlight potential security risks and unsafe coding patterns.
- **Performance Suggestions:** Receive recommendations for improving efficiency.
- **Maintainability:** Get suggestions to make code easier to understand and modify.
- **Python Best Practices:** Receive recommendations for cleaner Python code.
- **HTML Reports:** Generate structured, readable HTML reports of review results.
- **Error Handling:** Detect missing API key configuration and empty AI responses.

> AI-generated feedback is not guaranteed to be correct or complete. Always verify important findings through testing and manual review.

## Technologies

- Python
- Google Gemini API
- Google Gen AI SDK (`google-genai`)
- HTML and CSS

## Project Structure

```text
AI Code Reviewer/
├── app.py
├── sample.py
├── README.md
├── .gitignore
└── reviewer/
    ├── ai_reviewer.py
    └── html_report.py
```

*This is the expected core structure. The actual repository may contain additional files.*

## Requirements

- Python 3
- A Google Gemini API key
- Internet access for API requests

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/imanazinkhah/AI-Code-Reviewer.git
```

### 2. Navigate to the project directory

```bash
cd AI-Code-Reviewer
```

### 3. Install the Gemini SDK

```bash
python -m pip install google-genai
```

If a `requirements.txt` file is available, install the project's dependencies with:

```bash
python -m pip install -r requirements.txt
```

## Configure the Gemini API

AI Code Reviewer uses the `GEMINI_API_KEY` environment variable to access the Gemini API.

### 1. Get a Gemini API key

Visit Google AI Studio:

https://aistudio.google.com/apikey

Create or obtain an API key according to Google's current API access requirements.

### 2. Set the API key on Windows

Open Command Prompt (CMD) and run:

```cmd
set GEMINI_API_KEY=YOUR_API_KEY
```

Replace `YOUR_API_KEY` with your actual Gemini API key.

This setting applies only to the current CMD session.

**Security best practices:**

- Never hardcode your API key in source code.
- Never commit API keys or other secrets to GitHub.
- Do not share your API key publicly.
- If a key is accidentally exposed, revoke it and generate a replacement.

## Usage

### 1. Configure the API key

Make sure `GEMINI_API_KEY` is set in the terminal where you run the application.

### 2. Run the application

From the project directory, execute:

```bash
python app.py
```

Follow the application's instructions to start the code review process.

### 3. Review the results

The application uses the Gemini integration to analyze Python code and return review feedback.

The HTML report module can format the results into a structured report for easier reading.

The exact workflow depends on the current implementation of `app.py`.

## Review Categories

The AI reviewer is instructed to examine six main areas:

| Category | Description |
|---|---|
| Code Quality | Readability, organization, and clarity |
| Potential Bugs | Possible logical errors and runtime problems |
| Security | Potential vulnerabilities and unsafe patterns |
| Performance | Opportunities to improve efficiency |
| Maintainability | Ease of understanding and modifying the code |
| Python Best Practices | Recommendations for cleaner, more consistent Python code |

The reviewer generates its feedback in English, explains important issues, and suggests improvements. It can also identify strengths when the submitted code is already well written.

## How It Works

1. The application identifies the Python source file to review.
2. The reviewer reads the file using UTF-8 encoding.
3. The source code and review instructions are sent to the configured Gemini model.
4. Gemini generates the code review.
5. The application receives and validates the response.
6. The review results can be passed to the HTML report generator.

## Troubleshooting

### Missing API key

If you receive the following error:

```text
GEMINI_API_KEY environment variable is not set.
```

Set the environment variable in the same CMD session where you run the application.

### Empty Gemini response

If the application reports that Gemini returned an empty response, check your API request, model availability, API key configuration, and network connection.

### API or model errors

If a request fails, verify that:

- Your API key is valid.
- Your account has access to the requested model.
- The model identifier in `reviewer/ai_reviewer.py` is supported by the Gemini API.
- Your network allows requests to the Gemini API.
- You have not exceeded the applicable API usage limits.

## Limitations

- AI-generated feedback may contain mistakes or incomplete conclusions.
- The reviewer may miss bugs and security vulnerabilities.
- AI suggestions should be validated before being applied.
- API availability, model access, usage limits, and pricing depend on Google's current policies.
- The current review implementation is designed for Python source code.
- The quality of the review depends on the submitted code and the model's response.

AI Code Reviewer is a development aid and should not replace automated testing, static analysis, or professional security review.

## Roadmap

- [x] Python application foundation
- [x] Gemini API integration
- [x] API key configuration through an environment variable
- [x] HTML report generation
- [ ] Graphical user interface (GUI)
- [ ] Automated test suite
- [ ] Improved code analysis and validation
- [ ] Expanded security and quality checks
- [ ] Additional configuration options

## Contributing

Contributions, suggestions, and bug reports are welcome.

If you would like to improve the project, open an issue or submit a pull request.

## Author

**Iman Azinkhah**

GitHub: [@imanazinkhah](https://github.com/imanazinkhah)

## License

No license has been specified yet. Please check the repository for licensing information before reusing, modifying, or distributing this project.

---

If you find this project useful, consider giving it a ⭐ on GitHub.
