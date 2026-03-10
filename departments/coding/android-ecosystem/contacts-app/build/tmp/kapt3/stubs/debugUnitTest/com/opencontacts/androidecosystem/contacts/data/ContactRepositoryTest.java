package com.opencontacts.androidecosystem.contacts.data;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000L\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0002\n\u0002\u0018\u0002\n\u0002\b\n\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\t\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0005\n\u0002\u0010\b\n\u0002\b\u0005\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002J\f\u0010\u000b\u001a\u00060\fj\u0002`\rH\u0007J\f\u0010\u000e\u001a\u00060\fj\u0002`\rH\u0007J\f\u0010\u000f\u001a\u00060\fj\u0002`\rH\u0007J\f\u0010\u0010\u001a\u00060\fj\u0002`\rH\u0007J\f\u0010\u0011\u001a\u00060\fj\u0002`\rH\u0007J\f\u0010\u0012\u001a\u00060\fj\u0002`\rH\u0007J\f\u0010\u0013\u001a\u00060\fj\u0002`\rH\u0007J\f\u0010\u0014\u001a\u00060\fj\u0002`\rH\u0007J\f\u0010\u0015\u001a\u00060\fj\u0002`\rH\u0007J\f\u0010\u0016\u001a\u00060\fj\u0002`\rH\u0007J[\u0010\u0017\u001a\u00020\u00182\b\b\u0002\u0010\u0019\u001a\u00020\u001a2\b\b\u0002\u0010\u001b\u001a\u00020\u001c2\n\b\u0002\u0010\u001d\u001a\u0004\u0018\u00010\u001c2\n\b\u0002\u0010\u001e\u001a\u0004\u0018\u00010\u001c2\n\b\u0002\u0010\u001f\u001a\u0004\u0018\u00010\u001c2\n\b\u0002\u0010 \u001a\u0004\u0018\u00010\u001a2\b\b\u0002\u0010!\u001a\u00020\"H\u0002\u00a2\u0006\u0002\u0010#J\f\u0010$\u001a\u00060\fj\u0002`\rH\u0007J\f\u0010%\u001a\u00060\fj\u0002`\rH\u0007J\f\u0010&\u001a\u00060\fj\u0002`\rH\u0007R\u000e\u0010\u0003\u001a\u00020\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0006X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0007\u001a\u00020\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\t\u001a\u00020\nX\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\'"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/data/ContactRepositoryTest;", "", "()V", "contactDao", "Lcom/opencontacts/androidecosystem/contacts/data/ContactDao;", "permissionChecker", "Lcom/opencontacts/androidecosystem/contacts/data/ContactsPermissionChecker;", "repository", "Lcom/opencontacts/androidecosystem/contacts/data/ContactRepository;", "systemContactsSyncer", "Lcom/opencontacts/androidecosystem/contacts/data/SystemContactsSyncer;", "delete_delegatesToDao", "", "Lkotlinx/coroutines/test/TestResult;", "getAll_delegatesToDao", "getById_delegatesToDao", "getFrequentContacts_delegatesPositiveLimitToDao", "getFrequentContacts_returnsEmptyListForNonPositiveLimitWithoutDaoCall", "insert_delegatesToDaoAndReturnsId", "queryByName_returnsEmptyListForBlankInputWithoutDaoCall", "queryByName_trimsInputBeforeDelegating", "queryByPhone_returnsEmptyListForNullInputWithoutDaoCall", "queryByPhone_trimsInputBeforeDelegating", "sampleContact", "Lcom/opencontacts/androidecosystem/contacts/data/ContactEntity;", "id", "", "displayName", "", "phone", "email", "photoUri", "lastContacted", "connectionStrength", "", "(JLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Long;I)Lcom/opencontacts/androidecosystem/contacts/data/ContactEntity;", "syncWithSystemContacts_callsSyncerWhenPermissionGranted", "syncWithSystemContacts_returnsPermissionDeniedWhenPermissionMissing", "update_delegatesToDao", "contacts-app_debugUnitTest"})
public final class ContactRepositoryTest {
    @org.jetbrains.annotations.NotNull()
    private final com.opencontacts.androidecosystem.contacts.data.ContactDao contactDao = null;
    @org.jetbrains.annotations.NotNull()
    private final com.opencontacts.androidecosystem.contacts.data.ContactsPermissionChecker permissionChecker = null;
    @org.jetbrains.annotations.NotNull()
    private final com.opencontacts.androidecosystem.contacts.data.SystemContactsSyncer systemContactsSyncer = null;
    @org.jetbrains.annotations.NotNull()
    private final com.opencontacts.androidecosystem.contacts.data.ContactRepository repository = null;
    
    public ContactRepositoryTest() {
        super();
    }
    
    @org.junit.Test()
    public final void insert_delegatesToDaoAndReturnsId() {
    }
    
    @org.junit.Test()
    public final void update_delegatesToDao() {
    }
    
    @org.junit.Test()
    public final void delete_delegatesToDao() {
    }
    
    @org.junit.Test()
    public final void getById_delegatesToDao() {
    }
    
    @org.junit.Test()
    public final void queryByName_trimsInputBeforeDelegating() {
    }
    
    @org.junit.Test()
    public final void queryByName_returnsEmptyListForBlankInputWithoutDaoCall() {
    }
    
    @org.junit.Test()
    public final void queryByPhone_trimsInputBeforeDelegating() {
    }
    
    @org.junit.Test()
    public final void queryByPhone_returnsEmptyListForNullInputWithoutDaoCall() {
    }
    
    @org.junit.Test()
    public final void getAll_delegatesToDao() {
    }
    
    @org.junit.Test()
    public final void getFrequentContacts_returnsEmptyListForNonPositiveLimitWithoutDaoCall() {
    }
    
    @org.junit.Test()
    public final void getFrequentContacts_delegatesPositiveLimitToDao() {
    }
    
    @org.junit.Test()
    public final void syncWithSystemContacts_returnsPermissionDeniedWhenPermissionMissing() {
    }
    
    @org.junit.Test()
    public final void syncWithSystemContacts_callsSyncerWhenPermissionGranted() {
    }
    
    private final com.opencontacts.androidecosystem.contacts.data.ContactEntity sampleContact(long id, java.lang.String displayName, java.lang.String phone, java.lang.String email, java.lang.String photoUri, java.lang.Long lastContacted, int connectionStrength) {
        return null;
    }
}