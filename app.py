import os
import logging
from pathlib import Path

from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from google import genai
from google.genai import types

from database import (
    get_user_profile,
    save_conversation,
    update_user_profile_data,
)

from finance.market_data import get_stock_data
from finance.news import get_company_news
from documents.pdf_processor import extract_text_from_pdf
from voice.voice_processor import save_voice_file


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = os.getenv("GEMINI_MODEL")

if not TELEGRAM_TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN is missing from .env"
    )

if not GEMINI_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from .env"
    )

if not MODEL_ID:
    raise RuntimeError(
        "GEMINI_MODEL is missing from .env"
    )


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_KEY
)


# ============================================================
# DIRECTORIES
# ============================================================

DOWNLOADS_DIR = Path("downloads")
DOWNLOADS_DIR.mkdir(exist_ok=True)


# ============================================================
# TELEGRAM MESSAGE HELPER
# ============================================================

async def send_long_message(
    update: Update,
    text: str,
):
    """Send long Atlas responses in Telegram-safe chunks."""

    if not text:
        text = "Atlas could not generate a response."

    max_length = 4000

    for i in range(0, len(text), max_length):
        await update.message.reply_text(
            text[i:i + max_length]
        )


# ============================================================
# USER CONTEXT
# ============================================================

def get_user_context(user_id: str) -> str:
    """Load persistent user profile from SQLite."""

    try:
        profile = get_user_profile(user_id)
    except Exception:
        logger.exception(
            "Could not load profile for user %s",
            user_id,
        )
        profile = {}

    if not profile:
        return """
User Role: Unknown
Interests: Unknown
Watchlist: Unknown
"""

    return f"""
User Role: {profile.get("role", "Unknown")}
Interests: {profile.get("interests", "Unknown")}
Watchlist: {profile.get("watchlist", "Unknown")}
"""


# ============================================================
# ATLAS SYSTEM INSTRUCTIONS
# ============================================================

def build_system_instruction(
    user_context: str,
) -> str:

    return f"""
You are Atlas Signal Desk,
a professional AI financial research assistant.

USER CONTEXT:

{user_context}

============================================================
CAPABILITIES
============================================================

1. Live market information
2. Company financial information
3. Recent company news
4. Financial research
5. Persistent user memory
6. PDF document analysis
7. Voice understanding
8. Image and chart analysis

============================================================
TOOL RULES
============================================================

Use get_stock_data when the user asks about:

- stock price
- market capitalization
- market performance
- company metrics
- financial market information

Use get_company_news when the user asks about:

- recent company news
- developments
- headlines
- company events
- recent market-moving developments

Use update_user_profile_data when the user explicitly provides
durable information such as:

- professional role
- interests
- companies they follow
- watchlist information

Do not invent market data.

For comparison questions, retrieve information for each
relevant company when appropriate.

============================================================
RESPONSE STYLE
============================================================

For substantial financial research questions use:

ATLAS SIGNAL

WHAT HAPPENED

WHY IT MATTERS

ANALYST ANGLE

WATCH NEXT

For simple questions, answer directly.

Be factual and transparent.

Clearly distinguish facts from interpretation.

Never guarantee investment returns.

You are an AI research assistant,
not a licensed financial adviser.
"""


# ============================================================
# /START
# ============================================================

async def handle_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Introduce Atlas Signal Desk."""

    welcome = """
🛰️ ATLAS SIGNAL DESK

Your AI-powered financial research assistant.

I can help you with:

📊 MARKET DATA
Ask:
• What is the current price of NVIDIA?
• Compare NVIDIA and AMD.
• What is Microsoft's market cap?

📰 COMPANY NEWS
Ask:
• What is the latest news on NVIDIA?
• What happened with AMD recently?
• What are the important developments at Apple?

🧠 PERSONALIZED MEMORY
Tell me:
• I'm a senior investment analyst.
• I'm interested in AI infrastructure.
• Add NVIDIA and AMD to my watchlist.

Atlas can remember these details and use them
to personalize future analysis.

🎙️ VOICE
Send a voice message such as:
"What is the latest signal on NVIDIA?"

📄 PDF ANALYSIS
Upload a financial PDF and Atlas will analyze:
• Executive summary
• Financial developments
• Risks
• Positive signals
• Analyst angle
• What to watch next

