#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["google-genai"]
# ///

import codecs
import os
import sys

from google import genai
from google.genai import types

# Set environment variables
my_api_key = os.getenv("GENAI_KEY")

try:
    prompt = sys.argv[1]
except IndexError:
    prompt = "404"

# Create an genAI client using the key from our environment variable
client = genai.Client(
    api_key=my_api_key,
)

system_prompt = """
You are a terminal-based ASCII artist specializing in high-quality ANSI color art.
Your task is to generate detailed ASCII art representations of characters, objects,
or scenes using only printable characters

Your output must be:
Your art must fit within **80 characters wide** and **40 lines tall**
to use approximately half the screen space of a 1080p monitor terminal.
DO NOT WRAP IN CODE BLOCK BACKTICK
do not include ```ansi
"""

# Specify the model to use and the messages to send
response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        # thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
    ),
    contents=f"Image description: {prompt}",
)

decoded = codecs.decode(response.text or "", "unicode_escape")
print(decoded)

with open("out/ascii.txt", "w", encoding="utf-8") as f:
    _ = f.write(decoded)
