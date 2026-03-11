package com.opencontacts.androidecosystem.contacts;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000$\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0002\n\u0002\b\u000f\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002J\b\u0010\b\u001a\u00020\tH\u0007J\b\u0010\n\u001a\u00020\tH\u0007J\b\u0010\u000b\u001a\u00020\tH\u0007J\b\u0010\f\u001a\u00020\tH\u0007J\b\u0010\r\u001a\u00020\tH\u0007J\b\u0010\u000e\u001a\u00020\tH\u0007J\b\u0010\u000f\u001a\u00020\tH\u0007J\b\u0010\u0010\u001a\u00020\tH\u0007J\b\u0010\u0011\u001a\u00020\tH\u0007J\b\u0010\u0012\u001a\u00020\tH\u0007J\b\u0010\u0013\u001a\u00020\tH\u0007J\b\u0010\u0014\u001a\u00020\tH\u0007J\b\u0010\u0015\u001a\u00020\tH\u0007J\b\u0010\u0016\u001a\u00020\tH\u0007J\b\u0010\u0017\u001a\u00020\tH\u0007R\u0014\u0010\u0003\u001a\b\u0012\u0004\u0012\u00020\u00050\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0006\u001a\u00020\u0007X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0018"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/ContactSearchFilterTest;", "", "()V", "contacts", "", "Lcom/opencontacts/androidecosystem/contacts/ContactRecord;", "filter", "Lcom/opencontacts/androidecosystem/contacts/ContactSearchFilter;", "filter_combinesQueryFavoriteAndCompanyFilters", "", "filter_filtersByCompanyWithTrimmedCaseInsensitiveValue", "filter_filtersFavoritesOnly", "filter_handlesContactsWithNullFieldsWithoutCrashing", "filter_ignoresBlankCompanyFilter", "filter_ignoresBlankQuery", "filter_matchesCompanyCaseInsensitively", "filter_matchesDisplayNameCaseInsensitively", "filter_matchesEmailCaseInsensitively", "filter_matchesPhoneNumbersUsingDigitNormalization", "filter_matchesTagsCaseInsensitively", "filter_preservesDuplicateContactsInResults", "filter_returnsEmptyListForNullContacts", "filter_returnsEmptyWhenQueryDoesNotMatchAnyField", "filter_returnsOriginalContactsForNullQueryAndNoFilters", "contacts-app_debugUnitTest"})
public final class ContactSearchFilterTest {
    @org.jetbrains.annotations.NotNull()
    private final com.opencontacts.androidecosystem.contacts.ContactSearchFilter filter = null;
    @org.jetbrains.annotations.NotNull()
    private final java.util.List<com.opencontacts.androidecosystem.contacts.ContactRecord> contacts = null;
    
    public ContactSearchFilterTest() {
        super();
    }
    
    @org.junit.Test()
    public final void filter_returnsEmptyListForNullContacts() {
    }
    
    @org.junit.Test()
    public final void filter_returnsOriginalContactsForNullQueryAndNoFilters() {
    }
    
    @org.junit.Test()
    public final void filter_matchesDisplayNameCaseInsensitively() {
    }
    
    @org.junit.Test()
    public final void filter_matchesEmailCaseInsensitively() {
    }
    
    @org.junit.Test()
    public final void filter_matchesCompanyCaseInsensitively() {
    }
    
    @org.junit.Test()
    public final void filter_matchesTagsCaseInsensitively() {
    }
    
    @org.junit.Test()
    public final void filter_matchesPhoneNumbersUsingDigitNormalization() {
    }
    
    @org.junit.Test()
    public final void filter_returnsEmptyWhenQueryDoesNotMatchAnyField() {
    }
    
    @org.junit.Test()
    public final void filter_ignoresBlankQuery() {
    }
    
    @org.junit.Test()
    public final void filter_filtersFavoritesOnly() {
    }
    
    @org.junit.Test()
    public final void filter_filtersByCompanyWithTrimmedCaseInsensitiveValue() {
    }
    
    @org.junit.Test()
    public final void filter_ignoresBlankCompanyFilter() {
    }
    
    @org.junit.Test()
    public final void filter_combinesQueryFavoriteAndCompanyFilters() {
    }
    
    @org.junit.Test()
    public final void filter_handlesContactsWithNullFieldsWithoutCrashing() {
    }
    
    @org.junit.Test()
    public final void filter_preservesDuplicateContactsInResults() {
    }
}