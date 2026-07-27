import { useEffect, useState } from "react";
import { apiFetch } from "../api";

export default function DailyLesson({ onComplete }) {
  const [words, setWords] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    apiFetch("/lessons/today")
      .then((res) => res.json())
      .then((data) => {
        if (!cancelled) setWords(data);
      })
      .catch(() => {
        if (!cancelled) setError("Não foi possível carregar a lição de hoje. O backend está rodando?");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const isDone = words !== null && currentIndex >= words.length;

  useEffect(() => {
    if (isDone) {
      onComplete();
    }
  }, [isDone]);

  if (error) {
    return <p className="leveling-error">{error}</p>;
  }

  if (!words) {
    return <p>Carregando...</p>;
  }

  if (isDone) {
    return null;
  }

  const currentWord = words[currentIndex];

  return (
    <div className="leveling-card">
      <p className="phase-label">Lição de hoje</p>
      <p className="leveling-progress">
        {currentIndex + 1} / {words.length}
      </p>
      <p className="leveling-term">{currentWord.term}</p>
      <p className="lesson-translation">{currentWord.translation_pt}</p>
      <p className="lesson-example">{currentWord.example_sentence}</p>

      <button type="button" className="primary-button" onClick={() => setCurrentIndex((i) => i + 1)}>
        Próxima
      </button>
    </div>
  );
}
