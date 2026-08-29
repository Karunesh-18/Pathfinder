import React from 'react';
import { RefreshCw } from 'lucide-react';

export const ChangeSummaryBanner = ({ text }) => {
  if (!text) return null;

  return (
    <div style={{
      background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(129, 140, 248, 0.15) 100%)',
      border: '1px solid rgba(56, 189, 248, 0.3)',
      borderRadius: 'var(--radius-md)',
      padding: '0.85rem 1.25rem',
      marginBottom: '1.5rem',
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem'
    }}>
      <RefreshCw style={{ color: 'var(--accent-cyan)', width: 20, height: 20, flexShrink: 0 }} />
      <div>
        <strong style={{ color: 'var(--accent-cyan)', fontSize: '0.85rem', textTransform: 'uppercase' }}>
          Roadmap Auto-Adapted:
        </strong>
        <p style={{ margin: 0, fontSize: '0.95rem', color: 'var(--text-main)' }}>{text}</p>
      </div>
    </div>
  );
};
