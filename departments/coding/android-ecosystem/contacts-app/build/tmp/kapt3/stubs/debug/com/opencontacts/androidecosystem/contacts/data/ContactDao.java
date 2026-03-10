package com.opencontacts.androidecosystem.contacts.data;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00008\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\b\u0003\n\u0002\u0010\t\n\u0002\b\u0003\n\u0002\u0010\b\n\u0002\b\u0004\n\u0002\u0010\u000e\n\u0002\b\u0005\bg\u0018\u00002\u00020\u0001J\u0016\u0010\u0002\u001a\u00020\u00032\u0006\u0010\u0004\u001a\u00020\u0005H\u00a7@\u00a2\u0006\u0002\u0010\u0006J\u0014\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\u00050\bH\u00a7@\u00a2\u0006\u0002\u0010\tJ\u0018\u0010\n\u001a\u0004\u0018\u00010\u00052\u0006\u0010\u000b\u001a\u00020\fH\u00a7@\u00a2\u0006\u0002\u0010\rJ\u001c\u0010\u000e\u001a\b\u0012\u0004\u0012\u00020\u00050\b2\u0006\u0010\u000f\u001a\u00020\u0010H\u00a7@\u00a2\u0006\u0002\u0010\u0011J\u0016\u0010\u0012\u001a\u00020\f2\u0006\u0010\u0004\u001a\u00020\u0005H\u00a7@\u00a2\u0006\u0002\u0010\u0006J\u001e\u0010\u0013\u001a\b\u0012\u0004\u0012\u00020\u00050\b2\b\u0010\u0014\u001a\u0004\u0018\u00010\u0015H\u00a7@\u00a2\u0006\u0002\u0010\u0016J\u001e\u0010\u0017\u001a\b\u0012\u0004\u0012\u00020\u00050\b2\b\u0010\u0018\u001a\u0004\u0018\u00010\u0015H\u00a7@\u00a2\u0006\u0002\u0010\u0016J\u0016\u0010\u0019\u001a\u00020\u00032\u0006\u0010\u0004\u001a\u00020\u0005H\u00a7@\u00a2\u0006\u0002\u0010\u0006\u00a8\u0006\u001a"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/data/ContactDao;", "", "delete", "", "contact", "Lcom/opencontacts/androidecosystem/contacts/data/ContactEntity;", "(Lcom/opencontacts/androidecosystem/contacts/data/ContactEntity;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getAll", "", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getById", "id", "", "(JLkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getFrequentContacts", "limit", "", "(ILkotlin/coroutines/Continuation;)Ljava/lang/Object;", "insert", "queryByName", "name", "", "(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "queryByPhone", "phone", "update", "contacts-app_debug"})
@androidx.room.Dao()
public abstract interface ContactDao {
    
    @androidx.room.Insert(onConflict = 1)
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object insert(@org.jetbrains.annotations.NotNull()
    com.opencontacts.androidecosystem.contacts.data.ContactEntity contact, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.Long> $completion);
    
    @androidx.room.Update()
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object update(@org.jetbrains.annotations.NotNull()
    com.opencontacts.androidecosystem.contacts.data.ContactEntity contact, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion);
    
    @androidx.room.Delete()
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object delete(@org.jetbrains.annotations.NotNull()
    com.opencontacts.androidecosystem.contacts.data.ContactEntity contact, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM contacts WHERE id = :id LIMIT 1")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getById(long id, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super com.opencontacts.androidecosystem.contacts.data.ContactEntity> $completion);
    
    @androidx.room.Query(value = "\n        SELECT * FROM contacts\n        WHERE :name IS NOT NULL\n          AND TRIM(:name) != \'\'\n          AND displayName LIKE \'%\' || TRIM(:name) || \'%\' COLLATE NOCASE\n        ORDER BY displayName ASC, id ASC\n        ")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object queryByName(@org.jetbrains.annotations.Nullable()
    java.lang.String name, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.opencontacts.androidecosystem.contacts.data.ContactEntity>> $completion);
    
    @androidx.room.Query(value = "\n        SELECT * FROM contacts\n        WHERE :phone IS NOT NULL\n          AND TRIM(:phone) != \'\'\n          AND phone LIKE \'%\' || TRIM(:phone) || \'%\'\n        ORDER BY displayName ASC, id ASC\n        ")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object queryByPhone(@org.jetbrains.annotations.Nullable()
    java.lang.String phone, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.opencontacts.androidecosystem.contacts.data.ContactEntity>> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM contacts ORDER BY displayName ASC, id ASC")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getAll(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.opencontacts.androidecosystem.contacts.data.ContactEntity>> $completion);
    
    @androidx.room.Query(value = "\n        SELECT * FROM contacts\n        ORDER BY connectionStrength DESC, COALESCE(lastContacted, 0) DESC, displayName ASC, id ASC\n        LIMIT :limit\n        ")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getFrequentContacts(int limit, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.opencontacts.androidecosystem.contacts.data.ContactEntity>> $completion);
}