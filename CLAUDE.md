# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

Simplified vLLM server with unified token generation:
- `generate_tokens()` - Common model inference via AsyncLLMEngine  
- Streaming: extracts deltas from cumulative vLLM output
- Normal: returns final accumulated result
- Prompt format: `"Human: {message}\nBot:"` for DialoGPT

## Commands

```bash
# Setup
pip install -r requirements.txt

# Server
python simple_server.py --model microsoft/DialoGPT-medium [--port 8000]

# Client  
python simple_client.py --message "Hello" [--stream] [--url URL]
```

## API
- `POST /chat` - `{message: str, stream: bool}`
- Returns JSON (normal) or Server-Sent Events (streaming)