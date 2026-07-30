import { useEffect, useState } from "react";
import { apiFetch } from "../api";

export default function CognatesLibrary({ onBack }) {
  const [words, setWords] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    apiFetch("/library/cognates")
      .then((res) => res.json())
      .then((data) => {
        if (!cancelled) setWords(data);
      })
      .catch(() => {
        if (!cancelled) setError("Não foi possível carregar a biblioteca. O backend está rodando?");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="leveling-card">
      <h2>Cognatos</h2>
      <p className="level-picker-hint">
        Palavras muito parecidas com o português — você já sabe estas, por isso elas não entram nas
        lições nem nos exercícios.
      </p>

      {error && <p className="leveling-error">{error}</p>}
      {!error && !words && <p>Carregando...</p>}

      {words && (
        <ul className="cognates-list">
          {words.map((w) => (
            <li key={w.id} className="cognates-item">
              <span className="cognates-term">{w.term}</span>
              <span className="cognates-translation">{w.translation_pt}</span>
            </li>
          ))}
        </ul>
      )}

      <button type="button" className="primary-button" onClick={onBack}>
        Voltar
      </button>
    </div>
  );
}
