package com.opencontacts.androidecosystem.contacts;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000>\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000b\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0007\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u0002\n\u0002\b\u0003\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002J\u001e\u0010\u0012\u001a\b\u0012\u0004\u0012\u00020\n0\u00052\u0006\u0010\u0013\u001a\u00020\u00142\u0006\u0010\u0015\u001a\u00020\nH\u0002J\u000e\u0010\u0016\u001a\u00020\u00172\u0006\u0010\u0013\u001a\u00020\u0014J\u0016\u0010\u0018\u001a\b\u0012\u0004\u0012\u00020\u00060\u00052\u0006\u0010\u0013\u001a\u00020\u0014H\u0002J\u000e\u0010\u0019\u001a\u00020\u00172\u0006\u0010\u0013\u001a\u00020\u0014R\u001a\u0010\u0003\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00060\u00050\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0014\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\b0\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0016\u0010\t\u001a\n\u0012\u0006\u0012\u0004\u0018\u00010\n0\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u001d\u0010\u000b\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00060\u00050\f\u00a2\u0006\b\n\u0000\u001a\u0004\b\r\u0010\u000eR\u0017\u0010\u000f\u001a\b\u0012\u0004\u0012\u00020\b0\f\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000f\u0010\u000eR\u0019\u0010\u0010\u001a\n\u0012\u0006\u0012\u0004\u0018\u00010\n0\f\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0011\u0010\u000e\u00a8\u0006\u001a"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/ContactMapViewModel;", "Landroidx/lifecycle/ViewModel;", "()V", "_contacts", "Landroidx/lifecycle/MutableLiveData;", "", "Lcom/opencontacts/androidecosystem/contacts/ContactRecord;", "_isLoading", "", "_loadError", "", "contacts", "Landroidx/lifecycle/LiveData;", "getContacts", "()Landroidx/lifecycle/LiveData;", "isLoading", "loadError", "getLoadError", "getContactGroups", "context", "Landroid/content/Context;", "contactId", "loadContacts", "", "loadContactsFromDeviceOptimized", "reloadContacts", "contacts_debug"})
public final class ContactMapViewModel extends androidx.lifecycle.ViewModel {
    @org.jetbrains.annotations.NotNull
    private final androidx.lifecycle.MutableLiveData<java.util.List<com.opencontacts.androidecosystem.contacts.ContactRecord>> _contacts = null;
    @org.jetbrains.annotations.NotNull
    private final androidx.lifecycle.LiveData<java.util.List<com.opencontacts.androidecosystem.contacts.ContactRecord>> contacts = null;
    @org.jetbrains.annotations.NotNull
    private final androidx.lifecycle.MutableLiveData<java.lang.Boolean> _isLoading = null;
    @org.jetbrains.annotations.NotNull
    private final androidx.lifecycle.LiveData<java.lang.Boolean> isLoading = null;
    @org.jetbrains.annotations.NotNull
    private final androidx.lifecycle.MutableLiveData<java.lang.String> _loadError = null;
    @org.jetbrains.annotations.NotNull
    private final androidx.lifecycle.LiveData<java.lang.String> loadError = null;
    
    public ContactMapViewModel() {
        super();
    }
    
    @org.jetbrains.annotations.NotNull
    public final androidx.lifecycle.LiveData<java.util.List<com.opencontacts.androidecosystem.contacts.ContactRecord>> getContacts() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final androidx.lifecycle.LiveData<java.lang.Boolean> isLoading() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final androidx.lifecycle.LiveData<java.lang.String> getLoadError() {
        return null;
    }
    
    public final void loadContacts(@org.jetbrains.annotations.NotNull
    android.content.Context context) {
    }
    
    public final void reloadContacts(@org.jetbrains.annotations.NotNull
    android.content.Context context) {
    }
    
    /**
     * Optimized contact loading - single query for all contacts,
     * then batch queries for related data.
     */
    private final java.util.List<com.opencontacts.androidecosystem.contacts.ContactRecord> loadContactsFromDeviceOptimized(android.content.Context context) {
        return null;
    }
    
    private final java.util.List<java.lang.String> getContactGroups(android.content.Context context, java.lang.String contactId) {
        return null;
    }
}