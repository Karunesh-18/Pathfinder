import { Badge } from '../common/Badge'

export function ExtractionMethodBadge({ method }: { method: string }) {
  const isLlm = method.toLowerCase().includes('llm')
  return <Badge tone={isLlm ? 'coral' : 'neutral'}>{isLlm ? 'AI-generated' : 'Rule-based'}</Badge>
}
