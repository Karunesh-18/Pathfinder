import React, { createContext, useContext, useState, useEffect } from 'react';

const LearnerContext = createContext();

export const LearnerProvider = ({ children }) => {
  const [userId, setUserId] = useState('demo_user_123');
  const [activeScreen, setActiveScreen] = useState('onboarding'); // onboarding, home, roadmap, resources, session, progress, mentor
  const [profile, setProfile] = useState(null);
  const [path, setPath] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch all user state
  const refreshUserData = async () => {
    setLoading(true);
    try {
      // 1. Fetch Profile
      const profRes = await fetch(`/api/profile/${userId}`);
      if (profRes.ok) {
        const profData = await profRes.json();
        setProfile(profData);
      }

      // 2. Fetch Path
      const pathRes = await fetch(`/api/path/${userId}`);
      if (pathRes.ok) {
        const pathData = await pathRes.json();
        setPath(pathData);
      }

      // 3. Fetch Dashboard
      const dashRes = await fetch(`/api/dashboard/${userId}`);
      if (dashRes.ok) {
        const dashData = await dashRes.json();
        setDashboard(dashData);
      }

      // 4. Fetch Recommendations
      const recRes = await fetch(`/api/recommend/${userId}`);
      if (recRes.ok) {
        const recData = await recRes.json();
        setRecommendations(recData.recommendations || []);
      }
    } catch (err) {
      console.error('Error fetching learner state:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUserData();
  }, [userId]);

  // Send Chat Message
  const sendChatMessage = async (message) => {
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, message })
      });
      const data = await res.json();
      await refreshUserData();
      return data;
    } catch (err) {
      console.error('Error sending chat message:', err);
      return { reply: 'Sorry, failed to reach AI service.', asked_clarifying_question: false };
    }
  };

  // Report Progress
  const reportProgress = async (resourceId, quizScore = 0.85, timeSpentMin = 25) => {
    try {
      const res = await fetch(`/api/progress/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resource_id: resourceId,
          status: 'done',
          quiz_score: quizScore,
          time_spent_min: timeSpentMin
        })
      });
      const data = await res.json();
      await refreshUserData();
      return data;
    } catch (err) {
      console.error('Error reporting progress:', err);
    }
  };

  // Submit Feedback
  const submitFeedback = async (resourceId, text) => {
    try {
      const res = await fetch(`/api/feedback/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resource_id: resourceId, text })
      });
      const data = await res.json();
      await refreshUserData();
      return data;
    } catch (err) {
      console.error('Error submitting feedback:', err);
    }
  };

  // Fetch Explanation
  const getExplanation = async (resourceId) => {
    try {
      const res = await fetch(`/api/explain/${userId}/${resourceId}`);
      if (res.ok) {
        const data = await res.json();
        return data.explanation;
      }
    } catch (err) {
      console.error('Error fetching explanation:', err);
    }
    return 'Explanation unavailable.';
  };

  return (
    <LearnerContext.Provider value={{
      userId,
      activeScreen,
      setActiveScreen,
      profile,
      path,
      dashboard,
      recommendations,
      loading,
      refreshUserData,
      sendChatMessage,
      reportProgress,
      submitFeedback,
      getExplanation
    }}>
      {children}
    </LearnerContext.Provider>
  );
};

export const useLearner = () => useContext(LearnerContext);
