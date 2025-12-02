#!/usr/bin/env python
"""
Test script to verify that the OpenAI API key in .env is valid and working.
Attempts a simple API call and reports success or failure.
"""

import os
import sys

# Ensure local src directory is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from env_utils import safe_load_dotenv

# Load environment variables from .env
env_path = os.path.join(os.path.dirname(__file__), ".env")
print(f"Loading .env from: {env_path}")
safe_load_dotenv(env_path)

# Check if the API key is set
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    print("❌ OPENAI_API_KEY not found in .env file or environment.")
    print("   Please set OPENAI_API_KEY in your .env file.")
    sys.exit(1)

print(f"✓ OPENAI_API_KEY found (length: {len(openai_api_key)} chars)")

# Try to import and call the OpenAI API
try:
    from openai import OpenAI
    print("✓ openai module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import openai: {e}")
    print("   Install it with: pip install openai")
    sys.exit(1)

try:
    # Initialize the client
    client = OpenAI(api_key=openai_api_key)
    print("✓ OpenAI client initialized")
    
    # Attempt a simple API call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Say 'Hello from OpenAI API!' in exactly 5 words."}
        ]
    )
    print(f"✓ API call successful!")
    print(f"\nGenerated response:\n{response.choices[0].message.content}\n")
    print("✅ Your OpenAI API key is VALID and working!")
    sys.exit(0)

except Exception as e:
    print(f"❌ API call failed: {e}")
    print("\nPossible reasons:")
    print("  - Invalid or expired API key")
    print("  - API key does not have access to gpt-4o-mini model")
    print("  - Rate limit exceeded or insufficient credits")
    print("  - Network connectivity issue")
    sys.exit(1)
