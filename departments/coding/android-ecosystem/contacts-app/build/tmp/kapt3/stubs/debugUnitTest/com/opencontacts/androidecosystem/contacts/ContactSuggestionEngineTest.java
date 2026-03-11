package com.opencontacts.androidecosystem.contacts;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\t\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0002\n\u0002\b\r\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002J\b\u0010\u000b\u001a\u00020\fH\u0007J\b\u0010\r\u001a\u00020\fH\u0007J\b\u0010\u000e\u001a\u00020\fH\u0007J\b\u0010\u000f\u001a\u00020\fH\u0007J\b\u0010\u0010\u001a\u00020\fH\u0007J\b\u0010\u0011\u001a\u00020\fH\u0007J\b\u0010\u0012\u001a\u00020\fH\u0007J\b\u0010\u0013\u001a\u00020\fH\u0007J\b\u0010\u0014\u001a\u00020\fH\u0007J\b\u0010\u0015\u001a\u00020\fH\u0007J\b\u0010\u0016\u001a\u00020\fH\u0007J\b\u0010\u0017\u001a\u00020\fH\u0007J\b\u0010\u0018\u001a\u00020\fH\u0007R\u000e\u0010\u0003\u001a\u00020\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0006X\u0082D\u00a2\u0006\u0002\n\u0000R\u0014\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\u00060\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\t\u001a\u00020\nX\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0019"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/ContactSuggestionEngineTest;", "", "()V", "engine", "Lcom/opencontacts/androidecosystem/contacts/ContactSuggestionEngine;", "now", "", "nowProvider", "Lkotlin/Function0;", "origin", "Lcom/opencontacts/androidecosystem/contacts/ContactLocation;", "suggest_appliesCategoryFilterCaseInsensitively", "", "suggest_appliesFavoriteBoost", "suggest_breaksScoreTiesAlphabeticallyByTitle", "suggest_deduplicatesByNormalizedContactIdKeepingHighestScore", "suggest_limitsResultCount", "suggest_ordersContactsByProximity", "suggest_returnsEmptyForNonPositiveLimit", "suggest_returnsEmptyForNullContacts", "suggest_setsReasonToNearbyAndRecentWhenBothSignalsExist", "suggest_skipsContactsWithoutValidLocationWhenOriginIsValid", "suggest_usesInteractionCountToBreakTies", "suggest_usesRecencyOnlyWhenOriginIsInvalid", "suggest_usesRecencyWeightingToBoostRecentContacts", "contacts-app_debugUnitTest"})
public final class ContactSuggestionEngineTest {
    private final long now = 1700000000000L;
    @org.jetbrains.annotations.NotNull()
    private final kotlin.jvm.functions.Function0<java.lang.Long> nowProvider = null;
    @org.jetbrains.annotations.NotNull()
    private final com.opencontacts.androidecosystem.contacts.ContactSuggestionEngine engine = null;
    @org.jetbrains.annotations.NotNull()
    private final com.opencontacts.androidecosystem.contacts.ContactLocation origin = null;
    
    public ContactSuggestionEngineTest() {
        super();
    }
    
    @org.junit.Test()
    public final void suggest_returnsEmptyForNullContacts() {
    }
    
    @org.junit.Test()
    public final void suggest_returnsEmptyForNonPositiveLimit() {
    }
    
    @org.junit.Test()
    public final void suggest_ordersContactsByProximity() {
    }
    
    @org.junit.Test()
    public final void suggest_usesRecencyWeightingToBoostRecentContacts() {
    }
    
    @org.junit.Test()
    public final void suggest_usesInteractionCountToBreakTies() {
    }
    
    @org.junit.Test()
    public final void suggest_limitsResultCount() {
    }
    
    @org.junit.Test()
    public final void suggest_appliesCategoryFilterCaseInsensitively() {
    }
    
    @org.junit.Test()
    public final void suggest_usesRecencyOnlyWhenOriginIsInvalid() {
    }
    
    @org.junit.Test()
    public final void suggest_skipsContactsWithoutValidLocationWhenOriginIsValid() {
    }
    
    @org.junit.Test()
    public final void suggest_deduplicatesByNormalizedContactIdKeepingHighestScore() {
    }
    
    @org.junit.Test()
    public final void suggest_appliesFavoriteBoost() {
    }
    
    @org.junit.Test()
    public final void suggest_setsReasonToNearbyAndRecentWhenBothSignalsExist() {
    }
    
    @org.junit.Test()
    public final void suggest_breaksScoreTiesAlphabeticallyByTitle() {
    }
}