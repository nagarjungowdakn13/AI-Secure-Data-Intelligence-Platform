# AI Secure Data Intelligence Platform Architecture

## High-level flow

```text
Input Layer
  |- Inline text / chat / SQL
  |- Multi-file upload (PDF, DOCX, TXT, LOG, SQL)
            |
            v
Validation Layer
  |- Request schema validation
  |- File type and extraction validation
            |
            v
Extraction Layer
  |- PDF text extraction
  |- DOCX text extraction
  |- Plain text normalization
            |
            v
Detection Engine
  |- Regex detector
  |- Lightweight NER-style contextual detector
  |- Log analyzer
            |
            v
Risk Engine
  |- Severity weighting
  |- Risk score normalization
  |- Risk level mapping
            |
            v
Policy Engine
  |- block_and_alert
  |- review_required
  |- allow_with_masking
  |- allow
            |
            v
Response Formatter
  |- Findings
  |- Risk badge data
  |- Masked content
  |- AI insights
```

## Service responsibilities

- `ExtractionService`: Converts uploaded PDF and DOCX documents into analyzable text.
- `RegexDetector`: Scans line by line for sensitive data, secrets, network indicators, and credential patterns.
- `LogAnalyzer`: Detects repeated failures, stack traces, and suspicious command-like behavior.
- `RiskEngine`: Aggregates detections into a normalized `risk_score` and `risk_level`.
- `PolicyEngine`: Chooses a response action based on risk level and runtime options.
- `AIService`: Uses an OpenAI-compatible API if configured, otherwise falls back to deterministic local insight generation.

## Deployment shape

- Frontend: React + Tailwind built with Vite.
- Backend: FastAPI with file upload and JSON analysis endpoints.
- Packaging: Single Docker image that builds the frontend and serves both API and static assets.
