# Setup Guide

This guide will help you set up and run the Complaint Categorization and RAG System from scratch.

## Prerequisites

Before you start, make sure you have:

1. **Docker Desktop** installed and running
   - Download: https://www.docker.com/products/docker-desktop/
   - Make sure Docker Desktop is running before proceeding

2. **Python 3.9+** installed
   - Check: `python --version`

3. **Node.js 18+** installed (for frontend)
   - Check: `node --version`
   - Download: https://nodejs.org/

4. **Mistral API Key**
   - Get free API key: https://console.mistral.ai/
   - Free tier supports `open-mistral-7b` model

## Quick Setup (Step by Step)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Category-rag
```

### Step 2: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
copy .env.example .env
```

Edit `.env` and add your Mistral API key:
```
MISTRAL_API_KEY=your_actual_api_key_here
```

**Note:** The database URL is already configured for Docker. Don't change it unless you're using a different database setup.

### Step 3: Start PostgreSQL Database (Docker)

Open PowerShell or Terminal in the project root directory (`Category-rag`):

```powershell
# Start PostgreSQL with pgvector
docker-compose up -d
```

Wait a few seconds for the database to start. Verify it's running:

```powershell
# Check if container is running
docker-compose ps
```

You should see `complaints_db` container running.

### Step 4: Set Up Backend

Open a new terminal/PowerShell window and navigate to the backend directory:

```powershell
cd backend
```

**Create virtual environment:**
```powershell
python -m venv venv
```

**Activate virtual environment:**
```powershell
# Windows PowerShell
venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Mac/Linux
source venv/bin/activate
```

**Install dependencies:**
```powershell
pip install -r requirements.txt
```

**Initialize database:**
```powershell
# This creates tables and enables pgvector extension
python -c "from app.database import init_db; init_db()"
```

### Step 5: Start Backend Server

Still in the `backend` directory with virtual environment activated:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be running at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Keep this terminal window open.

### Step 6: Set Up Frontend

Open a **new** terminal/PowerShell window and navigate to the frontend directory:

```powershell
cd frontend
```

**Install dependencies:**
```powershell
npm install
```

**Start frontend development server:**
```powershell
npm run dev
```

The frontend will be running at:
- **Frontend**: http://localhost:5173

Keep this terminal window open.

### Step 7: Verify Everything Works

1. Open your browser and go to: http://localhost:5173
2. You should see the complaint submission form
3. Try submitting a test complaint
4. Check the backend API docs at: http://localhost:8000/docs

## Directory Structure & Commands Reference

### Project Root (`Category-rag/`)

**Docker commands:**
```powershell
# Start database
docker-compose up -d

# Stop database
docker-compose down

# View database logs
docker-compose logs -f postgres

# Stop and delete all data (⚠️ careful!)
docker-compose down -v
```

### Backend Directory (`backend/`)

**Setup (first time only):**
```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
python -c "from app.database import init_db; init_db()"
```

**Run backend:**
```powershell
cd backend
venv\Scripts\Activate.ps1  # Activate venv first
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Run tests:**
```powershell
cd backend
venv\Scripts\Activate.ps1
pytest
```

### Frontend Directory (`frontend/`)

**Setup (first time only):**
```powershell
cd frontend
npm install
```

**Run frontend:**
```powershell
cd frontend
npm run dev
```

**Build for production:**
```powershell
cd frontend
npm run build
```

## Loading Sample Data (Optional)

If you have complaint data in JSON format:

```powershell
cd backend
venv\Scripts\Activate.ps1
python scripts/ingest_complaints.py ../data/complaints-2024-08-15_20_15.json
```

## Troubleshooting

### Database Connection Issues

**Problem:** Backend can't connect to database

**Solution:**
1. Check if Docker container is running: `docker-compose ps`
2. If not running, start it: `docker-compose up -d`
3. Wait 10-15 seconds for database to fully start
4. Check database logs: `docker-compose logs postgres`

### Port Already in Use

**Problem:** Port 8000 or 5173 already in use

**Solution:**
- **Backend:** Change port in command: `uvicorn app.main:app --reload --port 8001`
- **Frontend:** Vite will automatically use next available port, or edit `vite.config.ts`

### Module Not Found Errors

**Problem:** `ModuleNotFoundError` when running backend

**Solution:**
1. Make sure virtual environment is activated: `venv\Scripts\Activate.ps1`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check you're in the `backend` directory

### Frontend Can't Connect to Backend

**Problem:** Frontend shows connection errors

**Solution:**
1. Make sure backend is running on port 8000
2. Check `frontend/src/services/api.ts` has correct backend URL
3. Check CORS settings in backend `main.py`

### Docker Issues

**Problem:** Docker commands fail

**Solution:**
1. Make sure Docker Desktop is running
2. Check Docker is accessible: `docker --version`
3. Try restarting Docker Desktop
4. Check if port 5432 is already in use (stop local PostgreSQL if running)

## Environment Variables

Key variables in `.env`:

- `DATABASE_URL` - PostgreSQL connection (default works with Docker)
- `MISTRAL_API_KEY` - Your Mistral API key (**required**)
- `MISTRAL_MODEL` - Model to use (`mistral-small` or `open-mistral-7b` for free tier)
- `EMBEDDING_MODEL` - Embedding model (default: `all-MiniLM-L6-v2`)

## Next Steps

Once everything is running:

1. **Submit a complaint** via the frontend form
2. **View similar complaints** - the system will find related complaints
3. **Check the dashboard** - see analytics and statistics
4. **Explore API docs** - http://localhost:8000/docs

## Stopping the Application

1. **Stop frontend:** Press `Ctrl+C` in frontend terminal
2. **Stop backend:** Press `Ctrl+C` in backend terminal
3. **Stop database:** `docker-compose down` (or leave it running for next time)

## Need Help?

- Check API documentation: http://localhost:8000/docs
- Review logs in terminal windows
- Check Docker logs: `docker-compose logs postgres`
- See `README.md` for architecture details
