# Smart Job Application Tracker

A full-stack, cloud-native application to manage and analyze job applications,
built as a learning project covering Python, FastAPI, AWS, and DevOps.

## Status
🚧 Under active development — currently in Phase 1 (local backend setup).

## Tech Stack (planned)
- **Frontend:** React
- **Backend:** Python, FastAPI
- **Cloud:** AWS (Lambda, API Gateway, DynamoDB, Cognito, S3, EventBridge, SNS, Bedrock)
- **DevOps:** Docker, Terraform, GitHub Actions

## Local Setup (Backend)
\`\`\`bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
\`\`\`

Visit http://127.0.0.1:8000/docs for the interactive API docs.

## Roadmap
- [x] Phase 1: Local FastAPI setup
- [ ] Phase 2: Backend CRUD (in-memory storage)
- [ ] Phase 3: DynamoDB integration
- [ ] Phase 4: AWS Lambda
- [ ] Phase 5: API Gateway
- [ ] Phase 6: Cognito authentication
- [ ] ... (see full roadmap as project progresses)