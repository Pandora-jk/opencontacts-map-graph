package com.opencontacts.androidecosystem.contacts;

/**
 * Activity showing contacts filtered by group.
 * Opens as full-screen Activity to avoid overlay issues.
 */
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00006\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0002\u0018\u0000 \u00122\u00020\u0001:\u0001\u0012B\u0005\u00a2\u0006\u0002\u0010\u0002J\b\u0010\f\u001a\u00020\rH\u0002J\b\u0010\u000e\u001a\u00020\rH\u0002J\u0012\u0010\u000f\u001a\u00020\r2\b\u0010\u0010\u001a\u0004\u0018\u00010\u0011H\u0014R\u000e\u0010\u0003\u001a\u00020\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0010\u0010\u0005\u001a\u0004\u0018\u00010\u0006X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u001c\u0010\u0007\u001a\u0010\u0012\f\u0012\n \t*\u0004\u0018\u00010\u00060\u00060\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\n\u001a\u00020\u000bX\u0082.\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0013"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/GroupContactsActivity;", "Landroidx/appcompat/app/AppCompatActivity;", "()V", "contactAdapter", "Lcom/opencontacts/androidecosystem/contacts/ContactAdapter;", "groupName", "", "requestPermissionLauncher", "Landroidx/activity/result/ActivityResultLauncher;", "kotlin.jvm.PlatformType", "viewModel", "Lcom/opencontacts/androidecosystem/contacts/ContactMapViewModel;", "checkPermissionAndLoad", "", "loadContacts", "onCreate", "savedInstanceState", "Landroid/os/Bundle;", "Companion", "contacts_debug"})
public final class GroupContactsActivity extends androidx.appcompat.app.AppCompatActivity {
    private com.opencontacts.androidecosystem.contacts.ContactMapViewModel viewModel;
    @org.jetbrains.annotations.Nullable
    private java.lang.String groupName;
    @org.jetbrains.annotations.NotNull
    private final com.opencontacts.androidecosystem.contacts.ContactAdapter contactAdapter = null;
    @org.jetbrains.annotations.NotNull
    private final androidx.activity.result.ActivityResultLauncher<java.lang.String> requestPermissionLauncher = null;
    @org.jetbrains.annotations.NotNull
    public static final java.lang.String EXTRA_GROUP_NAME = "group_name";
    @org.jetbrains.annotations.NotNull
    public static final com.opencontacts.androidecosystem.contacts.GroupContactsActivity.Companion Companion = null;
    
    public GroupContactsActivity() {
        super();
    }
    
    @java.lang.Override
    protected void onCreate(@org.jetbrains.annotations.Nullable
    android.os.Bundle savedInstanceState) {
    }
    
    private final void checkPermissionAndLoad() {
    }
    
    private final void loadContacts() {
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000 \n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\b\u0086\u0003\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002J\u0016\u0010\u0005\u001a\u00020\u00062\u0006\u0010\u0007\u001a\u00020\b2\u0006\u0010\t\u001a\u00020\u0004R\u000e\u0010\u0003\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000\u00a8\u0006\n"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/GroupContactsActivity$Companion;", "", "()V", "EXTRA_GROUP_NAME", "", "createIntent", "Landroid/content/Intent;", "context", "Landroid/content/Context;", "groupName", "contacts_debug"})
    public static final class Companion {
        
        private Companion() {
            super();
        }
        
        @org.jetbrains.annotations.NotNull
        public final android.content.Intent createIntent(@org.jetbrains.annotations.NotNull
        android.content.Context context, @org.jetbrains.annotations.NotNull
        java.lang.String groupName) {
            return null;
        }
    }
}