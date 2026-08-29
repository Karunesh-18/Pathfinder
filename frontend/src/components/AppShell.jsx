import React from 'react';
import { useLearner } from '../context/LearnerContext';
import { Compass, LayoutDashboard, Map, BookOpen, BarChart3, MessageSquare, PlayCircle } from 'lucide-react';

export const AppShell = ({ children }) => {
  const { activeScreen, setActiveScreen, dashboard } = useLearner();

  const navItems = [
    { id: 'onboarding', label: 'Onboarding Chat', icon: Compass },
    { id: 'home', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'roadmap', label: 'Roadmap', icon: Map },
    { id: 'resources', label: 'Resources', icon: BookOpen },
    { id: 'session', label: 'Learning Session', icon: PlayCircle },
    { id: 'progress', label: 'Skill Mastery', icon: BarChart3 },
    { id: 'mentor', label: 'AI Mentor', icon: MessageSquare },
  ];

  return (
    <div className="app-container">
      <header className="glass-panel nav-bar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Compass style={{ color: 'var(--accent-cyan)', width: 28, height: 28 }} />
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>PathFinder</h2>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>Adaptive Learning Agent</p>
          </div>
        </div>

        <nav className="nav-tabs">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeScreen === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveScreen(item.id)}
                className={`nav-tab ${isActive ? 'active' : ''}`}
              >
                <Icon size={16} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {dashboard && (
          <div className="badge badge-emerald" style={{ gap: '0.4rem' }}>
            <span>Target Role Match:</span>
            <strong>{dashboard.career_readiness_pct}%</strong>
          </div>
        )}
      </header>

      <main>{children}</main>
    </div>
  );
};
