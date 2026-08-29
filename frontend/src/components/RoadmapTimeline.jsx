import React from 'react';
import { useLearner } from '../context/LearnerContext';
import { MilestoneCard } from './MilestoneCard';
import { ChangeSummaryBanner } from './ChangeSummaryBanner';
import { GitCommit, Sparkles } from 'lucide-react';

export const RoadmapTimeline = () => {
  const { path, refreshUserData } = useLearner();

  if (!path || !path.milestones) {
    return <div className="glass-panel" style={{ padding: '2rem' }}>Generating Personalized Learning Roadmap...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <GitCommit style={{ color: 'var(--accent-cyan)' }} />
            Adaptive Learning Roadmap
          </h2>
          <p style={{ color: 'var(--text-muted)', margin: 0 }}>Version {path.path_version} • Self-rebuilding from evidence</p>
        </div>
        <button className="btn-secondary" onClick={refreshUserData}>
          <Sparkles size={16} />
          <span>Refresh Roadmap</span>
        </button>
      </div>

      <ChangeSummaryBanner text={path.change_summary} />

      <div style={{ position: 'relative' }}>
        {path.milestones.map((ms, idx) => (
          <MilestoneCard key={ms.milestone_id || idx} milestone={ms} index={idx} />
        ))}
      </div>
    </div>
  );
};
