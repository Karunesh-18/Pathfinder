import React from 'react';
import { useLearner } from '../context/LearnerContext';
import { Target, Award, Clock, Activity, ArrowRight } from 'lucide-react';

export const DashboardSummaryCard = () => {
  const { profile, dashboard, setActiveScreen } = useLearner();

  if (!dashboard) return <div className="glass-panel" style={{ padding: '2rem' }}>Loading Dashboard...</div>;

  const twinState = profile?.digital_twin?.state || {};
  const pace = twinState.pace || { value: 'moderate', confidence: 0.6 };
  const diffFit = twinState.difficulty_fit || { value: 'good', confidence: 0.7 };
  const emotion = twinState.emotion || { value: 'neutral', confidence: 0.5 };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="glass-panel glow-card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
          <div>
            <div className="badge badge-cyan" style={{ marginBottom: '0.5rem' }}>Goal & Target Role</div>
            <h2 style={{ fontSize: '1.5rem', margin: '0 0 0.25rem 0' }}>{dashboard.goal}</h2>
            <p style={{ color: 'var(--text-muted)', margin: 0 }}>Targeting Role: <strong>{dashboard.target_role}</strong></p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--accent-emerald)', lineHeight: 1 }}>
              {dashboard.career_readiness_pct}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Skill Overlap vs Role</div>
          </div>
        </div>

        {/* State estimations explicitly labeled with confidence */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.75rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Estimated Pace</div>
            <div style={{ fontWeight: 600, color: 'var(--accent-cyan)' }}>{pace.value} (conf: {Math.round(pace.confidence * 100)}%)</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.75rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Difficulty Fit</div>
            <div style={{ fontWeight: 600, color: 'var(--accent-indigo)' }}>{diffFit.value} (conf: {Math.round(diffFit.confidence * 100)}%)</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.75rem', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Learner State</div>
            <div style={{ fontWeight: 600, color: 'var(--accent-amber)' }}>{emotion.value} (conf: {Math.round(emotion.confidence * 100)}%)</div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity style={{ color: 'var(--accent-cyan)' }} />
            Next Recommended Action
          </h3>
          {dashboard.next_actions && dashboard.next_actions.length > 0 ? (
            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '12px' }}>
              <div style={{ fontWeight: 600, fontSize: '1.05rem' }}>{dashboard.next_actions[0].title}</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Type: {dashboard.next_actions[0].type} • Due in {dashboard.next_actions[0].due_in_days} days
              </div>
              <button
                className="btn-primary"
                style={{ marginTop: '1rem', width: '100%', justifyContent: 'center' }}
                onClick={() => setActiveScreen('session')}
              >
                <span>Start Learning Session</span>
                <ArrowRight size={16} />
              </button>
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)' }}>No pending actions.</p>
          )}
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Award style={{ color: 'var(--accent-amber)' }} />
            Latest Path Adaptation
          </h3>
          <div style={{ background: 'rgba(251, 191, 36, 0.1)', border: '1px solid rgba(251, 191, 36, 0.3)', padding: '1rem', borderRadius: '12px' }}>
            <p style={{ margin: 0, fontSize: '0.95rem', color: '#fef3c7' }}>
              {dashboard.latest_change_summary || "Roadmap generated based on your digital twin."}
            </p>
          </div>
          <button
            className="btn-secondary"
            style={{ marginTop: '1rem', width: '100%', justifyContent: 'center' }}
            onClick={() => setActiveScreen('roadmap')}
          >
            Inspect Interactive Roadmap
          </button>
        </div>
      </div>
    </div>
  );
};
