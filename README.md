# LinkedIn AI Agent

Automate your LinkedIn content with AI — from research to posting, entirely on autopilot.

The agent researches trending AI topics, writes 3 draft variations in your voice, sends them to your Telegram for approval, lets you edit inline, and posts directly to LinkedIn. You stay in control. The agent does the work.

---

## How It Works

```
You open Telegram
      ↓
Agent suggests 5 trending topics (via live Google Search)
      ↓
You pick one (or type your own idea)
      ↓
Agent researches the topic + fact-checks with Gemini
      ↓
Agent writes 3 draft variations, each self-critiqued and improved
      ↓
You pick a draft, edit it, or ask for 3 new ones
      ↓
You approve → Agent posts to LinkedIn
```

Everything happens through Telegram buttons. No code, no dashboards.

---

## Features

- **Live topic research** — Gemini searches the web for what's actually happening in AI this week, not training-data guesses
- **3 draft variations** — Story angle, Contrarian take, Tool/Resource drop
- **Self-critique loop** — Each draft is scored on hook, clarity, and engagement, then rewritten if below 7/10
- **Fact-checking** — Research is verified before writing begins
- **Inline editing** — Edit a draft by typing "make the opening punchier" in Telegram
- **Up to 3 edit cycles** per draft, up to 3 full regenerations per run
- **Scheduled posting** — Runs automatically Monday and Thursday at 9am
- **Google Sheets tracking** — Every topic, draft, and post is logged
- **Your voice, not generic AI** — Persona is fully configurable in `.env`

---

## What You Need

All of these have free tiers. Setup takes about 30–45 minutes total.

| Service | What it's for | Cost |
|---------|--------------|------|
| Google Gemini API | Writing and research | Free tier |
| Telegram Bot | Your approval interface | Free |
| Google Sheets + Service Account | Topic and draft tracking | Free |
| RapidAPI | Web scraping for research | Free tier |
| LinkedIn Developer | Posting to LinkedIn | Free |

Full step-by-step setup: see [SETUP.md](SETUP.md)

---

## Quick Start

```bash
# 1. Clone or unzip the project
cd linkedin-ai-agent

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your environment
cp .env.example .env
# Edit .env with your API keys — see SETUP.md for instructions

# 5. Run it
./run.sh
# or: python main.py
```

The agent will message you on Telegram to get started.

---

## Customizing Your Voice

Open `.env` and set these four values to make the AI write in your style:

```env
AUTHOR_NAME=Your Name
AUTHOR_ROLE=your job title or description
AUTHOR_TOPICS=the topics you post about
AUTHOR_AUDIENCE=who reads your posts
```

Example:
```env
AUTHOR_NAME=Sarah
AUTHOR_ROLE=product designer
AUTHOR_TOPICS=design systems, UX, and product thinking
AUTHOR_AUDIENCE=designers and product managers aged 25-40
```

The AI will write every post as you, for your audience, in a casual conversational voice.

---

## Scheduling

To run automatically on a schedule (Monday + Thursday 9am by default):

```bash
python scheduler.py
```

To change the schedule, edit in `config/settings.py`:

```python
SCHEDULE_DAYS = ["monday", "thursday"]
SCHEDULE_TIME = "09:00"
```

For unattended operation, run `scheduler.py` in the background using `tmux`, `screen`, or `systemd`.

---

## Project Structure

```
linkedin-ai-agent/
├── main.py              # Entry point — runs one pipeline cycle
├── scheduler.py         # Automated scheduling
├── run.sh               # Quick-start shell script
├── config/
│   └── settings.py      # All configuration and env var loading
├── src/
│   ├── agents/
│   │   ├── researcher.py  # Researches and fact-checks the topic
│   │   ├── writer.py      # Generates 3 drafts with self-critique
│   │   └── poster.py      # Approval loop + LinkedIn posting
│   ├── tools/
│   │   ├── gemini.py      # Gemini AI wrapper (write + search)
│   │   ├── telegram.py    # All Telegram interactions
│   │   ├── linkedin.py    # LinkedIn API posting
│   │   ├── sheets.py      # Google Sheets tracking
│   │   └── scraper.py     # Topic suggestion and research
│   └── prompts/
│       └── post_writer.py # All AI prompts
└── .env.example         # Template for your environment variables
```

---

## Troubleshooting

**Agent doesn't respond on Telegram**
Make sure your `TELEGRAM_CHAT_ID` is your personal chat ID, not a group ID. Message your bot first, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates` to find your ID.

**LinkedIn post fails**
Your access token may have expired — they last 60 days. Generate a new one following Step 5 in SETUP.md.

**Topics feel generic or outdated**
The agent uses live Google Search via Gemini. Check that `GEMINI_API_KEY` is valid and the model in `src/tools/gemini.py` is set to `gemini-2.5-flash` (not Flash Lite) for search grounding.

**Google Sheets errors**
Share the sheet with your service account email — visible in `credentials.json` as `client_email`.

---

## License

MIT — use it, modify it, build on it. See [LICENSE](LICENSE).
