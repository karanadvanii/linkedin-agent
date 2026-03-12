from src.tools.scraper import research_topic
from src.tools.gemini import generate_with_search
from src.prompts.post_writer import FACT_CHECK_PROMPT
from rich import print as rprint


def run_research(topic_row: dict) -> dict:
    """Research a topic and fact-check the results"""
    topic = topic_row["topic"]
    rprint(f"[bold cyan]🔬 Researcher Agent — Topic: '{topic}'[/bold cyan]")

    # Step 1: Research
    raw_research = research_topic(topic)

    # Step 2: Fact-check
    rprint(f"[cyan]✅ Fact-checking research...[/cyan]")
    fact_check_prompt = FACT_CHECK_PROMPT.format(research=raw_research)
    verified_research = generate_with_search(fact_check_prompt)
    rprint(f"[cyan]🔍 Fact-check complete[/cyan]")

    return {
        **topic_row,
        "research": verified_research
    }