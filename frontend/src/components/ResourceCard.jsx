import React, { useState } from 'react';
import { useLearner } from '../context/LearnerContext';
import { ExplanationPopover } from './ExplanationPopover';
import { ExternalLink, HelpCircle, Clock, BookOpen, Layers } from 'lucide-react';

export const ResourceCard = ({ recommendation }) => {
  const { getExplanation } = useLearner();
  const [explanation, setExplanation] = useState(null);
  const [loadingExpl, setLoadingExpl] = useState(false);

  const res = recommendation.resource || {};
  const scorePct = Math.round((recommendation.score || 0.8) * 100);

  const handleWhyThis = async () => {
    setLoadingExpl(true);
    const text = await getExplanation(recommendation.resource_id);
    setExplanation(text);
    setLoadingExpl(false);
  };

  return (
    <div className="glass-panel glow-card" style={{ padding: '1.25rem', marginBottom: '1rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
          <div className="badge badge-cyan">{res.format || 'course'}</div>
          <div className="badge badge-emerald">{scorePct}% Match</div>
        </div>

        <h3 style={{ fontSize: '1.15rem', margin: '0.5rem 0' }}>{res.title}</h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: '0 0 0.75rem 0' }}>
          Provider: <strong>{res.provider}</strong>
        </p>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', lineHeight: 1.4, margin: '0 0 1rem 0' }}>
          {res.description}
        </p>
      </div>

      <div>
        <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <Clock size={14} /> {res.est_hours} hours
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <Layers size={14} /> Difficulty: {res.difficulty}
          </span>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <a
            href={res.url || '#'}
            target="_blank"
            rel="noreferrer"
            className="btn-primary"
            style={{ flex: 1, textDecoration: 'none', justifyContent: 'center', fontSize: '0.85rem' }}
          >
            <span>Open Resource</span>
            <ExternalLink size={14} />
          </a>
          <button
            className="btn-secondary"
            onClick={handleWhyThis}
            disabled={loadingExpl}
            style={{ fontSize: '0.85rem' }}
          >
            <HelpCircle size={14} />
            <span>Why this?</span>
          </button>
        </div>
      </div>

      {explanation && (
        <ExplanationPopover explanation={explanation} onClose={() => setExplanation(null)} />
      )}
    </div>
  );
};
