import asyncio
import threading
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.request import HTTPXRequest
from config.settings import settings
from rich import print as rprint


def _escape_md(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def _build_app():
    """Build Telegram app with HTTP/1.1 to avoid async conflicts"""
    request = HTTPXRequest(http_version="1.1")
    return Application.builder().token(settings.TELEGRAM_BOT_TOKEN).request(request).build()


def send_notification(message: str):
    """Send a simple notification message"""
    async def _send():
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        async with bot:
            await bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=message,
                parse_mode="Markdown"
            )
    asyncio.run(_send())


def send_error(step: str, error: str):
    """Send a formatted error notification"""
    message = (
        f"❌ *LinkedIn Agent Error*\n\n"
        f"*Step:* {step}\n"
        f"*Error:* {error}\n\n"
        f"Check GitHub Actions logs for details."
    )
    send_notification(message)


def ask_mode_selection() -> str:
    """Ask user: Auto topic or their own idea? Returns: 'auto' or 'own'"""
    result = {"mode": None}

    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_ask_mode(result))
        finally:
            loop.close()

    thread = threading.Thread(target=run_in_thread)
    thread.start()
    thread.join(timeout=3700)
    return result.get("mode", "auto")


async def _ask_mode(result: dict):
    message = (
        "🤖 *LinkedIn Agent is ready\\!*\n\n"
        "How do you want to post today?"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌐 Auto Topic", callback_data="mode_auto"),
            InlineKeyboardButton("✍️ My Own Idea", callback_data="mode_own"),
        ]
    ])
    response_event = asyncio.Event()

    async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        try:
            await query.answer()
        except Exception:
            pass
        mode = query.data.split("_")[1]
        result["mode"] = mode
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        label = "Auto topic" if mode == "auto" else "Your own idea"
        await context.bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=f"✅ Got it! {label} selected.",
        )
        response_event.set()

    app = _build_app()
    app.add_handler(CallbackQueryHandler(callback_handler))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.bot.send_message(
        chat_id=settings.TELEGRAM_CHAT_ID,
        text=message,
        parse_mode="MarkdownV2",
        reply_markup=keyboard
    )
    try:
        await asyncio.wait_for(response_event.wait(), timeout=3600)
    except asyncio.TimeoutError:
        result["mode"] = "auto"
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


def ask_for_own_idea() -> str:
    """Ask user to type their own topic/key points. Returns the text they type."""
    result = {"text": None}

    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_ask_for_text(
                prompt=(
                    "✍️ Tell me your idea or key points.\n\n"
                    "Just type it naturally — what happened, what you built, "
                    "what you want to share. I'll do the rest."
                ),
                result=result
            ))
        finally:
            loop.close()

    thread = threading.Thread(target=run_in_thread)
    thread.start()
    thread.join(timeout=3700)
    return result.get("text", "")


def send_edit_request() -> str:
    """Ask user what edit they want. Returns their edit instruction as text."""
    result = {"text": None}

    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_ask_for_text(
                prompt=(
                    "✏️ What should I change?\n\n"
                    "Type your edit request — e.g. 'Make the opening punchier' "
                    "or 'Remove the last sentence'"
                ),
                result=result
            ))
        finally:
            loop.close()

    thread = threading.Thread(target=run_in_thread)
    thread.start()
    thread.join(timeout=3700)
    return result.get("text", "")


async def _ask_for_text(prompt: str, result: dict):
    """Generic text input handler — sends a message and waits for user reply"""
    response_event = asyncio.Event()

    async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.message.chat_id) == str(settings.TELEGRAM_CHAT_ID):
            result["text"] = update.message.text
            await context.bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text="✅ Got it! Working on it...",
            )
            response_event.set()

    app = _build_app()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.bot.send_message(
        chat_id=settings.TELEGRAM_CHAT_ID,
        text=prompt,
    )
    try:
        await asyncio.wait_for(response_event.wait(), timeout=3600)
    except asyncio.TimeoutError:
        result["text"] = ""
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


def ask_topic_selection(topics: list[str]) -> int:
    """Send 5 topics as buttons, return selected index (0-based)"""
    result = {"index": 0}

    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_send_topic_selector(topics, result))
        finally:
            loop.close()

    thread = threading.Thread(target=run_in_thread)
    thread.start()
    thread.join(timeout=3700)
    return result.get("index", 0)


