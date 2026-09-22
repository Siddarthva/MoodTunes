# MoodTunes

MoodTunes is a mood-based music recommendation web application that captures a user's facial expression via webcam, classifies the emotion using OpenCV face detection and a custom 7-class CNN model, maps the emotion to a musical mood profile, and recommends top matching songs.

---

## Workspace Structure

```
nndl/
├── Emotion-detection/            # Reference implementation repository (untouched)
├── backend/                      # Production FastAPI Backend Service
├── frontend/                     # Production React + Vite Editorial Frontend
└── ml/                           # Jupyter Notebook for FER2013 Model Training
```

---

## Quick Start Guide

### 1. Run Backend Service

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
- Health Check: `http://localhost:8000/health`
- Swagger Docs: `http://localhost:8000/docs`

### 2. Run Frontend Application

```powershell
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:5173`

---

## Environment Configuration

Copy `backend/.env.example` to `backend/.env` and update configuration values as needed:

```powershell
cp backend/.env.example backend/.env
```

Refer to [`.env.example`](file:///c:/nndl/backend/.env.example) for all supported configuration options and default key templates.

---

## Development Modes

### Mock Mode (Default for Testing Before Model Training)
Set `EMOTION_PROVIDER=mock` in your `backend/.env` (derived from `backend/.env.example`):
```ini
EMOTION_PROVIDER=mock
```
Allows testing the full pipeline and frontend integration before training the custom CNN model.

### Real Model Inference Mode
1. Train the model using `ml/notebooks/MoodTunes_FER2013_Emotion_Training.ipynb`.
2. Copy `moodtunes_emotion_cnn.keras` into `backend/app/models/emotion/`.
3. Set `EMOTION_PROVIDER=moodtunes_cnn` in `backend/.env`:
```ini
EMOTION_PROVIDER=moodtunes_cnn
```

---

## Reference Repository

The original reference implementation in `Emotion-detection/` remains untouched.
