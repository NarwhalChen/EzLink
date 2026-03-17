import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ExperienceUpload from "../components/ExperienceUpload";
import GoalForm from "../components/GoalForm";
import {
  getCurrentExperience,
  createSession,
  collectProfile,
  evaluateCandidate,
  draftMessage,
} from "../api/client";
import type { ExperienceDocument, UserGoal } from "../types/api";

type Step = "collect" | "evaluate" | "draft" | "done";

interface PipelineStatus {
  step: Step | null;
  urlIndex: number;
  total: number;
  error: string | null;
}

export default function SetupPage() {
  const navigate = useNavigate();
  const [expDoc, setExpDoc] = useState<ExperienceDocument | null>(null);
  const [goalConfirmed, setGoalConfirmed] = useState(false);
  const [confirmedGoal, setConfirmedGoal] = useState<UserGoal | null>(null);
  const [urlsText, setUrlsText] = useState("");
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus>({
    step: null,
    urlIndex: 0,
    total: 0,
    error: null,
  });
  const [running, setRunning] = useState(false);

  useEffect(() => {
    getCurrentExperience().then((doc) => {
      if (doc) setExpDoc(doc);
    });
  }, []);

  function handleGoalSubmit(goal: UserGoal) {
    setConfirmedGoal(goal);
    setGoalConfirmed(true);
  }

  async function handleStartPipeline() {
    if (!expDoc?.id) {
      setPipelineStatus((s) => ({ ...s, error: "Please upload an experience document first." }));
      return;
    }
    if (!confirmedGoal) {
      setPipelineStatus((s) => ({ ...s, error: "Please confirm your goal first." }));
      return;
    }

    const urls = urlsText
      .split("\n")
      .map((u) => u.trim())
      .filter(Boolean);

    if (urls.length === 0) {
      setPipelineStatus((s) => ({ ...s, error: "Add at least one profile URL." }));
      return;
    }

    setRunning(true);
    setPipelineStatus({ step: null, urlIndex: 0, total: urls.length, error: null });

    let sessionId: number;
    try {
      const session = await createSession(confirmedGoal, expDoc.id);
      sessionId = session.id!;
      localStorage.setItem("ezlink_session_id", String(sessionId));
      localStorage.setItem("ezlink_goal", JSON.stringify(confirmedGoal));
    } catch (e) {
      setPipelineStatus((s) => ({
        ...s,
        error: e instanceof Error ? e.message : "Failed to create session",
      }));
      setRunning(false);
      return;
    }

    for (let i = 0; i < urls.length; i++) {
      const url = urls[i];
      try {
        setPipelineStatus({ step: "collect", urlIndex: i + 1, total: urls.length, error: null });
        const collected = await collectProfile(url, sessionId);

        setPipelineStatus({ step: "evaluate", urlIndex: i + 1, total: urls.length, error: null });
        const evaluated = await evaluateCandidate(collected.id!);

        if (evaluated.evaluation?.should_contact !== false) {
          setPipelineStatus({ step: "draft", urlIndex: i + 1, total: urls.length, error: null });
          await draftMessage(collected.id!);
        }
      } catch (e) {
        setPipelineStatus((s) => ({
          ...s,
          error: `Error on URL ${i + 1}: ${e instanceof Error ? e.message : String(e)}`,
        }));
      }
    }

    setPipelineStatus({ step: "done", urlIndex: urls.length, total: urls.length, error: null });
    setRunning(false);
    navigate("/review");
  }

  const canStart = !!expDoc && goalConfirmed && urlsText.trim().length > 0 && !running;

  return (
    <div className="page">
      <h1 className="page-title">Setup</h1>
      <p className="page-subtitle">Configure your outreach campaign in three steps</p>

      {/* ── Step 1 ── */}
      <div className="section">
        <div className="section-heading">
          <span className="section-step">1</span>
          Upload Experience File
          {expDoc && <span style={{ fontSize: "0.78rem", color: "var(--color-success)", fontWeight: 400 }}>✓ Ready</span>}
        </div>
        <p className="section-desc">
          Upload your resume or background as a Markdown or plain-text file. This helps personalise outreach messages.
        </p>
        <div className="card">
          <ExperienceUpload
            existing={expDoc}
            onUploaded={(doc) => setExpDoc(doc)}
          />
        </div>
      </div>

      {/* ── Step 2 ── */}
      <div className="section">
        <div className="section-heading">
          <span className="section-step">2</span>
          Set Your Goal
          {goalConfirmed && <span style={{ fontSize: "0.78rem", color: "var(--color-success)", fontWeight: 400 }}>✓ Confirmed</span>}
        </div>
        <p className="section-desc">
          Define what you're looking for so the agent can evaluate and prioritise contacts.
        </p>
        <div className="card">
          {goalConfirmed && confirmedGoal ? (
            <div>
              <div className="alert alert-success">
                ✓ Goal confirmed: <strong>{confirmedGoal.primary_goal}</strong>
              </div>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setGoalConfirmed(false)}
              >
                Edit Goal
              </button>
            </div>
          ) : (
            <GoalForm onSubmit={handleGoalSubmit} />
          )}
        </div>
      </div>

      {/* ── Step 3 ── */}
      <div className="section">
        <div className="section-heading">
          <span className="section-step">3</span>
          Add Profile URLs
        </div>
        <p className="section-desc">
          Paste LinkedIn, Twitter/X, or other profile URLs — one per line. The agent will collect, evaluate, and draft messages for each.
        </p>
        <div className="card">
          <div className="form-group">
            <label className="form-label">Profile URLs</label>
            <textarea
              className="form-textarea"
              value={urlsText}
              onChange={(e) => setUrlsText(e.target.value)}
              placeholder={`https://www.linkedin.com/in/johndoe\nhttps://www.linkedin.com/in/janedoe`}
              rows={6}
              disabled={running}
            />
            <div className="form-hint">
              {urlsText.split("\n").filter((u) => u.trim()).length} URL(s) added
            </div>
          </div>
        </div>
      </div>

      {/* Pipeline Status */}
      {running && pipelineStatus.step && (
        <div className="card" style={{ marginBottom: "1.25rem" }}>
          <div className="card-title" style={{ marginBottom: "0.75rem" }}>
            <span className="loading-spinner" style={{ marginRight: "0.5rem" }} />
            Running pipeline…
          </div>
          <ul className="pipeline-steps">
            {(["collect", "evaluate", "draft"] as Step[]).map((s) => {
              const stepOrder: Step[] = ["collect", "evaluate", "draft", "done"];
              const currentIdx = stepOrder.indexOf(pipelineStatus.step!);
              const thisIdx = stepOrder.indexOf(s);
              const cls =
                currentIdx > thisIdx ? "done" : currentIdx === thisIdx ? "active" : "";
              return (
                <li key={s} className={`pipeline-step ${cls}`}>
                  <span className="step-icon">
                    {cls === "done" ? "✓" : cls === "active" ? "⟳" : "○"}
                  </span>
                  {s.charAt(0).toUpperCase() + s.slice(1)}
                  {cls === "active" && ` (${pipelineStatus.urlIndex}/${pipelineStatus.total})`}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {pipelineStatus.error && (
        <div className="alert alert-error" style={{ marginBottom: "1rem" }}>
          ⚠ {pipelineStatus.error}
        </div>
      )}

      <button
        className="btn btn-primary btn-lg btn-full"
        onClick={handleStartPipeline}
        disabled={!canStart}
      >
        {running ? (
          <><span className="loading-spinner" /> Processing…</>
        ) : (
          "🚀 Start Pipeline"
        )}
      </button>

      {!expDoc && (
        <p style={{ textAlign: "center", fontSize: "0.8rem", color: "var(--color-text-muted)", marginTop: "0.75rem" }}>
          Upload an experience file to enable the pipeline
        </p>
      )}
    </div>
  );
}
