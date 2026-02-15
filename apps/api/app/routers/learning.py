from datetime import datetime, UTC
import hashlib
import random

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..deps import current_user
from ..models import Lesson, LessonProgress, LessonQuestion, User
from ..schemas import LessonCheckRequest, LessonListOut, LessonOut, LessonSubmitRequest
from ..services import grant_reward


router = APIRouter(prefix="/lessons", tags=["learning"])


def _selected_quiz_for_user(user_id: int, lesson_id: int, quiz_pool: list[dict], sample_size: int = 10) -> list[dict]:
    if len(quiz_pool) <= sample_size:
        return quiz_pool
    seed_material = f"{user_id}:{lesson_id}".encode()
    seed = int(hashlib.sha256(seed_material).hexdigest()[:16], 16)
    rng = random.Random(seed)
    return rng.sample(quiz_pool, sample_size)


@router.get("", response_model=LessonListOut)
def list_lessons(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=6, ge=1, le=50),
):
    total = db.query(Lesson).count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    if page > total_pages:
        page = total_pages
    offset = (page - 1) * page_size
    lessons = db.query(Lesson).order_by(Lesson.id.asc()).offset(offset).limit(page_size).all()
    out = []
    for lesson in lessons:
        quiz_pool = [
            {"id": row.question_key, "question": row.question_text, "options": row.options_json, "answer": row.answer}
            for row in db.query(LessonQuestion).filter(LessonQuestion.lesson_id == lesson.id).order_by(LessonQuestion.id.asc()).all()
        ]
        selected_quiz = _selected_quiz_for_user(user.id, lesson.id, quiz_pool)
        progress = (
            db.query(LessonProgress)
            .filter(LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson.id)
            .first()
        )
        out.append(
            {
                "id": lesson.id,
                "title": lesson.title,
                "body": lesson.body,
                "quiz": [
                    {"id": q["id"], "question": q["question"], "options": q["options"]}
                    for q in selected_quiz
                ],
                "question_count": len(selected_quiz),
                "reward_xp": lesson.reward_xp,
                "reward_coins": lesson.reward_coins,
                "completed": bool(progress and progress.status == "completed"),
                "score": None if not progress else progress.score,
            }
        )
    return {
        "items": out,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }


@router.get("/{lesson_id}", response_model=LessonOut)
def get_lesson(lesson_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="lesson not found")
    quiz_pool = [
        {"id": row.question_key, "question": row.question_text, "options": row.options_json, "answer": row.answer}
        for row in db.query(LessonQuestion).filter(LessonQuestion.lesson_id == lesson.id).order_by(LessonQuestion.id.asc()).all()
    ]
    selected_quiz = _selected_quiz_for_user(user.id, lesson.id, quiz_pool)

    progress = (
        db.query(LessonProgress)
        .filter(LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson.id)
        .first()
    )
    return {
        "id": lesson.id,
        "title": lesson.title,
        "body": lesson.body,
        "quiz": [{"id": q["id"], "question": q["question"], "options": q["options"]} for q in selected_quiz],
        "question_count": len(selected_quiz),
        "reward_xp": lesson.reward_xp,
        "reward_coins": lesson.reward_coins,
        "completed": bool(progress and progress.status == "completed"),
        "score": None if not progress else progress.score,
    }


@router.post("/{lesson_id}/submit")
def submit_lesson(
    lesson_id: int,
    payload: LessonSubmitRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="lesson not found")
    quiz_pool = [
        {"id": row.question_key, "question": row.question_text, "options": row.options_json, "answer": row.answer}
        for row in db.query(LessonQuestion).filter(LessonQuestion.lesson_id == lesson.id).order_by(LessonQuestion.id.asc()).all()
    ]
    selected_quiz = _selected_quiz_for_user(user.id, lesson.id, quiz_pool)

    progress = (
        db.query(LessonProgress)
        .filter(LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson.id)
        .first()
    )
    if not progress:
        progress = LessonProgress(user_id=user.id, lesson_id=lesson.id)
        db.add(progress)

    correct = 0
    for q in selected_quiz:
        if payload.answers.get(q["id"]) == q["answer"]:
            correct += 1
    score = round((correct / max(1, len(selected_quiz))) * 100, 2)

    progress.status = "completed"
    progress.score = score
    progress.completed_at = datetime.now(UTC).replace(tzinfo=None)

    grant_reward(
        db,
        user.id,
        "lesson_completion",
        settings.reward_lesson_complete_xp,
        settings.reward_lesson_complete_coins,
        "lesson",
        f"{lesson.id}:{payload.idempotency_key}",
    )
    if score == 100.0:
        grant_reward(
            db,
            user.id,
            "quiz_perfect",
            settings.reward_quiz_perfect_xp,
            settings.reward_quiz_perfect_coins,
            "lesson_perfect",
            f"{lesson.id}:{payload.idempotency_key}",
        )
    db.commit()
    return {"completed": True, "score": score}


@router.post("/{lesson_id}/check-answer")
def check_answer(
    lesson_id: int,
    payload: LessonCheckRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="lesson not found")
    quiz_pool = [
        {"id": row.question_key, "question": row.question_text, "options": row.options_json, "answer": row.answer}
        for row in db.query(LessonQuestion).filter(LessonQuestion.lesson_id == lesson.id).order_by(LessonQuestion.id.asc()).all()
    ]
    selected_quiz = _selected_quiz_for_user(user.id, lesson.id, quiz_pool)
    question = next((q for q in selected_quiz if q["id"] == payload.question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="question not found for this lesson set")

    is_correct = payload.answer == question["answer"]
    return {
        "question_id": payload.question_id,
        "correct": is_correct,
        "correct_answer": question["answer"] if not is_correct else payload.answer,
    }
