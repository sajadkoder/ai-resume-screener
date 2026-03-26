# AI Resume Screener API

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-00.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/sajadkoder/ai-resume-screener?style=social)](https://github.com/sajadkoder/ai-resume-screener/stargazers)

A FastAPI-based REST API that uses AI to screen resumes against job descriptions. The API leverages Groq's free LLM (llama-3.1-8b-instant) to analyze resumes and provide match scores, levels, and feedback.

## Features

- 🤖 **AI-Powered Screening** - Uses Groq's LLM to analyze resume-job description matches
- 🔐 **JWT Authentication** - Secure user registration and login with JWT tokens
- 📊 **Screening History** - Track all your resume screenings with pagination
- 📈 **Statistics** - View match level distribution and average scores
- 👥 **User Management** - Admin role for managing users and viewing all data
- 💾 **SQLite Database** - Lightweight, persistent storage with SQLAlchemy
- 📚 **Interactive Docs** - Swagger UI for easy API exploration

## Demo Video

![API Demo](Screen%20Recording%202026-03-25%20221338.mp4)

## Screenshots

### Swagger UI - API Documentation
![Swagger UI](Screenshot%202026-03-26%20011724.png)

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

### Quick Start
```bash
# Clone and setup
git clone https://github.com/sajadkoder/ai-resume-screener.git
cd ai-resume-screener-api

# Install dependencies
pip install -r requirements.txt

# Add your Groq API key in .env file

# Run the server
uvicorn app.main:app --reload
```

### 1. Clone the repository
```bash
git clone https://github.com/sajadkoder/ai-resume-screener.git
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
Get all screenings (admin only). Supports pagination with `skip` and `limit` params.

**Query Parameters:**
- `skip` (int, default=0): Number of records to skip
- `limit` (int, default=10, max=100): Number of records to return
- `match_level` (string, optional): Filter by "Strong", "Moderate", or "Weak"

**Headers:**
```
Authorization: Bearer <admin_jwt_token>
```

#### GET /screen/{screening_id}
Get a specific screening by ID (owner or admin only).

#### GET /screen/stats/me
Get current user's screening statistics.

**Response:**
```json
{
  "total_screenings": 15,
  "strong_matches": 5,
  "moderate_matches": 7,
  "weak_matches": 3,
  "average_score": 62.5
}
```

#### GET /screen/stats/all
Get overall statistics (admin only).

**Response:**
```json
{
  "total_screenings": 150,
  "total_users": 25,
  "strong_matches": 45,
  "moderate_matches": 70,
  "weak_matches": 35,
  "average_score": 58.3
}
```

#### DELETE /screen/{screening_id}
Delete a screening (owner or admin only).

### Users

#### GET /users/me
Get current user's profile.

**Response:**
```json
{
  "id": 1,
  "username": "johndoe",
  "role": "user"
}
```

#### GET /users/
List all users (admin only).

#### PATCH /users/{user_id}/role
Update a user's role (admin only).

**Request Body:**
```json
{
  "role": "admin"
}
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
- To make a user admin, use `PATCH /users/{user_id}/role` with role="admin"
- Groq offers free API access with generous limits - perfect for development and testing
- All endpoints support pagination (skip/limit) for better performance
- Filter screenings by match_level (Strong/Moderate/Weak) on history and all endpoints

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
