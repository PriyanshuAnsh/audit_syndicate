"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import Nav from "../../components/nav";
import { api } from "../../lib/api";

function randomKey() {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export default function LearnPage() {
  const qc = useQueryClient();
  const lessons = useQuery({ queryKey: ["lessons"], queryFn: () => api("/lessons") });
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const selectedLesson = useMemo(
    () => (lessons.data || []).find((lesson: any) => lesson.id === selectedId),
    [lessons.data, selectedId]
  );

  const submit = useMutation({
    mutationFn: () =>
      api(`/lessons/${selectedId}/submit`, {
        method: "POST",
        body: JSON.stringify({ answers, idempotency_key: randomKey() }),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["lessons"] });
      qc.invalidateQueries({ queryKey: ["me"] });
    },
  });

  return (
    <div className="space-y-4">
      <Nav />
      <div className="glass p-5">
        <h1 className="page-title">Learn</h1>
        <p className="page-subtitle">Short, practical lessons to build safe investing habits.</p>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <ul className="space-y-2">
          {(lessons.data || []).map((lesson: any) => (
            <li key={lesson.id}>
              <button
                className="glass w-full p-4 text-left transition hover:-translate-y-[1px]"
                onClick={() => {
                  setSelectedId(lesson.id);
                  setAnswers({});
                }}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold">{lesson.title}</span>
                  <span className="text-sm">{lesson.completed ? "✅" : "⏳"}</span>
                </div>
              </button>
            </li>
          ))}
        </ul>
        {selectedLesson && (
          <div className="glass p-4">
            <h2 className="text-lg font-semibold">{selectedLesson.title}</h2>
            <p className="mb-3 mt-1 text-sm text-slate-600">{selectedLesson.body}</p>
            {selectedLesson.quiz.map((q: any) => (
              <div key={q.id} className="mb-3 rounded-xl bg-white/75 p-3">
                <p className="text-sm font-medium">{q.question}</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {q.options.map((option: string) => (
                    <button
                      key={option}
                      className={answers[q.id] === option ? "btn-primary !px-3 !py-1 text-sm" : "btn-secondary !px-3 !py-1 text-sm"}
                      onClick={() => setAnswers((prev) => ({ ...prev, [q.id]: option }))}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              </div>
            ))}
            <button className="btn-primary" onClick={() => submit.mutate()}>Submit Quiz</button>
            {submit.data && <p className="mt-2 text-sm font-medium">Score: {submit.data.score}%</p>}
          </div>
        )}
      </div>
    </div>
  );
}
