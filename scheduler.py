import schedule
import time
from main import run_pipeline
from config.settings import settings
from rich import print as rprint

def start_scheduler():
    rprint(f"[bold]⏰ Scheduler started — runs every {settings.SCHEDULE_DAYS} at {settings.SCHEDULE_TIME}[/bold]")

    for day in settings.SCHEDULE_DAYS:
        getattr(schedule.every(), day).at(settings.SCHEDULE_TIME).do(run_pipeline)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    start_scheduler()