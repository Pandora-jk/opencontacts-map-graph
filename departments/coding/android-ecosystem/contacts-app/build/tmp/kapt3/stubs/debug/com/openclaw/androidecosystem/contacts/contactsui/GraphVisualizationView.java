package com.openclaw.androidecosystem.contacts.contactsui;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000J\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0004\n\u0002\u0010$\n\u0002\u0010\t\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\u0018\u00002\u00020\u0001B\u001b\b\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0005\u00a2\u0006\u0002\u0010\u0006J&\u0010\u000e\u001a\u000e\u0012\u0004\u0012\u00020\u0010\u0012\u0004\u0012\u00020\u00110\u000f2\b\b\u0002\u0010\u0012\u001a\u00020\u00132\b\b\u0002\u0010\u0014\u001a\u00020\u0013J\u0010\u0010\u0015\u001a\u00020\u00162\u0006\u0010\u0017\u001a\u00020\u0018H\u0014J\u000e\u0010\u0019\u001a\u00020\u00162\u0006\u0010\u001a\u001a\u00020\nR\u000e\u0010\u0007\u001a\u00020\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\t\u001a\u00020\nX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u000b\u001a\u00020\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\f\u001a\u00020\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\r\u001a\u00020\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u001b"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactsui/GraphVisualizationView;", "Landroid/view/View;", "context", "Landroid/content/Context;", "attrs", "Landroid/util/AttributeSet;", "(Landroid/content/Context;Landroid/util/AttributeSet;)V", "edgePaint", "Landroid/graphics/Paint;", "graph", "Lcom/openclaw/androidecosystem/contacts/contactsgraph/ConnectionGraph;", "nodeHighlightPaint", "nodePaint", "textPaint", "calculateNodePositions", "", "", "Landroid/graphics/PointF;", "widthPx", "", "heightPx", "onDraw", "", "canvas", "Landroid/graphics/Canvas;", "setGraph", "connectionGraph", "contacts-app_debug"})
public final class GraphVisualizationView extends android.view.View {
    @org.jetbrains.annotations.NotNull()
    private com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionGraph graph;
    @org.jetbrains.annotations.NotNull()
    private final android.graphics.Paint edgePaint = null;
    @org.jetbrains.annotations.NotNull()
    private final android.graphics.Paint nodePaint = null;
    @org.jetbrains.annotations.NotNull()
    private final android.graphics.Paint nodeHighlightPaint = null;
    @org.jetbrains.annotations.NotNull()
    private final android.graphics.Paint textPaint = null;
    
    @kotlin.jvm.JvmOverloads()
    public GraphVisualizationView(@org.jetbrains.annotations.NotNull()
    android.content.Context context, @org.jetbrains.annotations.Nullable()
    android.util.AttributeSet attrs) {
        super(null);
    }
    
    public final void setGraph(@org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionGraph connectionGraph) {
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.Map<java.lang.Long, android.graphics.PointF> calculateNodePositions(int widthPx, int heightPx) {
        return null;
    }
    
    @java.lang.Override()
    protected void onDraw(@org.jetbrains.annotations.NotNull()
    android.graphics.Canvas canvas) {
    }
    
    @kotlin.jvm.JvmOverloads()
    public GraphVisualizationView(@org.jetbrains.annotations.NotNull()
    android.content.Context context) {
        super(null);
    }
}