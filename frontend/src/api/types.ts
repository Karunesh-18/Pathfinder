// Mirrors backend/api_schemas.py exactly — keep in sync with that file.

export interface SkillEntry {
  skill: string
  level: string
}

export interface Profile {
  learner_id: string
  target_role: string | null
  current_skills: SkillEntry[]
  completed_courses: string[]
  time_budget_hours_per_week: number | null
  format_preference: string | null
  missing_fields: string[]
  follow_up_questions: string[]
  raw_text: string
  extraction_method: string
}

export interface SkillGap {
  skill: string
  required_level: string
  current_level: string
  weight: number
  gap_score: number
  priority_rank: number
}

export interface PathStep {
  step_index: number
  course_id: string
  title: string
  provider: string
  skill_gap_addressed: string
  milestone: boolean
  estimated_hours: number
  cumulative_hours: number
  estimated_completion_week: number | null
}

export interface ExplainedStep {
  step: PathStep
  rationale: string
}

export interface ReplanResult {
  learner_id: string
  completed_course_id: string | null
  skill_updates: { skill: string; level: string }[]
  total_gap_before: number
  total_gap_after: number
  replan_triggered: boolean
  new_path_step_count: number
}

export interface SkillRadarPoint {
  skill: string
  required_level: string
  current_level: string
  required_value: number
  current_value: number
}

export interface HistoryItem {
  course_id: string
  title: string
  provider: string
  estimated_hours: number
}

export interface TimelineStep {
  step_index: number
  title: string
  provider: string
  milestone: boolean
  cumulative_hours: number
  estimated_completion_week: number | null
}

export interface NextAction {
  step_index: number
  title: string
  provider: string
  skill_gap_addressed: string
}

export interface SummaryStats {
  completed_courses: number
  remaining_steps: number
  completed_hours: number
  remaining_hours: number
  overall_progress_pct: number
  weeks_remaining: number | null
}

export interface Dashboard {
  learner_id: string
  target_role: string
  skill_radar: SkillRadarPoint[]
  completed_history: HistoryItem[]
  remaining_timeline: TimelineStep[]
  next_action: NextAction | null
  summary: SummaryStats
}

export interface Course {
  id: string
  title: string
  provider: string
  url: string | null
  description: string
  skills_taught: string[]
  level: string | null
  format: string | null
  target_roles: string[]
  prerequisites: string[]
  estimated_hours: number | null
  source: string
}

export interface SystemStatus {
  profile_store_backend: string
  path_store_backend: string
  course_kb_backend: string
  taxonomy_store_backend: string
  llm_configured: boolean
}
