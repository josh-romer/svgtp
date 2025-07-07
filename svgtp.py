#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["google-genai", "tqdm"]
# ///
#
import argparse
import os
import sys

from google import genai
from google.genai import types
from tqdm import trange

# Set environment variables
GENAI_KEY = os.getenv("GENAI_KEY")

try:
    prompt = sys.argv[1]
except IndexError:
    prompt = "404"

parser = argparse.ArgumentParser(description="gemini svg generation script")
_ = parser.add_argument("prompt", type=str, help="svg prompt")
_ = parser.add_argument("-c", "--count", type=int, default=1, help="Number of times to print")
_ = parser.add_argument(
    "-t",
    "--thinking",
    type=bool,
    action=argparse.BooleanOptionalAction,
    help="Enable model thinking",
)


# Type hint the result of parse_args() more specifically
# We'll create a Namespace-like object with the expected attributes
class Args(argparse.Namespace):
    prompt: str = "404"
    count: int = 1
    thinking: bool = False


args = parser.parse_args(namespace=Args())
count: int = args.count
prompt: str = args.prompt
thinking = args.thinking

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

# -1 means automatic and 0 means disabled
thinking_budget = -1 if thinking else 0


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
            thinking_config=types.ThinkingConfig(
                thinking_budget=thinking_budget
            ),  # Disables thinking
        ),
        contents=f"Image description: {description}",
    )

    svg = response.text or ""
    return svg


svgs = [get_svg(enhanced_prompt) for _ in trange(count)]

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
with open("out/out.html", "w", encoding="utf-8") as f:
    _ = f.write(html)