🖼️ IMAGE / CHART ANALYSIS
Upload a financial chart or screenshot and ask:
• Explain this chart.
• What trends do you see?
• What does this financial table show?

━━━━━━━━━━━━━━━━━━━━

Try this first:

"What is the latest signal on NVIDIA?"

⚠️ Atlas provides research and analysis,
not guaranteed investment advice.
"""

    await update.message.reply_text(welcome)


# ============================================================
# /HELP
# ============================================================

async def handle_help(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show available Atlas capabilities."""

    help_text = """
🛰️ ATLAS SIGNAL DESK — HELP

You can interact naturally with Atlas.

📊 Market:
"What is NVIDIA's current price?"

📰 News:
"What is the latest news about AMD?"

🔎 Research:
"Compare NVIDIA and AMD."

🧠 Memory:
"I'm an investment analyst focused on semiconductors."

📈 Watchlist:
"Add NVIDIA and AMD to my watchlist."

🎙️ Voice:
Send a voice message with your financial question.

📄 PDF:
Upload a financial PDF for document analysis.

🖼️ Image:
Upload a chart or financial screenshot.

Commands:
/start — Introduction
/help — Show this help
"""

    await update.message.reply_text(help_text)
# ============================================================
# START / WELCOME HANDLER
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Atlas Signal Desk introduction and available capabilities."""

    welcome_message = """
🛰️ ATLAS SIGNAL DESK

AI-Powered Financial Research Assistant

Welcome to Atlas. I can help you research markets,
analyze financial documents, understand charts,
and answer financial questions using natural language.

━━━━━━━━━━━━━━━━━━━━━━

📊 MARKET INTELLIGENCE
Ask about stock prices, market performance,
company metrics, and comparisons.

📰 COMPANY NEWS
Ask about recent developments, headlines,
and events affecting a company.

🧠 PERSISTENT MEMORY
Tell me your role, interests, or watchlist.
I can remember these details for future analysis.

🎙️ VOICE ANALYSIS
Send a voice message and ask your financial question.

🖼️ CHART ANALYSIS
Upload a stock chart or financial screenshot
and ask me to analyze what is visible.

📄 PDF INTELLIGENCE
Upload a financial report or PDF and ask
for summaries, risks, developments, and signals.

━━━━━━━━━━━━━━━━━━━━━━

💡 TRY THESE QUERIES

• What's the current price of NVIDIA?

• Compare NVIDIA and AMD.

• I'm a senior investment analyst focused on
  AI infrastructure and semiconductors.

• Add NVIDIA and AMD to my watchlist.

• What is the latest news about NVIDIA?

• Analyze this chart.

• Summarize this financial report.

━━━━━━━━━━━━━━━━━━━━━━

📌 ATLAS SIGNAL FORMAT

For deeper research, responses can include:

WHAT HAPPENED
WHY IT MATTERS
ANALYST ANGLE
WATCH NEXT

⚠️ Atlas provides research and educational information,
not guaranteed investment advice or returns.

