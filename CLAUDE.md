# Repository Overview

## Project: format-book

Python utility to format OCR-processed books using AI (GPT-4o). Focuses on Finnish text.

## Tech Stack

- **Python 3.13+** with Poetry
- **OpenAI GPT-4o** for text formatting
- **Click** for CLI
- **Pandas** for statistics
- **pytest** for testing

## Structure

```
main.py                    # CLI entry point
src/utils/
  ├── format_folder.py     # Orchestration logic
  └── helpers.py           # Core utilities (AI, parsing, file ops)
tests/                     # pytest suite
.github/workflows/         # CI/CD
```

## Core Features

**`format-folder`** - Batch process text files with AI
- Concurrent processing (ThreadPoolExecutor)
- Smart text splitting at sentence boundaries
- Preserves chapter structure
- Exponential backoff for rate limits

**`generate-stats`** - Compare input/output metrics

**`combine-chapters`** - Aggregate chapters by word count

## Key Implementation

**Chapter Detection:** Regex `r"(\d+)\.\s*([^\n]+)\n(.*?)(?=\n\d+\.|$)"`

**AI Formatting:** GPT-4o with JSON output
- Replaces quotes with dashes (Finnish convention)
- Fixes OCR errors
- Normalizes capitalization/punctuation
- Improves paragraph structure

**Resilience:** 5 retries, exponential backoff (1s → 16s)

**Concurrency:** Default 5 workers, configurable

## Usage

```bash
# Install
pipx install poetry
poetry install

# Format texts
poetry run python main.py format-folder input/ output/

# With options
poetry run python main.py format-folder input/ output/ \
  --max-length 1500 \
  --max-workers 3

# Generate stats
poetry run python main.py generate-stats input/ output/

# Combine chapters
poetry run python main.py combine-chapters input/ --max-words 2000

# Run tests
poetry run pytest
```

## Configuration

Create `.env` file:
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

## Development

- **Pre-commit hooks:** black, flake8, trailing whitespace
- **CI/CD:** GitHub Actions on push/PR
- **Testing:** pytest with mock fixtures

## Recent Activity

- Added GitHub Actions CI/CD
- Fixed 429 rate limit errors
- Improved retry logic with exponential backoff
- Code cleanup

## Planned Features

- [ ] Logger integration
- [ ] Sentence-level comparison
- [ ] EPUB/PDF text extraction
- [ ] Simplified Finnish text generation
- [ ] Anki CSV export

## Code Quality

- Well-organized with separation of concerns
- Stateless utility functions
- Automated code formatting (black)
- CI/CD pipeline with automated tests
