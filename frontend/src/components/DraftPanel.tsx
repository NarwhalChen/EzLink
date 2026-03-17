import { useState } from "react";
import { updateDraft } from "../api/client";
import type { DraftResult } from "../types/api";

interface Props {
  draft: DraftResult;
  candidateId: number;
  onUpdated: (draft: DraftResult) => void;
}

function confidenceClass(n: number) {
  if (n >= 0.7) return "high";
  if (n >= 0.4) return "medium";
  return "low";
}

export default function DraftPanel({ draft, candidateId, onUpdated }: Props) {
  const [text, setText] = useState(draft.message_draft);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pct = Math.round(draft.confidence * 100);
  const cls = confidenceClass(draft.confidence);
  const dirty = text !== draft.message_draft;

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      const updated = await updateDraft(candidateId, text);
      if (updated.draft) {
        onUpdated(updated.draft);
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={{ marginTop: "1rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.6rem", flexWrap: "wrap" }}>
        <span style={{ fontSize: "0.82rem", color: "var(--color-text-muted)", fontWeight: 600 }}>Tone</span>
        <span className="badge badge-neutral">{draft.tone}</span>
      </div>

      <div className="confidence-wrap" style={{ marginBottom: "0.75rem" }}>
        <div className="confidence-label">
          <span>Draft Confidence</span>
          <span>{pct}%</span>
        </div>
        <div className="confidence-bar">
          <div className={`confidence-fill ${cls}`} style={{ width: `${pct}%` }} />
        </div>
      </div>

      {draft.personalization_used.length > 0 && (
        <div style={{ marginBottom: "0.75rem" }}>
          <div className="section-label">Personalization Used</div>
          <div className="tag-list">
            {draft.personalization_used.map((p, i) => (
              <span key={i} className="tag tag-signal">✦ {p}</span>
            ))}
          </div>
        </div>
      )}

      <div className="section-label">Message Draft</div>
      <textarea
        className="form-textarea"
        value={text}
        onChange={(e) => { setText(e.target.value); setSaved(false); }}
        rows={8}
        style={{ fontFamily: "var(--font-sans)", fontSize: "0.875rem", lineHeight: 1.7 }}
      />

      {error && <div className="alert alert-error" style={{ marginTop: "0.5rem" }}>⚠ {error}</div>}

      <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.6rem", alignItems: "center" }}>
        <button
          className="btn btn-primary btn-sm"
          onClick={handleSave}
          disabled={saving || !dirty}
        >
          {saving ? <><span className="loading-spinner" style={{ width: 14, height: 14 }} /> Saving…</> : "Save Draft"}
        </button>
        {saved && <span style={{ fontSize: "0.8rem", color: "var(--color-success)" }}>✓ Saved</span>}
        {dirty && !saved && <span style={{ fontSize: "0.78rem", color: "var(--color-text-muted)" }}>Unsaved changes</span>}
      </div>
    </div>
  );
}