Send a message, voice note, chart, or PDF to begin.
"""

    await update.message.reply_text(welcome_message)

# ============================================================
# PDF DOCUMENT HANDLER
# ============================================================

async def handle_document(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Handle financial PDF uploads."""

    user_id = str(update.effective_user.id)
    document = update.message.document

    if not document:
        return

    if document.mime_type != "application/pdf":
        await update.message.reply_text(
            "Please upload a PDF document for financial analysis."
        )
        return

    filename = document.file_name or "uploaded_document.pdf"

    logger.info(
        "PDF received from user %s: %s",
        user_id,
        filename,
    )

    status_message = await update.message.reply_text(
        "📥 Receiving document and extracting financial data..."
    )

    safe_filename = (
        f"{user_id}_{document.file_unique_id}.pdf"
    )

    file_path = DOWNLOADS_DIR / safe_filename

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    try:
        telegram_file = await context.bot.get_file(
            document.file_id
        )

        await telegram_file.download_to_drive(
            custom_path=str(file_path)
        )

    except Exception:
        logger.exception(
            "PDF download failed"
        )

        await status_message.edit_text(
            "I could not download the PDF. "
            "Please upload it again."
        )
        return

    # --------------------------------------------------------
    # Extract
    # --------------------------------------------------------

    await status_message.edit_text(
        "📄 Document received. Extracting financial information..."
    )

    try:
        extracted_text = extract_text_from_pdf(
            str(file_path)
        )

    except Exception:
        logger.exception(
            "PDF extraction failed"
        )

        await status_message.edit_text(
            "I could not read this PDF. "
            "Please make sure it contains readable text."
        )
        return

    if not extracted_text:
        await status_message.edit_text(
            "The PDF does not contain readable text."
        )
        return

    if len(extracted_text.strip()) < 100:
        await status_message.edit_text(
            "The PDF contains too little readable text for analysis."
        )
        return

    logger.info(
        "Extracted %s characters from %s",
        len(extracted_text),
        filename,
    )

    # --------------------------------------------------------
    # User context
    # --------------------------------------------------------

    user_context = get_user_context(user_id)

    # Keep request manageable
    document_text = extracted_text[:120000]

    prompt = f"""
You are Atlas Signal Desk,
an AI financial research assistant.

USER PROFILE:

{user_context}

The user has uploaded a financial document.

DOCUMENT NAME:
{filename}

Analyze ONLY the information contained
in the supplied document.

Do not invent figures, events, companies,
dates, or conclusions.

Produce:

ATLAS DOCUMENT SIGNAL

DOCUMENT
Identify the document type, company/entity,
reporting period, and purpose if available.

EXECUTIVE SUMMARY
Give a concise overview.

KEY FINANCIAL DEVELOPMENTS
Identify important financial figures,
business developments, operational changes,
and material information.

TOP RISKS
Identify 3 to 5 concrete risks supported
by the document.

POSITIVE SIGNALS
Identify important strengths,
opportunities, or positive developments.

ANALYST ANGLE
Explain why the information matters in
the context of the user's interests.

WATCH NEXT
List metrics, developments, risks,
or events an analyst should monitor.

SOURCE DISCIPLINE
If something cannot be established from
the document, say so explicitly.

Do not provide guaranteed investment returns.
Do not present speculation as fact.

DOCUMENT CONTENT:

{document_text}
"""

    await status_message.edit_text(
        "🔎 Document extracted. Atlas is analyzing the financial signals..."
    )

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
        )

        analysis = response.text

        if not analysis:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

    except Exception:
        logger.exception(
            "Gemini PDF analysis failed"
        )

        await status_message.edit_text(
            "Atlas could not analyze this document right now."
        )
        return

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    try:
        save_conversation(
            user_id,
            f"Uploaded PDF: {filename}",
            analysis,
        )
    except Exception:
        logger.exception(
            "Could not save PDF conversation"
        )

    try:
        await status_message.delete()
    except Exception:
        pass

    await send_long_message(
        update,
        analysis,
    )


# ============================================================
# VOICE HANDLER
# ============================================================

async def handle_voice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Handle Telegram voice messages."""

    user_id = str(update.effective_user.id)
    voice = update.message.voice

    if not voice:
        return

    status_message = await update.message.reply_text(
        "🎙️ Listening to your request..."
    )

    try:
        telegram_file = await context.bot.get_file(
            voice.file_id
        )

        file_path = (
            DOWNLOADS_DIR /
            f"{user_id}_{voice.file_id}.ogg"
        )

        audio_data = (
            await telegram_file.download_as_bytearray()
        )

        save_voice_file(
            bytes(audio_data),
            str(file_path),
        )

        logger.info(
            "Voice message saved: %s",
            file_path,
        )

        user_context = get_user_context(user_id)

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[
                types.Part.from_bytes(
                    data=bytes(audio_data),
                    mime_type="audio/ogg",
                ),
                f"""
You are Atlas Signal Desk,
a professional AI financial research assistant.

USER CONTEXT:

{user_context}

Listen carefully to the user's voice message.

Understand the actual question before answering.

If current market information is required,
use get_stock_data.

If recent company developments are required,
use get_company_news.

Available tools:

- get_stock_data
- get_company_news

For substantial financial research use:

ATLAS SIGNAL

WHAT HAPPENED

WHY IT MATTERS

ANALYST ANGLE

WATCH NEXT

Be factual and transparent.

Never guarantee investment returns.

