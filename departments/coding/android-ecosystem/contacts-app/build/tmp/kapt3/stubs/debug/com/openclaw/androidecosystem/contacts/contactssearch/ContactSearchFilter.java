package com.openclaw.androidecosystem.contacts.contactssearch;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000J\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0006\n\u0000\n\u0002\u0010\"\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0002\b\u0005\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002Jk\u0010\u0003\u001a\b\u0012\u0004\u0012\u00020\u00050\u00042\f\u0010\u0006\u001a\b\u0012\u0004\u0012\u00020\u00050\u00042\b\b\u0002\u0010\u0007\u001a\u00020\b2\b\b\u0002\u0010\t\u001a\u00020\n2\u000e\b\u0002\u0010\u000b\u001a\b\u0012\u0004\u0012\u00020\f0\u00042\n\b\u0002\u0010\r\u001a\u0004\u0018\u00010\u000e2\n\b\u0002\u0010\u000f\u001a\u0004\u0018\u00010\u00102\u000e\b\u0002\u0010\u0011\u001a\b\u0012\u0004\u0012\u00020\u00130\u0012\u00a2\u0006\u0002\u0010\u0014JE\u0010\u0015\u001a\u00020\u00162\u0006\u0010\u0017\u001a\u00020\u00052\f\u0010\u0018\u001a\b\u0012\u0004\u0012\u00020\f0\u00042\b\u0010\r\u001a\u0004\u0018\u00010\u000e2\b\u0010\u000f\u001a\u0004\u0018\u00010\u00102\f\u0010\u0011\u001a\b\u0012\u0004\u0012\u00020\u00130\u0012H\u0002\u00a2\u0006\u0002\u0010\u0019J\u0018\u0010\u001a\u001a\u00020\u00162\u0006\u0010\u0017\u001a\u00020\u00052\u0006\u0010\u0007\u001a\u00020\bH\u0002\u00a8\u0006\u001b"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactssearch/ContactSearchFilter;", "", "()V", "filterContacts", "", "Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactEntity;", "contacts", "query", "", "minimumConnectionStrength", "", "locations", "Lcom/openclaw/androidecosystem/contacts/contactsmap/ContactLocation;", "anchor", "Lcom/openclaw/androidecosystem/contacts/contactsmap/GeoCoordinate;", "maxDistanceKm", "", "categories", "", "Lcom/openclaw/androidecosystem/contacts/contactsmap/LocationCategory;", "(Ljava/util/List;Ljava/lang/String;ILjava/util/List;Lcom/openclaw/androidecosystem/contacts/contactsmap/GeoCoordinate;Ljava/lang/Double;Ljava/util/Set;)Ljava/util/List;", "matchesLocationFilter", "", "contact", "contactLocations", "(Lcom/openclaw/androidecosystem/contacts/contactsdata/ContactEntity;Ljava/util/List;Lcom/openclaw/androidecosystem/contacts/contactsmap/GeoCoordinate;Ljava/lang/Double;Ljava/util/Set;)Z", "matchesQuery", "contacts-app_debug"})
public final class ContactSearchFilter {
    
    public ContactSearchFilter() {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity> filterContacts(@org.jetbrains.annotations.NotNull()
    java.util.List<com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity> contacts, @org.jetbrains.annotations.NotNull()
    java.lang.String query, int minimumConnectionStrength, @org.jetbrains.annotations.NotNull()
    java.util.List<com.openclaw.androidecosystem.contacts.contactsmap.ContactLocation> locations, @org.jetbrains.annotations.Nullable()
    com.openclaw.androidecosystem.contacts.contactsmap.GeoCoordinate anchor, @org.jetbrains.annotations.Nullable()
    java.lang.Double maxDistanceKm, @org.jetbrains.annotations.NotNull()
    java.util.Set<? extends com.openclaw.androidecosystem.contacts.contactsmap.LocationCategory> categories) {
        return null;
    }
    
    private final boolean matchesQuery(com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity contact, java.lang.String query) {
        return false;
    }
    
    private final boolean matchesLocationFilter(com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity contact, java.util.List<com.openclaw.androidecosystem.contacts.contactsmap.ContactLocation> contactLocations, com.openclaw.androidecosystem.contacts.contactsmap.GeoCoordinate anchor, java.lang.Double maxDistanceKm, java.util.Set<? extends com.openclaw.androidecosystem.contacts.contactsmap.LocationCategory> categories) {
        return false;
    }
}