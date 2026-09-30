import React, { useState } from 'react';
import { Mail, Lock, ArrowRight } from 'lucide-react';

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();

    setError('');

    if (!email || !password) {
      setError('Please enter your email and password.');
      return;
    }

    // Demo authentication
    if (
      email === 'admin@walkjourney.ai' &&
      password === 'walkjourney'
    ) {
      onLogin();
      return;
    }

    setError('Invalid email or password.');
  };

  return (
    <div className="login-page">
      <div className="login-background-glow" />

      <div className="login-card">
        <div className="login-brand">
          <span className="login-brand-name">
            WALKJOURNEY AI
          </span>

          <span className="login-brand-subtitle">
            AI - Based Crowd Navigation and Collision Prevention System
          </span>
        </div>

        <div className="login-heading">
          <h1>Welcome back</h1>
          <p>Sign in to continue to Lyra.</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="login-field">
            <label htmlFor="email">Email</label>

            <div className="login-input-wrapper">
              <Mail size={18} />
              <input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
              />
            </div>
          </div>

          <div className="login-field">
            <label htmlFor="password">Password</label>

            <div className="login-input-wrapper">
              <Lock size={18} />
              <input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
              />
            </div>
          </div>

          {error && (
            <div className="login-error">
              {error}
            </div>
          )}

          <button type="submit" className="login-button">
            <span>Sign in</span>
            <ArrowRight size={18} />
          </button>
        </form>

        <div className="login-footer">
          <span>Powered by</span>
          <strong>Lyra</strong>
          <span>•</span>
          <span>WalkJourney AI</span>
        </div>
      </div>
    </div>
  );
}