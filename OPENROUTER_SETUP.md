# OpenRouter Setup Guide

## Quick Start with OpenRouter

OpenRouter gives you access to multiple AI models (Claude, GPT-4, Gemini, etc.) through a single API.

### 1. Get Your OpenRouter API Key

1. Go to [https://openrouter.ai](https://openrouter.ai)
2. Sign up or log in
3. Go to "Keys" section
4. Create a new API key
5. Copy your API key

### 2. Configure Your .env File

Your `.env` file is already configured for OpenRouter. Just add your API key:

```bash
# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
USE_OPENROUTER=true

# Model Configuration
MODEL_NAME=anthropic/claude-3.5-sonnet
```

### 3. Choose Your Model

OpenRouter supports many models. Popular options:

**Recommended for this project:**
- `anthropic/claude-3.5-sonnet` - Best for analysis and reasoning (default)
- `openai/gpt-4-turbo` - Great all-rounder
- `google/gemini-pro-1.5` - Fast and cost-effective

**Budget-friendly:**
- `anthropic/claude-3-haiku` - Fast and cheap
- `meta-llama/llama-3.1-70b-instruct` - Open source, good quality

**Premium:**
- `anthropic/claude-3-opus` - Highest quality
- `openai/gpt-4` - Very capable

Just update the `MODEL_NAME` in your `.env` file!

### 4. Restart Streamlit

After updating your `.env` file:

1. Stop the current Streamlit server (Ctrl+C in terminal)
2. Restart: `streamlit run app.py`
3. The app will now use OpenRouter!

### 5. Test It

1. Upload the sample document: `examples/sample_document.txt`
2. Click "🚀 Process Document"
3. Watch the three agents analyze your document!

## Pricing

OpenRouter charges per token used. Typical costs for a 600-word document:

- Claude 3.5 Sonnet: ~$0.01-0.02 per document
- GPT-4 Turbo: ~$0.02-0.03 per document
- Claude 3 Haiku: ~$0.001-0.002 per document

You can add credits at [https://openrouter.ai/credits](https://openrouter.ai/credits)

## Troubleshooting

**"Invalid API key" error:**
- Make sure you copied the full key (starts with `sk-or-v1-`)
- Check that `USE_OPENROUTER=true` is set
- Verify you have credits in your OpenRouter account

**"Model not found" error:**
- Check the model name format: `provider/model-name`
- See available models at: https://openrouter.ai/models

**Rate limit errors:**
- OpenRouter has rate limits per model
- Try a different model or wait a moment

## Switching Back to OpenAI

If you want to use OpenAI instead:

1. Set `USE_OPENROUTER=false` in `.env`
2. Uncomment and set `OPENAI_API_KEY=your-openai-key`
3. Change `MODEL_NAME=gpt-4-turbo-preview`
4. Restart Streamlit

## Benefits of OpenRouter

✅ Access to multiple AI providers  
✅ Automatic fallback if one model is down  
✅ Unified billing across all models  
✅ Often cheaper than direct API access  
✅ Easy to switch between models  
