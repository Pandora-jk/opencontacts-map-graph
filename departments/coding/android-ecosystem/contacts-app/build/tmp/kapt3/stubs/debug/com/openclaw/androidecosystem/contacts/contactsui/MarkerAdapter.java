package com.openclaw.androidecosystem.contacts.contactsui;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000*\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u0002\n\u0002\b\u0002\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0004\u0018\u00002\u000e\u0012\u0004\u0012\u00020\u0002\u0012\u0004\u0012\u00020\u00030\u0001:\u0002\u000e\u000fB\u0005\u00a2\u0006\u0002\u0010\u0004J\u0018\u0010\u0005\u001a\u00020\u00062\u0006\u0010\u0007\u001a\u00020\u00032\u0006\u0010\b\u001a\u00020\tH\u0016J\u0018\u0010\n\u001a\u00020\u00032\u0006\u0010\u000b\u001a\u00020\f2\u0006\u0010\r\u001a\u00020\tH\u0016\u00a8\u0006\u0010"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactsui/MarkerAdapter;", "Landroidx/recyclerview/widget/ListAdapter;", "error/NonExistentClass", "Lcom/openclaw/androidecosystem/contacts/contactsui/MarkerAdapter$MarkerViewHolder;", "()V", "onBindViewHolder", "", "holder", "position", "", "onCreateViewHolder", "parent", "Landroid/view/ViewGroup;", "viewType", "DiffCallback", "MarkerViewHolder", "contacts-app_debug"})
public final class MarkerAdapter extends androidx.recyclerview.widget.ListAdapter<error.NonExistentClass, com.openclaw.androidecosystem.contacts.contactsui.MarkerAdapter.MarkerViewHolder> {
    
    public MarkerAdapter() {
        super(null);
    }
    
    @java.lang.Override()
    @org.jetbrains.annotations.NotNull()
    public com.openclaw.androidecosystem.contacts.contactsui.MarkerAdapter.MarkerViewHolder onCreateViewHolder(@org.jetbrains.annotations.NotNull()
    android.view.ViewGroup parent, int viewType) {
        return null;
    }
    
    @java.lang.Override()
    public void onBindViewHolder(@org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsui.MarkerAdapter.MarkerViewHolder holder, int position) {
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0014\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u000b\n\u0002\b\u0005\b\u00c2\u0002\u0018\u00002\b\u0012\u0004\u0012\u00020\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0003J\u001d\u0010\u0004\u001a\u00020\u00052\u0006\u0010\u0006\u001a\u00020\u00022\u0006\u0010\u0007\u001a\u00020\u0002H\u0016\u00a2\u0006\u0002\u0010\bJ\u001d\u0010\t\u001a\u00020\u00052\u0006\u0010\u0006\u001a\u00020\u00022\u0006\u0010\u0007\u001a\u00020\u0002H\u0016\u00a2\u0006\u0002\u0010\b\u00a8\u0006\n"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactsui/MarkerAdapter$DiffCallback;", "Landroidx/recyclerview/widget/DiffUtil$ItemCallback;", "error/NonExistentClass", "()V", "areContentsTheSame", "", "oldItem", "newItem", "(Lerror/NonExistentClass;Lerror/NonExistentClass;)Z", "areItemsTheSame", "contacts-app_debug"})
    static final class DiffCallback extends androidx.recyclerview.widget.DiffUtil.ItemCallback<error.NonExistentClass> {
        @org.jetbrains.annotations.NotNull()
        public static final com.openclaw.androidecosystem.contacts.contactsui.MarkerAdapter.DiffCallback INSTANCE = null;
        
        private DiffCallback() {
            super();
        }
        
        @java.lang.Override()
        public boolean areItemsTheSame(@org.jetbrains.annotations.NotNull()
        error.NonExistentClass oldItem, @org.jetbrains.annotations.NotNull()
        error.NonExistentClass newItem) {
            return false;
        }
        
        @java.lang.Override()
        public boolean areContentsTheSame(@org.jetbrains.annotations.NotNull()
        error.NonExistentClass oldItem, @org.jetbrains.annotations.NotNull()
        error.NonExistentClass newItem) {
            return false;
        }
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u001a\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u0002\n\u0002\b\u0004\u0018\u00002\u00020\u0001B\r\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\u0004J\u0013\u0010\u0005\u001a\u00020\u00062\u0006\u0010\u0007\u001a\u00020\b\u00a2\u0006\u0002\u0010\tR\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\n"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactsui/MarkerAdapter$MarkerViewHolder;", "Landroidx/recyclerview/widget/RecyclerView$ViewHolder;", "item", "Lcom/openclaw/androidecosystem/contacts/contactsui/ContactMarkerInfoWindow;", "(Lcom/openclaw/androidecosystem/contacts/contactsui/ContactMarkerInfoWindow;)V", "bind", "", "marker", "error/NonExistentClass", "(Lerror/NonExistentClass;)V", "contacts-app_debug"})
    public static final class MarkerViewHolder extends androidx.recyclerview.widget.RecyclerView.ViewHolder {
        @org.jetbrains.annotations.NotNull()
        private final com.openclaw.androidecosystem.contacts.contactsui.ContactMarkerInfoWindow item = null;
        
        public MarkerViewHolder(@org.jetbrains.annotations.NotNull()
        com.openclaw.androidecosystem.contacts.contactsui.ContactMarkerInfoWindow item) {
            super(null);
        }
        
        public final void bind(@org.jetbrains.annotations.NotNull()
        error.NonExistentClass marker) {
        }
    }
}