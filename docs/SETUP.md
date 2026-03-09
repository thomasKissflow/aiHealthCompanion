# AI Health Companion - Setup Guide

## Project Structure

```
bharatAI_MVP/
├── backend/          # Python FastAPI backend
│   └── venv/        # Python virtual environment
├── frontend/        # React frontend
├── docs/            # Documentation
├── .env             # Local environment variables (not committed)
├── .env.example     # Example environment variables
└── .gitignore       # Git ignore rules
```

## Environment Setup

### Backend Setup

1. Activate the virtual environment:
   ```bash
   source backend/venv/bin/activate  # On macOS/Linux
   # or
   backend\venv\Scripts\activate     # On Windows
   ```

2. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your AWS credentials and API keys

### Environment Variables

Required environment variables (see `.env.example`):

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_REGION`: AWS region (default: us-east-1)
- `OPENAI_API_KEY`: OpenAI API key for Bedrock
- `OPENAI_BASE_URL`: Bedrock endpoint URL
- `ENVIRONMENT`: Application environment (development/production)
- `LOG_LEVEL`: Logging level (INFO/DEBUG/WARNING/ERROR)

## Next Steps

1. Install Python dependencies (see Task 2.1)
2. Set up frontend React application (see Task 19)
3. Configure AWS services (Transcribe, Polly, Bedrock)
