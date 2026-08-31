export function FollowUpQuestionChips({ questions }: { questions: string[] }) {
  if (questions.length === 0) return null

  return (
    <div className="flex flex-wrap gap-2 pl-1">
      {questions.map((q) => (
        <span
          key={q}
          className="rounded-full border border-coral/40 bg-coral/10 px-3 py-1 text-xs font-medium text-coral-dark dark:text-coral-light"
        >
          {q}
        </span>
      ))}
    </div>
  )
}
