import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL;

export default function DailyLesson() {
  const [words, setWords] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/lessons/today`)
      .then((res) => res.json())
      .then(setWords)
      .catch(() => setError("Não foi possível carregar a lição de hoje. O backend está rodando?"));
  }, []);

  if (error) {
    return <p className="leveling-error">{error}</p>;
  }

  if (!words) {
    return <p>Carregando...</p>;
  }

  if (words.length === 0) {
    return (
      <div className="leveling-card">
        <h2>Sem palavras novas</h2>
        <p>Você já viu todo o vocabulário disponível por enquanto.</p>
      </div>
    );
  }

  const isDone = currentIndex >= words.length;

  if (isDone) {
    return (
      <div className="leveling-card">
        <h2>Lição de hoje concluída</h2>
        <p>Você aprendeu {words.length} palavras novas.</p>
      </div>
    );
  }

  const currentWord = words[currentIndex];

  return (
    <div className="leveling-card">
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
