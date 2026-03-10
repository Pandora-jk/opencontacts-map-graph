package com.opencontacts.androidecosystem.contacts;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000D\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\t\n\u0002\b\u0002\n\u0002\u0010\b\n\u0000\n\u0002\u0010\u0006\n\u0002\b\u0005\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0005\u0018\u0000 \u001b2\u00020\u0001:\u0001\u001bB\u0015\u0012\u000e\b\u0002\u0010\u0002\u001a\b\u0012\u0004\u0012\u00020\u00040\u0003\u00a2\u0006\u0002\u0010\u0005J\u0017\u0010\u0006\u001a\u00020\u00072\b\u0010\b\u001a\u0004\u0018\u00010\tH\u0002\u00a2\u0006\u0002\u0010\nJ\u0017\u0010\u000b\u001a\u00020\u00072\b\u0010\f\u001a\u0004\u0018\u00010\u0004H\u0002\u00a2\u0006\u0002\u0010\rJ>\u0010\u000e\u001a\b\u0012\u0004\u0012\u00020\u00100\u000f2\u000e\u0010\u0011\u001a\n\u0012\u0004\u0012\u00020\u0012\u0018\u00010\u000f2\n\b\u0002\u0010\u0013\u001a\u0004\u0018\u00010\u00142\b\b\u0002\u0010\u0015\u001a\u00020\u00072\n\b\u0002\u0010\u0016\u001a\u0004\u0018\u00010\u0017J$\u0010\u0018\u001a\u0004\u0018\u00010\u00102\u0006\u0010\u0019\u001a\u00020\u00122\b\u0010\u0013\u001a\u0004\u0018\u00010\u00142\u0006\u0010\u001a\u001a\u00020\u0017H\u0002R\u0014\u0010\u0002\u001a\b\u0012\u0004\u0012\u00020\u00040\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u001c"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/ContactSuggestionEngine;", "", "nowProvider", "Lkotlin/Function0;", "", "(Lkotlin/jvm/functions/Function0;)V", "proximityScore", "", "distanceKm", "", "(Ljava/lang/Double;)I", "recencyScore", "lastContactedAtEpochMillis", "(Ljava/lang/Long;)I", "suggest", "", "Lcom/opencontacts/androidecosystem/contacts/ContactSuggestion;", "contacts", "Lcom/opencontacts/androidecosystem/contacts/ContactRecord;", "origin", "Lcom/opencontacts/androidecosystem/contacts/ContactLocation;", "maxSuggestions", "category", "", "toSuggestion", "contact", "normalizedCategory", "Companion", "contacts-app_debug"})
public final class ContactSuggestionEngine {
    @org.jetbrains.annotations.NotNull()
    private final kotlin.jvm.functions.Function0<java.lang.Long> nowProvider = null;
    @java.lang.Deprecated()
    public static final long DAY_IN_MILLIS = 86400000L;
    @org.jetbrains.annotations.NotNull()
    private static final com.opencontacts.androidecosystem.contacts.ContactSuggestionEngine.Companion Companion = null;
    
    public ContactSuggestionEngine(@org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function0<java.lang.Long> nowProvider) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.opencontacts.androidecosystem.contacts.ContactSuggestion> suggest(@org.jetbrains.annotations.Nullable()
    java.util.List<com.opencontacts.androidecosystem.contacts.ContactRecord> contacts, @org.jetbrains.annotations.Nullable()
    com.opencontacts.androidecosystem.contacts.ContactLocation origin, int maxSuggestions, @org.jetbrains.annotations.Nullable()
    java.lang.String category) {
        return null;
    }
    
    private final com.opencontacts.androidecosystem.contacts.ContactSuggestion toSuggestion(com.opencontacts.androidecosystem.contacts.ContactRecord contact, com.opencontacts.androidecosystem.contacts.ContactLocation origin, java.lang.String normalizedCategory) {
        return null;
    }
    
    private final int proximityScore(java.lang.Double distanceKm) {
        return 0;
    }
    
    private final int recencyScore(java.lang.Long lastContactedAtEpochMillis) {
        return 0;
    }
    
    public ContactSuggestionEngine() {
        super();
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0012\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\t\n\u0000\b\u0082\u0003\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002R\u000e\u0010\u0003\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0005"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/ContactSuggestionEngine$Companion;", "", "()V", "DAY_IN_MILLIS", "", "contacts-app_debug"})
    static final class Companion {
        
        private Companion() {
            super();
        }
    }
}