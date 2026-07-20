import { useState } from "react";
import LevelingTest from "./components/LevelingTest";
import DailyLesson from "./components/DailyLesson";
import PracticeExercise from "./components/PracticeExercise";
import Auth from "./components/Auth";
import { clearToken, getToken } from "./api";
import "./App.css";

const TABS = {
  lesson: { label: "Lição de hoje", Component: DailyLesson },
  practice: { label: "Exercícios", Component: PracticeExercise },
  leveling: { label: "Nivelamento", Component: LevelingTest },
};

export default function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(getToken()));
  const [tab, setTab] = useState("lesson");

  if (!authenticated) {
    return (
      <main className="app">
        <h1>Daily10</h1>
        <Auth onAuthenticated={() => setAuthenticated(true)} />
      </main>
    );
  }

  function handleLogout() {
    clearToken();
    setAuthenticated(false);
  }

  const ActiveComponent = TABS[tab].Component;

  return (
    <main className="app">
      <h1>Daily10</h1>

      <nav className="nav-tabs">
        {Object.entries(TABS).map(([key, { label }]) => (
          <button key={key} className={tab === key ? "active" : ""} onClick={() => setTab(key)}>
            {label}
          </button>
        ))}
      </nav>

      <ActiveComponent />

      <button type="button" className="link-button" onClick={handleLogout}>
        Sair
      </button>
    </main>
  );
}
