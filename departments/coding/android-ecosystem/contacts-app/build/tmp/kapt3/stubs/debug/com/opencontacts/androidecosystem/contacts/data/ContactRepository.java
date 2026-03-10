package com.opencontacts.androidecosystem.contacts.data;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000T\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\b\u0003\n\u0002\u0010\t\n\u0002\b\u0003\n\u0002\u0010\b\n\u0002\b\u0004\n\u0002\u0010\u000e\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0002\b\u0002\u0018\u00002\u00020\u0001B!\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\b\b\u0002\u0010\u0004\u001a\u00020\u0005\u0012\b\b\u0002\u0010\u0006\u001a\u00020\u0007\u00a2\u0006\u0002\u0010\bJ\u0016\u0010\t\u001a\u00020\n2\u0006\u0010\u000b\u001a\u00020\fH\u0086@\u00a2\u0006\u0002\u0010\rJ\u0014\u0010\u000e\u001a\b\u0012\u0004\u0012\u00020\f0\u000fH\u0086@\u00a2\u0006\u0002\u0010\u0010J\u0018\u0010\u0011\u001a\u0004\u0018\u00010\f2\u0006\u0010\u0012\u001a\u00020\u0013H\u0086@\u00a2\u0006\u0002\u0010\u0014J\u001c\u0010\u0015\u001a\b\u0012\u0004\u0012\u00020\f0\u000f2\u0006\u0010\u0016\u001a\u00020\u0017H\u0086@\u00a2\u0006\u0002\u0010\u0018J\u0016\u0010\u0019\u001a\u00020\u00132\u0006\u0010\u000b\u001a\u00020\fH\u0086@\u00a2\u0006\u0002\u0010\rJ\u001e\u0010\u001a\u001a\b\u0012\u0004\u0012\u00020\f0\u000f2\b\u0010\u001b\u001a\u0004\u0018\u00010\u001cH\u0086@\u00a2\u0006\u0002\u0010\u001dJ\u001e\u0010\u001e\u001a\b\u0012\u0004\u0012\u00020\f0\u000f2\b\u0010\u001f\u001a\u0004\u0018\u00010\u001cH\u0086@\u00a2\u0006\u0002\u0010\u001dJ\u000e\u0010 \u001a\u00020!H\u0086@\u00a2\u0006\u0002\u0010\u0010J\u0016\u0010\"\u001a\u00020\n2\u0006\u0010\u000b\u001a\u00020\fH\u0086@\u00a2\u0006\u0002\u0010\rR\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0004\u001a\u00020\u0005X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0006\u001a\u00020\u0007X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006#"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/data/ContactRepository;", "", "contactDao", "Lcom/opencontacts/androidecosystem/contacts/data/ContactDao;", "permissionChecker", "Lcom/opencontacts/androidecosystem/contacts/data/ContactsPermissionChecker;", "systemContactsSyncer", "Lcom/opencontacts/androidecosystem/contacts/data/SystemContactsSyncer;", "(Lcom/opencontacts/androidecosystem/contacts/data/ContactDao;Lcom/opencontacts/androidecosystem/contacts/data/ContactsPermissionChecker;Lcom/opencontacts/androidecosystem/contacts/data/SystemContactsSyncer;)V", "delete", "", "contact", "Lcom/opencontacts/androidecosystem/contacts/data/ContactEntity;", "(Lcom/opencontacts/androidecosystem/contacts/data/ContactEntity;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getAll", "", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getById", "id", "", "(JLkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getFrequentContacts", "limit", "", "(ILkotlin/coroutines/Continuation;)Ljava/lang/Object;", "insert", "queryByName", "name", "", "(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "queryByPhone", "phone", "syncWithSystemContacts", "Lcom/opencontacts/androidecosystem/contacts/data/ContactSyncResult;", "update", "contacts-app_debug"})
public final class ContactRepository {
    @org.jetbrains.annotations.NotNull()
    private final com.opencontacts.androidecosystem.contacts.data.ContactDao contactDao = null;
    @org.jetbrains.annotations.NotNull()
    private final com.opencontacts.androidecosystem.contacts.data.ContactsPermissionChecker permissionChecker = null;
    @org.jetbrains.annotations.NotNull()
    private final com.opencontacts.androidecosystem.contacts.data.SystemContactsSyncer systemContactsSyncer = null;
    
    public ContactRepository(@org.jetbrains.annotations.NotNull()
    com.opencontacts.androidecosystem.contacts.data.ContactDao contactDao, @org.jetbrains.annotations.NotNull()
    com.opencontacts.androidecosystem.contacts.data.ContactsPermissionChecker permissionChecker, @org.jetbrains.annotations.NotNull()
    com.opencontacts.androidecosystem.contacts.data.SystemContactsSyncer systemContactsSyncer) {
        super();
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object insert(@org.jetbrains.annotations.NotNull()
    com.opencontacts.androidecosystem.contacts.data.ContactEntity contact, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.Long> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object update(@org.jetbrains.annotations.NotNull()
    com.opencontacts.androidecosystem.contacts.data.ContactEntity contact, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object delete(@org.jetbrains.annotations.NotNull()
    com.opencontacts.androidecosystem.contacts.data.ContactEntity contact, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object getById(long id, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super com.opencontacts.androidecosystem.contacts.data.ContactEntity> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object queryByName(@org.jetbrains.annotations.Nullable()
    java.lang.String name, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.opencontacts.androidecosystem.contacts.data.ContactEntity>> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object queryByPhone(@org.jetbrains.annotations.Nullable()
    java.lang.String phone, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.opencontacts.androidecosystem.contacts.data.ContactEntity>> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object getAll(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.opencontacts.androidecosystem.contacts.data.ContactEntity>> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object getFrequentContacts(int limit, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.opencontacts.androidecosystem.contacts.data.ContactEntity>> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object syncWithSystemContacts(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super com.opencontacts.androidecosystem.contacts.data.ContactSyncResult> $completion) {
        return null;
    }
}