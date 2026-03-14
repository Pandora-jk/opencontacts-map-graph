package com.opencontacts.androidecosystem.contacts;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000L\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\u0018\u00002\u00020\u0001B\u0019\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0005\u00a2\u0006\u0002\u0010\u0006J\b\u0010\u000e\u001a\u00020\u000fH\u0002J\b\u0010\u0010\u001a\u00020\u000fH\u0002J&\u0010\u0011\u001a\u0004\u0018\u00010\u00122\u0006\u0010\u0013\u001a\u00020\u00142\b\u0010\u0015\u001a\u0004\u0018\u00010\u00162\b\u0010\u0017\u001a\u0004\u0018\u00010\u0018H\u0016R\u000e\u0010\u0007\u001a\u00020\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0010\u0010\u0004\u001a\u0004\u0018\u00010\u0005X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u001c\u0010\t\u001a\u0010\u0012\f\u0012\n \u000b*\u0004\u0018\u00010\u00050\u00050\nX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\f\u001a\u00020\rX\u0082.\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0019"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/ContactListFragment;", "Landroidx/fragment/app/Fragment;", "mode", "Lcom/opencontacts/androidecosystem/contacts/ContactListMode;", "groupName", "", "(Lcom/opencontacts/androidecosystem/contacts/ContactListMode;Ljava/lang/String;)V", "contactAdapter", "Lcom/opencontacts/androidecosystem/contacts/ContactAdapter;", "requestPermissionLauncher", "Landroidx/activity/result/ActivityResultLauncher;", "kotlin.jvm.PlatformType", "viewModel", "Lcom/opencontacts/androidecosystem/contacts/ContactMapViewModel;", "checkPermissionAndLoad", "", "loadContacts", "onCreateView", "Landroid/view/View;", "inflater", "Landroid/view/LayoutInflater;", "container", "Landroid/view/ViewGroup;", "savedInstanceState", "Landroid/os/Bundle;", "contacts_debug"})
public final class ContactListFragment extends androidx.fragment.app.Fragment {
    @org.jetbrains.annotations.NotNull
    private final com.opencontacts.androidecosystem.contacts.ContactListMode mode = null;
    @org.jetbrains.annotations.Nullable
    private final java.lang.String groupName = null;
    private com.opencontacts.androidecosystem.contacts.ContactMapViewModel viewModel;
    @org.jetbrains.annotations.NotNull
    private final com.opencontacts.androidecosystem.contacts.ContactAdapter contactAdapter = null;
    @org.jetbrains.annotations.NotNull
    private final androidx.activity.result.ActivityResultLauncher<java.lang.String> requestPermissionLauncher = null;
    
    public ContactListFragment(@org.jetbrains.annotations.NotNull
    com.opencontacts.androidecosystem.contacts.ContactListMode mode, @org.jetbrains.annotations.Nullable
    java.lang.String groupName) {
        super();
    }
    
    @java.lang.Override
    @org.jetbrains.annotations.Nullable
    public android.view.View onCreateView(@org.jetbrains.annotations.NotNull
    android.view.LayoutInflater inflater, @org.jetbrains.annotations.Nullable
    android.view.ViewGroup container, @org.jetbrains.annotations.Nullable
    android.os.Bundle savedInstanceState) {
        return null;
    }
    
    private final void checkPermissionAndLoad() {
    }
    
    private final void loadContacts() {
    }
}