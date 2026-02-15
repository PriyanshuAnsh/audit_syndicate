"use client";

import { CheckCircle, Clock } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import Nav from "../../components/nav";
import { api } from "../../lib/api";

type Lesson = {
  id: number;
  title: string;
  body: string;
  quiz: { id: string; question: string; options: string[] }[];
  question_count: number;
  reward_xp: number;
  reward_coins: number;
  completed: boolean;
  score: number | null;
};

type LessonListResponse = {
  items: Lesson[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
};

function randomKey() {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export default function LearnPage() {
  const qc = useQueryClient();
  const [page, setPage] = useState(1);
  const lessons = useQuery<LessonListResponse>({
    queryKey: ["lessons", page],
    queryFn: () => api(`/lessons?page=${page}&page_size=6`),
  });

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [checkedCorrect, setCheckedCorrect] = useState<Record<string, boolean>>(
    {},
  );
  const [questionIndex, setQuestionIndex] = useState(0);
  const [slideKey, setSlideKey] = useState(0);
  const [feedback, setFeedback] = useState<{
    status: "correct" | "wrong";
    text: string;
  } | null>(null);

  useEffect(() => {
    if (
      (!selectedId ||
        !(lessons.data?.items || []).some((l) => l.id === selectedId)) &&
      lessons.data &&
      lessons.data.items.length > 0
    ) {
      setSelectedId(lessons.data.items[0].id);
      setQuestionIndex(0);
      setAnswers({});
      setCheckedCorrect({});
      setFeedback(null);
    }
  }, [lessons.data, selectedId]);

  const selectedLesson = useMemo(
    () =>
      (lessons.data?.items || []).find((lesson) => lesson.id === selectedId),
    [lessons.data, selectedId],
  );

  const currentQuestion = selectedLesson?.quiz[questionIndex] ?? null;
  const answeredCount = selectedLesson
    ? selectedLesson.quiz.filter((q) => Boolean(answers[q.id])).length
    : 0;
  const allChecked = selectedLesson
    ? selectedLesson.quiz.every((q) => checkedCorrect[q.id])
    : false;
  const completionPct =
    selectedLesson && selectedLesson.quiz.length > 0
      ? Math.round(
          (Object.keys(checkedCorrect).length / selectedLesson.quiz.length) *
            100,
        )
      : 0;

  const checkAnswer = useMutation({
    mutationFn: () =>
      api(`/lessons/${selectedId}/check-answer`, {
        method: "POST",
        body: JSON.stringify({
          question_id: currentQuestion?.id,
          answer: currentQuestion ? answers[currentQuestion.id] : "",
        }),
      }),
    onSuccess: (data) => {
      if (data.correct) {
        setCheckedCorrect((prev) => ({ ...prev, [data.question_id]: true }));
        setFeedback({ status: "correct", text: "Correct! Great job." });
        if (selectedLesson && questionIndex < selectedLesson.quiz.length - 1) {
          setTimeout(() => {
            setQuestionIndex((idx) => idx + 1);
            setSlideKey((k) => k + 1);
            setFeedback(null);
          }, 650);
        }
      } else {
        setFeedback({
          status: "wrong",
          text: `Not quite. Correct answer: ${data.correct_answer}`,
        });
      }
    },
  });

  const submit = useMutation({
    mutationFn: () =>
      api(`/lessons/${selectedId}/submit`, {
        method: "POST",
        body: JSON.stringify({ answers, idempotency_key: randomKey() }),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["lessons", page] });
      qc.invalidateQueries({ queryKey: ["me"] });
    },
  });

  return (
    <div className="space-y-4">
      <Nav />
      <div className="glass p-5">
        <h1 className="page-title">Learn Hub</h1>
        <p className="page-subtitle">
          One question at a time. Check answers, then move forward with
          confidence.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <section className="glass p-4">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Lessons</h2>
            <span className="text-xs text-slate-600">
              {(lessons.data?.items || []).filter((l) => l.completed).length}/
              {(lessons.data?.items || []).length} completed
            </span>
          </div>
          <ul className="space-y-2">
            {(lessons.data?.items || []).map((lesson) => {
              const active = lesson.id === selectedId;
              return (
                <li key={lesson.id}>
                  <button
                    className={`w-full rounded-xl border p-3 text-left transition ${active ? "border-emerald-500 bg-emerald-50" : "border-slate-200 bg-white/80 hover:bg-white"}`}
                    onClick={() => {
                      setSelectedId(lesson.id);
                      setAnswers({});
                      setCheckedCorrect({});
                      setQuestionIndex(0);
                      setSlideKey((k) => k + 1);
                      setFeedback(null);
                      checkAnswer.reset();
                      submit.reset();
                    }}
                  >
                    <div className="mb-1 flex items-center justify-between gap-2">
                      <span className="font-semibold">{lesson.title}</span>

                      {lesson.completed ? (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      ) : (
                        <Clock className="h-5 w-5 text-slate-400" />
                      )}
                    </div>
                    <p className="text-xs text-slate-600">
                      {lesson.question_count} questions • +{lesson.reward_xp} XP
                      • +{lesson.reward_coins} coins
                    </p>
                    {lesson.score !== null && (
                      <p className="mt-1 text-xs font-medium text-slate-700">
                        Last score: {lesson.score}%
                      </p>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
          <div className="mt-4 flex items-center justify-between rounded-xl border border-slate-200 bg-white/80 p-2">
            <button
              className="btn-secondary !px-3 !py-1.5 text-sm disabled:opacity-50"
              disabled={(lessons.data?.page || 1) <= 1}
              onClick={() => {
                setPage((prev) => Math.max(1, prev - 1));
                setAnswers({});
                setCheckedCorrect({});
                setQuestionIndex(0);
                setFeedback(null);
              }}
            >
              Prev
            </button>
            <span className="text-xs text-slate-600">
              Page {lessons.data?.page || 1} / {lessons.data?.total_pages || 1}
            </span>
            <button
              className="btn-secondary !px-3 !py-1.5 text-sm disabled:opacity-50"
              disabled={
                (lessons.data?.page || 1) >= (lessons.data?.total_pages || 1)
              }
              onClick={() => {
                setPage((prev) => prev + 1);
                setAnswers({});
                setCheckedCorrect({});
                setQuestionIndex(0);
                setFeedback(null);
              }}
            >
              Next
            </button>
          </div>
        </section>

        {selectedLesson && currentQuestion && (
          <section className="glass p-4">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">
                  {selectedLesson.title}
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  {selectedLesson.body}
                </p>
              </div>
              <div className="rounded-xl bg-white/80 px-3 py-2 text-xs">
                <p>
                  Reward: +{selectedLesson.reward_xp} XP • +
                  {selectedLesson.reward_coins} coins
                </p>
              </div>
            </div>

            <div className="mb-4 rounded-xl bg-white/80 p-3">
              <div className="mb-1 flex items-center justify-between text-xs text-slate-600">
                <span>Quiz progress</span>
                <span>
                  {Object.keys(checkedCorrect).length}/
                  {selectedLesson.quiz.length} checked
                </span>
              </div>
              <div className="h-2 rounded-full bg-slate-200">
                <div
                  className="h-2 rounded-full bg-emerald-600 transition-all"
                  style={{ width: `${completionPct}%` }}
                />
              </div>
              <p className="mt-2 text-xs text-slate-600">
                Question {questionIndex + 1} of {selectedLesson.quiz.length} •{" "}
                {answeredCount} answered
              </p>
            </div>

            <div
              key={`${currentQuestion.id}-${slideKey}`}
              className={`learn-question-card ${feedback?.status === "correct" ? "learn-correct-pop" : "learn-slide-right"}`}
            >
              <p className="text-base font-medium">
                Q{questionIndex + 1}. {currentQuestion.question}
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {currentQuestion.options.map((option) => (
                  <button
                    key={option}
                    className={
                      answers[currentQuestion.id] === option
                        ? "btn-primary !px-3 !py-1.5 text-sm"
                        : "btn-secondary !px-3 !py-1.5 text-sm"
                    }
                    onClick={() => {
                      setAnswers((prev) => ({
                        ...prev,
                        [currentQuestion.id]: option,
                      }));
                      setFeedback(null);
                    }}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
              <button
                className="btn-secondary"
                onClick={() => {
                  if (questionIndex > 0) {
                    setQuestionIndex((idx) => idx - 1);
                    setSlideKey((k) => k + 1);
                    setFeedback(null);
                  }
                }}
                disabled={questionIndex <= 0}
              >
                Previous Question
              </button>
              <button
                className="btn-primary"
                onClick={() => checkAnswer.mutate()}
                disabled={
                  !answers[currentQuestion.id] ||
                  checkAnswer.isPending ||
                  checkedCorrect[currentQuestion.id]
                }
              >
                {checkedCorrect[currentQuestion.id]
                  ? "Checked"
                  : checkAnswer.isPending
                    ? "Checking..."
                    : "Check Answer"}
              </button>
              <button
                className="btn-secondary"
                onClick={() => {
                  if (questionIndex < selectedLesson.quiz.length - 1) {
                    setQuestionIndex((idx) => idx + 1);
                    setSlideKey((k) => k + 1);
                    setFeedback(null);
                  }
                }}
                disabled={questionIndex >= selectedLesson.quiz.length - 1}
              >
                Next Question
              </button>
            </div>

            {feedback?.status === "correct" && (
              <p className="mt-3 text-center text-sm font-semibold text-emerald-700">
                ✅ {feedback.text}
              </p>
            )}
            {feedback?.status === "wrong" && (
              <p className="mt-3 text-center text-sm font-semibold text-rose-700">
                ❌ {feedback.text}
              </p>
            )}

            <div className="mt-5 border-t border-slate-200/70 pt-5 text-center">
              <button
                className="btn-primary"
                onClick={() => submit.mutate()}
                disabled={!allChecked || submit.isPending}
              >
                {submit.isPending ? "Submitting..." : "Submit Lesson"}
              </button>
              {!allChecked && (
                <p className="mx-auto mt-2 max-w-md text-sm text-slate-600">
                  Check all 10 questions before submitting lesson.
                </p>
              )}
              {submit.data && (
                <p className="mt-3 text-sm font-semibold text-emerald-700">
                  Completed. Score: {submit.data.score}%
                </p>
              )}
              {submit.error && (
                <p className="mt-3 text-sm font-semibold text-red-700">
                  {(submit.error as Error).message}
                </p>
              )}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
