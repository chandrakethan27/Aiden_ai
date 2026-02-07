#!/usr/bin/env python3
"""
Quick test script to verify OpenRouter API is working
"""
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Get configuration
api_key = os.getenv('OPENROUTER_API_KEY')
model = os.getenv('MODEL_NAME', 'anthropic/claude-3.5-sonnet')

print(f"Testing OpenRouter API...")
print(f"Model: {model}")
print(f"API Key: {api_key[:20]}..." if api_key else "API Key: NOT SET")
print()

try:
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    print("Making test API call...")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": "Say 'Hello, OpenRouter is working!' and nothing else."}
        ],
        max_tokens=50
    )
    
    print(f"Full response object: {response}")
    print(f"Response choices: {response.choices}")
    print(f"Message: {response.choices[0].message}")
    
    result = response.choices[0].message.content
    print(f"Content: '{result}'")
    print(f"Content length: {len(result) if result else 0}")
    
    if result and len(result.strip()) > 0:
        print(f"✅ SUCCESS! Response: {result}")
        print()
        print("OpenRouter API is working correctly!")
    else:
        print("⚠️  WARNING: API call succeeded but returned empty content!")
        print("This model may not be compatible. Try a different model.")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
