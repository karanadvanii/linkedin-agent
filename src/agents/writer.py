from src.tools.gemini import generate_post
from src.prompts.post_writer import SYSTEM_PROMPT, VARIATION_PROMPTS, build_user_prompt, CRITIQUE_PROMPT
from src.tools.sheets import save_draft, update_row_status
from rich import print as rprint


def run_writer(enriched_topic: dict) -> dict:
    """
    Generate 3 draft variations of the LinkedIn post.
    Each uses a different angle/format, then is self-critiqued and improved.
    """
    topic = enriched_topic["topic"]
    research = enriched_topic["research"]
    row_index = enriched_topic["row_index"]

    rprint(f"[bold yellow]✍️  Writer Agent — Generating 3 drafts for: '{topic}'[/bold yellow]")

    drafts = []
    for i, variation_instruction in enumerate(VARIATION_PROMPTS, 1):
        rprint(f"[yellow]  Writing variation {i}/3...[/yellow]")
        user_prompt = build_user_prompt(topic, research, variation_instruction)
        draft = generate_post(SYSTEM_PROMPT, user_prompt)

        rprint(f"[yellow]  Self-critiquing variation {i}/3...[/yellow]")
        critique_prompt = CRITIQUE_PROMPT.replace("{draft}", draft)
        improved = generate_post(SYSTEM_PROMPT, critique_prompt)
        drafts.append(improved.strip() if improved.strip() else draft)

    # Save first draft to sheets as reference
    save_draft(row_index, drafts[0])
    update_row_status(row_index, "drafts_ready")

    return {
        **enriched_topic,
        "drafts": drafts
    }