async def _send_topic_selector(topics: list[str], result: dict):
    message = "🧠 Pick a topic to post about:\n\n"
    for i, topic in enumerate(topics, 1):
        message += f"{i}. {topic}\n\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(str(i + 1), callback_data=f"topic_{i}")]
        for i in range(len(topics))
    ])
    response_event = asyncio.Event()

    async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        try:
            await query.answer()
        except Exception:
            pass
        idx = int(query.data.split("_")[1])
        result["index"] = idx
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=f"✅ Topic {idx + 1} selected! Researching now...",
        )
        response_event.set()

    app = _build_app()
    app.add_handler(CallbackQueryHandler(callback_handler))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.bot.send_message(
        chat_id=settings.TELEGRAM_CHAT_ID,
        text=message,
    )
    await app.bot.send_message(
        chat_id=settings.TELEGRAM_CHAT_ID,
        text="Tap a number to select:",
        reply_markup=keyboard
    )
    try:
        await asyncio.wait_for(response_event.wait(), timeout=3600)
    except asyncio.TimeoutError:
        result["index"] = 0
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


def send_draft_variations(topic: str, drafts: list[str]) -> int:
    """Send 3 draft variations to Telegram. User picks 1, 2, or 3."""
    result = {"index": 0}

    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_send_variations(topic, drafts, result))
        finally:
            loop.close()

    thread = threading.Thread(target=run_in_thread)
    thread.start()
    thread.join(timeout=3700)
    return result.get("index", 0)


async def _send_variations(topic: str, drafts: list[str], result: dict):
    labels = ["🗣 Story angle", "💡 Insight angle", "🛠 Tool/Resource angle"]
    response_event = asyncio.Event()

    async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        try:
            await query.answer()
        except Exception:
            pass
        idx = int(query.data.split("_")[1])
        result["index"] = idx
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=f"✅ Draft {idx + 1} selected!",
        )
        response_event.set()

    app = _build_app()
    app.add_handler(CallbackQueryHandler(callback_handler))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Send each draft as a separate message
    for i, (draft, label) in enumerate(zip(drafts, labels)):
        await app.bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=f"Draft {i + 1} — {label}\n\n{draft}",
        )

    # Send picker buttons
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("1️⃣ Pick this", callback_data="draft_0"),
        InlineKeyboardButton("2️⃣ Pick this", callback_data="draft_1"),
        InlineKeyboardButton("3️⃣ Pick this", callback_data="draft_2"),
    ]])
    await app.bot.send_message(
        chat_id=settings.TELEGRAM_CHAT_ID,
        text="👆 Which draft do you want to go with?",
        reply_markup=keyboard
    )
    rprint("[green]📨 3 draft variations sent to Telegram[/green]")

    try:
        await asyncio.wait_for(response_event.wait(), timeout=3600)
    except asyncio.TimeoutError:
        result["index"] = 0
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


def send_draft_for_approval(topic: str, draft: str, row_index: int) -> str:
    """Send selected draft with Post/Edit/New Drafts/Reject buttons."""
    result = {"action": None}

    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_send_and_wait(topic, draft, row_index, result))
        finally:
            loop.close()

    thread = threading.Thread(target=run_in_thread)
    thread.start()
    thread.join(timeout=3700)
    return result.get("action", "reject")


async def _send_and_wait(topic: str, draft: str, row_index: int, result: dict):
    message = (
        f"📝 Your Selected Draft\n\n"
        f"Topic: {topic}\n\n"
        f"---\n\n"
        f"{draft}\n\n"
        f"---"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Post it", callback_data=f"approve_{row_index}"),
            InlineKeyboardButton("✏️ Edit it", callback_data=f"edit_{row_index}"),
        ],
        [
            InlineKeyboardButton("🔄 New Drafts", callback_data=f"regenerate_{row_index}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{row_index}"),
        ]
    ])
    response_event = asyncio.Event()

    async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        data = query.data
        action, idx = data.rsplit("_", 1)
        if int(idx) == row_index:
            result["action"] = action
            try:
                await query.answer()
            except Exception:
                pass
            try:
                await query.edit_message_reply_markup(reply_markup=None)
            except Exception:
                pass
            await context.bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=f"Got it! {action} ✅",
            )
            response_event.set()

    app = _build_app()
    app.add_handler(CallbackQueryHandler(callback_handler))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.bot.send_message(
        chat_id=settings.TELEGRAM_CHAT_ID,
        text=message,
        reply_markup=keyboard
    )
    rprint("[green]📨 Draft sent for final approval[/green]")
    try:
        await asyncio.wait_for(response_event.wait(), timeout=3600)
    except asyncio.TimeoutError:
        result["action"] = "reject"
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()