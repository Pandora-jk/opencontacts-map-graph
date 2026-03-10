package com.openclaw.androidecosystem.contacts.contactsgraph;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000@\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0010\t\n\u0000\n\u0002\u0010\"\n\u0002\b\u0004\n\u0002\u0010\u000b\n\u0002\b\u0007\u0018\u0000 \u001b2\u00020\u0001:\u0001\u001bB\u0005\u00a2\u0006\u0002\u0010\u0002J\"\u0010\u0003\u001a\u00020\u00042\f\u0010\u0005\u001a\b\u0012\u0004\u0012\u00020\u00070\u00062\f\u0010\b\u001a\b\u0012\u0004\u0012\u00020\t0\u0006J\u0018\u0010\n\u001a\u00020\u000b2\u0006\u0010\f\u001a\u00020\t2\b\b\u0002\u0010\r\u001a\u00020\u000eJ$\u0010\u000f\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u000e0\u00100\u00062\u0006\u0010\u0011\u001a\u00020\u00042\b\b\u0002\u0010\u0012\u001a\u00020\u000bJ\u0014\u0010\u0013\u001a\u00020\u00042\f\u0010\u0005\u001a\b\u0012\u0004\u0012\u00020\u00070\u0006J\u0018\u0010\u0014\u001a\u00020\u00152\u0006\u0010\u0016\u001a\u00020\u00072\u0006\u0010\u0017\u001a\u00020\u0007H\u0002J&\u0010\u0018\u001a\b\u0012\u0004\u0012\u00020\u000e0\u00062\u0006\u0010\u0019\u001a\u00020\u000e2\u0006\u0010\u0011\u001a\u00020\u00042\b\b\u0002\u0010\u001a\u001a\u00020\u000b\u00a8\u0006\u001c"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactsgraph/GraphAlgorithm;", "", "()V", "buildGraph", "Lcom/openclaw/androidecosystem/contacts/contactsgraph/ConnectionGraph;", "contacts", "", "Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactEntity;", "interactions", "Lcom/openclaw/androidecosystem/contacts/contactsgraph/ConnectionEdge;", "calculateConnectionStrength", "", "edge", "now", "", "findClusters", "", "graph", "minimumStrength", "inferGraph", "sameEmailDomain", "", "first", "second", "suggestConnections", "contactId", "limit", "Companion", "contacts-app_debug"})
public final class GraphAlgorithm {
    @java.lang.Deprecated()
    public static final long WEEK_MS = 604800000L;
    @java.lang.Deprecated()
    public static final long MONTH_MS = 2592000000L;
    @org.jetbrains.annotations.NotNull()
    private static final com.openclaw.androidecosystem.contacts.contactsgraph.GraphAlgorithm.Companion Companion = null;
    
    public GraphAlgorithm() {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionGraph buildGraph(@org.jetbrains.annotations.NotNull()
    java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity> contacts, @org.jetbrains.annotations.NotNull()
    java.util.List<com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionEdge> interactions) {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionGraph inferGraph(@org.jetbrains.annotations.NotNull()
    java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity> contacts) {
        return null;
    }
    
    public final int calculateConnectionStrength(@org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionEdge edge, long now) {
        return 0;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<java.util.Set<java.lang.Long>> findClusters(@org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionGraph graph, int minimumStrength) {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<java.lang.Long> suggestConnections(long contactId, @org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionGraph graph, int limit) {
        return null;
    }
    
    private final boolean sameEmailDomain(com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity first, com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity second) {
        return false;
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0014\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\t\n\u0002\b\u0002\b\u0082\u0003\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002R\u000e\u0010\u0003\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0006"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactsgraph/GraphAlgorithm$Companion;", "", "()V", "MONTH_MS", "", "WEEK_MS", "contacts-app_debug"})
    static final class Companion {
        
        private Companion() {
            super();
        }
    }
}