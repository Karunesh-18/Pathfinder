import { useState } from 'react'
import type { FormEvent } from 'react'

import type { ProfileUpdate } from '../../api/learnerApi'
import type { Profile, Role, SkillEntry } from '../../api/types'
import { Badge } from '../common/Badge'

const FORMAT_OPTIONS = ['self-paced', 'video', 'live']
const LEVEL_OPTIONS = ['beginner', 'intermediate', 'advanced']

const inputClass =
  'w-full rounded-lg border border-border bg-bg px-3.5 py-2.5 text-sm outline-none focus:border-navy'
const labelClass = 'mb-1 block text-xs font-medium uppercase tracking-wide text-fg-muted'

interface ProfileEditFormProps {
  profile: Profile
  roles: Role[]
  onSave: (updates: ProfileUpdate) => void
  isPending: boolean
}

export function ProfileEditForm({ profile, roles, onSave, isPending }: ProfileEditFormProps) {
  const [targetRole, setTargetRole] = useState(profile.target_role ?? '')
  const [timeBudget, setTimeBudget] = useState(profile.time_budget_hours_per_week?.toString() ?? '')
  const [formatPreference, setFormatPreference] = useState(profile.format_preference ?? '')
  const [skills, setSkills] = useState<SkillEntry[]>(profile.current_skills)
  const [newSkill, setNewSkill] = useState('')
  const [newLevel, setNewLevel] = useState('beginner')

  function handleAddSkill() {
    const skill = newSkill.trim()
    if (!skill) return
    setSkills((prev) => [
      ...prev.filter((s) => s.skill.toLowerCase() !== skill.toLowerCase()),
      { skill, level: newLevel },
    ])
    setNewSkill('')
  }

  function handleRemoveSkill(skill: string) {
    setSkills((prev) => prev.filter((s) => s.skill !== skill))
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    onSave({
      target_role: targetRole || null,
      time_budget_hours_per_week: timeBudget ? Number(timeBudget) : null,
      format_preference: formatPreference || null,
      current_skills: skills,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label htmlFor="targetRole" className={labelClass}>
          Target role
        </label>
        <select
          id="targetRole"
          value={targetRole}
          onChange={(e) => setTargetRole(e.target.value)}
          className={inputClass}
        >
          <option value="">Not set</option>
          {roles.map((r) => (
            <option key={r.role} value={r.role}>
              {r.role}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="timeBudget" className={labelClass}>
          Time budget (hours/week)
        </label>
        <input
          id="timeBudget"
          type="number"
          min={1}
          max={80}
          value={timeBudget}
          onChange={(e) => setTimeBudget(e.target.value)}
          className={inputClass}
        />
      </div>

      <div>
        <label htmlFor="formatPreference" className={labelClass}>
          Format preference
        </label>
        <select
          id="formatPreference"
          value={formatPreference}
          onChange={(e) => setFormatPreference(e.target.value)}
          className={inputClass}
        >
          <option value="">Not set</option>
          {FORMAT_OPTIONS.map((f) => (
            <option key={f} value={f}>
              {f}
            </option>
          ))}
        </select>
      </div>

      <div>
        <span className={labelClass}>Current skills</span>
        <div className="mb-2 flex flex-wrap gap-2">
          {skills.length === 0 && <p className="text-sm text-fg-muted">No skills added yet.</p>}
          {skills.map((s) => (
            <button
              key={s.skill}
              type="button"
              onClick={() => handleRemoveSkill(s.skill)}
              title="Remove"
              className="transition hover:opacity-70"
            >
              <Badge tone="navy">
                {s.skill} · {s.level} ✕
              </Badge>
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            value={newSkill}
            onChange={(e) => setNewSkill(e.target.value)}
            placeholder="Add a skill (e.g. SQL)"
            className={`flex-1 ${inputClass}`}
          />
          <select value={newLevel} onChange={(e) => setNewLevel(e.target.value)} className="rounded-lg border border-border bg-bg px-2 text-sm outline-none focus:border-navy">
            {LEVEL_OPTIONS.map((l) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={handleAddSkill}
            className="shrink-0 rounded-lg border border-border px-3 text-sm font-medium hover:bg-bg-raised"
          >
            Add
          </button>
        </div>
      </div>

      <button
        type="submit"
        disabled={isPending}
        className="rounded-full bg-coral px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-coral-dark disabled:opacity-50"
      >
        {isPending ? 'Saving…' : 'Save changes'}
      </button>
    </form>
  )
}
