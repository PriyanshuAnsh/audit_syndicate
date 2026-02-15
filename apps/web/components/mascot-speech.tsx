"use client";

import { useEffect, useState } from "react";

type MascotSpeechProps = {
  text: string;
  speedMs?: number;
  pauseMs?: number;
};

export default function MascotSpeech({ text, speedMs = 45, pauseMs = 1400 }: MascotSpeechProps) {
  const [index, setIndex] = useState(0);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (!deleting && index < text.length) {
        setIndex((v) => v + 1);
        return;
      }
      if (!deleting && index >= text.length) {
        setDeleting(true);
        return;
      }
      if (deleting && index > 0) {
        setIndex((v) => v - 1);
        return;
      }
      if (deleting && index === 0) {
        setDeleting(false);
      }
    }, !deleting && index >= text.length ? pauseMs : speedMs);

    return () => clearTimeout(timeout);
  }, [index, deleting, text, speedMs, pauseMs]);

  return (
    <div className="mascot-speech">
      <span className="typing-live">{text.slice(0, index)}</span>
      <span className="typing-cursor" aria-hidden="true">|</span>
    </div>
  );
}
