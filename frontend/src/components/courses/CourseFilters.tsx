export interface CourseFilterValues {
  role: string
  provider: string
  level: string
  search: string
}

interface CourseFiltersProps {
  roles: string[]
  providers: string[]
  levels: string[]
  values: CourseFilterValues
  onChange: (values: CourseFilterValues) => void
}

const selectClass =
  'rounded-lg border border-border bg-bg px-3 py-2 text-sm outline-none focus:border-navy'

export function CourseFilters({ roles, providers, levels, values, onChange }: CourseFiltersProps) {
  return (
    <div className="mb-5 flex flex-wrap gap-2">
      <input
        value={values.search}
        onChange={(e) => onChange({ ...values, search: e.target.value })}
        placeholder="Search courses or skills…"
        className={`min-w-[12rem] flex-1 ${selectClass}`}
      />
      <select value={values.role} onChange={(e) => onChange({ ...values, role: e.target.value })} className={selectClass}>
        <option value="">All roles</option>
        {roles.map((r) => (
          <option key={r} value={r}>
            {r}
          </option>
        ))}
      </select>
      <select
        value={values.provider}
        onChange={(e) => onChange({ ...values, provider: e.target.value })}
        className={selectClass}
      >
        <option value="">All providers</option>
        {providers.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
      <select value={values.level} onChange={(e) => onChange({ ...values, level: e.target.value })} className={selectClass}>
        <option value="">All levels</option>
        {levels.map((l) => (
          <option key={l} value={l}>
            {l}
          </option>
        ))}
      </select>
    </div>
  )
}
