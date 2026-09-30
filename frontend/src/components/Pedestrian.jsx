import React from 'react';

export default function Pedestrian({
  x = 50,
  y = 50,
  scale = 1,
  opacity = 0.85,
  color = '#d1d5db',
}) {
  const width = 20 * scale;
  const height = 34 * scale;

  return (
    <g
      transform={`translate(${x}, ${y})`}
      style={{
        opacity,
        transition:
          'transform 0.6s ease, opacity 0.6s ease',
      }}
    >
      {/* Computer vision detection box */}
      <rect
        x={-width / 2}
        y={-height}
        width={width}
        height={height}
        fill="none"
        stroke="rgba(255,255,255,0.5)"
        strokeWidth="0.8"
        strokeDasharray="3 2"
      />

      {/* head */}
      <circle
        cx="0"
        cy={-height + 5}
        r={3.5 * scale}
        fill={color}
      />

      {/* body */}
      <path
        d={`
          M ${-4 * scale} ${-height + 11 * scale}
          C ${-4 * scale} ${-height + 8 * scale},
            ${4 * scale} ${-height + 8 * scale},
            ${4 * scale} ${-height + 11 * scale}

          L ${3 * scale} ${-4 * scale}

          L ${1 * scale} ${-4 * scale}
          L ${0} ${-15 * scale}

          L ${-1 * scale} ${-4 * scale}
          L ${-3 * scale} ${-4 * scale}

          Z
        `}
        fill={color}
      />

      {/* detection label */}
      <text
        x={-width / 2}
        y={-height - 5}
        fill="rgba(255,255,255,0.72)"
        fontSize="4"
        fontFamily="Inter, sans-serif"
        letterSpacing="0.4"
      >
        PERSON
      </text>
    </g>
  );
}