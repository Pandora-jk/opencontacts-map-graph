package com.openclaw.androidecosystem.contacts.contactsui

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.PointF
import android.util.AttributeSet
import android.view.View
import com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionGraph
import kotlin.math.cos
import kotlin.math.min
import kotlin.math.sin

class GraphVisualizationView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {
    private var graph: ConnectionGraph = ConnectionGraph(emptyMap(), emptyList())
    private val edgePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#5F6F52")
        strokeWidth = 4f
    }
    private val nodePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#D97706")
    }
    private val nodeHighlightPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#0F766E")
    }
    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#1F2937")
        textSize = 28f
    }

    fun setGraph(connectionGraph: ConnectionGraph) {
        graph = connectionGraph
        contentDescription = "Graph with ${graph.nodes.size} contacts and ${graph.edges.size} connections"
        invalidate()
    }

    fun calculateNodePositions(
        widthPx: Int = width.takeIf { it > 0 } ?: 600,
        heightPx: Int = height.takeIf { it > 0 } ?: 400
    ): Map<Long, PointF> {
        if (graph.nodes.isEmpty()) {
            return emptyMap()
        }

        val centerX = widthPx / 2f
        val centerY = heightPx / 2f
        val radius = min(widthPx, heightPx) * 0.32f
        val ids = graph.nodes.keys.sorted()
        return ids.mapIndexed { index, contactId ->
            val angle = (2 * Math.PI * index / ids.size).toFloat()
            contactId to PointF(
                centerX + radius * cos(angle),
                centerY + radius * sin(angle)
            )
        }.toMap()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val positions = calculateNodePositions()
        graph.edges.forEach { edge ->
            val start = positions[edge.fromContactId] ?: return@forEach
            val end = positions[edge.toContactId] ?: return@forEach
            canvas.drawLine(start.x, start.y, end.x, end.y, edgePaint)
        }
        positions.forEach { (contactId, point) ->
            val isHighlighted = graph.degreeOf(contactId) >= 2
            canvas.drawCircle(point.x, point.y, 24f, if (isHighlighted) nodeHighlightPaint else nodePaint)
            val label = graph.nodes[contactId]?.contact?.displayName?.take(1).orEmpty()
            canvas.drawText(label, point.x - 8f, point.y + 10f, textPaint)
        }
    }
}
