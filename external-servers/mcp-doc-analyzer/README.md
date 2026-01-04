# Document Analyzer MCP

A FastMCP server for analyzing text documents with sentiment, keyword extraction, readability metrics, and basic statistics. This project provides a set of tools for document analysis, search, and management, with a built-in sample document store.

## Features

- **Sentiment Analysis**: Detects positive, negative, or neutral sentiment in documents or arbitrary text.
- **Keyword Extraction**: Identifies the most relevant keywords in a document.
- **Readability Metrics**: Calculates Flesch Reading Ease, Flesch-Kincaid Grade Level, and other readability statistics.
- **Text Statistics**: Provides word count, sentence count, character count, and more.
- **Document Management**: Add, search, and list documents with metadata.
- **Sample Data**: Comes with 15+ sample documents across various categories.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd document-analyzer-mcp
   ```

2. **Install dependencies** (requires Python 3.11+):
   ```bash
   pip install -r requirements.txt
   ```
   Or, if using `pyproject.toml`:
   ```bash
   pip install .
   ```

## Usage

Start the MCP server:

```bash
python main.py
```

The server exposes several tools via FastMCP, including:

- `analyze_document(document_id)`: Full analysis of a document by ID.
- `get_sentiment(text)`: Sentiment analysis for any text.
- `extract_keywords(text, limit=10)`: Extract top keywords from text.
- `add_document(title, content, author=None, category=None, tags=None)`: Add a new document.
- `search_documents(query)`: Search documents by content, title, or tags.
- `list_documents()`: List all documents in the store.
- `get_document_info(document_id)`: Get detailed info about a document.
- `get_readability_score(text)`: Readability metrics for any text.
- `get_text_statistics(text)`: Basic statistics for any text.

## Example

```python
from fastmcp import FastMCPClient

client = FastMCPClient("http://localhost:8000")
result = client.analyze_document(document_id="1")
print(result)
```

## Project Structure

- `main.py` — Main FastMCP server and all tool definitions.
- `pyproject.toml` — Project metadata and dependencies.
- `README.md` — Project documentation.

## Requirements

- Python 3.11+
- fastmcp >= 2.10.1
- pydantic

## License

MIT License
