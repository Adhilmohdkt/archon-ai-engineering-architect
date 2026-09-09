"use client";

import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import type { ArchitectureDiagram } from "@/types/archon";

interface ArchitectureDiagramProps {
  diagram?: ArchitectureDiagram;
}

export default function ArchitectureDiagramView({
  diagram,
}: ArchitectureDiagramProps) {
  if (!diagram || diagram.nodes.length === 0) {
    return (
      <div className="flex h-[600px] items-center justify-center rounded-xl border bg-white">
        <p className="text-sm text-slate-500">
          Architecture diagram is not available yet.
        </p>
      </div>
    );
  }

  const nodes: Node[] = diagram.nodes.map((node, index) => ({
    id: node.id,
    position: {
      x: (index % 3) * 300,
      y: Math.floor(index / 3) * 180,
    },
    data: {
      label: node.label,
    },
    type: "default",
  }));

  const edges: Edge[] = diagram.edges.map((edge, index) => ({
    id: `edge-${index}`,
    source: edge.source,
    target: edge.target,
    label: edge.label ?? undefined,
    animated: true,
  }));

  return (
    <div className="h-[600px] overflow-hidden rounded-xl border bg-slate-50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        attributionPosition="bottom-left"
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}