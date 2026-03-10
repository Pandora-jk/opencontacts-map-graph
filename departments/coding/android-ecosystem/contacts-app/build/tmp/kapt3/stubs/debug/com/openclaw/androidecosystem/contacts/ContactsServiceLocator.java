package com.openclaw.androidecosystem.contacts;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00000\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u0002\n\u0002\b\u0004\b\u00c6\u0002\u0018\u00002\u00020\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002J\u0010\u0010\t\u001a\u00020\u00042\u0006\u0010\n\u001a\u00020\u000bH\u0002J\u000e\u0010\f\u001a\u00020\u00062\u0006\u0010\n\u001a\u00020\u000bJ\u000e\u0010\r\u001a\u00020\b2\u0006\u0010\n\u001a\u00020\u000bJ\u0016\u0010\u000e\u001a\u00020\u000f2\u0006\u0010\u0010\u001a\u00020\b2\u0006\u0010\u0011\u001a\u00020\u0006J\u0006\u0010\u0012\u001a\u00020\u000fR\u0010\u0010\u0003\u001a\u0004\u0018\u00010\u0004X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0010\u0010\u0005\u001a\u0004\u0018\u00010\u0006X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0010\u0010\u0007\u001a\u0004\u0018\u00010\bX\u0082\u000e\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0013"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/ContactsServiceLocator;", "", "()V", "database", "Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactsDatabase;", "locationRepositoryOverride", "Lcom/openclaw/androidecosystem/contacts/contactsmap/ContactLocationRepository;", "repositoryOverride", "Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactRepository;", "provideDatabase", "context", "Landroid/content/Context;", "provideLocationRepository", "provideRepository", "replaceForTests", "", "repository", "locationRepository", "reset", "contacts-app_debug"})
public final class ContactsServiceLocator {
    @org.jetbrains.annotations.Nullable()
    private static com.openclaw.androidecosystem.contacts.contactsdata.ContactsDatabase database;
    @org.jetbrains.annotations.Nullable()
    private static com.openclaw.androidecosystem.contacts.contactsdata.ContactRepository repositoryOverride;
    @org.jetbrains.annotations.Nullable()
    private static com.openclaw.androidecosystem.contacts.contactsmap.ContactLocationRepository locationRepositoryOverride;
    @org.jetbrains.annotations.NotNull()
    public static final com.openclaw.androidecosystem.contacts.ContactsServiceLocator INSTANCE = null;
    
    private ContactsServiceLocator() {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.openclaw.androidecosystem.contacts.contactsdata.ContactRepository provideRepository(@org.jetbrains.annotations.NotNull()
    android.content.Context context) {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.openclaw.androidecosystem.contacts.contactsmap.ContactLocationRepository provideLocationRepository(@org.jetbrains.annotations.NotNull()
    android.content.Context context) {
        return null;
    }
    
    public final void replaceForTests(@org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsdata.ContactRepository repository, @org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsmap.ContactLocationRepository locationRepository) {
    }
    
    public final void reset() {
    }
    
    private final com.openclaw.androidecosystem.contacts.contactsdata.ContactsDatabase provideDatabase(android.content.Context context) {
        return null;
    }
}