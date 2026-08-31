import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts'

import type { SkillRadarPoint } from '../../api/types'

const AXIS_COLOR = '#94a3b8'

export function SkillRadarChart({ points }: { points: SkillRadarPoint[] }) {
  if (points.length === 0) {
    return <p className="text-sm text-fg-muted">No skill data yet.</p>
  }

  const data = points.map((p) => ({
    skill: p.skill,
    Required: p.required_value,
    Current: p.current_value,
  }))

  return (
    <div className="h-64 w-full sm:h-80 lg:h-96">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} outerRadius="72%">
          <PolarGrid stroke={AXIS_COLOR} strokeOpacity={0.35} />
          <PolarAngleAxis dataKey="skill" tick={{ fill: AXIS_COLOR, fontSize: 11 }} />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 3]}
            tickCount={4}
            tick={{ fill: AXIS_COLOR, fontSize: 10 }}
            axisLine={false}
          />
          <Radar name="Required" dataKey="Required" stroke="#1e3a8a" fill="#1e3a8a" fillOpacity={0.15} />
          <Radar name="Current" dataKey="Current" stroke="#fb7185" fill="#fb7185" fillOpacity={0.35} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{ fontSize: 12, borderRadius: 8 }}
            formatter={(value) =>
              ['none', 'beginner', 'intermediate', 'advanced'][Number(value)] ?? String(value)
            }
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
