import { useState, useRef } from "react";
import { uploadExperience } from "../api/client";
import type { ExperienceDocument } from "../types/api";

interface Props {
  existing?: ExperienceDocument | null;
  onUploaded: (doc: ExperienceDocument) => void;
}

export default function ExperienceUpload({ existing, onUploaded }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    setError(null);
    const text = await file.text();
    setPreview(text);
    setLoading(true);
    try {
      const doc = await uploadExperience(file);
      onUploaded(doc);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  function onInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  }

  const displayDoc = existing;

  return (
    <div>
      {displayDoc && !preview && (
        <div className="alert alert-success" style={{ marginBottom: "1rem" }}>
          <span>✓</span>
          <span>
            <strong>{displayDoc.filename}</strong> already uploaded
            {displayDoc.uploaded_at && (
              <> — {new Date(displayDoc.uploaded_at).toLocaleDateString()}</>
            )}
          </span>
        </div>
      )}

      <div
        className={`upload-zone${dragOver ? " drag-over" : ""}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <div className="upload-zone-icon">📄</div>
        <div className="upload-zone-text">
          <strong>Click to upload</strong> or drag and drop
          <br />
          <span style={{ fontSize: "0.78rem" }}>Markdown (.md) or plain text (.txt)</span>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept=".md,.txt"
          style={{ display: "none" }}
          onChange={onInputChange}
        />
      </div>

      {loading && (
        <div style={{ marginTop: "0.75rem", display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--color-text-muted)", fontSize: "0.875rem" }}>
          <span className="loading-spinner" />
          Uploading…
        </div>
      )}

      {error && <div className="alert alert-error" style={{ marginTop: "0.75rem" }}>⚠ {error}</div>}

      {(preview || displayDoc?.markdown_content) && (
        <div>
          <div className="section-label" style={{ marginTop: "1rem" }}>Preview</div>
          <div className="file-preview">
            {preview ?? displayDoc?.markdown_content}
          </div>
        </div>
      )}
    </div>
  );
}
