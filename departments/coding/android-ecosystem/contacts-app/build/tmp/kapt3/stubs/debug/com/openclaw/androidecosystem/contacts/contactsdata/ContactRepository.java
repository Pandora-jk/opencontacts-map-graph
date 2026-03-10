package com.openclaw.androidecosystem.contacts.contactsdata;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000F\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\t\n\u0002\b\u0002\n\u0002\u0010 \n\u0000\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0002\b\u0003\bf\u0018\u00002\u00020\u0001J\u0016\u0010\u0002\u001a\u00020\u00032\u0006\u0010\u0004\u001a\u00020\u0005H\u00a6@\u00a2\u0006\u0002\u0010\u0006J\u0018\u0010\u0007\u001a\u0004\u0018\u00010\u00052\u0006\u0010\b\u001a\u00020\tH\u00a6@\u00a2\u0006\u0002\u0010\nJ\u001c\u0010\u000b\u001a\b\u0012\u0004\u0012\u00020\u00050\f2\u0006\u0010\r\u001a\u00020\u000eH\u00a6@\u00a2\u0006\u0002\u0010\u000fJ\u0014\u0010\u0010\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00050\f0\u0011H&J\u001c\u0010\u0012\u001a\b\u0012\u0004\u0012\u00020\u00050\f2\u0006\u0010\u0013\u001a\u00020\u0014H\u00a6@\u00a2\u0006\u0002\u0010\u0015J\u001c\u0010\u0016\u001a\b\u0012\u0004\u0012\u00020\u00050\f2\u0006\u0010\u0013\u001a\u00020\u0014H\u00a6@\u00a2\u0006\u0002\u0010\u0015J\u001c\u0010\u0017\u001a\b\u0012\u0004\u0012\u00020\u00050\f2\u0006\u0010\u0013\u001a\u00020\u0014H\u00a6@\u00a2\u0006\u0002\u0010\u0015J\u000e\u0010\u0018\u001a\u00020\u0019H\u00a6@\u00a2\u0006\u0002\u0010\u001aJ\u0016\u0010\u001b\u001a\u00020\t2\u0006\u0010\u0004\u001a\u00020\u0005H\u00a6@\u00a2\u0006\u0002\u0010\u0006\u00a8\u0006\u001c"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactRepository;", "", "deleteContact", "", "contact", "Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactEntity;", "(Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactEntity;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getContact", "id", "", "(JLkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getFrequentContacts", "", "limit", "", "(ILkotlin/coroutines/Continuation;)Ljava/lang/Object;", "observeContacts", "Lkotlinx/coroutines/flow/Flow;", "searchByEmail", "query", "", "(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "searchByName", "searchByPhone", "syncSystemContacts", "Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactSyncResult;", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "upsertContact", "contacts-app_debug"})
public abstract interface ContactRepository {
    
    @org.jetbrains.annotations.NotNull()
    public abstract kotlinx.coroutines.flow.Flow<java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity>> observeContacts();
    
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getContact(long id, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity> $completion);
    
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object upsertContact(@org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity contact, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.Long> $completion);
    
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object deleteContact(@org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity contact, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion);
    
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object searchByName(@org.jetbrains.annotations.NotNull()
    java.lang.String query, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity>> $completion);
    
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object searchByPhone(@org.jetbrains.annotations.NotNull()
    java.lang.String query, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity>> $completion);
    
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object searchByEmail(@org.jetbrains.annotations.NotNull()
    java.lang.String query, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity>> $completion);
    
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getFrequentContacts(int limit, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity>> $completion);
    
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object syncSystemContacts(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super com.openclaw.androidecosystem.contacts.contactsdata.ContactSyncResult> $completion);
}