import { useEffect, useState } from "react";
import { apiFetch } from "../api";

export default function PracticeExercise({ endpoint, label, onComplete }) {
  const [exercises, setExercises] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [feedback, setFeedback] = useState(null);
  const [correctCount, setCorrectCount] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    apiFetch(endpoint)
      .then((res) => res.json())
      .then((data) => {
        if (!cancelled) setExercises(data);
      })
      .catch(() => {
        if (!cancelled) setError("Não foi possível carregar os exercícios. O backend está rodando?");
      });
    return () => {
      cancelled = true;
    };
  }, [endpoint]);

  const isDone = exercises !== null && currentIndex >= exercises.length;

  useEffect(() => {
    if (isDone) {
      onComplete();
    }
  }, [isDone]);

  if (error) {
    return <p className="leveling-error">{error}</p>;
  }

  if (!exercises) {
    return <p>Carregando...</p>;
  }

  if (isDone) {
    return null;
  }

  const exercise = exercises[currentIndex];
  const [before, after] = exercise.sentence_template.split("___");

  async function handleOptionClick(option) {
    if (feedback) return;
    const res = await apiFetch("/practice/check", {
      method: "POST",
      body: JSON.stringify({ sentence_id: exercise.sentence_id, option_word_id: option.word_id }),
    });
    const result = await res.json();
    setFeedback({ ...result, chosenId: option.word_id });
    if (result.correct) {
      setCorrectCount((c) => c + 1);
    }
  }

  function handleNext() {
    setFeedback(null);
    setCurrentIndex((i) => i + 1);
  }

  return (
    <div className="leveling-card">
      {label && <p className="phase-label">{label}</p>}
      <p className="leveling-progress">
        {currentIndex + 1} / {exercises.length}
      </p>
      <p className="practice-sentence">
        {before}
        <span className="practice-blank">___</span>
        {after}
      </p>

      <div className="practice-options">
        {exercise.options.map((option) => {
          let optionClass = "practice-option";
          if (feedback && option.word_id === feedback.chosenId) {
            optionClass += feedback.correct ? " practice-option-correct" : " practice-option-wrong";
          } else if (feedback && option.term === feedback.correct_term) {
            optionClass += " practice-option-correct";
          }
          return (
            <button
              key={option.word_id}
              type="button"
              className={optionClass}
              onClick={() => handleOptionClick(option)}
              disabled={Boolean(feedback)}
            >
              {option.term}
            </button>
          );
        })}
      </div>

      {feedback && (
        <button type="button" onClick={handleNext} className="primary-button">
          Próxima
        </button>
      )}
    </div>
  );
}
