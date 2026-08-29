import React from 'react';
import { useLearner } from '../context/LearnerContext';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts';
import { BarChart2, Info } from 'lucide-react';

export const SkillMasteryChart = () => {
  const { dashboard } = useLearner();

  if (!dashboard || !dashboard.skill_growth) {
    return <div className="glass-panel" style={{ padding: '2rem' }}>Loading Skill Growth Data...</div>;
  }

  const chartData = Object.entries(dashboard.skill_growth).map(([skill, data]) => ({
    name: skill.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    Completion: data.completion,
    Mastery: data.mastery
  }));

  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.3rem', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <BarChart2 style={{ color: 'var(--accent-cyan)' }} />
            Skill Completion vs Mastery Analysis
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
            Distinguishing course completion % from actual evaluated skill mastery %
          </p>
        </div>
      </div>

      <div style={{ background: 'rgba(56, 189, 248, 0.08)', border: '1px solid rgba(56, 189, 248, 0.2)', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', gap: '0.5rem', alignItems: 'center', fontSize: '0.85rem' }}>
        <Info style={{ color: 'var(--accent-cyan)', width: 18, height: 18, flexShrink: 0 }} />
        <span>
          <strong>Key Agent Principle:</strong> Completion measures consumed content, whereas Mastery incorporates quiz accuracy and pace penalty evidence.
        </span>
      </div>

      <div style={{ width: '100%', height: 350 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
            <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis unit="%" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} domain={[0, 100]} />
            <Tooltip
              contentStyle={{ background: '#1e293b', borderColor: 'rgba(255,255,255,0.15)', borderRadius: '8px', color: '#fff' }}
            />
            <Legend wrapperStyle={{ paddingTop: 10 }} />
            <Bar dataKey="Completion" fill="#38bdf8" radius={[4, 4, 0, 0]} name="Completion %" />
            <Bar dataKey="Mastery" fill="#34d399" radius={[4, 4, 0, 0]} name="Evaluated Mastery %" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
