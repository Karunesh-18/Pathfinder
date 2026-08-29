import React from 'react';
import { CheckCircle2, Clock, PlayCircle, BookOpen } from 'lucide-react';

export const MilestoneCard = ({ milestone, index }) => {
  const isDone = milestone.status === 'done';
  const isCurrent = milestone.status === 'in_progress';

  return (
    <div className={`glass-panel glow-card`} style={{
      padding: '1.25rem',
      marginBottom: '1rem',
      borderLeft: `4px solid ${isDone ? 'var(--accent-emerald)' : (isCurrent ? 'var(--accent-cyan)' : 'var(--text-muted)')}`
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            background: isDone ? 'rgba(52, 211, 153, 0.2)' : (isCurrent ? 'rgba(56, 189, 248, 0.2)' : 'rgba(255, 255, 255, 0.05)'),
            padding: '0.5rem',
            borderRadius: '50%',
            color: isDone ? 'var(--accent-emerald)' : (isCurrent ? 'var(--accent-cyan)' : 'var(--text-muted)')
          }}>
            {isDone ? <CheckCircle2 size={20} /> : (isCurrent ? <PlayCircle size={20} /> : <Clock size={20} />)}
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Milestone {index + 1}
            </span>
            <h4 style={{ margin: 0, fontSize: '1.1rem' }}>{milestone.title}</h4>
          </div>
        </div>

        <div className={`badge ${isDone ? 'badge-emerald' : (isCurrent ? 'badge-cyan' : 'badge-indigo')}`}>
          {milestone.status ? milestone.status.replace('_', ' ') : 'upcoming'}
        </div>
      </div>

      <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', margin: '0.75rem 0 0 0' }}>
        {milestone.explanation}
      </p>

      {milestone.resources && milestone.resources.length > 0 && (
        <div style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <BookOpen size={14} />
          <span>Resource Attached: {milestone.resources.join(', ')}</span>
        </div>
      )}
    </div>
  );
};
