package com.opencontacts.androidecosystem.contacts;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\b\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\u0010\"\n\u0002\b\u0006\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002J\"\u0010\u0003\u001a\u00020\u00042\u0006\u0010\u0005\u001a\u00020\u00062\b\u0010\u0007\u001a\u0004\u0018\u00010\b2\b\u0010\t\u001a\u0004\u0018\u00010\bJ$\u0010\n\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\b0\f0\u000b2\u0006\u0010\u0005\u001a\u00020\u00062\b\b\u0002\u0010\r\u001a\u00020\u0004J\u0014\u0010\u000e\u001a\u0004\u0018\u00010\b2\b\u0010\u000f\u001a\u0004\u0018\u00010\bH\u0002J)\u0010\u0010\u001a\u0004\u0018\u00010\u00042\u0006\u0010\u0005\u001a\u00020\u00062\b\u0010\u0007\u001a\u0004\u0018\u00010\b2\b\u0010\t\u001a\u0004\u0018\u00010\b\u00a2\u0006\u0002\u0010\u0011\u00a8\u0006\u0012"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/GraphAlgorithm;", "", "()V", "connectionStrength", "", "graph", "Lcom/opencontacts/androidecosystem/contacts/ConnectionGraph;", "firstId", "", "secondId", "findClusters", "", "", "minimumSize", "normalize", "id", "shortestPathLength", "(Lcom/opencontacts/androidecosystem/contacts/ConnectionGraph;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Integer;", "contacts-app_debug"})
public final class GraphAlgorithm {
    
    public GraphAlgorithm() {
        super();
    }
    
    public final int connectionStrength(@org.jetbrains.annotations.NotNull()
    com.opencontacts.androidecosystem.contacts.ConnectionGraph graph, @org.jetbrains.annotations.Nullable()
    java.lang.String firstId, @org.jetbrains.annotations.Nullable()
    java.lang.String secondId) {
        return 0;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Integer shortestPathLength(@org.jetbrains.annotations.NotNull()
    com.opencontacts.androidecosystem.contacts.ConnectionGraph graph, @org.jetbrains.annotations.Nullable()
    java.lang.String firstId, @org.jetbrains.annotations.Nullable()
    java.lang.String secondId) {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<java.util.Set<java.lang.String>> findClusters(@org.jetbrains.annotations.NotNull()
    com.opencontacts.androidecosystem.contacts.ConnectionGraph graph, int minimumSize) {
        return null;
    }
    
    private final java.lang.String normalize(java.lang.String id) {
        return null;
    }
}