import React from 'react';
import { HelpCircle } from 'lucide-react';

export const ClarifyingQuestionBubble = ({ text }) => {
  return (
    <div style={{
      background: 'rgba(251, 191, 36, 0.1)',
      border: '1px solid rgba(251, 191, 36, 0.3)',
      borderRadius: '12px',
      padding: '1rem',
      margin: '0.75rem 0',
      display: 'flex',
      gap: '0.75rem',
      alignItems: 'flex-start'
    }}>
      <HelpCircle style={{ color: 'var(--accent-amber)', width: 22, height: 22, flexShrink: 0, marginTop: 2 }} />
      <div>
        <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-amber)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
          Clarifying Question (Active Assessment)
        </div>
        <p style={{ fontSize: '0.9rem', color: '#fef3c7', margin: 0, lineHeight: 1.4 }}>
          {text}
        </p>
      </div>
    </div>
  );
};
