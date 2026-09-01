import { Background, Controls, ReactFlow } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { useMemo } from 'react'

import type { SkillTreeNode } from '../../api/types'
import { buildTreeLayout } from '../../utils/treeLayout'
import { SkillNode } from './SkillNode'

const nodeTypes = { skillNode: SkillNode }

export function CourseTreeGraph({ skills }: { skills: SkillTreeNode[] }) {
  const { nodes, edges } = useMemo(() => buildTreeLayout(skills), [skills])

  return (
    <div className="h-[70vh] min-h-[28rem] overflow-hidden rounded-2xl border border-border bg-bg-raised">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        proOptions={{ hideAttribution: true }}
        nodesConnectable={false}
      >
        <Background gap={24} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  )
}
