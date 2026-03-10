package com.opencontacts.androidecosystem.contacts

import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.min
import kotlin.math.sin

class GraphVisualizationView {
    fun render(
        graph: ConnectionGraph?,
        width: Int,
        height: Int,
    ): GraphRenderState {
        val nodeIds = graph?.nodes().orEmpty().toList()
        if (nodeIds.isEmpty() || width <= 0 || height <= 0) {
            return GraphRenderState(
                nodes = emptyList(),
                edges = emptyList(),
                width = width,
                height = height,
            )
        }
        val centerX = width / 2f
        val centerY = height / 2f
        val radius = min(width, height) * 0.35f
        val nodes = if (nodeIds.size == 1) {
            listOf(GraphRenderNode(nodeIds.single(), centerX, centerY))
        } else {
            nodeIds.mapIndexed { index, nodeId ->
                val angle = (2 * PI * index / nodeIds.size) - (PI / 2)
                val x = (centerX + radius * cos(angle)).toFloat().coerceIn(0f, width.toFloat())
                val y = (centerY + radius * sin(angle)).toFloat().coerceIn(0f, height.toFloat())
                GraphRenderNode(nodeId, x, y)
            }
        }
        val edges = graph?.asMap()
            ?.flatMap { (nodeId, neighbors) ->
                neighbors.map { neighbor ->
                    if (nodeId <= neighbor) {
                        GraphRenderEdge(nodeId, neighbor)
                    } else {
                        GraphRenderEdge(neighbor, nodeId)
                    }
                }
            }
            ?.distinct()
            .orEmpty()
        return GraphRenderState(
            nodes = nodes,
            edges = edges,
            width = width,
            height = height,
        )
    }
}
