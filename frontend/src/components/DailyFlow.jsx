import { useState } from "react";
import DailyLesson from "./DailyLesson";
import PracticeExercise from "./PracticeExercise";

const PHASES = ["review", "lesson", "practice", "done"];

export default function DailyFlow() {
  const [phaseIndex, setPhaseIndex] = useState(0);
  const phase = PHASES[phaseIndex];

  function next() {
    setPhaseIndex((i) => i + 1);
  }

  if (phase === "review") {
    return <PracticeExercise endpoint="/practice/review" label="Revisão" onComplete={next} />;
  }

  if (phase === "lesson") {
    return <DailyLesson onComplete={next} />;
  }

  if (phase === "practice") {
    return <PracticeExercise endpoint="/practice/today" label="Exercícios" onComplete={next} />;
  }

  return (
    <div className="leveling-card">
      <h2>Tudo pronto por hoje!</h2>
      <p>Volte amanhã pra continuar aprendendo.</p>
    </div>
  );
}
