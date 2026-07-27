const LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];

export default function LevelPicker({ value, onChange }) {
  return (
    <div className="level-options">
      {LEVELS.map((level) => (
        <button
          key={level}
          type="button"
          className={level === value ? "level-option active" : "level-option"}
          onClick={() => onChange(level)}
        >
          {level}
        </button>
      ))}
    </div>
  );
}
