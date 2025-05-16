# 🏃‍♂️ AI Fitness Coach

**AI Fitness Coach** is a local, privacy-friendly fitness tracker and recommender that lets you upload your workout data (CSV from HealthFit or Apple Fitness), analyse it, and receive smart training suggestions from a local large language model (LLM) — all via a clean Streamlit interface.

No cloud processing. No data sharing. Just instant, on-device feedback.

---

## 🗂️ Project Overview

This app helps fitness enthusiasts and athletes track and analyse their workouts while generating AI-powered suggestions for future training. It combines:

- **Custom CSV parsing** from HealthFit-style exports
- **Workout summarisation** (distance, heart rate, cadence, power, elevation)
- **Local LLM interaction** for workout recommendations
- **Streamlit UI** for intuitive use
- **SQLite logging** to store and view workout history

---

## 🔧 Core Functionalities

- 📥 **CSV Upload & Parsing**  
  Parses workout files exported from HealthFit or Apple Fitness using custom logic.

- 📊 **Workout Analysis**  
  Calculates total distance, average heart rate, cadence, calories, power, elevation, and workout duration.

- 🧠 **AI-Powered Suggestions**  
  Queries a locally running LLM (via [LM Studio](https://lmstudio.ai)) to suggest your next workout.

- 💾 **Workout Logging**  
  Stores all workouts in a SQLite database with key statistics for easy review.

- 🖥️ **Streamlit UI**  
  Enables file uploads, displays analytics, and shows workout history + AI advice.

---

## 📁 Project Structure
AI Fitness Coach/
├── dashboard.py               # Streamlit app (main UI)
├── main.py                    # (optional CLI runner)
├── model/
│   ├── recommender.py         # Handles LLM suggestions + logging
│   ├── llm_handler.py         # Connects to LM Studio’s local LLM API
├── parser/
│   └── csv_parser.py          # Custom HealthFit CSV parser
├── utils/
│   ├── stats_utils.py         # Workout metrics & LLM prompt prep
│   └── analyzer.py            # (Legacy logic moved to stats_utils)
├── data/
│   └── workout_log.db         # SQLite database
├── temp.csv                   # Temporary file for uploaded data
└── .venv/                     # Python virtual environment

---

## 🧠 LLM Configuration

- **Model**: DeepSeek-R1-Distill-Qwen-7B-GGUF  
- **Serving Tool**: [LM Studio](https://lmstudio.ai) (running locally)
- **API Endpoint**: `http://localhost:1234/v1/chat/completions`

---

## ✅ Current Features

- [x] Upload and parse HealthFit/Apple CSV files
- [x] Display workout summary (distance, HR, calories, duration, etc.)
- [x] Log workouts to a local SQLite database
- [x] Generate training suggestions from a local LLM
- [x] Show logged workout history

---

## ⚠️ Known Issues

1. **Database schema mismatch**  
   Error when logging:  
   `sqlite3.OperationalError: table workouts has no column named avg_cadence`  
   → Fix: Drop and recreate the database or migrate schema.

2. **UI loading**  
   Requires clicking “Continue” to complete some actions.

3. **AI delay**  
   The model’s “thinking” messages appear — could be suppressed for smoother UX.

---

## 🚧 Next Steps

- 🛠 Fix CSV parsing:
  - Properly convert numeric fields with commas to periods
  - Ensure total distance is summed accurately

- ⏱ Improve duration calculation:
  - Use timestamps to calculate precise elapsed time

- 🔄 Add GPX support:
  - Allow toggling between CSV and GPX input

- 📈 Improve visuals:
  - Add charts (e.g., HR over time) to the Streamlit dashboard

---

## 📌 Requirements

- Python 3.10+
- Streamlit
- Requests
- SQLite3
- LM Studio installed and running locally

Install dependencies:
```bash
pip install -r requirements.txt
```

🚀 Running the App
	1.	Start LM Studio and serve the model at http://localhost:1234
	2.	Run the Streamlit app:
```bash
streamlit run dashboard.py
```

🧑‍💻 Author

Simone Mezzabotta
Data Analyst | AI for Good Advocate | O24 BlueBook Trainee at the European Commission

⸻

📄 License

This project is licensed under the MIT License.