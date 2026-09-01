import type { Edge, Node } from '@xyflow/react'

import type { SkillTreeNode } from '../api/types'

const COLUMN_WIDTH = 300
const ROW_HEIGHT = 190

// Layout is precomputed server-side (taxonomy_store.compute_skill_tiers)
// as a "tier" per skill — this just buckets nodes into columns by tier
// and stacks same-tier nodes vertically. Deliberately no client-side
// graph-layout library (dagre/elkjs): the graph is small (10-14 nodes per
// role) and the backend already owns the "what depends on what" math.
export function buildTreeLayout(skills: SkillTreeNode[]): { nodes: Node[]; edges: Edge[] } {
  const countPerTier = new Map<number, number>()

  const nodes: Node[] = skills.map((skill) => {
    const row = countPerTier.get(skill.tier) ?? 0
    countPerTier.set(skill.tier, row + 1)
    return {
      id: skill.skill,
      type: 'skillNode',
      position: { x: skill.tier * COLUMN_WIDTH, y: row * ROW_HEIGHT },
      data: { skill },
      draggable: false,
    }
  })

  const edges: Edge[] = []
  for (const skill of skills) {
    for (const prerequisite of skill.prerequisites) {
      edges.push({
        id: `${prerequisite}->${skill.skill}`,
        source: prerequisite,
        target: skill.skill,
      })
    }
  }

  return { nodes, edges }
}
