import { useState } from 'react';
import type { ExperienceDocument } from '../types/api';
import { uploadExperience } from '../api/client';

export function ExperienceUpload({ onUploaded }: { onUploaded: (doc: ExperienceDocument) => void }) {
  const [error, setError] = useState('');

  async function onChange(file: File | null) {
    if (!file) return;
    try {
      const doc = await uploadExperience(file);
      onUploaded(doc);
      setError('');
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="panel">
      <h3>Upload Experience Markdown</h3>
      <input type="file" accept=".md,text/markdown" onChange={(e) => onChange(e.target.files?.[0] ?? null)} />
      {error && <p className="error">{error}</p>}
    </div>
  );
}
