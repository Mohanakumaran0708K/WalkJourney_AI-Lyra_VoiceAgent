# WalkJourney AI — Lyra Voice Agent (Hackathon MVP Foundation)

> **Phase 1 Implementation Phase**  
> Real-time AI voice navigation assistant foundation built with **FastAPI** (Backend) and **React + Vite** (Frontend).

---

## 📁 Project Architecture & Folder Structure

```
walkjourney-lyra/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app initialization, CORS middleware & routes
│   │   ├── config.py            # Environment configuration with pydantic-settings
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── router.py        # API endpoints (/health, /agent/status, /agent/chat)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── voice_service.py # Voice interaction service orchestration layer
│   │   ├── agent/
│   │   │   ├── __init__.py
│   │   │   └── lyra_agent.py    # Lyra AI Voice Agent core decision logic
│   │   └── tools/
│   │       ├── __init__.py
│   │       └── navigation_tool.py # Crowd density & path calculation helpers
│   ├── requirements.txt         # Python dependencies (FastAPI, Uvicorn, Pydantic, etc.)
│   ├── .env                     # Local environment variables
│   └── .env.example             # Example environment template
├── frontend/                    # React + Vite application
│   ├── src/
│   │   ├── App.jsx              # Main UI component (Mic visualizer, transcript, status)
│   │   ├── index.css            # Dark mode glassmorphic styling system & animations
│   │   └── main.jsx             # React entrypoint
│   ├── package.json
│   └── vite.config.js
├── README.md                    # Project documentation & run guide
└── .gitignore                   # Git ignore settings
```

---

## 🚀 How to Run Locally

### 1. Running the Backend (FastAPI)

1. Open a terminal and navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. (Optional but recommended) Create and activate a Python virtual environment:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. Access interactive API documentation:
   - Swagger UI: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
   - Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

### 2. Running the Frontend (React + Vite)

1. Open a separate terminal window and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (if not already installed):
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

4. Open your browser at:
   - [http://localhost:5173](http://localhost:5173)

---

## 📄 File Details & Purpose

### Backend:
- **`app/main.py`**: Entry point that configures CORS for local React frontend development and binds API routes.
- **`app/config.py`**: Loads environment settings safely from `.env` using Pydantic Settings.
- **`app/api/router.py`**: Handles API requests such as `/health`, `/agent/status`, and `/agent/chat`.
- **`app/services/voice_service.py`**: Manages voice pipeline operations and connects API controllers with agent logic.
- **`app/agent/lyra_agent.py`**: Encapsulates the core agent response logic for navigation queries.
- **`app/tools/navigation_tool.py`**: Contains mock crowd density estimation and navigation route calculation tools.

### Frontend:
- **`src/App.jsx`**: Features a voice interaction hub with a dynamic mic visualizer, status indicators connected to backend `/health`, Web Speech API integration, sample prompt triggers, and a conversation transcript panel.
- **`src/index.css`**: Implements a glassmorphic design system with CSS animations, glowing neon accents, and responsive layout.

---

## 🎯 Phase 1 Constraints (Hackathon Scope)

As mandated for Phase 1:
1. ❌ **AssemblyAI**: Not implemented yet (speech pipeline hooks ready for Phase 2).
2. ❌ **LLM**: Not implemented yet (mock decision rules in `lyra_agent.py`).
3. ❌ **YOLO**: Not implemented yet (mock crowd density tools in `navigation_tool.py`).
4. ❌ **Database**: No DB attached.
5. ❌ **Authentication**: Kept open for rapid hackathon iteration.
