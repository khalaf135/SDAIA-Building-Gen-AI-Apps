# Module 01 Labs: Architecture Fundamentals

This directory contains the labs for Module 01.

## Labs Overview

### [00: Setup `uv`](00_setup_uv.md)
Instructions on installing and initializing `uv`, the fast Python package manager used throughout this course.

### [01: Tokenization & Cost Analysis](lab_01_tokenization_cost.ipynb)
Explore how LLMs see text as tokens, compare costs across different models, and understand why context window scaling matters.

### [02: API Client Integration](lab_02_api_client.ipynb)
Learn how to use **LiteLLM** to securely authenticate with models via OpenRouter, handle rate limits with retries, and implement caching.

---

## Setup Instructions

1. Ensure you have followed the [Setup Guide](00_setup_uv.md).
2. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your API keys.
