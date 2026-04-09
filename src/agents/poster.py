from src.tools.telegram import send_draft_variations, send_edit_request, send_draft_for_approval
from src.tools.linkedin import post_to_linkedin
from src.tools.sheets import update_row_status, mark_posted
from src.tools.gemini import generate_post
from src.prompts.post_writer import SYSTEM_PROMPT, VARIATION_PROMPTS, build_user_prompt, build_edit_prompt
from datetime import datetime, timezone
from rich import print as rprint


def run_poster(enriched_topic: dict) -> tuple[bool, str]:
    """
    Full approval loop:
    1. Show 3 draft variations
    2. User picks one
    3. User can edit, rewrite all, or post
    4. Posts to LinkedIn on approval
    """
    topic = enriched_topic["topic"]
    research = enriched_topic["research"]
    drafts = enriched_topic["drafts"]
    row_index = enriched_topic["row_index"]

    max_cycles = 3
    cycle = 0

    while cycle < max_cycles:
        cycle += 1
        rprint(f"[bold magenta]📬 Poster Agent — Cycle {cycle}[/bold magenta]")

        # Step 1: Show 3 variations, user picks one
        selected_index = send_draft_variations(topic, drafts)
        selected_draft = drafts[selected_index]
        rprint(f"[magenta]✅ User selected draft {selected_index + 1}[/magenta]")

        # Step 2: Approval loop for selected draft
        edit_cycles = 0
        max_edits = 3
        action = None

        while edit_cycles < max_edits:
            action = send_draft_for_approval(topic, selected_draft, row_index)

            if action == "approve":
                result = post_to_linkedin(selected_draft)
                if result["success"]:
                    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                    mark_posted(row_index, timestamp)
                    rprint(f"[bold green]🎉 Post published successfully![/bold green]")
                    post_url = result.get("post_url", "")
                    return True, post_url
                else:
                    rprint(f"[red]❌ LinkedIn posting failed[/red]")
                    update_row_status(row_index, "post_failed")
                    return False, ""

            elif action == "edit":
                edit_request = send_edit_request()
                if edit_request:
                    rprint(f"[yellow]✏️  Applying edit: '{edit_request}'[/yellow]")
                    edit_prompt = build_edit_prompt(selected_draft, edit_request)
                    selected_draft = generate_post(SYSTEM_PROMPT, edit_prompt)
                    rprint(f"[yellow]✅ Edit applied[/yellow]")
                edit_cycles += 1

            elif action == "regenerate":
                # Break inner loop — regenerate all 3 drafts
                break

            elif action == "reject":
                update_row_status(row_index, "rejected")
                rprint(f"[red]🚫 Post rejected[/red]")
                return False, ""

        # Regenerate all 3 drafts if requested
        if action == "regenerate":
            rprint(f"[yellow]🔄 Regenerating all 3 drafts...[/yellow]")
            drafts = []
            for variation_instruction in VARIATION_PROMPTS:
                user_prompt = build_user_prompt(topic, research, variation_instruction)
                draft = generate_post(SYSTEM_PROMPT, user_prompt)
                drafts.append(draft)

    rprint(f"[red]❌ Max cycles reached[/red]")
    update_row_status(row_index, "rejected")
    return False, ""