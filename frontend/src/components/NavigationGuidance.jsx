import React from 'react';

export default function NavigationGuidance({ telemetry }) {
  const { crowdDensity, recommendedDirection, obstacleDetected, guidanceText } = telemetry;

  return (
    <div className="navigation-guidance-overlay">
      {/* Obstacle warning alert */}
      {obstacleDetected && (
        <div className="guidance-tag obstacle">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <span>⚠ OBSTACLE AHEAD</span>
        </div>
      )}

      {/* Crowded zone tag */}
      {crowdDensity === 'high' && (
        <div className="guidance-tag crowded">
          <span>CROWDED AREA</span>
        </div>
      )}

      {/* Direction guidance indicator arrow & text */}
      {guidanceText && (
        <div className={`guidance-arrow-card ${recommendedDirection}`}>
          <span className="arrow-text">{guidanceText}</span>
        </div>
      )}
    </div>
  );
}
