from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..deps import current_user
from ..models import Lesson, LessonProgress, User, Pet
from ..schemas import LessonOut, LessonSubmitRequest
from ..services import grant_reward


router = APIRouter(prefix="/lessons", tags=["learning"])


@router.get("", response_model=list[LessonOut])
def list_lessons(user: User = Depends(current_user), db: Session = Depends(get_db)):
    lessons = db.query(Lesson).order_by(Lesson.id.asc()).all()
    out = []
    for lesson in lessons:
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
                    for q in lesson.quiz_json
                ],
                "completed": bool(progress and progress.status == "completed"),
                "score": None if not progress else progress.score,
            }
        )
    return out


@router.get("/{lesson_id}", response_model=LessonOut)
def get_lesson(lesson_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="lesson not found")

    progress = (
        db.query(LessonProgress)
        .filter(LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson.id)
        .first()
    )
    return {
        "id": lesson.id,
        "title": lesson.title,
        "body": lesson.body,
        "quiz": [{"id": q["id"], "question": q["question"], "options": q["options"]} for q in lesson.quiz_json],
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

    progress = (
        db.query(LessonProgress)
        .filter(LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson.id)
        .first()
    )
    if not progress:
        progress = LessonProgress(user_id=user.id, lesson_id=lesson.id)
        db.add(progress)

    correct = 0
    for q in lesson.quiz_json:
        if payload.answers.get(q["id"]) == q["answer"]:
            correct += 1
    score = round((correct / max(1, len(lesson.quiz_json))) * 100, 2)

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
    pet = db.query(Pet).filter(Pet.user_id == user.id).first()

    if pet and score >= 60:
        HUNGER_RESTORE = 20
        pet.hunger = min(100, pet.hunger + HUNGER_RESTORE)
    
    db.commit()
    return {"completed": True, "score": score}
