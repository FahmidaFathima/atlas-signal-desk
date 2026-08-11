# 🤖 Atlas Signal Desk

**AI-Powered Financial Research Assistant for Telegram**

Atlas Signal Desk is a multimodal AI financial research assistant that brings market intelligence, company news, document analysis, voice interaction, and persistent user memory into a single Telegram-based workflow.

Instead of navigating multiple financial tools, users can simply ask Atlas questions naturally.

---

## 🚀 What Atlas Does

Atlas combines Gemini's reasoning and tool-calling capabilities with financial data services and persistent SQLite memory.

### 📈 Market Intelligence

Ask Atlas about:

* Current stock prices
* Previous closing prices
* Market capitalization
* Company information
* Sector and industry
* Market performance

Example:

> What is the current price of NVIDIA?

Atlas can invoke its market-data tool to retrieve the requested information.

---

### 📰 Company News

Users can ask about recent developments affecting companies.

Examples:

> What is happening with NVIDIA?

> What are the latest developments around AMD?

Atlas can use its company-news tool to retrieve relevant information.

---

### 🧠 Persistent Memory

Atlas maintains a persistent user profile using SQLite.

It can remember:

* User role
* Areas of interest
* Watchlist companies

For example:

> I'm a senior investment analyst focused on AI infrastructure and semiconductors. Add NVIDIA and AMD to my watchlist.

Atlas stores this information and can use it during future conversations.

---

### 🎤 Voice Interaction

Users can send natural-language voice messages through Telegram.

Atlas processes the voice input and responds through the same conversational workflow.

Example:

> What is the latest signal on NVIDIA?

---

### 📄 Financial Document Analysis

Users can upload financial PDFs.

Atlas extracts the document text and passes the relevant content to Gemini for analysis.

This allows users to ask questions about financial reports and other documents without manually reading the entire file.

---

### 🖼 Multimodal Analysis

Atlas is designed to process visual financial information such as charts and screenshots.

Example:

> Explain this stock chart.

> What trend does this image show?

---

## 🧩 AI Tool Calling

Atlas uses Gemini's function/tool-calling capability.

Available tools include:

```text
get_stock_data
get_company_news
update_user_profile_data
```

Gemini decides when these capabilities are relevant to the user's request.

---

## 🧠 Memory Architecture

Atlas uses SQLite for persistent memory.

### User Profile

```text
user_profiles
├── user_id
├── role
├── interests
├── watchlist
├── preferences
├── created_at
├── updated_at
└── last_updated
```

### Conversation Memory

```text
conversations
├── user_id
├── user_message
├── assistant_message
└── created_at
```

This allows Atlas to maintain useful context across sessions rather than relying only on the current conversation.

---

## 🏗 Architecture

```text
Telegram User
      │
      ▼
Telegram Bot
      │
      ▼
Atlas Application
      │
      ├── Text
      ├── Voice
      ├── PDF
      └── Image
      │
      ▼
Gemini AI
      │
      ├── Market Data Tool
      ├── Company News Tool
      └── Memory Tool
      │
      ▼
SQLite Memory
      │
      ▼
Personalized Response
```

---

## 🛠 Technology Stack

### AI

* Google Gemini
* Google GenAI SDK

### Backend

* Python
* python-telegram-bot

### Financial Data

* yfinance
* Company news integration

### Document Processing

* PDF extraction

### Memory

* SQLite

### Environment

* Python virtual environment
* dotenv

---

## 📁 Project Structure

```text
atlas-signal-desk/
│
├── app.py
├── database.py
├── .env.example
├── requirements.txt
├── README.md
│
├── finance/
│   ├── market_data.py
│   └── news.py
│
├── documents/
│   └── pdf_processor.py
│
└── voice/
    └── voice_processor.py
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY
cd atlas-signal-desk
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate it

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file:

```text
TELEGRAM_BOT_TOKEN=your_token
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Never commit `.env` to GitHub.

### 6. Start Atlas

```bash
python app.py
```

Open the Telegram bot and send `/start`.

---

## 💬 Example Queries

### Market

> What is the current price of NVIDIA?

> Compare NVIDIA and AMD.

> What is Microsoft's market capitalization?

### News

> What are the latest developments around NVIDIA?

> What happened to AMD recently?

### Memory

> I'm a semiconductor analyst.

> I'm interested in AI infrastructure.

> Add NVIDIA and AMD to my watchlist.

### Voice

Send a voice message:

> Give me the latest signal on NVIDIA.

### Documents

Upload a financial PDF and ask:

> Summarize this report.

> What are the key financial risks?

> What changed in this report?

### Images

Upload a chart and ask:

> Explain this chart.

---

## ⚠️ Disclaimer

Atlas Signal Desk is an AI-powered financial research assistant.

It provides informational and research-oriented responses and does not provide guaranteed investment returns or personalized regulated financial advice.

Users should independently verify financial information before making investment decisions.

---

## 🔗 Live Demo

**Telegram Bot:**
https://t.me/atlas_financial_advice_ai_bot

---

## 👨‍💻 Developer

**Fahmida Fathima**

Atlas Signal Desk was developed as an AI financial-assistant project focusing on multimodal interaction, tool calling, financial information retrieval, and persistent conversational memory.
