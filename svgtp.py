#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["google-genai"]
# ///
#
import os
import sys

from google import genai
from google.genai import types

# Set environment variables
GENAI_KEY = os.getenv("GENAI_KEY")

try:
    prompt = sys.argv[1]
except IndexError:
    prompt = "404"

print(GENAI_KEY)
print(prompt)

# Create an genAI client using the key from our environment variable
client = genai.Client(
    api_key=GENAI_KEY,
)

prompt_enhancement_instruction = """
You are an expert at writing prompts for image generation.
You reword the given prompt with added detail in order to make prompts for amazing images.
Emphasize important details, but keep the description succinct.
ONLY RESPOND WITH THE TEXT OF THE IMPROVED PROMPT
"""

prompt_response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=prompt_enhancement_instruction,
        thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking
    ),
    contents=f"initial prompt: {prompt}",
)

enhanced_prompt = prompt_response.text or "Request Failed"
print(enhanced_prompt)


def get_svg(description: str):
    system_prompt = """
        You are an expert svg design and creation machine that Outputs only raw,
        valid SVG code no explanations, no comments, no markdown, no text before
        or after.
        The SVG must be extremely detailed, with intricate line work, complex shapes,
        fine gradients, and layered visual elements for maximum richness and precision.
        Add animations to the svg when there is movement described in the prompt.
        NEVER SURROUND THE SVG WITH A MARKDOWN CODE BLOCK!
        THE OUTPUT MUST BE SAVEABLE AS A CORRECT SVG. NEVER OUTPUT "```xml"
        """

    # Specify the model to use and the messages to send
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking
        ),
        contents=f"Image description: {description}",
    )

    svg = response.text or ""
    return svg


svgs = [get_svg(enhanced_prompt) for _ in range(1)]

# with open("out.svg", "w", encoding="utf-8") as f:
#    f.write(svg)

html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Inline SVG Viewer</title>
  <style>
    body {{
      margin: 0;
      background: #111;
      display: flex;
      justify-content: center;
      align-items: center;
      flex-direction: column;
    }}
    svg {{
      width: 100%;
    }}
  </style>
</head>
<body>
  {"\n".join(svgs)}
</body>
</html>
"""
with open("out.html", "w", encoding="utf-8") as f:
    _ = f.write(html)
