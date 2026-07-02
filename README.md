# 📄 AI Resume Analyzer

A full-featured AI-powered resume analyzer built with **Streamlit**, **Claude AI (Anthropic)**, and **MongoDB**.

---

## 🚀 Features

| Feature | Description |
|---|---|
| 📤 Upload | PDF, DOCX, TXT resume upload |
| 🤖 AI Analysis | Claude scores and analyzes the resume |
| 🎯 Job Match | Paste a JD to get match % + keyword gap |
| 📊 Scores | Overall, ATS, Section-wise radar chart |
| 💡 Suggestions | Prioritized improvement suggestions |
| 🗃️ MongoDB | All analyses saved and browsable in History |
| 📈 Dashboard | Aggregate stats, charts, career-level breakdown |

---

## 🛠️ Setup & Installation

### 1. Clone / Copy the project
```bash
cd ai-resume-analyzer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env`:
```env
ANTHROPIC_API_KEY=your_actual_anthropic_api_key
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=resume_analyzer
```

### 4. Start MongoDB
```bash
# macOS (Homebrew)
brew services start mongodb-community

# Ubuntu / Linux
sudo systemctl start mongod

# Windows
net start MongoDB

# OR use Docker
docker run -d -p 27017:27017 --name mongo mongo:latest
```

### 5. Run the app
```bash
streamlit run app.py
```

Open: [http://localhost:8501](http://localhost:8501)

---

## 📁 Project Structure

```
ai-resume-analyzer/
├── app.py              ← Main Streamlit UI (3 pages)
├── ai_analyzer.py      ← Claude API integration & text extraction
├── database.py         ← MongoDB connectivity & CRUD operations
├── requirements.txt    ← Python dependencies
├── .env.example        ← Environment variables template
└── README.md
```

---

## 🔑 Getting API Keys

### Anthropic API Key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up / Log in
3. Navigate to **API Keys** → Create new key
4. Copy it to `.env` as `ANTHROPIC_API_KEY`

### MongoDB
- **Local**: Install [MongoDB Community](https://www.mongodb.com/try/download/community)
- **Cloud**: Use [MongoDB Atlas](https://www.mongodb.com/atlas) (free tier available)
  - Atlas URI format: `mongodb+srv://user:pass@cluster.mongodb.net/`

---

## 🧪 Usage

1. **Analyze Resume** page → Upload PDF/DOCX/TXT → (optional) paste job description → Click **Analyze Resume**
2. View scores, radar chart, strengths/weaknesses, suggestions, ATS issues, job match
3. **History** page → Browse all past analyses stored in MongoDB
4. **Dashboard** → See aggregate stats and visual charts

---

## 🌐 Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo, set `app.py` as entry point
4. Add secrets in **Settings → Secrets**:
```toml
ANTHROPIC_API_KEY = "your_key"
MONGODB_URI = "your_mongodb_atlas_uri"
MONGODB_DB_NAME = "resume_analyzer"
```
