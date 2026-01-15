# AI Chat Application

A production-ready web-based chat application that allows interaction with multiple AI language models through OpenRouter as a gateway. Built with OpenTelemetry tracing for full observability.

![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)
![Python](https://img.shields.io/badge/Python-3.11-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-Enabled-orange)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [OpenTelemetry & Jaeger](#opentelemetry--jaeger)
- [Project Structure](#project-structure)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This application provides a clean, intuitive interface for chatting with various AI models. It leverages OpenRouter as a unified gateway to access multiple LLMs, while providing full observability through OpenTelemetry tracing exported to Jaeger.

### Key Capabilities

- **Multi-Model Support**: Choose from various free AI models (Llama, Gemma, Phi, Qwen, etc.)
- **Session-Based Memory**: Maintains conversation context within sessions
- **Image Upload**: Support for multimodal models that accept images
- **Full Tracing**: Every request is traced with detailed spans
- **Production-Ready**: Docker-based deployment with health checks

## ✨ Features

### Core Features
- 💬 Real-time chat interface with AI models
- 🤖 Dynamic model selection from OpenRouter's free tier
- 📜 Session-based chat history
- 🖼️ Image upload for multimodal models
- ⚡ Async API calls for better performance
- 🔍 Full OpenTelemetry instrumentation

### UI Features
- 🎨 Modern, minimal design with TailwindCSS
- 📱 Responsive layout
- ⏳ Loading states and typing indicators
- ❌ Clear error messages
- 🔗 Direct link to Jaeger UI

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│    Frontend     │────▶│    Backend      │────▶│   OpenRouter    │
│   (React/TS)    │     │   (FastAPI)     │     │      API        │
│   Port: 3000    │     │   Port: 8000    │     │                 │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 │ OTLP/gRPC
                                 ▼
                        ┌─────────────────┐
                        │                 │
                        │     Jaeger      │
                        │  (Tracing UI)   │
                        │   Port: 16686   │
                        │                 │
                        └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
| Technology | Purpose | Why? |
|------------|---------|------|
| **Python 3.11** | Runtime | Modern features, async support |
| **FastAPI** | Web Framework | High performance, automatic docs, async native |
| **httpx** | HTTP Client | Async HTTP requests with HTTP/2 support |
| **Pydantic** | Data Validation | Type-safe request/response handling |
| **OpenTelemetry** | Observability | Industry-standard distributed tracing |

### Frontend
| Technology | Purpose | Why? |
|------------|---------|------|
| **React 18** | UI Framework | Component-based, large ecosystem |
| **TypeScript** | Type Safety | Better DX, catch errors early |
| **Vite** | Build Tool | Fast HMR, optimized builds |
| **TailwindCSS** | Styling | Utility-first, rapid development |
| **Lucide React** | Icons | Clean, consistent icon set |

### Infrastructure
| Technology | Purpose | Why? |
|------------|---------|------|
| **Docker** | Containerization | Consistent environments |
| **Docker Compose** | Orchestration | Simple multi-container setup |
| **Jaeger** | Tracing Backend | Powerful trace visualization |
| **Nginx** | Reverse Proxy | Production-grade static serving |

## 📦 Prerequisites

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **OpenRouter API Key** ([Get one here](https://openrouter.ai/keys))

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd madlen-case-study
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenRouter API key
nano .env  # or use your preferred editor
```

Your `.env` file should contain:
```
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
```

### 3. Start the Application

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### 4. Access the Application

| Service | URL | Description |
|---------|-----|-------------|
| **Chat UI** | http://localhost:3000 | Main application |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Jaeger UI** | http://localhost:16686 | Trace visualization |
| **Health Check** | http://localhost:8000/health | Backend health |

### 5. Stop the Application

```bash
docker-compose down

# Remove volumes too
docker-compose down -v
```

## 📡 API Documentation

### Endpoints

#### `POST /api/chat`
Send a message to the AI model.

**Request:**
```json
{
  "message": "Hello, how are you?",
  "model": "meta-llama/llama-3.2-3b-instruct:free",
  "image": {
    "base64_data": "...",
    "media_type": "image/png"
  }
}
```

**Response:**
```json
{
  "message": {
    "role": "assistant",
    "content": "Hello! I'm doing well, thank you for asking...",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "model": "meta-llama/llama-3.2-3b-instruct:free"
  },
  "success": true
}
```

#### `GET /api/models`
List available AI models.

**Response:**
```json
{
  "models": [
    {
      "id": "meta-llama/llama-3.2-3b-instruct:free",
      "name": "Llama 3.2 3B Instruct",
      "supports_images": false
    }
  ],
  "count": 8
}
```

#### `GET /api/chat/history`
Get current session chat history.

**Response:**
```json
{
  "messages": [...],
  "count": 10,
  "session_id": "uuid-here"
}
```

#### `POST /api/chat/clear`
Clear current session history.

#### `POST /api/chat/new-session`
Start a new chat session.

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔍 OpenTelemetry & Jaeger

### What is Traced?

The application creates detailed traces for:

1. **Incoming API Requests**
   - HTTP method, path, status code
   - Request duration
   - Client information

2. **OpenRouter API Calls**
   - Model selection
   - Request/response sizes
   - Latency metrics

3. **Chat History Operations**
   - Message additions
   - History retrievals
   - Session management

4. **Errors & Exceptions**
   - Full stack traces
   - Error context

### Accessing Jaeger UI

1. Open http://localhost:16686
2. Select "chat-backend" from the Service dropdown
3. Click "Find Traces"
4. Click on any trace to see detailed spans

### Understanding Traces

Each trace shows the full request lifecycle:

```
api.chat.send_message (total: 1.2s)
├── chat_history.add_message (5ms)
├── openrouter.send_message (1.1s)
│   ├── HTTP POST openrouter.ai/api/v1/chat/completions
│   └── Response received
└── chat_history.add_message (3ms)
```

### Trace Attributes

Key attributes captured in spans:

| Attribute | Description |
|-----------|-------------|
| `model` | AI model used |
| `message_length` | Input message length |
| `response_length` | AI response length |
| `session_id` | Chat session identifier |
| `has_image` | Whether request included an image |

## 📁 Project Structure

```
madlen-case-study/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration management
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py          # Chat endpoints
│   │   │   └── models.py        # Models endpoint
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── chat.py          # Pydantic models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── openrouter.py    # OpenRouter integration
│   │   │   └── chat_history.py  # Session management
│   │   └── telemetry/
│   │       ├── __init__.py
│   │       └── setup.py         # OpenTelemetry config
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── ModelSelector.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── ErrorMessage.tsx
│   │   │   └── TypingIndicator.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 💻 Development

### Local Development (Without Docker)

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export OPENROUTER_API_KEY=your-key-here

# Run development server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Running Tests

```bash
# Backend tests (if added)
cd backend
pytest

# Frontend tests (if added)
cd frontend
npm test
```

## 🔧 Troubleshooting

### Common Issues

#### 1. "Connection refused" error

**Cause**: Backend or Jaeger not ready yet.

**Solution**: Wait a few seconds for services to start, or check logs:
```bash
docker-compose logs backend
```

#### 2. "API key not found" error

**Cause**: Missing or invalid OpenRouter API key.

**Solution**: 
1. Check `.env` file exists and contains valid key
2. Ensure no extra spaces or quotes around the key
3. Restart containers after updating `.env`

#### 3. "Model not found" error

**Cause**: Selected model may not be available.

**Solution**: Refresh the page to get updated model list.

#### 4. Frontend not loading

**Cause**: Frontend build failed.

**Solution**:
```bash
docker-compose logs frontend
docker-compose up --build frontend
```

#### 5. Traces not appearing in Jaeger

**Cause**: Jaeger not receiving traces.

**Solution**:
1. Ensure Jaeger is running: `docker-compose ps`
2. Check backend logs for telemetry errors
3. Wait a few seconds for traces to appear

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f jaeger
```

### Restarting Services

```bash
# Restart specific service
docker-compose restart backend

# Rebuild and restart
docker-compose up --build -d backend
```

## 📄 License

This project is for demonstration purposes.

---

**Built with ❤️ using FastAPI, React, and OpenTelemetry**