You are an AI research assistant,
not a licensed financial adviser.
""",
            ],
            config=types.GenerateContentConfig(
                tools=[
                    get_stock_data,
                    get_company_news,
                ]
            ),
        )

        response_text = response.text

        if not response_text:
            raise RuntimeError(
                "Gemini returned an empty voice response."
            )

        save_conversation(
            user_id,
            "[Voice Message]",
            response_text,
        )

        await status_message.delete()

        await send_long_message(
            update,
            response_text,
        )

    except Exception:
        logger.exception(
            "Voice processing error"
        )

        await status_message.edit_text(
            "⚠️ I couldn't process that voice message. "
            "Please try again or send the question as text."
        )


# ============================================================
# IMAGE / CHART HANDLER
# ============================================================

async def handle_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Analyze financial charts and screenshots."""

    user_id = str(update.effective_user.id)

    if not update.message.photo:
        return

    status_message = await update.message.reply_text(
        "🖼️ Analyzing your financial image..."
    )

    try:
        photo = update.message.photo[-1]

        telegram_file = await context.bot.get_file(
            photo.file_id
        )

        image_path = (
            DOWNLOADS_DIR /
            f"{user_id}_{photo.file_unique_id}.jpg"
        )

        image_data = (
            await telegram_file.download_as_bytearray()
        )

        with open(image_path, "wb") as image_file:
            image_file.write(bytes(image_data))

        caption = (
            update.message.caption
            or "Analyze this financial chart or image."
        )

        user_context = get_user_context(user_id)

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[
                types.Part.from_bytes(
                    data=bytes(image_data),
                    mime_type="image/jpeg",
                ),
                f"""
You are Atlas Signal Desk.

USER CONTEXT:

{user_context}

The user uploaded a financial image.

USER QUESTION:

{caption}

Analyze the visible information carefully.

Do not invent values that cannot be read.

If the image contains a chart, explain:
- visible trend
- important levels
- notable changes
- patterns that can actually be observed

If it contains a table, explain:
- key values
- relationships
- notable differences

Clearly state when information is unreadable.

Do not guarantee investment returns.

Provide an analyst-oriented explanation.
""",
            ],
        )

        response_text = response.text

        if not response_text:
            raise RuntimeError(
                "Gemini returned an empty image response."
            )

        save_conversation(
            user_id,
            f"[Image] {caption}",
            response_text,
        )

        await status_message.delete()

        await send_long_message(
            update,
            response_text,
        )

    except Exception:
        logger.exception(
            "Image processing error"
        )

        await status_message.edit_text(
            "⚠️ Atlas could not analyze that image. "
            "Please try another chart or screenshot."
        )


# ============================================================
# TEXT HANDLER
# ============================================================

async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Handle normal text conversations."""

    user_id = str(update.effective_user.id)
    user_text = update.message.text

    if not user_text:
        return

    logger.info(
        "User %s: %s",
        user_id,
        user_text,
    )

    user_context = get_user_context(user_id)

    tools = [
        get_stock_data,
        get_company_news,
        update_user_profile_data,
    ]

    config = types.GenerateContentConfig(
        tools=tools,
        system_instruction=build_system_instruction(
            user_context
        ),
    )

    try:
        chat = client.chats.create(
            model=MODEL_ID,
            config=config,
        )

        response = chat.send_message(
            user_text
        )

        atlas_reply = response.text

        if not atlas_reply:
            atlas_reply = (
                "Atlas could not generate a response."
            )

        try:
            save_conversation(
                user_id,
                user_text,
                atlas_reply,
            )
        except Exception:
            logger.exception(
                "Could not save conversation"
            )

        await send_long_message(
            update,
            atlas_reply,
        )

    except Exception:
        logger.exception(
            "Text handler error"
        )

        await update.message.reply_text(
            "Atlas encountered an error while "
            "processing your request."
        )


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    print("========================================")
    print("Starting Atlas Signal Desk...")
    print("Atlas Signal Desk is running.")
    print("Open your Telegram bot and send /start")
    print("========================================")

    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    # Commands
    application.add_handler(
        CommandHandler(
            "start",
            handle_start,
        )
    )

    application.add_handler(
        CommandHandler(
            "help",
            handle_help,
        )
    )

    # PDF
    application.add_handler(
        MessageHandler(
            filters.Document.PDF,
            handle_document,
        )
    )

    # Voice
    application.add_handler(
        MessageHandler(
            filters.VOICE,
            handle_voice,
        )
    )

    # Images
    application.add_handler(
        MessageHandler(
            filters.PHOTO,
            handle_photo,
        )
    )

    # Text
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text,
        )
    )

    application.run_polling()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()