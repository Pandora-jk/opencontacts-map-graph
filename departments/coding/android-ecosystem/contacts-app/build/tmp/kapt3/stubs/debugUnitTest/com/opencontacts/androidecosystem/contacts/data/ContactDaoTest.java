package com.opencontacts.androidecosystem.contacts.data;

@org.junit.runner.RunWith(value = org.robolectric.RobolectricTestRunner.class)
@org.robolectric.annotation.Config(sdk = {34})
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000@\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0002\n\u0002\u0018\u0002\n\u0002\b\f\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\t\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0005\n\u0002\u0010\b\n\u0002\b\u0005\b\u0007\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002J\f\u0010\u0007\u001a\u00060\bj\u0002`\tH\u0007J\f\u0010\n\u001a\u00060\bj\u0002`\tH\u0007J\f\u0010\u000b\u001a\u00060\bj\u0002`\tH\u0007J\f\u0010\f\u001a\u00060\bj\u0002`\tH\u0007J\f\u0010\r\u001a\u00060\bj\u0002`\tH\u0007J\f\u0010\u000e\u001a\u00060\bj\u0002`\tH\u0007J\f\u0010\u000f\u001a\u00060\bj\u0002`\tH\u0007J\f\u0010\u0010\u001a\u00060\bj\u0002`\tH\u0007J\f\u0010\u0011\u001a\u00060\bj\u0002`\tH\u0007J\f\u0010\u0012\u001a\u00060\bj\u0002`\tH\u0007J\f\u0010\u0013\u001a\u00060\bj\u0002`\tH\u0007J\f\u0010\u0014\u001a\u00060\bj\u0002`\tH\u0007J[\u0010\u0015\u001a\u00020\u00162\b\b\u0002\u0010\u0017\u001a\u00020\u00182\b\b\u0002\u0010\u0019\u001a\u00020\u001a2\n\b\u0002\u0010\u001b\u001a\u0004\u0018\u00010\u001a2\n\b\u0002\u0010\u001c\u001a\u0004\u0018\u00010\u001a2\n\b\u0002\u0010\u001d\u001a\u0004\u0018\u00010\u001a2\n\b\u0002\u0010\u001e\u001a\u0004\u0018\u00010\u00182\b\b\u0002\u0010\u001f\u001a\u00020 H\u0002\u00a2\u0006\u0002\u0010!J\b\u0010\"\u001a\u00020\bH\u0007J\b\u0010#\u001a\u00020\bH\u0007J\f\u0010$\u001a\u00060\bj\u0002`\tH\u0007R\u000e\u0010\u0003\u001a\u00020\u0004X\u0082.\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0006X\u0082.\u00a2\u0006\u0002\n\u0000\u00a8\u0006%"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/data/ContactDaoTest;", "", "()V", "contactDao", "Lcom/opencontacts/androidecosystem/contacts/data/ContactDao;", "database", "Lcom/opencontacts/androidecosystem/contacts/data/ContactsDatabase;", "delete_removesPersistedContact", "", "Lkotlinx/coroutines/test/TestResult;", "getAll_returnsContactsSortedByDisplayName", "getAll_returnsEmptyListWhenDatabaseIsEmpty", "getById_returnsNullWhenContactDoesNotExist", "getFrequentContacts_ordersByStrengthThenRecencyAndAppliesLimit", "getFrequentContacts_returnsEmptyListForZeroLimit", "insert_allowsDuplicateContactDetailsAsSeparateRows", "insert_persistsContactAndReturnsGeneratedId", "queryByName_matchesPartialNameCaseInsensitively", "queryByName_returnsEmptyListForNullOrBlankInput", "queryByPhone_matchesPartialPhoneNumberAndSortsByName", "queryByPhone_returnsEmptyListForNullInput", "sampleContact", "Lcom/opencontacts/androidecosystem/contacts/data/ContactEntity;", "id", "", "displayName", "", "phone", "email", "photoUri", "lastContacted", "connectionStrength", "", "(JLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Long;I)Lcom/opencontacts/androidecosystem/contacts/data/ContactEntity;", "setUp", "tearDown", "update_persistsModifiedFields", "contacts-app_debugUnitTest"})
public final class ContactDaoTest {
    private com.opencontacts.androidecosystem.contacts.data.ContactsDatabase database;
    private com.opencontacts.androidecosystem.contacts.data.ContactDao contactDao;
    
    public ContactDaoTest() {
        super();
    }
    
    @org.junit.Before()
    public final void setUp() {
    }
    
    @org.junit.After()
    public final void tearDown() {
    }
    
    @org.junit.Test()
    public final void insert_persistsContactAndReturnsGeneratedId() {
    }
    
    @org.junit.Test()
    public final void getById_returnsNullWhenContactDoesNotExist() {
    }
    
    @org.junit.Test()
    public final void update_persistsModifiedFields() {
    }
    
    @org.junit.Test()
    public final void delete_removesPersistedContact() {
    }
    
    @org.junit.Test()
    public final void queryByName_matchesPartialNameCaseInsensitively() {
    }
    
    @org.junit.Test()
    public final void queryByName_returnsEmptyListForNullOrBlankInput() {
    }
    
    @org.junit.Test()
    public final void queryByPhone_matchesPartialPhoneNumberAndSortsByName() {
    }
    
    @org.junit.Test()
    public final void queryByPhone_returnsEmptyListForNullInput() {
    }
    
    @org.junit.Test()
    public final void getAll_returnsContactsSortedByDisplayName() {
    }
    
    @org.junit.Test()
    public final void getAll_returnsEmptyListWhenDatabaseIsEmpty() {
    }
    
    @org.junit.Test()
    public final void getFrequentContacts_ordersByStrengthThenRecencyAndAppliesLimit() {
    }
    
    @org.junit.Test()
    public final void getFrequentContacts_returnsEmptyListForZeroLimit() {
    }
    
    @org.junit.Test()
    public final void insert_allowsDuplicateContactDetailsAsSeparateRows() {
    }
    
    private final com.opencontacts.androidecosystem.contacts.data.ContactEntity sampleContact(long id, java.lang.String displayName, java.lang.String phone, java.lang.String email, java.lang.String photoUri, java.lang.Long lastContacted, int connectionStrength) {
        return null;
    }
}