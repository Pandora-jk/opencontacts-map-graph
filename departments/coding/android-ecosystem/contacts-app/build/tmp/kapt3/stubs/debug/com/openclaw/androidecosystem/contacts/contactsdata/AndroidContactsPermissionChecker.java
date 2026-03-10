package com.openclaw.androidecosystem.contacts.contactsdata;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0000\u0018\u00002\u00020\u0001B\r\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\u0004J\b\u0010\u0005\u001a\u00020\u0006H\u0016R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0007"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactsdata/AndroidContactsPermissionChecker;", "Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactsPermissionChecker;", "context", "Landroid/content/Context;", "(Landroid/content/Context;)V", "hasContactsPermission", "", "contacts-app_debug"})
public final class AndroidContactsPermissionChecker implements com.openclaw.androidecosystem.contacts.contactsdata.ContactsPermissionChecker {
    @org.jetbrains.annotations.NotNull()
    private final android.content.Context context = null;
    
    public AndroidContactsPermissionChecker(@org.jetbrains.annotations.NotNull()
    android.content.Context context) {
        super();
    }
    
    @java.lang.Override()
    public boolean hasContactsPermission() {
        return false;
    }
}