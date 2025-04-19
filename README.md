# COMP631-RAG-Agent: Dream Analysis System

## 🎯 Project Purpose

This project builds a full-stack **Dream Analysis Agent** that combines document retrieval and large language models (LLMs) to provide natural, structured, and psychologically grounded dream interpretations.

It supports user input in **English** or **Chinese**, automatically retrieves relevant symbolic and scientific materials, and generates a coherent dream analysis.

**Main Features:**
- Retrieve both **folk dream interpretations** and **scientific psychological articles**.
- Summarize and clean the retrieved text for better LLM prompting.
- Generate structured dream analyses with sections: Symbolism Interpretation, Scientific Support, and Psychological Analysis.
- Full frontend + backend stack for smooth user experience.

---

## 🛠️ Project Structure

COMP631-RAG-agent/
├── backend/           # FastAPI backend
├── rag-frontend/      # React/Vite Next.js frontend
├── retriever/         # retriever
├── README.md
├── requirements.txt

---

## 🚀 How to Run the Project

### Prerequisites
- Python 3.10+
- Node.js (for frontend, v16+ recommended)
- pip and npm installed

---

### Step 1: Clone the repository

```bash
git clone https://github.com/Shalalalaa/COMP631-RAG-agent.git
cd COMP631-RAG-agent
```

### Step 2: Install backend dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install frontend dependencies

```bash
cd rag-frontend
npm install
```

### Step 4: Start backend and frontend servers

Open **two terminals**:

**Terminal 1 (Backend):**

```bash
cd ..
python -m pip install fastapi uvicorn
python -m pip install torch torchvision torchaudio
python -m backend.main
```

Backend runs at: http://localhost:8000


**Terminal 2 (Frontend):**
```bash
cd COMP631-RAG-agent/rag-frontend
npm run dev
```

Frontend runs at: http://localhost:3000

Frontend automatically communicates with backend through API.

## ⚙️ Important Notes

- **Corpus data** must be pre-built and placed under `retriever/` folders.
- **GPU strongly recommended** for LLM model loading (DeepSeek 1.5B requires ~6GB VRAM).
- **Model and corpus download** are handled automatically through HuggingFace Hub if missing.
- **Two types of sources** are guaranteed in retrieval results: folk dream interpretations and scientific articles.

---

## ✨ Future Improvements

- Add multi-turn conversation support
- Implement memory for dream histories
- Fine-tune model outputs for more academic or creative styles
- Auto-update scientific literature corpus periodically

---

## 📄 License

This project is intended for academic and educational use only.


