from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from explanation_module import explain_concept
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="EduGenie - Google Gemini Powered Learning Assistant",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


class TextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=20000,
    )


class QARequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )


class QuizRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=20000,
    )
    count: int = Field(
        default=3,
        ge=1,
        le=10,
    )


class LearningPathRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )
    level: Literal[
        "beginner",
        "intermediate",
        "advanced",
    ] = "beginner"
    weeks: int = Field(
        default=4,
        ge=1,
        le=24,
    )


def _handle(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
        },
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "EduGenie",
    }


@app.post("/qa")
async def qa(payload: QARequest):
    answer = _handle(
        answer_question,
        payload.question,
    )

    return {
        "answer": answer,
    }


@app.post("/explain")
async def explain(payload: TextRequest):
    explanation = _handle(
        explain_concept,
        payload.text,
    )

    return {
        "explanation": explanation,
    }


@app.post("/quiz")
async def quiz(payload: QuizRequest):
    quiz_data = _handle(
        generate_quiz,
        payload.text,
        payload.count,
    )

    return {
        "quiz": quiz_data,
    }


@app.post("/summarize")
async def summarize(payload: TextRequest):
    summary = _handle(
        summarize_text,
        payload.text,
    )

    return {
        "summary": summary,
    }


@app.post("/learn/recommendations")
async def learn(payload: LearningPathRequest):
    recommendations = _handle(
        get_learning_recommendations,
        payload.topic,
        payload.level,
        payload.weeks,
    )

    return {
        "recommendations": recommendations,
    }