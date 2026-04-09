from src.tools.gemini import generate_post, generate_with_search
from src.prompts.post_writer import TOPIC_SUGGESTER_PROMPT
from rich import print as rprint

RESEARCH_PROMPT = """
You are an AI content researcher. Given a topic, find:
1. The most interesting and specific facts, numbers, or recent developments around it
2. What makes it genuinely cool or surprising — the "wow" angle
3. Real examples, demos, repos, or tools people can actually try
4. Why a tech-curious professional would find this interesting or useful right now

Be specific and concrete. No fluff. No generic statements.
Return 5-7 bullet points of sharp, useful research insights.
"""

def research_topic(topic: str) -> str:
    """Use Gemini to research a topic for post writing"""
    rprint(f"[cyan]🔍 Researching topic: '{topic}'[/cyan]")
    user_prompt = f"Research this topic for a casual LinkedIn post about AI:\n\n{topic}"
    research = generate_post(RESEARCH_PROMPT, user_prompt)
    rprint(f"[cyan]📊 Research complete — {len(research)} characters[/cyan]")
    return research


def suggest_topics() -> list[str]:
    """
    Use Gemini to suggest 5 fresh AI topics for this week.
    Returns a list of topic strings.
    """
    rprint(f"[cyan]💡 Asking Gemini to suggest trending topics (with live search)...[/cyan]")

    raw = generate_with_search(TOPIC_SUGGESTER_PROMPT)
    
    # Parse numbered list into clean list
    topics = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if line and line[0].isdigit():
            # Remove "1. " prefix
            topic = line.split(".", 1)[-1].strip()
            if topic:
                topics.append(topic)
    
    rprint(f"[cyan]✅ Got {len(topics)} topic suggestions[/cyan]")
    for i, t in enumerate(topics, 1):
        rprint(f"  [white]{i}. {t}[/white]")
    
    return topics