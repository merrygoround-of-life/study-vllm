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

# Server (text only)
python simple_server.py --model microsoft/DialoGPT-medium [--port 8000]

# Server (text + image)  
python simple_server.py --model microsoft/DialoGPT-medium --image-model nota-ai/bk-sdm-tiny [--port 8000]

# Client (text)
python simple_client.py --message "Hello" [--stream] [--url URL]

# Client (image)
python simple_client.py --prompt "a cat on a table" [--steps 20] [--url URL]
```

## API
- `POST /chat` - `{message: str, stream: bool}` - Returns JSON (normal) or Server-Sent Events (streaming)
- `POST /image` - `{prompt: str, steps: int}` - Returns JSON with base64 encoded image