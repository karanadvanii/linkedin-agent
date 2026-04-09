# Setup Guide

This guide walks you through getting all 5 required API credentials. Each service has a free tier — you won't need a credit card for any of them.

Total time: ~30–45 minutes.

---

## Step 0 — Python Setup

Make sure you have Python 3.11 or higher:

```bash
python3 --version
```

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
```

Open `.env` in a text editor. You'll fill in each section as you go through the steps below.

---

## Step 1 — Google Gemini API Key

The agent uses Gemini to research topics, write posts, and fact-check.

1. Go to [aistudio.google.com](https://aistudio.google.com/app/apikey)
2. Sign in with a Google account
3. Click **Create API key**
4. Copy the key

In your `.env`:
```env
GEMINI_API_KEY=your_key_here
```

The agent uses `gemini-2.5-flash` for research (with live Google Search) and `gemini-2.5-flash-lite` for writing. Both are available on the free tier.

---

## Step 2 — Telegram Bot

The agent sends you drafts and receives your approvals through a Telegram bot. Takes about 5 minutes.

**Create the bot:**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name (e.g. "LinkedIn Agent") and username (e.g. `my_linkedin_bot`)
4. BotFather will give you a token like `7123456789:AAF...` — copy it

**Get your chat ID:**
1. Message your new bot (send it anything — "hello")
2. Open this URL in your browser (replace `TOKEN` with your bot token):
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
3. In the JSON response, find `"chat": {"id": 123456789}` — that number is your chat ID

In your `.env`:
```env
TELEGRAM_BOT_TOKEN=7123456789:AAF...
TELEGRAM_CHAT_ID=123456789
```

---

## Step 3 — Google Sheets + Service Account

The agent logs every topic, draft, and posted status to a Google Sheet.

**Create the sheet:**
1. Go to [sheets.google.com](https://sheets.google.com) and create a new blank spreadsheet
2. Name it anything (e.g. "LinkedIn Agent")
3. The Sheet ID is in the URL:
   ```
   https://docs.google.com/spreadsheets/d/THIS_IS_YOUR_SHEET_ID/edit
   ```

**Create a service account:**
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (or use an existing one)
3. Go to **APIs & Services → Enable APIs** and enable:
   - Google Sheets API
   - Google Drive API
4. Go to **APIs & Services → Credentials → Create Credentials → Service Account**
5. Give it any name, click through the wizard
6. On the service account page, go to **Keys → Add Key → Create new key → JSON**
7. Download the JSON file and save it as `credentials.json` in the project root

**Share the sheet with the service account:**
1. Open the `credentials.json` file and find `"client_email"` — it looks like `something@project.iam.gserviceaccount.com`
2. Open your Google Sheet, click **Share**, and share it with that email address (Editor access)

In your `.env`:
```env
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_CREDENTIALS_PATH=credentials.json
```

---

## Step 4 — RapidAPI Key

Used for web scraping during topic research.

1. Go to [rapidapi.com](https://rapidapi.com) and create a free account
2. Go to your [Dashboard → Apps](https://rapidapi.com/developer/apps)
3. Select the default app and find your API key under **Security**

In your `.env`:
```env
RAPIDAPI_KEY=your_rapidapi_key_here
```

---

## Step 5 — LinkedIn Access Token

This is the most involved step (~20 minutes). LinkedIn requires a developer app to post on your behalf.

**Create a LinkedIn app:**
1. Go to [linkedin.com/developers/apps](https://www.linkedin.com/developers/apps)
2. Click **Create app**
3. Fill in the details — use your own LinkedIn profile as the company if you don't have one
4. Under **Products**, request access to **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect**

**Get your access token:**

LinkedIn uses OAuth 2.0. The easiest way to get a token is using the Authorization Code flow:

1. In your app settings, go to **Auth** and add a redirect URL:
   ```
   http://localhost:8080/callback
   ```
2. Note your **Client ID** and **Client Secret**

3. Open this URL in your browser (replace `CLIENT_ID`):
   ```
   https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=CLIENT_ID&redirect_uri=http://localhost:8080/callback&scope=openid%20profile%20w_member_social
   ```

4. Authorize the app — you'll be redirected to `localhost:8080/callback?code=LONG_CODE`

5. Copy the `code` value from the URL, then exchange it for a token using curl:
   ```bash
   curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
     -d "grant_type=authorization_code" \
     -d "code=PASTE_CODE_HERE" \
     -d "redirect_uri=http://localhost:8080/callback" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET"
   ```

6. The response includes `access_token` — copy it

**Get your Person URN:**
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://api.linkedin.com/v2/userinfo
```
The response includes `"sub": "abc123"` — your URN is `urn:li:person:abc123`

In your `.env`:
```env
LINKEDIN_ACCESS_TOKEN=your_access_token_here
LINKEDIN_PERSON_URN=urn:li:person:your_id_here
```

> **Note:** LinkedIn access tokens expire after **60 days**. When the agent can't post, generate a new token using steps 3–6 above.

---

## Step 6 — Set Your Persona

Open `.env` and fill in your author details:

```env
AUTHOR_NAME=Your Name
AUTHOR_ROLE=software engineer
AUTHOR_TOPICS=AI, developer tools, and software architecture
AUTHOR_AUDIENCE=developers and tech leads aged 25-40
```

This controls how the AI writes. Be specific — the more accurate your role and audience, the better the posts.

---

## Step 7 — Run It

```bash
./run.sh
```

Or:
```bash
source venv/bin/activate
python main.py
```

The agent will send you a Telegram message and walk you through the rest.

---

## Running on a Schedule

To post automatically every Monday and Thursday at 9am:

```bash
python scheduler.py
```

Keep this running in the background using `tmux` or `screen`:

```bash
tmux new -s linkedin-agent
python scheduler.py
# Press Ctrl+B then D to detach
```

---

## Common Issues

| Problem | Fix |
|---------|-----|
| `Missing required environment variables` | Check your `.env` — all 6 required vars must be filled in |
| Telegram bot doesn't respond | Message the bot first, verify `TELEGRAM_CHAT_ID` is your personal ID |
| `401` from LinkedIn | Token expired — regenerate following Step 5 |
| `Invalid credentials` from Google Sheets | Make sure `credentials.json` is in the project root and the sheet is shared with the service account email |
| Posts are about old topics | Verify `GEMINI_API_KEY` is valid — search grounding requires an active key |
