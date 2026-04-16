<div align="center">
  <h1>🕵️ AI Conversation Analyzer</h1>
  <p>Break down your WhatsApp chats like a social scientist + therapist (but fully automated and slightly savage).</p>
</div>

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-green.svg)
![Streamlit](https://img.shields.io/badge/Powered%20by-Streamlit-red.svg)

## 🚀 What This Is
A Python and Streamlit web application that accepts a WhatsApp chat export and automatically parses it to tell you:
* **Who talks the most** (Carrying the convo? 👀)
* **Response time patterns** (Who takes hours to reply?)
* **Emotional tone over time** (Are the vibes fading or growing?)
* **Dry Replies** (Who is sending "k" and "💀")
* **Conversation “Health Score”** (A custom algorithm tracking balance, sentiment, and effort)

Wait, there's more. **Drop in a Google Gemini API Key**, and it will actively read these stats and output a brutally honest, human-like summary of your relationship dynamic.

## 🛠️ The Tech Stack
* **Python** 🐍
* **Streamlit** (For the aesthetic frontend dashboard)
* **vaderSentiment** (Lightning-fast sentiment analysis for mood tracking over time)
* **google-generativeai** (Gemini for generating those savage insights)
* **Matplotlib & Pandas** (For the data crunching and visualizations)

## 💻 Running It Locally

### 1. Clone & Setup
```bash
git clone https://github.com/YOUR_USERNAME/ai-conversation-analyzer.git
cd ai-conversation-analyzer
pip install -r requirements.txt
```

### 2. Run the App
```bash
streamlit run app.py
```

## 📱 How to Export Your WhatsApp Data
1. Open up a WhatsApp chat on your phone.
2. Tap the `3 dots` (menu) -> **More** -> **Export Chat**.
3. Select **"Without Media"**.
4. You will get a `.txt` file. Drop this file into the analyzer!

*(Note: The app runs completely locally on your machine. Unless you decide to use the Gemini AI API, none of your messages leave your computer!)*

## 🧠 What's Being Analyzed?
We rely on raw logic to figure out social dynamics:
* **Dry Replies:** Defined as messages `< 5` characters with `<= 0` sentiment.
* **Initiations:** Logged anytime someone texts after a 1+ hour silence gap.
* **Health Score:** Calculates response fairness, conversation share, and average sentiment multiplier.

## FAQ
* **Do I need a GPU?** Nope. We use VADER for the heavy NLP text logic which runs incredibly fast on literally any laptop. 
* **Is it free?** Yes, completely open source. Getting a Gemini API key from Google AI Studio is also free for developers!

---
