package com.opencontacts.androidecosystem.contacts;

/**
 * Mutable data class for contact records.
 * Fields are mutable to allow efficient batch loading from ContactsContract.
 */
@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000D\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0005\n\u0002\u0010!\n\u0002\b\u0004\n\u0002\u0010\u0006\n\u0002\b\u0002\n\u0002\u0010\"\n\u0000\n\u0002\u0010 \n\u0000\n\u0002\u0010\u000b\n\u0002\b\u0002\n\u0002\u0010\t\n\u0000\n\u0002\u0010\b\n\u0002\b)\u0018\u00002\u00020\u0001B\u00f1\u0001\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\n\b\u0002\u0010\u0004\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0005\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0006\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0007\u001a\u0004\u0018\u00010\u0003\u0012\u000e\b\u0002\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00030\t\u0012\n\b\u0002\u0010\n\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u000b\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\f\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\r\u001a\u0004\u0018\u00010\u000e\u0012\n\b\u0002\u0010\u000f\u001a\u0004\u0018\u00010\u000e\u0012\u000e\b\u0002\u0010\u0010\u001a\b\u0012\u0004\u0012\u00020\u00030\u0011\u0012\u000e\b\u0002\u0010\u0012\u001a\b\u0012\u0004\u0012\u00020\u00030\u0013\u0012\b\b\u0002\u0010\u0014\u001a\u00020\u0015\u0012\n\b\u0002\u0010\u0016\u001a\u0004\u0018\u00010\u0003\u0012\n\b\u0002\u0010\u0017\u001a\u0004\u0018\u00010\u0018\u0012\b\b\u0002\u0010\u0019\u001a\u00020\u001a\u0012\u000e\b\u0002\u0010\u001b\u001a\b\u0012\u0004\u0012\u00020\u00030\u0013\u0012\n\b\u0002\u0010\u001c\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\u0002\u0010\u001dR\u001c\u0010\f\u001a\u0004\u0018\u00010\u0003X\u0086\u000e\u00a2\u0006\u000e\n\u0000\u001a\u0004\b\u001e\u0010\u001f\"\u0004\b \u0010!R\u001c\u0010\n\u001a\u0004\u0018\u00010\u0003X\u0086\u000e\u00a2\u0006\u000e\n\u0000\u001a\u0004\b\"\u0010\u001f\"\u0004\b#\u0010!R\u0017\u0010\u0012\u001a\b\u0012\u0004\u0012\u00020\u00030\u0013\u00a2\u0006\b\n\u0000\u001a\u0004\b$\u0010%R\u0013\u0010\u0004\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b&\u0010\u001fR\u001c\u0010\u0007\u001a\u0004\u0018\u00010\u0003X\u0086\u000e\u00a2\u0006\u000e\n\u0000\u001a\u0004\b\'\u0010\u001f\"\u0004\b(\u0010!R\u001c\u0010\u0005\u001a\u0004\u0018\u00010\u0003X\u0086\u000e\u00a2\u0006\u000e\n\u0000\u001a\u0004\b)\u0010\u001f\"\u0004\b*\u0010!R \u0010\u001b\u001a\b\u0012\u0004\u0012\u00020\u00030\u0013X\u0086\u000e\u00a2\u0006\u000e\n\u0000\u001a\u0004\b+\u0010%\"\u0004\b,\u0010-R\u0011\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b.\u0010\u001fR\u0011\u0010\u0019\u001a\u00020\u001a\u00a2\u0006\b\n\u0000\u001a\u0004\b/\u00100R\u0011\u0010\u0014\u001a\u00020\u0015\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0014\u00101R\u001c\u0010\u000b\u001a\u0004\u0018\u00010\u0003X\u0086\u000e\u00a2\u0006\u000e\n\u0000\u001a\u0004\b2\u0010\u001f\"\u0004\b3\u0010!R\u0015\u0010\u0017\u001a\u0004\u0018\u00010\u0018\u00a2\u0006\n\n\u0002\u00106\u001a\u0004\b4\u00105R\u001c\u0010\u0006\u001a\u0004\u0018\u00010\u0003X\u0086\u000e\u00a2\u0006\u000e\n\u0000\u001a\u0004\b7\u0010\u001f\"\u0004\b8\u0010!R\u0015\u0010\r\u001a\u0004\u0018\u00010\u000e\u00a2\u0006\n\n\u0002\u0010;\u001a\u0004\b9\u0010:R\u0013\u0010\u0016\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b<\u0010\u001fR\u0015\u0010\u000f\u001a\u0004\u0018\u00010\u000e\u00a2\u0006\n\n\u0002\u0010;\u001a\u0004\b=\u0010:R \u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00030\tX\u0086\u000e\u00a2\u0006\u000e\n\u0000\u001a\u0004\b>\u0010%\"\u0004\b?\u0010-R\u0013\u0010\u001c\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b@\u0010\u001fR\u0017\u0010\u0010\u001a\b\u0012\u0004\u0012\u00020\u00030\u0011\u00a2\u0006\b\n\u0000\u001a\u0004\bA\u0010B\u00a8\u0006C"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/ContactRecord;", "", "id", "", "displayName", "firstName", "lastName", "email", "phoneNumbers", "", "company", "jobTitle", "address", "latitude", "", "longitude", "tags", "", "connectionIds", "", "isFavorite", "", "locationCategory", "lastContactedAtEpochMillis", "", "interactionCount", "", "groups", "photoUri", "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/util/List;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Double;Ljava/lang/Double;Ljava/util/Set;Ljava/util/List;ZLjava/lang/String;Ljava/lang/Long;ILjava/util/List;Ljava/lang/String;)V", "getAddress", "()Ljava/lang/String;", "setAddress", "(Ljava/lang/String;)V", "getCompany", "setCompany", "getConnectionIds", "()Ljava/util/List;", "getDisplayName", "getEmail", "setEmail", "getFirstName", "setFirstName", "getGroups", "setGroups", "(Ljava/util/List;)V", "getId", "getInteractionCount", "()I", "()Z", "getJobTitle", "setJobTitle", "getLastContactedAtEpochMillis", "()Ljava/lang/Long;", "Ljava/lang/Long;", "getLastName", "setLastName", "getLatitude", "()Ljava/lang/Double;", "Ljava/lang/Double;", "getLocationCategory", "getLongitude", "getPhoneNumbers", "setPhoneNumbers", "getPhotoUri", "getTags", "()Ljava/util/Set;", "contacts_debug"})
public final class ContactRecord {
    @org.jetbrains.annotations.NotNull
    private final java.lang.String id = null;
    @org.jetbrains.annotations.Nullable
    private final java.lang.String displayName = null;
    @org.jetbrains.annotations.Nullable
    private java.lang.String firstName;
    @org.jetbrains.annotations.Nullable
    private java.lang.String lastName;
    @org.jetbrains.annotations.Nullable
    private java.lang.String email;
    @org.jetbrains.annotations.NotNull
    private java.util.List<java.lang.String> phoneNumbers;
    @org.jetbrains.annotations.Nullable
    private java.lang.String company;
    @org.jetbrains.annotations.Nullable
    private java.lang.String jobTitle;
    @org.jetbrains.annotations.Nullable
    private java.lang.String address;
    @org.jetbrains.annotations.Nullable
    private final java.lang.Double latitude = null;
    @org.jetbrains.annotations.Nullable
    private final java.lang.Double longitude = null;
    @org.jetbrains.annotations.NotNull
    private final java.util.Set<java.lang.String> tags = null;
    @org.jetbrains.annotations.NotNull
    private final java.util.List<java.lang.String> connectionIds = null;
    private final boolean isFavorite = false;
    @org.jetbrains.annotations.Nullable
    private final java.lang.String locationCategory = null;
    @org.jetbrains.annotations.Nullable
    private final java.lang.Long lastContactedAtEpochMillis = null;
    private final int interactionCount = 0;
    @org.jetbrains.annotations.NotNull
    private java.util.List<java.lang.String> groups;
    @org.jetbrains.annotations.Nullable
    private final java.lang.String photoUri = null;
    
