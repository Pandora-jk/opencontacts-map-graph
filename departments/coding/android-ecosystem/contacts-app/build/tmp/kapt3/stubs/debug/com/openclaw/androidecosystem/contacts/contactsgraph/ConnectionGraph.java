package com.openclaw.androidecosystem.contacts.contactsgraph;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000@\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010$\n\u0002\u0010\t\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\b\n\u0002\u0010\u000b\n\u0002\b\u0003\n\u0002\u0010\b\n\u0002\b\u0007\n\u0002\u0010\"\n\u0000\n\u0002\u0010\u000e\n\u0000\b\u0086\b\u0018\u00002\u00020\u0001B\'\u0012\u0012\u0010\u0002\u001a\u000e\u0012\u0004\u0012\u00020\u0004\u0012\u0004\u0012\u00020\u00050\u0003\u0012\f\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\b0\u0007\u00a2\u0006\u0002\u0010\tJ\u0015\u0010\u000e\u001a\u000e\u0012\u0004\u0012\u00020\u0004\u0012\u0004\u0012\u00020\u00050\u0003H\u00c6\u0003J\u000f\u0010\u000f\u001a\b\u0012\u0004\u0012\u00020\b0\u0007H\u00c6\u0003J\u000e\u0010\u0010\u001a\u00020\u00112\u0006\u0010\u0012\u001a\u00020\u0004J/\u0010\u0013\u001a\u00020\u00002\u0014\b\u0002\u0010\u0002\u001a\u000e\u0012\u0004\u0012\u00020\u0004\u0012\u0004\u0012\u00020\u00050\u00032\u000e\b\u0002\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\b0\u0007H\u00c6\u0001J\u000e\u0010\u0014\u001a\u00020\u00152\u0006\u0010\u0012\u001a\u00020\u0004J\u0018\u0010\u0016\u001a\u0004\u0018\u00010\b2\u0006\u0010\u0017\u001a\u00020\u00042\u0006\u0010\u0018\u001a\u00020\u0004J\u0013\u0010\u0019\u001a\u00020\u00112\b\u0010\u001a\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010\u001b\u001a\u00020\u0015H\u00d6\u0001J\u0014\u0010\u001c\u001a\b\u0012\u0004\u0012\u00020\u00040\u001d2\u0006\u0010\u0012\u001a\u00020\u0004J\t\u0010\u001e\u001a\u00020\u001fH\u00d6\u0001R\u0017\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\b0\u0007\u00a2\u0006\b\n\u0000\u001a\u0004\b\n\u0010\u000bR\u001d\u0010\u0002\u001a\u000e\u0012\u0004\u0012\u00020\u0004\u0012\u0004\u0012\u00020\u00050\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\f\u0010\r\u00a8\u0006 "}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactsgraph/ConnectionGraph;", "", "nodes", "", "", "Lcom/openclaw/androidecosystem/contacts/contactsgraph/ConnectionNode;", "edges", "", "Lcom/openclaw/androidecosystem/contacts/contactsgraph/ConnectionEdge;", "(Ljava/util/Map;Ljava/util/List;)V", "getEdges", "()Ljava/util/List;", "getNodes", "()Ljava/util/Map;", "component1", "component2", "contains", "", "contactId", "copy", "degreeOf", "", "edgeBetween", "firstContactId", "secondContactId", "equals", "other", "hashCode", "neighborsOf", "", "toString", "", "contacts-app_debug"})
public final class ConnectionGraph {
    @org.jetbrains.annotations.NotNull()
    private final java.util.Map<java.lang.Long, com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionNode> nodes = null;
    @org.jetbrains.annotations.NotNull()
    private final java.util.List<com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionEdge> edges = null;
    
    public ConnectionGraph(@org.jetbrains.annotations.NotNull()
    java.util.Map<java.lang.Long, com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionNode> nodes, @org.jetbrains.annotations.NotNull()
    java.util.List<com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionEdge> edges) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.Map<java.lang.Long, com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionNode> getNodes() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionEdge> getEdges() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.Set<java.lang.Long> neighborsOf(long contactId) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionEdge edgeBetween(long firstContactId, long secondContactId) {
        return null;
    }
    
    public final int degreeOf(long contactId) {
        return 0;
    }
    
    public final boolean contains(long contactId) {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.Map<java.lang.Long, com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionNode> component1() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionEdge> component2() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionGraph copy(@org.jetbrains.annotations.NotNull()
    java.util.Map<java.lang.Long, com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionNode> nodes, @org.jetbrains.annotations.NotNull()
    java.util.List<com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionEdge> edges) {
        return null;
    }
    
    @java.lang.Override()
    public boolean equals(@org.jetbrains.annotations.Nullable()
    java.lang.Object other) {
        return false;
    }
    
    @java.lang.Override()
    public int hashCode() {
        return 0;
    }
    
    @java.lang.Override()
    @org.jetbrains.annotations.NotNull()
    public java.lang.String toString() {
        return null;
    }
}