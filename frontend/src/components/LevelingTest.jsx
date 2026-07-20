import { useEffect, useState } from "react";
import { apiFetch } from "../api";

const MAX_CONSECUTIVE_WRONG = 3;

export default function LevelingTest() {
  const [currentWord, setCurrentWord] = useState(null);
  const [testedIds, setTestedIds] = useState([]);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [consecutiveWrong, setConsecutiveWrong] = useState(0);
  const [correctCount, setCorrectCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [testEnded, setTestEnded] = useState(false);
  const [status, setStatus] = useState("loading"); // loading | testing | done | error

  async function fetchNextWord(excludeIds) {
    const res = await apiFetch(`/leveling/next-word?exclude=${excludeIds.join(",")}`);
    const word = await res.json();
    if (word === null) {
      setStatus("done");
      return;
    }
    setCurrentWord(word);
    setStatus("testing");
  }

  useEffect(() => {
    fetchNextWord([]).catch(() => setStatus("error"));
  }, []);

  if (status === "error") {
    return <p className="leveling-error">Não foi possível carregar as palavras. O backend está rodando?</p>;
  }

  if (status === "loading") {
    return <p>Carregando...</p>;
  }

  if (status === "done") {
    return (
      <div className="leveling-card">
        <h2>Nivelamento concluído</h2>
        <p>
          Você acertou {correctCount} de {totalCount} palavras testadas.
        </p>
      </div>
    );
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (feedback) {
      if (testEnded) {
        setStatus("done");
        return;
      }
      const newTestedIds = [...testedIds, currentWord.id];
      setTestedIds(newTestedIds);
      setFeedback(null);
      setAnswer("");
      await fetchNextWord(newTestedIds);
      return;
    }

    const res = await apiFetch("/leveling/check", {
      method: "POST",
      body: JSON.stringify({ word_id: currentWord.id, answer }),
    });
    const result = await res.json();
    setFeedback(result);
    setTotalCount((c) => c + 1);

    if (result.correct) {
      setCorrectCount((c) => c + 1);
      setConsecutiveWrong(0);
    } else {
      const newConsecutiveWrong = consecutiveWrong + 1;
      setConsecutiveWrong(newConsecutiveWrong);
      if (newConsecutiveWrong >= MAX_CONSECUTIVE_WRONG) {
        setTestEnded(true);
      }
    }
  }

  return (
    <div className="leveling-card">
      <p className="leveling-term">{currentWord.term}</p>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          inputMode="text"
          autoCapitalize="none"
          autoCorrect="off"
          placeholder="Digite a tradução em português"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          disabled={Boolean(feedback)}
          autoFocus
        />
        <button type="submit" className="primary-button">
          {feedback ? (testEnded ? "Ver resultado" : "Próxima") : "Confirmar"}
        </button>
      </form>

      {feedback && (
        <p className={feedback.correct ? "leveling-feedback-correct" : "leveling-feedback-wrong"}>
          {feedback.correct
            ? "Certo!"
            : `Errado. Tradução correta: ${feedback.correct_translation}`}
        </p>
      )}
    </div>
  );
}
