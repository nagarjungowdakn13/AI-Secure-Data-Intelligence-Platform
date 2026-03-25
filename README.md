# AI Secure Data Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-API%20Layer-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=0b1220)
![AI Powered](https://img.shields.io/badge/AI-Powered-111827?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Risk%20Detection-B91C1C?style=for-the-badge)

AI Secure Data Intelligence Platform is a full-stack security analysis system that scans text and uploaded files for exposed sensitive data, secrets, suspicious patterns, and operational risk. It combines automated pattern detection, log analysis, masking, risk scoring, AI-generated insights, and deployment-ready configuration for modern frontend/backend hosting.

## Project Title

**AI Secure Data Intelligence Platform**

## Problem Statement

Organizations routinely move logs, reports, SQL snippets, documents, and chat content across teams and tools. These inputs often contain exposed credentials, sensitive identifiers, stack traces, and internal context that increase security risk. Manual review is slow, inconsistent, and difficult to scale during development, incident response, and audit workflows.

## Solution Overview

This project provides a unified AI-assisted security scanning platform that:

- Ingests inline text, chat, SQL, logs, and uploaded documents
- Detects secrets and sensitive data with regex-based scanning
- Analyzes logs line by line for anomalies and suspicious activity
- Applies masking to reduce accidental exposure during review
- Generates AI-supported summaries and risk explanations
- Produces a structured response with findings, risk score, risk level, remediation recommendations, and recommended action

## Architecture

```text
Input Layer
  -> Validation Layer
  -> Extraction Layer
  -> Detection Engine
       -> Regex Detector
       -> AI Detector
       -> Log Analyzer
  -> Risk Engine
  -> Policy Engine
  -> Response Formatter
```

### Architecture Diagram Explanation

- **Input Layer** accepts text, chat, SQL, logs, and multi-file uploads.
- **Validation Layer** enforces request schema rules and supported file types.
- **Extraction Layer** converts PDF and DOCX documents into plain text for scanning.
- **Detection Engine** combines regex-based detection, contextual entity detection, heuristic secret discovery, and log analysis.
- **Risk Engine** converts findings into a normalized score, severity breakdown, and remediation recommendations.
- **Policy Engine** determines the response action such as `allow`, `review_required`, or `block_and_alert`.
- **Response Formatter** returns analyst-friendly findings, masked content, AI insights, and recommended next steps to the frontend or API client.

Detailed notes are available in [docs/architecture.md](docs/architecture.md).

## Features

- Multi-input analysis for text, chat, SQL, logs, PDF, DOCX, and TXT
- Multi-file drag-and-drop upload workflow
- Detection of emails, phone numbers, API keys, passwords, tokens, secret keys, client secrets, connection strings, credit cards, IP addresses, and private keys
- Heuristic high-entropy secret detection for secret-like values
- Log anomaly detection for stack traces, repeated failures, and suspicious command patterns
- Risk scoring with severity mapping, breakdown, and remediation recommendations
- Masking engine for safer analyst review
- OpenAI-compatible AI service wrapper with fallback local insight generation
- Vercel-compatible frontend deployment and Render-compatible backend deployment

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Python, FastAPI, Pydantic |
| AI Layer | OpenAI-compatible API wrapper, HTTPX |
| Detection | Regex engine, contextual entity matching, heuristic secret detection, log analysis |
| Extraction | PyPDF, python-docx |
| Frontend | React, Vite, Tailwind CSS |
| Deployment | Render, Vercel, Docker |
| Storage | Local file processing, no database required |

## Project Structure

```text
backend/
  main.py
  Dockerfile
  api/
    routes.py
  models/
    request_model.py
    response_model.py
  services/
    ai_service.py
    extraction_service.py
    log_analyzer.py
    masking_service.py
    policy_engine.py
    regex_detector.py
    risk_engine.py
frontend/
  src/
    App.jsx
    components/
      UploadBox.jsx
      ResultPanel.jsx
      LogViewer.jsx
      InsightsPanel.jsx
docs/
  architecture.md
  demo_script.md
tests/
  sample_logs.log
  test_cases.json
main.py
render.yaml
vercel.json
README.md
Dockerfile
requirements.txt
.env.example
```

## API Documentation

### `POST /analyze`

Analyzes inline content such as text, chat, SQL, or log input.

**Request**

```json
{
  "input_type": "log",
  "content": "2026-03-10 INFO login\nemail=admin@company.com\npassword=admin123\napi_key=sk-test-xyzABC12345\nERROR stack trace: null pointer",
  "options": {
    "mask": true,
    "block_high_risk": true,
    "log_analysis": true
  }
}
```

**Response**

```json
{
  "summary": "Analyzed log content and found notable indicators.",
  "content_type": "log",
  "findings": [],
  "risk_score": 100,
  "risk_level": "critical",
  "action": "block_and_alert",
  "risk_breakdown": {
    "critical": 1,
    "high": 1,
    "medium": 1,
    "low": 1
  },
  "recommendations": [
    "Rotate exposed credentials immediately and invalidate any active sessions or tokens."
  ],
  "insights": [
    {
      "title": "Risk Explanation",
      "detail": "Credentials and stack traces were detected in the submitted log data."
    }
  ],
  "masked_content": "2026-03-10 INFO login\nemail=************\npassword=********\napi_key=************\nERROR stack trace: null pointer",
  "source_name": "inline-input"
}
```

### `POST /analyze/files`

Analyzes one or more uploaded files using multipart form data.

**Form fields**

- `files`: one or more `.pdf`, `.docx`, `.txt`, `.log`, or `.sql` files
- `mask`: boolean
- `block_high_risk`: boolean
- `log_analysis`: boolean

### `GET /health`

Returns service health status and environment metadata.

## How It Works

1. The client submits inline content or uploads one or more supported files.
2. The backend validates the request and extracts text from document formats when needed.
3. The detection engine scans the content for sensitive data, secrets, and suspicious log behavior.
4. The risk engine calculates a risk score, assigns a risk level, and generates remediation guidance.
5. The policy engine selects the recommended action based on severity and request options.
6. The AI layer generates a concise summary, anomaly insight, and risk explanation.
7. The frontend renders findings, severity breakdown, recommendations, highlighted content, and insight cards.

## Setup Instructions

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

By default:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Deployment Instructions

### Environment variables

Create a `.env` file from `.env.example` and configure:

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=20
APP_ENV=production
FRONTEND_URL=https://your-frontend.vercel.app
CORS_ORIGINS=https://your-frontend.vercel.app
VITE_API_BASE_URL=https://your-render-service.onrender.com
```

### Frontend deployment on Vercel

1. Push the repository to GitHub.
2. Create a new Vercel project connected to the repository.
3. Keep the root directory as the repository root, or set the project root to `frontend` if preferred.
4. Vercel will use the compatible configuration in [vercel.json](vercel.json).
5. Set `VITE_API_BASE_URL` in the Vercel project environment variables to your Render backend URL.
6. Deploy. Vercel will build the frontend using:

```bash
npm install
npm run build
```

### Backend deployment on Render

1. Create a new Web Service on Render from the same repository.
2. Use the configuration in [render.yaml](render.yaml), or manually set:

```bash
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port 10000
```

3. Set environment variables in Render:
   - `OPENAI_API_KEY`
   - `APP_ENV=production`
   - `FRONTEND_URL=https://your-frontend.vercel.app`
   - `CORS_ORIGINS=https://your-frontend.vercel.app`
4. Deploy and confirm `https://your-render-service.onrender.com/health` responds successfully.

### Backend Docker deployment

Use the backend-only container definition in [backend/Dockerfile](backend/Dockerfile):

```bash
docker build -f backend/Dockerfile -t ai-secure-data-intelligence-platform-api .
docker run -p 10000:10000 --env-file .env ai-secure-data-intelligence-platform-api
```

## Screenshots Placeholders

- Dashboard view: `docs/screenshots/dashboard-placeholder.png`
- Analysis results view: `docs/screenshots/results-placeholder.png`

## Future Improvements

- Add user authentication and role-based access control
- Introduce policy rules for tenant-specific compliance workflows
- Expand file support to CSV and JSON
- Add asynchronous batch processing for large uploads
- Integrate persistent audit logging and reporting
- Add SIEM and alerting integrations for enterprise workflows

## Security Considerations

- Sensitive values are masked before analyst review when masking is enabled
- Risk scoring distinguishes between low, medium, high, and critical findings
- High-risk and critical outputs can be blocked through policy decisions
- CORS is enabled and can be restricted through `FRONTEND_URL` or `CORS_ORIGINS`
- The AI layer is provider-configurable through an OpenAI-compatible interface
- Production deployment should secure secrets with environment management and place the service behind HTTPS

## Additional Resources

- Architecture notes: [docs/architecture.md](docs/architecture.md)
- Demo script: [docs/demo_script.md](docs/demo_script.md)
- Sample log input: [tests/sample_logs.log](tests/sample_logs.log)
- Test cases: [tests/test_cases.json](tests/test_cases.json)

## Advanced Features

- Real-time log streaming analysis through `POST /analyze/stream` using Server-Sent Events
- Cross-log anomaly detection and correlation through `POST /analyze/files/correlate`
- Correlation across repeated credentials, failures, stack traces, and shared indicators
- In-memory rate limiting for repeated and large log uploads
- Efficient chunk-based processing for large log content with processing metadata in responses

### Advanced Endpoints

#### `POST /analyze/stream`

Streams chunk-level analysis events for large inline log payloads and ends with a final `complete` event containing the full response payload.

#### `POST /analyze/files/correlate`

Analyzes multiple uploaded log sources and returns:

- per-file analysis results
- cross-log correlation insights
- aggregate source and finding counts
