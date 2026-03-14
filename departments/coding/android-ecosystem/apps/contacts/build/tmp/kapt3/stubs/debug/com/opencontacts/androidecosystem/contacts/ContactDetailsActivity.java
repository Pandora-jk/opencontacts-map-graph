package com.opencontacts.androidecosystem.contacts;

/**
 * Full-screen contact details view.
 * Shows contact info with action buttons (call, message, etc.)
 * Only displays fields that have actual values.
 */
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00004\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\b\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0004\u0018\u0000 \u00122\u00020\u0001:\u0001\u0012B\u0005\u00a2\u0006\u0002\u0010\u0002J\u0012\u0010\u0005\u001a\u00020\u00062\b\u0010\u0007\u001a\u0004\u0018\u00010\bH\u0014J(\u0010\t\u001a\u00020\u00062\u0006\u0010\n\u001a\u00020\u000b2\b\u0010\f\u001a\u0004\u0018\u00010\r2\f\u0010\u000e\u001a\b\u0012\u0004\u0012\u00020\u00060\u000fH\u0002J$\u0010\u0010\u001a\u00020\u00062\u0006\u0010\n\u001a\u00020\u000b2\b\u0010\f\u001a\u0004\u0018\u00010\r2\b\u0010\u0011\u001a\u0004\u0018\u00010\rH\u0002R\u0010\u0010\u0003\u001a\u0004\u0018\u00010\u0004X\u0082\u000e\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0013"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/ContactDetailsActivity;", "Landroidx/appcompat/app/AppCompatActivity;", "()V", "contact", "Lcom/opencontacts/androidecosystem/contacts/ContactRecord;", "onCreate", "", "savedInstanceState", "Landroid/os/Bundle;", "setupClickableField", "viewId", "", "value", "", "onClick", "Lkotlin/Function0;", "setupTextView", "hideIfBlank", "Companion", "contacts_debug"})
public final class ContactDetailsActivity extends androidx.appcompat.app.AppCompatActivity {
    @org.jetbrains.annotations.Nullable
    private com.opencontacts.androidecosystem.contacts.ContactRecord contact;
    @org.jetbrains.annotations.NotNull
    public static final java.lang.String EXTRA_CONTACT_ID = "contact_id";
    @org.jetbrains.annotations.NotNull
    public static final java.lang.String EXTRA_CONTACT_NAME = "contact_name";
    @org.jetbrains.annotations.NotNull
    public static final java.lang.String EXTRA_CONTACT_PHONE = "contact_phone";
    @org.jetbrains.annotations.NotNull
    public static final java.lang.String EXTRA_CONTACT_EMAIL = "contact_email";
    @org.jetbrains.annotations.NotNull
    public static final java.lang.String EXTRA_CONTACT_COMPANY = "contact_company";
    @org.jetbrains.annotations.NotNull
    public static final java.lang.String EXTRA_CONTACT_JOB_TITLE = "contact_job_title";
    @org.jetbrains.annotations.NotNull
    public static final java.lang.String EXTRA_CONTACT_ADDRESS = "contact_address";
    @org.jetbrains.annotations.NotNull
    public static final java.lang.String EXTRA_CONTACT_FIRST_NAME = "contact_first_name";
    @org.jetbrains.annotations.NotNull
    public static final java.lang.String EXTRA_CONTACT_LAST_NAME = "contact_last_name";
    @org.jetbrains.annotations.NotNull
    public static final java.lang.String EXTRA_IS_FAVORITE = "is_favorite";
    @org.jetbrains.annotations.NotNull
    public static final java.lang.String EXTRA_CONTACT_GROUPS = "contact_groups";
    @org.jetbrains.annotations.NotNull
    public static final com.opencontacts.androidecosystem.contacts.ContactDetailsActivity.Companion Companion = null;
    
    public ContactDetailsActivity() {
        super();
    }
    
    @java.lang.Override
    protected void onCreate(@org.jetbrains.annotations.Nullable
    android.os.Bundle savedInstanceState) {
    }
    
    /**
     * Sets text and visibility - only shows if value is not blank
     */
    private final void setupTextView(int viewId, java.lang.String value, java.lang.String hideIfBlank) {
    }
    
    /**
     * Makes a field clickable only if it has a value
     */
    private final void setupClickableField(int viewId, java.lang.String value, kotlin.jvm.functions.Function0<kotlin.Unit> onClick) {
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000&\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u000b\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\b\u0086\u0003\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002J\u0016\u0010\u000f\u001a\u00020\u00102\u0006\u0010\u0011\u001a\u00020\u00122\u0006\u0010\u0013\u001a\u00020\u0014R\u000e\u0010\u0003\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0006\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0007\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\b\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\t\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\n\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u000b\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\f\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\r\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u000e\u001a\u00020\u0004X\u0086T\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0015"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/ContactDetailsActivity$Companion;", "", "()V", "EXTRA_CONTACT_ADDRESS", "", "EXTRA_CONTACT_COMPANY", "EXTRA_CONTACT_EMAIL", "EXTRA_CONTACT_FIRST_NAME", "EXTRA_CONTACT_GROUPS", "EXTRA_CONTACT_ID", "EXTRA_CONTACT_JOB_TITLE", "EXTRA_CONTACT_LAST_NAME", "EXTRA_CONTACT_NAME", "EXTRA_CONTACT_PHONE", "EXTRA_IS_FAVORITE", "createIntent", "Landroid/content/Intent;", "context", "Landroid/content/Context;", "contact", "Lcom/opencontacts/androidecosystem/contacts/ContactRecord;", "contacts_debug"})
    public static final class Companion {
        
        private Companion() {
            super();
        }
        
        @org.jetbrains.annotations.NotNull
        public final android.content.Intent createIntent(@org.jetbrains.annotations.NotNull
        android.content.Context context, @org.jetbrains.annotations.NotNull
        com.opencontacts.androidecosystem.contacts.ContactRecord contact) {
            return null;
        }
    }
}