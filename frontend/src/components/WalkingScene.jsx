import React, { useEffect, useMemo, useState } from 'react';
import Pedestrian from './Pedestrian';
import NavigationGuidance from './NavigationGuidance';
import EnvironmentOverlay from './EnvironmentOverlay';

const POV_SCENARIOS = [
  {
    name: 'CLEAR STREET',
    crowd: 'low',
    obstacle: false,
    direction: 'straight',
  },
  {
    name: 'PEDESTRIAN CROSSING',
    crowd: 'moderate',
    obstacle: false,
    direction: 'right',
  },
  {
    name: 'DENSE CROWD',
    crowd: 'high',
    obstacle: false,
    direction: 'left',
  },
  {
    name: 'OBSTACLE DETECTED',
    crowd: 'moderate',
    obstacle: true,
    direction: 'left',
  },
  {
    name: 'CROWD CONVERGENCE',
    crowd: 'high',
    obstacle: false,
    direction: 'right',
  },
  {
    name: 'OPEN CORRIDOR',
    crowd: 'low',
    obstacle: false,
    direction: 'straight',
  },
];

export default function WalkingScene({ telemetry }) {
  const [scenarioIndex, setScenarioIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setScenarioIndex((current) => (current + 1) % POV_SCENARIOS.length);
    }, 5000);

    return () => clearInterval(timer);
  }, []);

  const scenario = POV_SCENARIOS[scenarioIndex];

  const crowdDensity = scenario.crowd;
  const obstacleDetected =
    scenario.obstacle || Boolean(telemetry?.obstacleDetected);

  const recommendedDirection =
    telemetry?.recommendedDirection || scenario.direction;

  const pedestrians = useMemo(() => {
    if (crowdDensity === 'high') {
      return [
        { x: 122, y: 142, scale: 0.58, opacity: 0.72 },
        { x: 157, y: 128, scale: 0.62, opacity: 0.78 },
        { x: 193, y: 143, scale: 0.67, opacity: 0.82 },
        { x: 229, y: 132, scale: 0.64, opacity: 0.78 },
        { x: 267, y: 147, scale: 0.7, opacity: 0.82 },
        { x: 303, y: 137, scale: 0.62, opacity: 0.76 },

        { x: 115, y: 192, scale: 0.78, opacity: 0.82 },
        { x: 158, y: 181, scale: 0.82, opacity: 0.86 },
        { x: 203, y: 193, scale: 0.88, opacity: 0.9 },
        { x: 250, y: 183, scale: 0.84, opacity: 0.86 },
        { x: 292, y: 198, scale: 0.9, opacity: 0.88 },

        { x: 135, y: 246, scale: 0.98, opacity: 0.9 },
        { x: 190, y: 235, scale: 1.02, opacity: 0.94 },
        { x: 255, y: 248, scale: 1.0, opacity: 0.92 },
      ];
    }

    if (crowdDensity === 'moderate') {
      return [
        { x: 132, y: 135, scale: 0.58, opacity: 0.72 },
        { x: 265, y: 139, scale: 0.62, opacity: 0.74 },
        { x: 173, y: 177, scale: 0.78, opacity: 0.84 },
        { x: 231, y: 170, scale: 0.82, opacity: 0.86 },
        { x: 116, y: 231, scale: 0.94, opacity: 0.88 },
        { x: 290, y: 220, scale: 0.96, opacity: 0.9 },
      ];
    }

    return [
      { x: 118, y: 145, scale: 0.56, opacity: 0.68 },
      { x: 286, y: 150, scale: 0.58, opacity: 0.7 },
      { x: 145, y: 220, scale: 0.9, opacity: 0.78 },
      { x: 274, y: 225, scale: 0.92, opacity: 0.8 },
    ];
  }, [crowdDensity]);

  return (
    <section className="walking-scene-panel">
      <div className="panel-title-area">
        <h2 className="panel-main-title">
          SMART GLASSES · FIRST-PERSON VIEW
        </h2>

        <span className="panel-sub-title">
          Camera inside spectacles
        </span>
      </div>

      <div className="scene-viewport-container smart-glasses-viewport">

        {/* Minimal smart-glasses camera HUD */}
        <div className="smart-glasses-topbar">
          <div className="smart-glasses-brand">
            SMART GLASSES
          </div>

          <div className="smart-glasses-live">
            <span className="smart-live-dot" />
            LIVE VISION
          </div>
        </div>

        <div className="smart-glasses-scenario">
          {scenario.name}
        </div>

        <svg
          className="street-perspective-canvas smart-glasses-canvas"
          viewBox="0 0 400 360"
          preserveAspectRatio="none"
        >
          <defs>

            {/* Sky */}
            <linearGradient
              id="visionSky"
              x1="0"
              y1="0"
              x2="0"
              y2="1"
            >
              <stop
                offset="0%"
                stopColor="#111827"
              />

              <stop
                offset="100%"
                stopColor="#1f2937"
              />
            </linearGradient>

            {/* Street */}
            <linearGradient
              id="visionStreet"
              x1="0"
              y1="0"
              x2="0"
              y2="1"
            >
              <stop
                offset="0%"
                stopColor="#263446"
              />

              <stop
                offset="100%"
                stopColor="#0b111a"
              />
            </linearGradient>

            {/* Safe path */}
            <linearGradient
              id="safePath"
              x1="0"
              y1="1"
              x2="0"
              y2="0"
            >
              <stop
                offset="0%"
                stopColor="#ffffff"
                stopOpacity="0.11"
              />

              <stop
                offset="100%"
                stopColor="#ffffff"
                stopOpacity="0"
              />
            </linearGradient>

            {/* Crowd risk */}
            <radialGradient id="crowdRisk">
              <stop
                offset="0%"
                stopColor="#ef233c"
                stopOpacity="0.24"
              />

              <stop
                offset="100%"
                stopColor="#ef233c"
                stopOpacity="0"
              />
            </radialGradient>

            {/* Lens vignette */}
            <radialGradient id="lensVignette">
              <stop
                offset="55%"
                stopColor="#000000"
                stopOpacity="0"
              />

              <stop
                offset="100%"
                stopColor="#000000"
                stopOpacity="0.5"
              />
            </radialGradient>
          </defs>

          {/* =========================
              REAL-WORLD POV BACKGROUND
              ========================= */}

          <rect
            width="400"
            height="360"
            fill="url(#visionSky)"
          />

          {/* distant buildings */}
          <g opacity="0.45">
            <rect
              x="0"
              y="80"
              width="74"
              height="72"
              fill="#0a111c"
            />

            <rect
              x="78"
              y="66"
              width="56"
              height="86"
              fill="#111827"
            />

            <rect
              x="266"
              y="68"
              width="60"
              height="84"
              fill="#111827"
            />

            <rect
              x="330"
              y="84"
              width="70"
              height="68"
              fill="#0a111c"
            />
          </g>

          {/* distant horizon */}
          <line
            x1="0"
            y1="152"
            x2="400"
            y2="152"
            stroke="#ffffff"
            strokeOpacity="0.12"
            strokeWidth="1"
          />

          {/* road */}
          <polygon
            points="142,152 258,152 390,360 10,360"
            fill="url(#visionStreet)"
          />

          {/* sidewalks */}
          <polygon
            points="0,152 142,152 10,360 0,360"
            fill="#111b29"
          />

          <polygon
            points="258,152 400,152 400,360 390,360"
            fill="#111b29"
          />

          {/* road edges */}
          <line
            x1="142"
            y1="152"
            x2="10"
            y2="360"
            stroke="#ffffff"
            strokeOpacity="0.28"
            strokeWidth="2"
          />

          <line
            x1="258"
            y1="152"
            x2="390"
            y2="360"
            stroke="#ffffff"
            strokeOpacity="0.28"
            strokeWidth="2"
          />

          {/* road lane markings */}
          <line
            x1="174"
            y1="152"
            x2="94"
            y2="360"
            stroke="#ffffff"
            strokeOpacity="0.09"
            strokeWidth="1"
            strokeDasharray="10 10"
          />

          <line
            x1="226"
            y1="152"
            x2="306"
            y2="360"
            stroke="#ffffff"
            strokeOpacity="0.09"
            strokeWidth="1"
            strokeDasharray="10 10"
          />

          {/* =========================
              NAVIGATION CORRIDOR
              ========================= */}

          {recommendedDirection === 'left' && (
            <polygon
              points="178,345 92,345 142,152 183,152"
              fill="url(#safePath)"
            />
          )}

          {recommendedDirection === 'right' && (
            <polygon
              points="222,345 308,345 258,152 217,152"
              fill="url(#safePath)"
            />
          )}

          {recommendedDirection === 'straight' && (
            <polygon
              points="172,345 228,345 211,152 189,152"
              fill="url(#safePath)"
            />
          )}

          {/* =========================
              CROWD ANALYSIS
              ========================= */}

          {crowdDensity === 'high' && (
            <ellipse
              cx="200"
              cy="202"
              rx="102"
              ry="60"
              fill="url(#crowdRisk)"
              stroke="#ef233c"
              strokeOpacity="0.4"
              strokeWidth="1"
              strokeDasharray="5 6"
            />
          )}

          {/* =========================
              PEOPLE DETECTED BY VISION
              ========================= */}

          {pedestrians.map((person, index) => (
            <g key={index}>

              <Pedestrian
                x={person.x}
                y={person.y}
                scale={person.scale}
                opacity={person.opacity}
                color="#e5e7eb"
              />

              {/* CV detection box */}
              <rect
                x={person.x - 11 * person.scale}
                y={person.y - 27 * person.scale}
                width={22 * person.scale}
                height={38 * person.scale}
                fill="none"
                stroke="#d8dee8"
                strokeOpacity="0.55"
                strokeWidth="0.8"
                strokeDasharray="3 3"
              />

              {/* CV label */}
              <text
                x={person.x - 11 * person.scale}
                y={person.y - 31 * person.scale}
                fill="#d8dee8"
                fillOpacity="0.65"
                fontSize="5"
                fontFamily="Arial, sans-serif"
                letterSpacing="0.8"
              >
                PERSON
              </text>
            </g>
          ))}

          {/* =========================
              OBSTACLE DETECTION
              ========================= */}

          {obstacleDetected && (
            <g transform="translate(200 235)">

              <rect
                x="-25"
                y="-17"
                width="50"
                height="34"
                rx="4"
                fill="#05080d"
                fillOpacity="0.65"
                stroke="#fbbf24"
                strokeWidth="1.5"
              />

              <line
                x1="-13"
                y1="-9"
                x2="13"
                y2="9"
                stroke="#fbbf24"
                strokeWidth="4"
              />

              <line
                x1="13"
                y1="-9"
                x2="-13"
                y2="9"
                stroke="#fbbf24"
                strokeWidth="4"
              />

              <text
                x="-25"
                y="-23"
                fill="#fbbf24"
                fontSize="7"
                fontFamily="Arial, sans-serif"
                letterSpacing="0.8"
              >
                OBSTACLE
              </text>
            </g>
          )}

          {/* =========================
              CENTER VISION RETICLE
              ========================= */}

          <g
            transform="translate(200 180)"
            opacity="0.5"
          >
            <circle
              cx="0"
              cy="0"
              r="8"
              fill="none"
              stroke="#ffffff"
              strokeWidth="0.8"
            />

            <line
              x1="-13"
              y1="0"
              x2="-6"
              y2="0"
              stroke="#ffffff"
              strokeWidth="0.8"
            />

            <line
              x1="6"
              y1="0"
              x2="13"
              y2="0"
              stroke="#ffffff"
              strokeWidth="0.8"
            />

            <line
              x1="0"
              y1="-13"
              x2="0"
              y2="-6"
              stroke="#ffffff"
              strokeWidth="0.8"
            />

            <line
              x1="0"
              y1="6"
              x2="0"
              y2="13"
              stroke="#ffffff"
              strokeWidth="0.8"
            />
          </g>

          {/* =========================
              SMART GLASSES LENS EFFECT
              ========================= */}

          <rect
            width="400"
            height="360"
            fill="url(#lensVignette)"
            pointerEvents="none"
          />
        </svg>

        {/* Lens framing */}
        <div className="spectacle-lens-left" />
        <div className="spectacle-lens-right" />

        {/* Vision HUD */}
        <div className="vision-hud-bottom">
          <span>VISION INPUT · SPECTACLE CAM</span>
          <span>TRACKING · ACTIVE</span>
          <span>SCENE · {scenarioIndex + 1}/6</span>
        </div>

        <div className="vision-direction-indicator">
          {recommendedDirection === 'left' && '← SAFE PATH'}
          {recommendedDirection === 'right' && 'SAFE PATH →'}
          {recommendedDirection === 'straight' && '↑ PATH CLEAR'}
        </div>

        <NavigationGuidance telemetry={telemetry} />
        <EnvironmentOverlay telemetry={telemetry} />
      </div>
    </section>
  );
}