package com.openclaw.androidecosystem.contacts.contactssearch;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000:\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\"\n\u0002\u0010\t\n\u0000\n\u0002\u0010\b\n\u0002\b\u0002\u0018\u0000 \u00112\u00020\u0001:\u0001\u0011B\u000f\u0012\b\b\u0002\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\u0004J<\u0010\u0005\u001a\b\u0012\u0004\u0012\u00020\u00070\u00062\f\u0010\b\u001a\b\u0012\u0004\u0012\u00020\t0\u00062\u0006\u0010\n\u001a\u00020\u000b2\u000e\b\u0002\u0010\f\u001a\b\u0012\u0004\u0012\u00020\u000e0\r2\b\b\u0002\u0010\u000f\u001a\u00020\u0010R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0012"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactssearch/ContactSuggestionEngine;", "", "graphAlgorithm", "Lcom/openclaw/androidecosystem/contacts/contactsgraph/GraphAlgorithm;", "(Lcom/openclaw/androidecosystem/contacts/contactsgraph/GraphAlgorithm;)V", "suggestContacts", "", "Lcom/openclaw/androidecosystem/contacts/contactssearch/ContactSuggestion;", "contacts", "Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactEntity;", "graph", "Lcom/openclaw/androidecosystem/contacts/contactsgraph/ConnectionGraph;", "recentContactIds", "", "", "limit", "", "Companion", "contacts-app_debug"})
public final class ContactSuggestionEngine {
    @org.jetbrains.annotations.NotNull()
    private final com.openclaw.androidecosystem.contacts.contactsgraph.GraphAlgorithm graphAlgorithm = null;
    @java.lang.Deprecated()
    public static final long DAY_MS = 86400000L;
    @org.jetbrains.annotations.NotNull()
    private static final com.openclaw.androidecosystem.contacts.contactssearch.ContactSuggestionEngine.Companion Companion = null;
    
    public ContactSuggestionEngine(@org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsgraph.GraphAlgorithm graphAlgorithm) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.openclaw.androidecosystem.contacts.contactssearch.ContactSuggestion> suggestContacts(@org.jetbrains.annotations.NotNull()
    java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity> contacts, @org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionGraph graph, @org.jetbrains.annotations.NotNull()
    java.util.Set<java.lang.Long> recentContactIds, int limit) {
        return null;
    }
    
    public ContactSuggestionEngine() {
        super();
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0012\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\t\n\u0000\b\u0082\u0003\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002R\u000e\u0010\u0003\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0005"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactssearch/ContactSuggestionEngine$Companion;", "", "()V", "DAY_MS", "", "contacts-app_debug"})
    static final class Companion {
        
        private Companion() {
            super();
        }
    }
}