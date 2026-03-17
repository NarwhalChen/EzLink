import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { startSession } from '../api/client';
import { ExperienceUpload } from '../components/ExperienceUpload';
import { GoalForm } from '../components/GoalForm';
import type { ExperienceDocument, UserGoal } from '../types/api';

export function SetupPage() {
  const [doc, setDoc] = useState<ExperienceDocument | null>(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  async function handleGoal(goal: UserGoal) {
    if (!doc) {
      setError('Please upload an experience file first.');
      return;
    }
    try {
      const session = await startSession(doc.id, goal);
      localStorage.setItem('sessionId', String(session.id));
      navigate('/review');
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div>
      <h2>Setup</h2>
      <ExperienceUpload onUploaded={setDoc} />
      {doc && <pre className="panel">{doc.markdown_content.slice(0, 400)}</pre>}
      <GoalForm onSubmit={handleGoal} />
      {error && <p className="error">{error}</p>}
    </div>
  );
}
