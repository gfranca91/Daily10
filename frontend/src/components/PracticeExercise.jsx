import { useEffect, useState } from "react";
import { apiFetch } from "../api";

export default function PracticeExercise() {
  const [exercises, setExercises] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [feedback, setFeedback] = useState(null);
  const [correctCount, setCorrectCount] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    apiFetch("/practice/today")
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
  }, []);

  if (error) {
    return <p className="leveling-error">{error}</p>;
  }

  if (!exercises) {
    return <p>Carregando...</p>;
  }

  if (exercises.length === 0) {
    return (
      <div className="leveling-card">
        <h2>Sem exercícios ainda</h2>
        <p>As palavras da lição de hoje ainda não têm frase de exercício cadastrada.</p>
      </div>
    );
  }

  const isDone = currentIndex >= exercises.length;

  if (isDone) {
    return (
      <div className="leveling-card">
        <h2>Exercícios concluídos</h2>
        <p>
          Você acertou {correctCount} de {exercises.length}.
        </p>
      </div>
    );
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
