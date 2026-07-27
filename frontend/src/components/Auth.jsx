import { useState } from "react";
import { setToken } from "../api";
import LevelPicker from "./LevelPicker";

const API_URL = import.meta.env.VITE_API_URL;

export default function Auth({ onAuthenticated }) {
  const [mode, setMode] = useState("login"); // login | signup
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [declaredLevel, setDeclaredLevel] = useState("A1");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const body = mode === "signup" ? { email, password, declared_level: declaredLevel } : { email, password };
      const res = await fetch(`${API_URL}/auth/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Algo deu errado");
      }

      setToken(data.access_token);
      onAuthenticated();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="leveling-card">
      <h2>{mode === "login" ? "Entrar" : "Criar conta"}</h2>

      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="E-mail"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoFocus
        />
        <input
          type="password"
          placeholder="Senha (mínimo 8 caracteres)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        {mode === "signup" && (
          <div className="level-picker">
            <p className="level-picker-label">Qual é o seu nível em espanhol?</p>
            <LevelPicker value={declaredLevel} onChange={setDeclaredLevel} />
            <p className="level-picker-hint">Não se preocupe em acertar — você vai fazer um teste rápido depois pra confirmar.</p>
          </div>
        )}

        <button type="submit" className="primary-button" disabled={loading}>
          {mode === "login" ? "Entrar" : "Criar conta"}
        </button>
      </form>

      {error && <p className="leveling-feedback-wrong">{error}</p>}

      <button
        type="button"
        className="link-button"
        onClick={() => {
          setMode(mode === "login" ? "signup" : "login");
          setError(null);
        }}
      >
        {mode === "login" ? "Não tem conta? Criar uma" : "Já tem conta? Entrar"}
      </button>
    </div>
  );
}
