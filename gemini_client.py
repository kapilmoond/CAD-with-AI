import os
import google.generativeai as genai

SYSTEM_PROMPT = """
You are a helpful assistant for a CAD application. Your task is to take a user's natural language description of a 2D drawing and convert it into a structured JSON format that the application can parse.

The JSON output must contain a single root object with a key "commands". The value of "commands" must be a list of drawing command objects.

Each command object must have a "command" key specifying the type of entity to draw. The supported command types are:
- "line": Draws a line. Requires "start" and "end" points as [x, y] arrays.
- "circle": Draws a circle. Requires a "center" point as an [x, y] array and a "radius" as a number.
- "text": Draws a text label. Requires "text" as a string, an "insert" point as an [x, y] array, and an optional "height" as a number.

Here is an example of the expected JSON format:

User request: "Draw a line from (0,0) to (100, 200) and add a circle at (50,50) with a radius of 30."

{
  "commands": [
    {
      "command": "line",
      "start": [0, 0],
      "end": [100, 200]
    },
    {
      "command": "circle",
      "center": [50, 50],
      "radius": 30
    }
  ]
}

Now, please process the following user request and provide the JSON output. Do not include any other text or explanations in your response, only the JSON object.
"""

def get_gemini_response(prompt: str) -> str:
    """
    Sends a prompt to the Gemini API and returns the response.

    Args:
        prompt: The user's text prompt.

    Returns:
        The text response from the Gemini model, or an error message.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY environment variable not set."

    full_prompt = f"{SYSTEM_PROMPT}\n\nUser request: \"{prompt}\""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(full_prompt)
        # The response can sometimes be wrapped in ```json ... ```, so we need to clean it.
        cleaned_response = response.text.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        return cleaned_response.strip()
    except Exception as e:
        return f"Error interacting with Gemini API: {e}"
