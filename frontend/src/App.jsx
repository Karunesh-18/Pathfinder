import React from 'react';
import { LearnerProvider, useLearner } from './context/LearnerContext';
import { AppShell } from './components/AppShell';
import { ChatWindow } from './components/ChatWindow';
import { DashboardSummaryCard } from './components/DashboardSummaryCard';
import { RoadmapTimeline } from './components/RoadmapTimeline';
import { ResourceCard } from './components/ResourceCard';
import { FeedbackBox } from './components/FeedbackBox';
import { SkillMasteryChart } from './components/SkillMasteryChart';

const MainContent = () => {
  const { activeScreen, recommendations } = useLearner();

  switch (activeScreen) {
    case 'onboarding':
      return <ChatWindow title="AI Conversational Onboarding" mode="onboarding" />;
    case 'home':
      return <DashboardSummaryCard />;
    case 'roadmap':
      return <RoadmapTimeline />;
    case 'resources':
      return (
        <div>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Personalized Resource Recommendations</h2>
          <div className="grid-2">
            {recommendations.map((rec) => (
              <ResourceCard key={rec.resource_id} recommendation={rec} />
            ))}
          </div>
        </div>
      );
    case 'session':
      return <FeedbackBox resourceId="res_py_01" />;
    case 'progress':
      return <SkillMasteryChart />;
    case 'mentor':
      return <ChatWindow title="AI Mentor & Path Explainer" mode="mentor" />;
    default:
      return <DashboardSummaryCard />;
  }
};

export function App() {
  return (
    <LearnerProvider>
      <AppShell>
        <MainContent />
      </AppShell>
    </LearnerProvider>
  );
}

export default App;
