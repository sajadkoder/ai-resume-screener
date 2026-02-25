# AI Resume Screener API

A FastAPI-based REST API that uses AI to screen resumes against job descriptions. The API leverages Groq's free LLM (llama3-8b-8192) to analyze resumes and provide match scores, levels, and feedback.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL ORM with SQLite database
- **python-jose** - JWT token handling
- **passlib[bcrypt]** - Password hashing
- **groq** - Groq Python SDK for AI
- **python-dotenv** - Environment variable management
- **pydantic** - Data validation
- **uvicorn** - ASGI server

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd ai-resume-screener-api
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Edit the `.env` file and add your values:

```env
SECRET_KEY=your_secret_key_here_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GROQ_API_KEY=your_groq_key_here
```

### 4. Get a free Groq API key

1. Go to [groq.com](https://groq.com)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy it to your `.env` file

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 6. Access Swagger documentation

Open your browser and visit: `http://localhost:8000/docs`

You will see the interactive Swagger UI where you can test all endpoints.

## API Endpoints

### Authentication

#### POST /auth/register
Register a new user.

**Request:**
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response (201):**
```json
{
  "id": 1,
  "username": "johndoe",
  "role": "user"
}
```

#### POST /auth/login
Login and receive JWT token.

**Request (form-data):**
```
username=johndoe
password=securepassword123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Screenings

#### POST /screen/
Screen a resume against a job description (requires authentication).

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Request:**
```json
{
  "job_description": "We are looking for a Python developer with experience in FastAPI and SQLAlchemy.",
  "resume_text": "John Doe is a Python developer with 5 years of experience. He has worked extensively with FastAPI and SQLAlchemy."
}
```

**Response (201):**
```json
{
  "id": 1,
  "user_id": 1,
  "job_description": "We are looking for a Python developer...",
  "resume_text": "John Doe is a Python developer...",
  "score": 85.5,
  "feedback": "The candidate has strong Python skills and direct experience with the required frameworks. Their 5 years of experience aligns well with the position.",
  "match_level": "Strong",
  "created_at": "2024-01-15T10:30:00"
}
```

#### GET /screen/history
Get current user's screening history (requires authentication).

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "job_description": "We are looking for a Python developer...",
    "resume_text": "John Doe is a Python developer...",
    "score": 85.5,
    "feedback": "The candidate has strong Python skills...",
    "match_level": "Strong",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

#### GET /screen/all
Get all screenings (admin only).

**Headers:**
```
Authorization: Bearer <admin_jwt_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "job_description": "We are looking for a Python developer...",
    "resume_text": "John Doe is a Python developer...",
    "score": 85.5,
    "feedback": "The candidate has strong Python skills...",
    "match_level": "Strong",
    "created_at": "2024-01-15T10:30:00"
  },
  {
    "id": 2,
    "user_id": 2,
    "job_description": "We need a Java developer...",
    "resume_text": "Jane Smith is a Java developer...",
    "score": 45.0,
    "feedback": "The resume does not match...",
    "match_level": "Weak",
    "created_at": "2024-01-15T11:00:00"
  }
]
```

## Match Levels

- **Strong**: Score >= 75
- **Moderate**: Score >= 50 and < 75
- **Weak**: Score < 50

## Database Schema

### users
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| username | STRING | Unique username |
| hashed_password | STRING | Bcrypt hashed password |
| role | STRING | "user" or "admin" |

### screenings
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users |
| job_description | TEXT | Job description text |
| resume_text | TEXT | Resume text |
| score | FLOAT | Match score (0-100) |
| feedback | TEXT | AI-generated feedback |
| match_level | STRING | Strong/Moderate/Weak |
| created_at | DATETIME | Auto-generated timestamp |

## Notes

- The database (SQLite) is automatically created on first run
- JWT tokens expire after 30 minutes (configurable in .env)
- To create an admin user, manually update the `role` field in the database to "admin"
- Groq offers free API access with generous limits - perfect for development and testing
