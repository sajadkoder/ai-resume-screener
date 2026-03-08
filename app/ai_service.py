import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_key_here":
    raise ValueError("GROQ_API_KEY is not set in .env file")

client = Groq(api_key=GROQ_API_KEY)


def screen_resume(job_description: str, resume_text: str) -> dict:
    if not job_description or not job_description.strip():
        raise ValueError("Job description cannot be empty")
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text cannot be empty")
    
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": f"""
Analyze this resume against the job description.
Job Description: {job_description}
Resume: {resume_text}
Respond ONLY in valid JSON with no extra text or markdown:
{{"score": <0-100>, "match_level": "<Strong|Moderate|Weak>", "feedback": "<3-4 sentences>"}}
""",
            }
        ],
        temperature=0.3,
        max_tokens=500,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "score": 50.0,
            "match_level": "Moderate",
            "feedback": "Unable to parse AI response. Please try again."
        }

    if "score" in result:
        score = float(result["score"])
        result["score"] = max(0.0, min(100.0, score))
        if result["score"] >= 75:
            result["match_level"] = "Strong"
        elif result["score"] >= 50:
            result["match_level"] = "Moderate"
        else:
            result["match_level"] = "Weak"

    return result
