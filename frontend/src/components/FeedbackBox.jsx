import React, { useState } from 'react';
import { useLearner } from '../context/LearnerContext';
import { CheckCircle, MessageSquare, Award } from 'lucide-react';

export const FeedbackBox = ({ resourceId = 'res_py_01' }) => {
  const { reportProgress, submitFeedback, setActiveScreen } = useLearner();
  const [quizScore, setQuizScore] = useState(85);
  const [timeSpent, setTimeSpent] = useState(25);
  const [feedbackText, setFeedbackText] = useState('');
  const [isCompleted, setIsCompleted] = useState(false);
  const [feedbackResponse, setFeedbackResponse] = useState(null);

  const handleMarkComplete = async (e) => {
    e.preventDefault();
    await reportProgress(resourceId, quizScore / 100, timeSpent);
    setIsCompleted(true);
  };

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    if (!feedbackText.trim()) return;
    const res = await submitFeedback(resourceId, feedbackText);
    setFeedbackResponse(res);
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', maxWidth: '650px', margin: '0 auto' }}>
      <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Award style={{ color: 'var(--accent-cyan)' }} />
        Learning Session Progress & Feedback
      </h3>

      {!isCompleted ? (
        <form onSubmit={handleMarkComplete} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
              Quiz Score (%):
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={quizScore}
              onChange={(e) => setQuizScore(Number(e.target.value))}
              style={{
                width: '100%',
                background: 'rgba(0,0,0,0.25)',
                border: '1px solid rgba(255,255,255,0.15)',
                borderRadius: 'var(--radius-sm)',
                padding: '0.6rem 0.8rem',
                color: '#fff'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
              Time Spent (minutes):
            </label>
            <input
              type="number"
              value={timeSpent}
              onChange={(e) => setTimeSpent(Number(e.target.value))}
              style={{
                width: '100%',
                background: 'rgba(0,0,0,0.25)',
                border: '1px solid rgba(255,255,255,0.15)',
                borderRadius: 'var(--radius-sm)',
                padding: '0.6rem 0.8rem',
                color: '#fff'
              }}
            />
          </div>

          <button type="submit" className="btn-primary" style={{ justifyContent: 'center', marginTop: '0.5rem' }}>
            <CheckCircle size={16} />
            <span>Mark Complete & Submit Evidence</span>
          </button>
        </form>
      ) : (
        <div>
          <div style={{ background: 'rgba(52, 211, 153, 0.15)', border: '1px solid rgba(52, 211, 153, 0.3)', padding: '1rem', borderRadius: '12px', marginBottom: '1.5rem' }}>
            <strong style={{ color: 'var(--accent-emerald)' }}>Evidence Recorded!</strong>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.9rem' }}>
              Your digital twin has been updated with quiz score ({quizScore}%) and pace evidence.
            </p>
          </div>

          <form onSubmit={handleFeedbackSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                How was your learning experience? (Optional feedback for dynamic replanning)
              </label>
              <textarea
                rows="3"
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                placeholder="e.g., 'Felt a bit fast on SQL JOINs, but quiz was easy' or 'Super clear explanation!'"
                style={{
                  width: '100%',
                  background: 'rgba(0,0,0,0.25)',
                  border: '1px solid rgba(255,255,255,0.15)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '0.6rem 0.8rem',
                  color: '#fff',
                  resize: 'vertical'
                }}
              />
            </div>

            <button type="submit" className="btn-secondary" style={{ justifyContent: 'center' }}>
              <MessageSquare size={16} />
              <span>Submit Qualitative Feedback</span>
            </button>
          </form>

          {feedbackResponse && (
            <div style={{ marginTop: '1.5rem', background: 'rgba(56, 189, 248, 0.1)', border: '1px solid rgba(56, 189, 248, 0.3)', padding: '1rem', borderRadius: '12px' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>Signal Extracted:</div>
              <pre style={{ fontSize: '0.8rem', margin: '0.5rem 0', color: 'var(--text-muted)' }}>
                {JSON.stringify(feedbackResponse.extracted, null, 2)}
              </pre>
              {feedbackResponse.followup_question && (
                <div style={{ color: 'var(--accent-amber)', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                  <strong>Follow-up:</strong> {feedbackResponse.followup_question}
                </div>
              )}
            </div>
          )}

          <button
            className="btn-primary"
            style={{ width: '100%', marginTop: '1.5rem', justifyContent: 'center' }}
            onClick={() => setActiveScreen('roadmap')}
          >
            Inspect Updated Roadmap →
          </button>
        </div>
      )}
    </div>
  );
};
