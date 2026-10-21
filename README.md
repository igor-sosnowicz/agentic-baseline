# Agentic Baseline

## Setup

Prerequisites:

- `uv`

### Developer Setup

1. Install core and developer dependencies.

   ```bash
   uv sync --dev
   ```

2. Copy `.env` and insert your OpenRouter API key.

   ```bash
   copy .env.example .env
   nvim .env # Edit with your editor of choice.
   ```

3. Start the benchmark.

   ```bash
   uv run agentic-baseline
   ```

### User setup

To be written later...
