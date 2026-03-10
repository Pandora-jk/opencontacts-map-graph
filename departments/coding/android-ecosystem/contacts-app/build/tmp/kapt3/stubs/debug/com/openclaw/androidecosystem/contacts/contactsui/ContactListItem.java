package com.openclaw.androidecosystem.contacts.contactsui;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0000\u0018\u00002\u00020\u0001B\u001b\b\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0005\u00a2\u0006\u0002\u0010\u0006J\u0016\u0010\u000b\u001a\u00020\f2\u0006\u0010\r\u001a\u00020\u000e2\u0006\u0010\u000f\u001a\u00020\u0010R\u000e\u0010\u0007\u001a\u00020\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\t\u001a\u00020\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\n\u001a\u00020\bX\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0011"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactsui/ContactListItem;", "Landroid/widget/LinearLayout;", "context", "Landroid/content/Context;", "attrs", "Landroid/util/AttributeSet;", "(Landroid/content/Context;Landroid/util/AttributeSet;)V", "metaView", "Landroid/widget/TextView;", "subtitleView", "titleView", "bind", "", "contact", "Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactEntity;", "markerCount", "", "contacts-app_debug"})
public final class ContactListItem extends android.widget.LinearLayout {
    @org.jetbrains.annotations.NotNull()
    private final android.widget.TextView titleView = null;
    @org.jetbrains.annotations.NotNull()
    private final android.widget.TextView subtitleView = null;
    @org.jetbrains.annotations.NotNull()
    private final android.widget.TextView metaView = null;
    
    @kotlin.jvm.JvmOverloads()
    public ContactListItem(@org.jetbrains.annotations.NotNull()
    android.content.Context context, @org.jetbrains.annotations.Nullable()
    android.util.AttributeSet attrs) {
        super(null);
    }
    
    public final void bind(@org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity contact, int markerCount) {
    }
    
    @kotlin.jvm.JvmOverloads()
    public ContactListItem(@org.jetbrains.annotations.NotNull()
    android.content.Context context) {
        super(null);
    }
}