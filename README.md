# ATS CV Checker

A multi-agent CV evaluation system built with Python, Streamlit, and Google's Gemini AI.

## Features

- Extracts text from PDF CVs
- Analyzes CVs through 5 specialized AI agents:
  1. Format and ATS Friendliness Evaluation
  2. Contact Information and Professional Summary Evaluation
  3. Work Experience Evaluation
  4. Education and Skills Evaluation
  5. Optional Sections and Common Mistakes Evaluation
- Provides a comprehensive evaluation with:
  - Overall score (out of 100 points)
  - Key strengths of the CV
  - Identified shortcomings
  - Specific improvement suggestions

## Configuration

Create a `.streamlit/secrets.toml` file with the following configuration:

```toml
gemini_key = "your-google-api-key"
gemini_model = "gemini-2.0-flash-thinking-exp-01-21"  # optional, defaults to gemini-2.0-flash-thinking-exp-01-21
```

- `gemini_key` (required): Your Google Gemini API key
- `gemini_model` (optional): The Gemini model to use for evaluation. If not specified, defaults to `gemini-2.0-flash-thinking-exp-01-21`

## Installation

1. Clone this repository
2. Install the required dependencies: