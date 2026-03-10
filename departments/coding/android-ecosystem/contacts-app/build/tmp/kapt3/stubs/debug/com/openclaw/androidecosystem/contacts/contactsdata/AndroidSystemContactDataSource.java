package com.openclaw.androidecosystem.contacts.contactsdata;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0010\t\n\u0002\b\u0002\u0018\u00002\u00020\u0001B\r\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\u0004J\u0014\u0010\u0005\u001a\b\u0012\u0004\u0012\u00020\u00070\u0006H\u0096@\u00a2\u0006\u0002\u0010\bJ\u0012\u0010\t\u001a\u0004\u0018\u00010\n2\u0006\u0010\u000b\u001a\u00020\fH\u0002J\u0012\u0010\r\u001a\u0004\u0018\u00010\n2\u0006\u0010\u000b\u001a\u00020\fH\u0002R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u000e"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactsdata/AndroidSystemContactDataSource;", "Lcom/openclaw/androidecosystem/contacts/contactsdata/SystemContactDataSource;", "context", "Landroid/content/Context;", "(Landroid/content/Context;)V", "fetchContacts", "", "Lcom/openclaw/androidecosystem/contacts/contactsdata/SystemContactRecord;", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "queryEmail", "", "contactId", "", "queryPhone", "contacts-app_debug"})
public final class AndroidSystemContactDataSource implements com.openclaw.androidecosystem.contacts.contactsdata.SystemContactDataSource {
    @org.jetbrains.annotations.NotNull()
    private final android.content.Context context = null;
    
    public AndroidSystemContactDataSource(@org.jetbrains.annotations.NotNull()
    android.content.Context context) {
        super();
    }
    
    @java.lang.Override()
    @org.jetbrains.annotations.Nullable()
    public java.lang.Object fetchContacts(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.SystemContactRecord>> $completion) {
        return null;
    }
    
    private final java.lang.String queryPhone(long contactId) {
        return null;
    }
    
    private final java.lang.String queryEmail(long contactId) {
        return null;
    }
}