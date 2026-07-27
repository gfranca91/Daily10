import { useEffect, useRef, useState } from "react";
import { apiFetch } from "../api";

const LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];
const MAX_CONSECUTIVE_WRONG = 3;
const MAX_WORDS_PER_TIER = 8;
const PASS_THRESHOLD = 0.7;
const FAIL_THRESHOLD = 0.5;

export default function PlacementTest({ declaredLevel, onFinished }) {
  const [tier, setTier] = useState(declaredLevel);
  const [direction, setDirection] = useState(null); // null | "up" | "down"
  const [lastAcceptableTier, setLastAcceptableTier] = useState(null);

  const [currentWord, setCurrentWord] = useState(null);
  const [testedIds, setTestedIds] = useState([]);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [consecutiveWrong, setConsecutiveWrong] = useState(0);
  const [correctCount, setCorrectCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);

  const [status, setStatus] = useState("loading"); // loading | testing | finishing | error

  async function fetchNextWord(forTier, excludeIds) {
    const res = await apiFetch(`/leveling/next-word?level=${forTier}&exclude=${excludeIds.join(",")}`);
    const word = await res.json();
    if (word === null) {
      return null;
    }
    setCurrentWord(word);
    return word;
  }

  async function startTier(forTier) {
    setTier(forTier);
    setTestedIds([]);
    setConsecutiveWrong(0);
    setCorrectCount(0);
    setTotalCount(0);
    setFeedback(null);
    setAnswer("");
    setStatus("loading");
    const word = await fetchNextWord(forTier, []);
    if (word === null) {
      // nível sem nenhuma palavra cadastrada ainda — total=0 conta como aprovado automaticamente
      await decideAfterTier(forTier, 0, 0);
      return;
    }
    setStatus("testing");
  }

  const initedRef = useRef(false);
  useEffect(() => {
    if (initedRef.current) return;
    initedRef.current = true;
    startTier(declaredLevel);
  }, []);

  async function decideAfterTier(finishedTier, total, correct) {
    const accuracy = total === 0 ? 1 : correct / total;
    const tierIndex = LEVELS.indexOf(finishedTier);
    const newLastAcceptable = accuracy >= FAIL_THRESHOLD ? finishedTier : lastAcceptableTier;

    if (direction === null) {
      if (accuracy >= PASS_THRESHOLD && tierIndex < LEVELS.length - 1) {
        setDirection("up");
        setLastAcceptableTier(newLastAcceptable);
        await startTier(LEVELS[tierIndex + 1]);
        return;
      }
      if (accuracy < FAIL_THRESHOLD && tierIndex > 0) {
        setDirection("down");
        setLastAcceptableTier(newLastAcceptable);
        await startTier(LEVELS[tierIndex - 1]);
        return;
      }
      await finish(finishedTier);
      return;
    }

    if (direction === "up") {
      if (accuracy >= PASS_THRESHOLD && tierIndex < LEVELS.length - 1) {
        setLastAcceptableTier(newLastAcceptable);
        await startTier(LEVELS[tierIndex + 1]);
        return;
      }
      await finish(newLastAcceptable ?? finishedTier);
      return;
    }

    // direction === "down"
    if (accuracy < FAIL_THRESHOLD && tierIndex > 0) {
      setLastAcceptableTier(newLastAcceptable);
      await startTier(LEVELS[tierIndex - 1]);
      return;
    }
    await finish(accuracy >= FAIL_THRESHOLD ? finishedTier : newLastAcceptable ?? "A1");
  }

  async function finish(confirmedLevel) {
    setStatus("finishing");
    await apiFetch("/leveling/complete-placement", {
      method: "POST",
      body: JSON.stringify({ confirmed_level: confirmedLevel }),
    });
    onFinished(confirmedLevel);
  }

  if (status === "loading" || status === "finishing") {
    return <p>Carregando...</p>;
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (feedback) {
      const newTestedIds = [...testedIds, currentWord.id];
      setTestedIds(newTestedIds);
      setFeedback(null);
      setAnswer("");

      const tierExhausted =
        consecutiveWrong >= MAX_CONSECUTIVE_WRONG || totalCount >= MAX_WORDS_PER_TIER;

      if (tierExhausted) {
        await decideAfterTier(tier, totalCount, correctCount);
        return;
      }

      const word = await fetchNextWord(tier, newTestedIds);
      if (word === null) {
        await decideAfterTier(tier, totalCount, correctCount);
        return;
      }
      setStatus("testing");
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
      setConsecutiveWrong((c) => c + 1);
    }
  }

  return (
    <div className="leveling-card">
      <p className="phase-label">Testando nível {tier}</p>
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
          {feedback ? "Próxima" : "Confirmar"}
        </button>
      </form>

      {feedback && (
        <p className={feedback.correct ? "leveling-feedback-correct" : "leveling-feedback-wrong"}>
          {feedback.correct ? "Certo!" : `Errado. Tradução correta: ${feedback.correct_translation}`}
        </p>
      )}
    </div>
  );
}
