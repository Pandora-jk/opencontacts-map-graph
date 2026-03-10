package com.opencontacts.androidecosystem.contacts;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000.\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0010\u0006\n\u0000\n\u0002\u0010\u000b\n\u0002\b\u001b\b\u0086\b\u0018\u00002\u00020\u0001BK\u0012\u000e\b\u0002\u0010\u0002\u001a\b\u0012\u0004\u0012\u00020\u00040\u0003\u0012\b\b\u0002\u0010\u0005\u001a\u00020\u0006\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\b\u0012\n\b\u0002\u0010\t\u001a\u0004\u0018\u00010\n\u0012\b\b\u0002\u0010\u000b\u001a\u00020\f\u0012\b\b\u0002\u0010\r\u001a\u00020\b\u00a2\u0006\u0002\u0010\u000eJ\u000f\u0010\u001b\u001a\b\u0012\u0004\u0012\u00020\u00040\u0003H\u00c6\u0003J\t\u0010\u001c\u001a\u00020\u0006H\u00c6\u0003J\u000b\u0010\u001d\u001a\u0004\u0018\u00010\bH\u00c6\u0003J\u0010\u0010\u001e\u001a\u0004\u0018\u00010\nH\u00c6\u0003\u00a2\u0006\u0002\u0010\u0016J\t\u0010\u001f\u001a\u00020\fH\u00c6\u0003J\t\u0010 \u001a\u00020\bH\u00c6\u0003JT\u0010!\u001a\u00020\u00002\u000e\b\u0002\u0010\u0002\u001a\b\u0012\u0004\u0012\u00020\u00040\u00032\b\b\u0002\u0010\u0005\u001a\u00020\u00062\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\b2\n\b\u0002\u0010\t\u001a\u0004\u0018\u00010\n2\b\b\u0002\u0010\u000b\u001a\u00020\f2\b\b\u0002\u0010\r\u001a\u00020\bH\u00c6\u0001\u00a2\u0006\u0002\u0010\"J\u0013\u0010#\u001a\u00020\f2\b\u0010$\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010%\u001a\u00020\u0006H\u00d6\u0001J\t\u0010&\u001a\u00020\bH\u00d6\u0001R\u0013\u0010\u0007\u001a\u0004\u0018\u00010\b\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000f\u0010\u0010R\u0011\u0010\u000b\u001a\u00020\f\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0011\u0010\u0012R\u0017\u0010\u0002\u001a\b\u0012\u0004\u0012\u00020\u00040\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0013\u0010\u0014R\u0015\u0010\t\u001a\u0004\u0018\u00010\n\u00a2\u0006\n\n\u0002\u0010\u0017\u001a\u0004\b\u0015\u0010\u0016R\u0011\u0010\r\u001a\u00020\b\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0018\u0010\u0010R\u0011\u0010\u0005\u001a\u00020\u0006\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0019\u0010\u001a\u00a8\u0006\'"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/ContactMapUiState;", "", "markers", "", "Lcom/opencontacts/androidecosystem/contacts/ContactMapMarker;", "visibleCount", "", "activeCategory", "", "maxDistanceKm", "", "favoriteOnly", "", "statusMessage", "(Ljava/util/List;ILjava/lang/String;Ljava/lang/Double;ZLjava/lang/String;)V", "getActiveCategory", "()Ljava/lang/String;", "getFavoriteOnly", "()Z", "getMarkers", "()Ljava/util/List;", "getMaxDistanceKm", "()Ljava/lang/Double;", "Ljava/lang/Double;", "getStatusMessage", "getVisibleCount", "()I", "component1", "component2", "component3", "component4", "component5", "component6", "copy", "(Ljava/util/List;ILjava/lang/String;Ljava/lang/Double;ZLjava/lang/String;)Lcom/opencontacts/androidecosystem/contacts/ContactMapUiState;", "equals", "other", "hashCode", "toString", "contacts-app_debug"})
public final class ContactMapUiState {
    @org.jetbrains.annotations.NotNull()
    private final java.util.List<com.opencontacts.androidecosystem.contacts.ContactMapMarker> markers = null;
    private final int visibleCount = 0;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.String activeCategory = null;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.Double maxDistanceKm = null;
    private final boolean favoriteOnly = false;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String statusMessage = null;
    
    public ContactMapUiState(@org.jetbrains.annotations.NotNull()
    java.util.List<com.opencontacts.androidecosystem.contacts.ContactMapMarker> markers, int visibleCount, @org.jetbrains.annotations.Nullable()
    java.lang.String activeCategory, @org.jetbrains.annotations.Nullable()
    java.lang.Double maxDistanceKm, boolean favoriteOnly, @org.jetbrains.annotations.NotNull()
    java.lang.String statusMessage) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.opencontacts.androidecosystem.contacts.ContactMapMarker> getMarkers() {
        return null;
    }
    
    public final int getVisibleCount() {
        return 0;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String getActiveCategory() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Double getMaxDistanceKm() {
        return null;
    }
    
    public final boolean getFavoriteOnly() {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String getStatusMessage() {
        return null;
    }
    
    public ContactMapUiState() {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.util.List<com.opencontacts.androidecosystem.contacts.ContactMapMarker> component1() {
        return null;
    }
    
    public final int component2() {
        return 0;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.String component3() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Double component4() {
        return null;
    }
    
    public final boolean component5() {
        return false;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final java.lang.String component6() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.opencontacts.androidecosystem.contacts.ContactMapUiState copy(@org.jetbrains.annotations.NotNull()
    java.util.List<com.opencontacts.androidecosystem.contacts.ContactMapMarker> markers, int visibleCount, @org.jetbrains.annotations.Nullable()
    java.lang.String activeCategory, @org.jetbrains.annotations.Nullable()
    java.lang.Double maxDistanceKm, boolean favoriteOnly, @org.jetbrains.annotations.NotNull()
    java.lang.String statusMessage) {
        return null;
    }
    
    @java.lang.Override()
    public boolean equals(@org.jetbrains.annotations.Nullable()
    java.lang.Object other) {
        return false;
    }
    
    @java.lang.Override()
    public int hashCode() {
        return 0;
    }
    
    @java.lang.Override()
    @org.jetbrains.annotations.NotNull()
    public java.lang.String toString() {
        return null;
    }
}