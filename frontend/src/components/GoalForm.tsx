import { useState } from "react";
import type { UserGoal } from "../types/api";

interface Props {
  onSubmit: (goal: UserGoal) => void;
  loading?: boolean;
}

const CONTACT_TYPE_OPTIONS = [
  "LinkedIn connection",
  "Cold email",
  "Twitter/X DM",
  "Alumni network",
  "Conference contact",
  "Referral",
];

export default function GoalForm({ onSubmit, loading = false }: Props) {
  const [primaryGoal, setPrimaryGoal] = useState("");
  const [targetRoles, setTargetRoles] = useState("");
  const [targetCompanies, setTargetCompanies] = useState("");
  const [preferredContacts, setPreferredContacts] = useState<string[]>(["LinkedIn connection"]);
  const [avoidContacts, setAvoidContacts] = useState<string[]>([]);
  const [outreachStyle, setOutreachStyle] = useState<"formal" | "casual">("casual");
  const [userBackground, setUserBackground] = useState("");

  function togglePreferred(type: string) {
    setPreferredContacts((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  }

  function toggleAvoid(type: string) {
    setAvoidContacts((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  }

  function splitCsv(s: string) {
    return s
      .split(",")
      .map((x) => x.trim())
      .filter(Boolean);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const goal: UserGoal = {
      primary_goal: primaryGoal.trim(),
      target_roles: splitCsv(targetRoles),
      target_companies: splitCsv(targetCompanies),
      preferred_contact_types: preferredContacts,
      avoid_contact_types: avoidContacts,
      user_background: userBackground.trim() ? { summary: userBackground.trim() } : {},
      outreach_style: { style: outreachStyle },
    };
    onSubmit(goal);
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label className="form-label">Primary Goal *</label>
        <textarea
          className="form-textarea"
          value={primaryGoal}
          onChange={(e) => setPrimaryGoal(e.target.value)}
          placeholder="e.g. Find a senior software engineer role at a Series B startup in the fintech space"
          required
          rows={3}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Target Roles</label>
        <input
          className="form-input"
          value={targetRoles}
          onChange={(e) => setTargetRoles(e.target.value)}
          placeholder="e.g. Software Engineer, Engineering Manager, Staff Engineer"
        />
        <div className="form-hint">Comma-separated list of role titles</div>
      </div>

      <div className="form-group">
        <label className="form-label">Target Companies</label>
        <input
          className="form-input"
          value={targetCompanies}
          onChange={(e) => setTargetCompanies(e.target.value)}
          placeholder="e.g. Stripe, Plaid, Brex, Ramp"
        />
        <div className="form-hint">Comma-separated list of company names</div>
      </div>

      <div className="form-group">
        <label className="form-label">Your Background (optional)</label>
        <textarea
          className="form-textarea"
          value={userBackground}
          onChange={(e) => setUserBackground(e.target.value)}
          placeholder="Brief summary of your background, e.g. 5 years of backend engineering, Python & Go, previously at Acme Corp"
          rows={2}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Preferred Contact Types</label>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "0.25rem" }}>
          {CONTACT_TYPE_OPTIONS.map((type) => (
            <label
              key={type}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.35rem",
                fontSize: "0.85rem",
                cursor: "pointer",
                padding: "0.3rem 0.7rem",
                borderRadius: "var(--radius-sm)",
                border: "1.5px solid",
                borderColor: preferredContacts.includes(type)
                  ? "var(--color-primary)"
                  : "var(--color-border)",
                background: preferredContacts.includes(type)
                  ? "var(--color-primary-light)"
                  : "transparent",
                color: preferredContacts.includes(type)
                  ? "var(--color-primary)"
                  : "var(--color-text-muted)",
                transition: "all 0.15s ease",
              }}
            >
              <input
                type="checkbox"
                style={{ display: "none" }}
                checked={preferredContacts.includes(type)}
                onChange={() => togglePreferred(type)}
              />
              {type}
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Avoid Contact Types</label>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "0.25rem" }}>
          {CONTACT_TYPE_OPTIONS.map((type) => (
            <label
              key={type}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.35rem",
                fontSize: "0.85rem",
                cursor: "pointer",
                padding: "0.3rem 0.7rem",
                borderRadius: "var(--radius-sm)",
                border: "1.5px solid",
                borderColor: avoidContacts.includes(type)
                  ? "var(--color-danger)"
                  : "var(--color-border)",
                background: avoidContacts.includes(type)
                  ? "var(--color-danger-light)"
                  : "transparent",
                color: avoidContacts.includes(type)
                  ? "var(--color-danger)"
                  : "var(--color-text-muted)",
                transition: "all 0.15s ease",
              }}
            >
              <input
                type="checkbox"
                style={{ display: "none" }}
                checked={avoidContacts.includes(type)}
                onChange={() => toggleAvoid(type)}
              />
              {type}
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Outreach Style</label>
        <div className="form-radio-group">
          {(["casual", "formal"] as const).map((style) => (
            <label key={style} className="form-radio-label">
              <input
                type="radio"
                name="style"
                value={style}
                checked={outreachStyle === style}
                onChange={() => setOutreachStyle(style)}
              />
              {style.charAt(0).toUpperCase() + style.slice(1)}
            </label>
          ))}
        </div>
      </div>

      <button
        type="submit"
        className="btn btn-primary btn-lg"
        disabled={loading || !primaryGoal.trim()}
      >
        {loading ? <><span className="loading-spinner" /> Setting up…</> : "✓ Confirm Goal"}
      </button>
    </form>
  );
}
