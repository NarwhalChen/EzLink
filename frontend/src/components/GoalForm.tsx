import { useState } from 'react';
import type { UserGoal } from '../types/api';

const emptyGoal: UserGoal = {
  primary_goal: '',
  target_roles: [],
  target_companies: [],
  preferred_contact_types: [],
  avoid_contact_types: [],
  user_background: {},
  outreach_style: {},
};

export function GoalForm({ onSubmit }: { onSubmit: (goal: UserGoal) => void }) {
  const [goal, setGoal] = useState<UserGoal>(emptyGoal);

  return (
    <div className="panel">
      <h3>Session Goal</h3>
      <textarea
        placeholder="Primary goal"
        value={goal.primary_goal}
        onChange={(e) => setGoal({ ...goal, primary_goal: e.target.value })}
      />
      <input
        placeholder="Target roles (comma separated)"
        onChange={(e) => setGoal({ ...goal, target_roles: splitCsv(e.target.value) })}
      />
      <input
        placeholder="Target companies (comma separated)"
        onChange={(e) => setGoal({ ...goal, target_companies: splitCsv(e.target.value) })}
      />
      <button onClick={() => onSubmit(goal)} disabled={!goal.primary_goal.trim()}>
        Start Session
      </button>
    </div>
  );
}

function splitCsv(text: string): string[] {
  return text
    .split(',')
    .map((v) => v.trim())
    .filter(Boolean);
}
