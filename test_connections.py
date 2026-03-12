from rich import print as rprint

rprint("\n[bold]Testing all connections...[/bold]\n")

# Test 1: Google Sheets
rprint("[yellow]1. Testing Google Sheets...[/yellow]")
from src.tools.sheets import get_pending_topics
topics = get_pending_topics()
rprint(f"   Topics found: {topics}")

# Test 2: Gemini
rprint("\n[yellow]2. Testing Gemini...[/yellow]")
from src.tools.gemini import generate_post
from src.prompts.post_writer import SYSTEM_PROMPT, build_user_prompt
draft = generate_post(SYSTEM_PROMPT, build_user_prompt("AI agents are overrated", []))
rprint(f"   Draft preview: {draft[:200]}...")

# Test 3: Research Agent
rprint("\n[yellow]3. Testing Research Agent...[/yellow]")
from src.tools.scraper import research_topic
research = research_topic("Why most AI agents fail in production")
rprint(f"   Research preview: {research[:200]}...")

rprint("\n[bold green]✅ Connection tests complete[/bold green]")