# 🌱 Mitra — Private AI Mental Wellness Companion

> A Streamlit-based private wellness companion that detects your mood via facial expressions, supports daily journaling, and delivers personalized AI-driven wellness suggestions — all stored locally on your device.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📸 **Daily Check-In** | Facial mood detection + self-report sliders + streamed AI response |
| 📝 **Journal** | Free-form journaling with AI reflection, sentiment analysis & theme tagging |
| 📊 **Mood Trends** | 7-day mood chart, emotion pie, stress heatmap, sentiment bars |
| 💡 **Wellness Tips** | Personalized AI suggestions + guided 4-7-8 breathing exercise |
| 🔒 **Privacy First** | No facial images stored, all data local (SQLite), crisis helplines built-in |

---

## 🚀 Quick Start

### 1. Clone / open the project
```bash
cd e:\mentalhealth
```

### 2. Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key
Edit `.env`:
```
OPENAI_API_KEY=sk-...your-key-here...
```

### 5. Run the app
```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

---

## 📁 Project Structure

```
mentalhealth/
├── app.py                      # Main entrypoint + sidebar + home
├── requirements.txt
├── .env                        # OpenAI API key (never commit this!)
│
├── mood_tracker/
│   ├── __init__.py
│   └── detector.py             # DeepFace + OpenCV fallback detector
│
├── database/
│   ├── __init__.py
│   └── db.py                   # SQLite CRUD (auto-creates data/mitra.db)
│
├── pages/
│   ├── 1_Daily_Checkin.py      # Check-in flow
│   ├── 2_Journal.py            # Journaling + AI reflection
│   ├── 3_Mood_Trends.py        # Charts dashboard
│   └── 4_Wellness_Tips.py      # Suggestions + breathing
│
├── components/
│   ├── __init__.py
│   ├── mood_capture.py         # Camera + detector integration
│   ├── ai_companion.py         # OpenAI API calls
│   ├── journal_analyzer.py     # Cached journal analysis
│   └── crisis_support.py       # Crisis helpline banner
│
├── utils/
│   ├── __init__.py
│   ├── constants.py            # Mood maps, prompts, palette
│   └── helpers.py              # Date, greeting, streak utils
│
├── assets/
│   └── styles.css              # Custom premium CSS
│
└── data/
    └── mitra.db                # Auto-created SQLite database
```

---

## 🤖 AI Model

- **Provider:** OpenAI (`gpt-4o-mini`)
- **Used for:** Check-in responses, journal reflection, wellness suggestions, writing prompts
- **Privacy:** Only mood labels + journal text sent to API. No facial images. No names unless entered by user.

---

## 📷 Emotion Detection

- **Primary:** [DeepFace](https://github.com/serengil/deepface) (auto-downloads weights on first run)
- **Fallback:** OpenCV Haar Cascade (brightness heuristics)
- **Fallback #2:** Manual mood selection if no face detected

> DeepFace requires ~200MB for model weights downloaded on first use.

---

## 🛡️ Privacy & Ethics

1. Facial images are **never** written to disk or database
2. Only derived emotion labels are stored locally
3. All data stays on the device (SQLite)
4. Crisis helplines displayed for high-stress states
5. Mitra is explicitly positioned as a **companion, not a therapist**
6. One-click data deletion via sidebar

---

## 🏥 Crisis Resources (India)

| Helpline | Number | Hours |
|---|---|---|
| iCall India | 9152987821 | Mon–Sat, 8am–10pm |
| Vandrevala Foundation | 1860-2662-345 | 24/7 |
| NIMHANS | 080-46110007 | 24/7 |
| Snehi | 044-24640050 | Mon–Sat, 8am–10pm |

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |

---

## 📦 Dependencies

- `streamlit` — Web framework
- `openai` — GPT-4o-mini API
- `deepface` — Facial expression detection
- `opencv-python-headless` — Image processing + fallback detection
- `plotly` — Interactive charts
- `pillow` — Image handling
- `pandas` — Data manipulation
- `python-dotenv` — Environment variable loading

---

*Built with ❤️ for mental wellness. Remember: seeking help is a sign of strength.*
