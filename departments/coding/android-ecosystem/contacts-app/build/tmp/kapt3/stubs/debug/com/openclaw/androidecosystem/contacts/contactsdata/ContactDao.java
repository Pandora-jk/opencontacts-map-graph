package com.openclaw.androidecosystem.contacts.contactsdata;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000B\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\b\u0002\n\u0002\u0010\t\n\u0002\b\u0003\n\u0002\u0010\b\n\u0002\b\u0006\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0007\bg\u0018\u00002\u00020\u0001J\u000e\u0010\u0002\u001a\u00020\u0003H\u00a7@\u00a2\u0006\u0002\u0010\u0004J\u0016\u0010\u0005\u001a\u00020\u00032\u0006\u0010\u0006\u001a\u00020\u0007H\u00a7@\u00a2\u0006\u0002\u0010\bJ\u0014\u0010\t\u001a\b\u0012\u0004\u0012\u00020\u00070\nH\u00a7@\u00a2\u0006\u0002\u0010\u0004J\u0018\u0010\u000b\u001a\u0004\u0018\u00010\u00072\u0006\u0010\f\u001a\u00020\rH\u00a7@\u00a2\u0006\u0002\u0010\u000eJ\u001c\u0010\u000f\u001a\b\u0012\u0004\u0012\u00020\u00070\n2\u0006\u0010\u0010\u001a\u00020\u0011H\u00a7@\u00a2\u0006\u0002\u0010\u0012J\u0016\u0010\u0013\u001a\u00020\r2\u0006\u0010\u0006\u001a\u00020\u0007H\u00a7@\u00a2\u0006\u0002\u0010\bJ\"\u0010\u0014\u001a\b\u0012\u0004\u0012\u00020\r0\n2\f\u0010\u0015\u001a\b\u0012\u0004\u0012\u00020\u00070\nH\u00a7@\u00a2\u0006\u0002\u0010\u0016J\u0014\u0010\u0017\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00070\n0\u0018H\'J\u001c\u0010\u0019\u001a\b\u0012\u0004\u0012\u00020\u00070\n2\u0006\u0010\u001a\u001a\u00020\u001bH\u00a7@\u00a2\u0006\u0002\u0010\u001cJ\u001c\u0010\u001d\u001a\b\u0012\u0004\u0012\u00020\u00070\n2\u0006\u0010\u001e\u001a\u00020\u001bH\u00a7@\u00a2\u0006\u0002\u0010\u001cJ\u001c\u0010\u001f\u001a\b\u0012\u0004\u0012\u00020\u00070\n2\u0006\u0010 \u001a\u00020\u001bH\u00a7@\u00a2\u0006\u0002\u0010\u001cJ\u0016\u0010!\u001a\u00020\u00032\u0006\u0010\u0006\u001a\u00020\u0007H\u00a7@\u00a2\u0006\u0002\u0010\b\u00a8\u0006\""}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactDao;", "", "clear", "", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "delete", "contact", "Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactEntity;", "(Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactEntity;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getAll", "", "getById", "id", "", "(JLkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getFrequentContacts", "limit", "", "(ILkotlin/coroutines/Continuation;)Ljava/lang/Object;", "insert", "insertAll", "contacts", "(Ljava/util/List;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "observeAll", "Lkotlinx/coroutines/flow/Flow;", "queryByEmail", "email", "", "(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "queryByName", "name", "queryByPhone", "phone", "update", "contacts-app_debug"})
@androidx.room.Dao()
public abstract interface ContactDao {
    
    @androidx.room.Insert(onConflict = 1)
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object insert(@org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity contact, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.Long> $completion);
    
    @androidx.room.Insert(onConflict = 1)
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object insertAll(@org.jetbrains.annotations.NotNull()
    java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity> contacts, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<java.lang.Long>> $completion);
    
    @androidx.room.Update()
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object update(@org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity contact, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion);
    
    @androidx.room.Delete()
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object delete(@org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity contact, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM contacts WHERE id = :id LIMIT 1")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getById(long id, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM contacts WHERE displayName LIKE \'%\' || :name || \'%\' COLLATE NOCASE ORDER BY displayName ASC")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object queryByName(@org.jetbrains.annotations.NotNull()
    java.lang.String name, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity>> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM contacts WHERE phone LIKE \'%\' || :phone || \'%\' ORDER BY displayName ASC")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object queryByPhone(@org.jetbrains.annotations.NotNull()
    java.lang.String phone, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity>> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM contacts WHERE email LIKE \'%\' || :email || \'%\' COLLATE NOCASE ORDER BY displayName ASC")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object queryByEmail(@org.jetbrains.annotations.NotNull()
    java.lang.String email, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity>> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM contacts ORDER BY displayName ASC")
    @org.jetbrains.annotations.NotNull()
    public abstract kotlinx.coroutines.flow.Flow<java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity>> observeAll();
    
    @androidx.room.Query(value = "SELECT * FROM contacts ORDER BY displayName ASC")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getAll(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity>> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM contacts ORDER BY connectionStrength DESC, COALESCE(lastContacted, 0) DESC, displayName ASC LIMIT :limit")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getFrequentContacts(int limit, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity>> $completion);
    
    @androidx.room.Query(value = "DELETE FROM contacts")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object clear(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion);
}