import React from 'react';

export default function EnvironmentOverlay({ telemetry }) {
  const { environment = 'SIMULATION • DEMO', crowdDensity = 'moderate', recommendedDirection = 'straight' } = telemetry;

  const getCrowdLabel = () => {
    switch (crowdDensity.toLowerCase()) {
      case 'high':
        return 'High';
      case 'low':
        return 'Low';
      default:
        return 'Moderate';
    }
  };

  const getDirectionLabel = () => {
    switch (recommendedDirection.toLowerCase()) {
      case 'left':
        return '← LEFT';
      case 'right':
        return '→ RIGHT';
      default:
        return '↑ STRAIGHT';
    }
  };

  return (
    <div className="environment-overlay-card">
      <div className="env-item">
        <span className="env-label">Environment</span>
        <span className="env-val">{environment}</span>
      </div>
      <div className="env-item">
        <span className="env-label">Crowd</span>
        <span className={`env-val crowd-${crowdDensity.toLowerCase()}`}>
          {getCrowdLabel()}
        </span>
      </div>
      <div className="env-item">
        <span className="env-label">Direction</span>
        <span className="env-val direction-highlight">
          {getDirectionLabel()}
        </span>
      </div>
    </div>
  );
}
