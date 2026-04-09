from src.agents.researcher import run_research
from src.agents.writer import run_writer
from src.agents.poster import run_poster
from src.tools.sheets import get_pending_topics, update_row_status, add_suggested_topics
from src.tools.scraper import suggest_topics
from src.tools.telegram import (
    send_notification,
    send_error,
    ask_mode_selection,
    ask_for_own_idea,
    ask_topic_selection
)
from config.settings import settings
from rich import print as rprint


def _print_banner() -> None:
    rprint("\n[bold cyan]╔══════════════════════════════════════╗[/bold cyan]")
    rprint("[bold cyan]║   LinkedIn AI Agent  v1.0            ║[/bold cyan]")
    rprint("[bold cyan]║   Powered by Gemini AI               ║[/bold cyan]")
    rprint("[bold cyan]╚══════════════════════════════════════╝[/bold cyan]")
    rprint(f"[dim]  Author: {settings.AUTHOR_NAME} · {settings.AUTHOR_ROLE}[/dim]\n")


def run_pipeline():
    _print_banner()
    settings.validate()

    try:
        # Step 1: Ask mode — auto or own idea
        mode = ask_mode_selection()
        rprint(f"[bold]Mode selected: {mode}[/bold]")

        if mode == "auto":
            # Step 2a: Gemini suggests 5 topics
            try:
                suggested = suggest_topics()
            except Exception as e:
                send_error("topic_suggester", str(e))
                raise

            if not suggested:
                send_notification("❌ Could not generate topics. Check logs.")
                return

            # Step 3a: You pick one
            selected_index = ask_topic_selection(suggested)
            topic = suggested[selected_index]

        else:
            # Step 2b: You type your own idea
            try:
                topic = ask_for_own_idea()
            except Exception as e:
                send_error("own_idea_input", str(e))
                raise

            if not topic:
                send_notification("❌ No idea received. Pipeline stopped.")
                return

        rprint(f"[bold green]✅ Topic: '{topic}'[/bold green]")

        # Step 4: Add to sheets and get row
        add_suggested_topics([topic])
        topics = get_pending_topics()
        if not topics:
            send_notification("❌ Could not find topic in sheet.")
            return

        topic_row = topics[0]
        update_row_status(topic_row["row_index"], "processing")

        # Step 5: Research + fact-check
        try:
            enriched = run_research(topic_row)
        except Exception as e:
            send_error("researcher", str(e))
            update_row_status(topic_row["row_index"], "error")
            raise

        # Step 6: Write 3 variations
        try:
            enriched = run_writer(enriched)
        except Exception as e:
            send_error("writer", str(e))
            update_row_status(topic_row["row_index"], "error")
            raise

        # Step 7: Approve and post
        try:
            success, post_url = run_poster(enriched)
        except Exception as e:
            send_error("poster", str(e))
            update_row_status(topic_row["row_index"], "error")
            raise

        if success:
            url_line = f"\n\n[View post]({post_url})" if post_url else ""
            send_notification(f"🚀 *Posted to LinkedIn!*\n\n*Topic:* {topic}{url_line}")
        else:
            send_notification(f"🚫 *Not posted.*\n\n*Topic:* {topic}")

    except Exception as e:
        rprint(f"[red]❌ Pipeline error: {e}[/red]")
        raise


if __name__ == "__main__":
    run_pipeline()