from google import genai
from google.genai import types
from config.settings import settings
from rich import print as rprint

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Standard model for post writing
WRITE_MODEL = "gemini-2.5-flash-lite"

# Model with search grounding for research
SEARCH_MODEL = "gemini-2.5-flash"


def generate_post(system_prompt: str, user_prompt: str) -> str:
    """Generate content using standard Gemini — for post writing"""
    try:
        full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
        response = client.models.generate_content(
            model=WRITE_MODEL,
            contents=full_prompt
        )
        result = response.text.strip()
        rprint(f"[green]✨ Gemini generated {len(result)} characters[/green]")
        return result
    except Exception as e:
        rprint(f"[red]❌ Gemini error: {e}[/red]")
        raise


def generate_with_search(prompt: str) -> str:
    """
    Generate content with Google Search grounding.
    Gives real, current results for topic suggestions and research.
    """
    try:
        response = client.models.generate_content(
            model=SEARCH_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        result = response.text.strip()
        rprint(f"[green]🔍 Gemini Search generated {len(result)} characters[/green]")
        return result
    except Exception as e:
        rprint(f"[red]❌ Gemini Search error: {e}[/red]")
        rprint("[yellow]⚠️ Falling back to standard model...[/yellow]")
        return generate_post(prompt, "")