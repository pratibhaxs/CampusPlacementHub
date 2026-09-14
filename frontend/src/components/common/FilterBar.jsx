/**
 * Generic filter bar. `fields` is an array of:
 *   { name, label, type: "select"|"text"|"number", options?: [{value,label}], placeholder? }
 * `values`/`onChange(name, value)` are controlled from the parent.
 */
export default function FilterBar({ fields, values, onChange, onClear }) {
  return (
    <div className="filter-bar">
      {fields.map((f) => (
        <label key={f.name} className="filter-field">
          <span>{f.label}</span>
          {f.type === "select" ? (
            <select value={values[f.name] ?? ""} onChange={(e) => onChange(f.name, e.target.value)}>
              <option value="">All</option>
              {f.options.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          ) : (
            <input
              type={f.type === "number" ? "number" : "text"}
              value={values[f.name] ?? ""}
              onChange={(e) => onChange(f.name, e.target.value)}
              placeholder={f.placeholder || ""}
            />
          )}
        </label>
      ))}
      <button type="button" onClick={onClear} className="secondary-btn">Clear filters</button>
    </div>
  );
}
