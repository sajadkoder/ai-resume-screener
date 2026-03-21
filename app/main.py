from fastapi import FastAPI
from app.database import engine, Base
from app.routes import auth, screen, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Resume Screener API",
    description="A REST API that uses AI to screen resumes against job descriptions",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(screen.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"message": "AI Resume Screener API", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