    public ContactRecord(@org.jetbrains.annotations.NotNull
    java.lang.String id, @org.jetbrains.annotations.Nullable
    java.lang.String displayName, @org.jetbrains.annotations.Nullable
    java.lang.String firstName, @org.jetbrains.annotations.Nullable
    java.lang.String lastName, @org.jetbrains.annotations.Nullable
    java.lang.String email, @org.jetbrains.annotations.NotNull
    java.util.List<java.lang.String> phoneNumbers, @org.jetbrains.annotations.Nullable
    java.lang.String company, @org.jetbrains.annotations.Nullable
    java.lang.String jobTitle, @org.jetbrains.annotations.Nullable
    java.lang.String address, @org.jetbrains.annotations.Nullable
    java.lang.Double latitude, @org.jetbrains.annotations.Nullable
    java.lang.Double longitude, @org.jetbrains.annotations.NotNull
    java.util.Set<java.lang.String> tags, @org.jetbrains.annotations.NotNull
    java.util.List<java.lang.String> connectionIds, boolean isFavorite, @org.jetbrains.annotations.Nullable
    java.lang.String locationCategory, @org.jetbrains.annotations.Nullable
    java.lang.Long lastContactedAtEpochMillis, int interactionCount, @org.jetbrains.annotations.NotNull
    java.util.List<java.lang.String> groups, @org.jetbrains.annotations.Nullable
    java.lang.String photoUri) {
        super();
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.lang.String getId() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String getDisplayName() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String getFirstName() {
        return null;
    }
    
    public final void setFirstName(@org.jetbrains.annotations.Nullable
    java.lang.String p0) {
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String getLastName() {
        return null;
    }
    
    public final void setLastName(@org.jetbrains.annotations.Nullable
    java.lang.String p0) {
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String getEmail() {
        return null;
    }
    
    public final void setEmail(@org.jetbrains.annotations.Nullable
    java.lang.String p0) {
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.util.List<java.lang.String> getPhoneNumbers() {
        return null;
    }
    
    public final void setPhoneNumbers(@org.jetbrains.annotations.NotNull
    java.util.List<java.lang.String> p0) {
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String getCompany() {
        return null;
    }
    
    public final void setCompany(@org.jetbrains.annotations.Nullable
    java.lang.String p0) {
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String getJobTitle() {
        return null;
    }
    
    public final void setJobTitle(@org.jetbrains.annotations.Nullable
    java.lang.String p0) {
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String getAddress() {
        return null;
    }
    
    public final void setAddress(@org.jetbrains.annotations.Nullable
    java.lang.String p0) {
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.Double getLatitude() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.Double getLongitude() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.util.Set<java.lang.String> getTags() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.util.List<java.lang.String> getConnectionIds() {
        return null;
    }
    
    public final boolean isFavorite() {
        return false;
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String getLocationCategory() {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.Long getLastContactedAtEpochMillis() {
        return null;
    }
    
    public final int getInteractionCount() {
        return 0;
    }
    
    @org.jetbrains.annotations.NotNull
    public final java.util.List<java.lang.String> getGroups() {
        return null;
    }
    
    public final void setGroups(@org.jetbrains.annotations.NotNull
    java.util.List<java.lang.String> p0) {
    }
    
    @org.jetbrains.annotations.Nullable
    public final java.lang.String getPhotoUri() {
        return null;
    }
}