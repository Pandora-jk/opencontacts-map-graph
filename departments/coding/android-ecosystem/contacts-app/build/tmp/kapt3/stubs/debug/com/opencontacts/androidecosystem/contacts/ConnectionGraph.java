package com.opencontacts.androidecosystem.contacts;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000:\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000b\n\u0002\b\u0005\n\u0002\u0010$\n\u0002\u0010\"\n\u0000\n\u0002\u0010 \n\u0000\n\u0002\u0010\b\n\u0002\b\t\u0018\u0000 \u001b2\u00020\u0001:\u0001\u001bB\u0005\u00a2\u0006\u0002\u0010\u0002J\u001a\u0010\u0007\u001a\u00020\b2\b\u0010\t\u001a\u0004\u0018\u00010\u00052\b\u0010\n\u001a\u0004\u0018\u00010\u0005J\u0010\u0010\u000b\u001a\u00020\b2\b\u0010\f\u001a\u0004\u0018\u00010\u0005J\u0018\u0010\r\u001a\u0014\u0012\u0004\u0012\u00020\u0005\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00050\u000f0\u000eJ\u0012\u0010\u0010\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00050\u000f0\u0011J\u0006\u0010\u0012\u001a\u00020\u0013J\u001a\u0010\u0014\u001a\u00020\b2\b\u0010\t\u001a\u0004\u0018\u00010\u00052\b\u0010\n\u001a\u0004\u0018\u00010\u0005J\u0010\u0010\u0015\u001a\u00020\b2\b\u0010\f\u001a\u0004\u0018\u00010\u0005J\u0016\u0010\u0016\u001a\b\u0012\u0004\u0012\u00020\u00050\u000f2\b\u0010\f\u001a\u0004\u0018\u00010\u0005J\f\u0010\u0017\u001a\b\u0012\u0004\u0012\u00020\u00050\u000fJ\u0014\u0010\u0018\u001a\u0004\u0018\u00010\u00052\b\u0010\f\u001a\u0004\u0018\u00010\u0005H\u0002J\u001a\u0010\u0019\u001a\u00020\b2\b\u0010\t\u001a\u0004\u0018\u00010\u00052\b\u0010\n\u001a\u0004\u0018\u00010\u0005J\u0010\u0010\u001a\u001a\u00020\b2\b\u0010\f\u001a\u0004\u0018\u00010\u0005R \u0010\u0003\u001a\u0014\u0012\u0004\u0012\u00020\u0005\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00050\u00060\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u001c"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/ConnectionGraph;", "", "()V", "adjacency", "Ljava/util/LinkedHashMap;", "", "Ljava/util/LinkedHashSet;", "addEdge", "", "firstId", "secondId", "addNode", "id", "asMap", "", "", "clusters", "", "edgeCount", "", "hasEdge", "hasNode", "neighbors", "nodes", "normalize", "removeEdge", "removeNode", "Companion", "contacts-app_debug"})
public final class ConnectionGraph {
    @org.jetbrains.annotations.NotNull()
    private final java.util.LinkedHashMap<java.lang.String, java.util.LinkedHashSet<java.lang.String>> adjacency = null;
    @org.jetbrains.annotations.NotNull()
    public static final com.opencontacts.androidecosystem.contacts.ConnectionGraph.Companion Companion = null;
    
    public ConnectionGraph() {
        super();
    }
    
    public final boolean addNode(@org.jetbrains.annotations.Nullable()
    java.lang.String id) {
        return false;
    }
    
    public final boolean removeNode(@org.jetbrains.annotations.Nullable()
    java.lang.String id) {
        return false;
    }
    
    public final boolean addEdge(@org.jetbrains.annotations.Nullable()
    java.lang.String firstId, @org.jetbrains.annotations.Nullable()
    java.lang.String secondId) {
        return false;
    }
    
    public final boolean removeEdge(@org.jetbrains.annotations.Nullable()
    java.lang.String firstId, @org.jetbrains.annotations.Nullable()
    java.lang.String secondId) {
        return false;
    }
    
    public final boolean hasNode(@org.jetbrains.annotations.Nullable()
    java.lang.String id) {
        return false;
    }
    
    public final boolean hasEdge(@org.jetbrains.annotations.Nullable()
    java.lang.String firstId, @org.jetbrains.annotations.Nullable()
    java.lang.String secondId) {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.Set<java.lang.String> neighbors(@org.jetbrains.annotations.Nullable()
    java.lang.String id) {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.Set<java.lang.String> nodes() {
        return null;
    }
    
    public final int edgeCount() {
        return 0;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.Map<java.lang.String, java.util.Set<java.lang.String>> asMap() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<java.util.Set<java.lang.String>> clusters() {
        return null;
    }
    
    private final java.lang.String normalize(java.lang.String id) {
        return null;
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000 \n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010$\n\u0002\u0010\u000e\n\u0002\u0010\"\n\u0000\b\u0086\u0003\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002J\"\u0010\u0003\u001a\u00020\u00042\u001a\u0010\u0005\u001a\u0016\u0012\u0004\u0012\u00020\u0007\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00070\b\u0018\u00010\u0006\u00a8\u0006\t"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/ConnectionGraph$Companion;", "", "()V", "fromAdjacency", "Lcom/opencontacts/androidecosystem/contacts/ConnectionGraph;", "adjacency", "", "", "", "contacts-app_debug"})
    public static final class Companion {
        
        private Companion() {
            super();
        }
        
        @org.jetbrains.annotations.NotNull()
        public final com.opencontacts.androidecosystem.contacts.ConnectionGraph fromAdjacency(@org.jetbrains.annotations.Nullable()
        java.util.Map<java.lang.String, ? extends java.util.Set<java.lang.String>> adjacency) {
            return null;
        }
    }
}