import { useState } from "react";
import { apiFetch } from "../api";
import LevelPicker from "./LevelPicker";

export default function ChooseLevel({ onDone }) {
  const [level, setLevel] = useState("A1");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    await apiFetch("/auth/declared-level", {
      method: "POST",
      body: JSON.stringify({ declared_level: level }),
    });
    onDone(level);
  }

  return (
    <div className="leveling-card">
      <h2>Qual é o seu nível em espanhol?</h2>
      <p className="level-picker-hint">
        Sua conta é de antes do teste de nivelamento existir — escolha um nível de partida, você vai
        confirmar ele a seguir.
      </p>

      <form onSubmit={handleSubmit}>
        <LevelPicker value={level} onChange={setLevel} />
        <button type="submit" className="primary-button" disabled={loading}>
          Continuar
        </button>
      </form>
    </div>
  );
}
