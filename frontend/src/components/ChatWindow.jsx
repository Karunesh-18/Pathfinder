import React, { useState } from 'react';
import { useLearner } from '../context/LearnerContext';
import { ClarifyingQuestionBubble } from './ClarifyingQuestionBubble';
import { Send, Bot, User, Sparkles } from 'lucide-react';

export const ChatWindow = ({ title, mode = 'onboarding' }) => {
  const { sendChatMessage, setActiveScreen } = useLearner();
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: mode === 'onboarding'
        ? "Hello! I am your PathFinder Adaptive Learning Agent. What role or skill goal would you like to achieve? (e.g. 'I want to become a Data Scientist in 8 weeks, spending 10 hrs/week')"
        : "Hi! I am your AI Mentor. Ask me anything about your current roadmap, skill gaps, or why specific resources were chosen.",
      isQuestion: false
    }
  ]);
  const [isSending, setIsSending] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isSending) return;

    const userText = input;
    setInput('');
    setMessages(prev => [...prev, { sender: 'user', text: userText }]);
    setIsSending(true);

    const resp = await sendChatMessage(userText);

    setMessages(prev => [
      ...prev,
      {
        sender: 'bot',
        text: resp.reply,
        isQuestion: resp.asked_clarifying_question
      }
    ]);
    setIsSending(false);
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', height: '600px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', paddingBottom: '0.75rem', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles style={{ color: 'var(--accent-cyan)' }} />
          <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{title}</h3>
        </div>
        {mode === 'onboarding' && (
          <button className="btn-secondary" style={{ fontSize: '0.8rem' }} onClick={() => setActiveScreen('home')}>
            View Dashboard →
          </button>
        )}
      </div>

      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem', paddingRight: '0.5rem' }}>
        {messages.map((m, idx) => (
          <div key={idx} style={{
            display: 'flex',
            gap: '0.75rem',
            alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '85%'
          }}>
            {m.sender === 'bot' && (
              <div style={{ background: 'rgba(56, 189, 248, 0.2)', padding: '0.5rem', borderRadius: '50%', height: '36px', width: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Bot size={20} style={{ color: 'var(--accent-cyan)' }} />
              </div>
            )}

            <div style={{
              background: m.sender === 'user' ? 'linear-gradient(135deg, #38bdf8 0%, #818cf8 100%)' : 'rgba(255, 255, 255, 0.06)',
              color: m.sender === 'user' ? '#0f172a' : 'var(--text-main)',
              padding: '0.85rem 1.15rem',
              borderRadius: '16px',
              fontSize: '0.95rem',
              fontWeight: m.sender === 'user' ? 500 : 400
            }}>
              {m.isQuestion ? (
                <ClarifyingQuestionBubble text={m.text} />
              ) : (
                <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{m.text}</p>
              )}
            </div>

            {m.sender === 'user' && (
              <div style={{ background: 'rgba(255, 255, 255, 0.1)', padding: '0.5rem', borderRadius: '50%', height: '36px', width: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <User size={20} />
              </div>
            )}
          </div>
        ))}
        {isSending && (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontStyle: 'italic' }}>
            AI Agent is reasoning...
          </div>
        )}
      </div>

      <form onSubmit={handleSend} style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={mode === 'onboarding' ? "Describe your career goal or target skills..." : "Ask a mentor question..."}
          style={{
            flex: 1,
            background: 'rgba(0,0,0,0.25)',
            border: '1px solid rgba(255,255,255,0.15)',
            borderRadius: 'var(--radius-md)',
            padding: '0.75rem 1rem',
            color: '#fff',
            outline: 'none'
          }}
        />
        <button type="submit" className="btn-primary" disabled={isSending}>
          <Send size={16} />
          <span>Send</span>
        </button>
      </form>
    </div>
  );
};
