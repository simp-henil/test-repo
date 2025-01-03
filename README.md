# 🚀 Pull Request Analysis Tool

## Overview

The **Pull Request Analysis Tool** is an intelligent platform that leverages AI to automate and enhance the review of
pull requests. It simplifies code analysis by identifying bugs, improving performance, and enforcing best practices,
seamlessly integrating with GitHub.

---

## Key Features

- **AI-Powered Insights**:
    - Detects potential bugs, code style inconsistencies, and performance improvements.
    - Provides actionable recommendations for best practices.

- **Asynchronous Processing**:
    - Uses **Celery** and **Redis** for efficient task management.

- **Seamless GitHub Integration**:
    - Fetches pull request details directly from GitHub.

- **Robust Database**:
    - Built on **PostgreSQL** with SQLModel for secure data management.

---

## Project Architecture

- **Backend Framework**: FastAPI
- **Task Queue**: Celery with Redis
- **Database**: PostgreSQL
- **AI Integration**: Google Generative AI for code analysis

### Directory Structure

```plaintext
📂 Project Root
├── 📁 models
│   ├── database_engine.py   # Database setup and management
│   ├── github_model.py      # ORM models for GitHub data
│   └── schemas.py           # API schemas using Pydantic
├── 📁 background_processor
│   └── pr_review_celery_job.py   # Celery task handlers
├── 📁 routes
│   └── routes.py            # FastAPI endpoint definitions
├── 📁 helper
│   └── helper.py            # Utility functions for GitHub integration
├── gemini_code.py           # AI model configuration and analysis logic
├── main.py                  # Application entry point
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

---

## Installation & Setup

### Prerequisites

- **Python**: Version 3.9+
- **Redis**: For task queuing
- **PostgreSQL**: For database management
- **GitHub Personal Access Token**: For API authentication

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory with the following content:
   ```plaintext
   GEMINI_API_KEY=<your-api-key>
   DATABASE_URL=postgresql://<username>:<password>@localhost/<db-name>
   ```

5. **Initialize the Database**:
   ```bash
   python main.py
   ```

6. **Start Redis**:
   ```bash
   redis-server
   ```

7. **Run Celery Worker**:
   ```bash
   celery -A background_processor.pr_review_celery_job worker --loglevel=info
   ```

8. **Launch the API Server**:
   ```bash
   uvicorn main:app --reload
   ```

---

## API Documentation

The API provides endpoints for analyzing pull requests and retrieving task results.

### Analyze a Pull Request

**Endpoint**: `POST /analyze-pr`

**Request Payload**:

```json
{
  "repo_url": "https://github.com/<owner>/<repo>",
  "pr_number": 123,
  "github_token": "your-github-token"
}
```

**Response**:

```json
{
  "task_id": "unique-task-id",
  "status": "PENDING"
}
```

### Fetch Task Status

**Endpoint**: `GET /status/{task_id}`

**Response**:

```json
{
  "task_id": "unique-task-id",
  "status": "SUCCESS",
  "result": {
    ...
  }
}
```

---

## Technology Stack

| **Category**   | **Technology**       |
|----------------|----------------------|
| **Framework**  | FastAPI              |
| **Task Queue** | Celery + Redis       |
| **Database**   | PostgreSQL, SQLModel |
| **AI**         | Google Generative AI |
| **Language**   | Python               |

---

## Contributing

We welcome contributions to enhance the tool further. Please follow these steps:

1. Fork the repository.
2. Create a feature branch.
3. Commit changes and open a pull request.

---

### Demo


https://github.com/user-attachments/assets/55bed1e3-18c9-440c-a978-ca787f919604



### Acknowledgements

- Built with ❤️ using [FastAPI](https://fastapi.tiangolo.com/) and [Google Generative AI](https://ai.google/tools/).

# Thank you
