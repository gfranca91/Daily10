import { useEffect, useState } from "react";
import PlacementTest from "./components/PlacementTest";
import DailyFlow from "./components/DailyFlow";
import Auth from "./components/Auth";
import { apiFetch, clearToken, getToken } from "./api";
import "./App.css";

export default function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(getToken()));
  const [userState, setUserState] = useState(null);

  useEffect(() => {
    if (!authenticated) return;
    let cancelled = false;
    apiFetch("/auth/me")
      .then((res) => res.json())
      .then((data) => {
        if (!cancelled) setUserState(data);
      });
    return () => {
      cancelled = true;
    };
  }, [authenticated]);

  function handleLogout() {
    clearToken();
    setAuthenticated(false);
    setUserState(null);
  }

  if (!authenticated) {
    return (
      <main className="app">
        <h1>Daily10</h1>
        <Auth
          onAuthenticated={() => {
            setAuthenticated(true);
          }}
        />
      </main>
    );
  }

  if (!userState) {
    return (
      <main className="app">
        <h1>Daily10</h1>
        <p>Carregando...</p>
      </main>
    );
  }

  return (
    <main className="app">
      <h1>Daily10</h1>

      {!userState.placement_test_done ? (
        <PlacementTest
          declaredLevel={userState.declared_level}
          onFinished={(confirmedLevel) =>
            setUserState({ ...userState, current_level: confirmedLevel, placement_test_done: true })
          }
        />
      ) : (
        <DailyFlow />
      )}

      <button type="button" className="link-button" onClick={handleLogout}>
        Sair
      </button>
    </main>
  );
}
