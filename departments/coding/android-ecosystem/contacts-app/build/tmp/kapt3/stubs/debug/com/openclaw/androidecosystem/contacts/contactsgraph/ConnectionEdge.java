package com.openclaw.androidecosystem.contacts.contactsgraph;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000(\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\t\n\u0002\b\u0002\n\u0002\u0010\b\n\u0002\b\u0019\n\u0002\u0010\u000b\n\u0002\b\u0003\n\u0002\u0010\u000e\n\u0000\b\u0086\b\u0018\u00002\u00020\u0001B?\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\u0006\u0010\u0004\u001a\u00020\u0003\u0012\b\b\u0002\u0010\u0005\u001a\u00020\u0006\u0012\b\b\u0002\u0010\u0007\u001a\u00020\u0006\u0012\b\b\u0002\u0010\b\u001a\u00020\u0006\u0012\n\b\u0002\u0010\t\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\u0002\u0010\nJ\u000e\u0010\u0015\u001a\u00020\u00002\u0006\u0010\u0016\u001a\u00020\u0000J\t\u0010\u0017\u001a\u00020\u0003H\u00c6\u0003J\t\u0010\u0018\u001a\u00020\u0003H\u00c6\u0003J\t\u0010\u0019\u001a\u00020\u0006H\u00c6\u0003J\t\u0010\u001a\u001a\u00020\u0006H\u00c6\u0003J\t\u0010\u001b\u001a\u00020\u0006H\u00c6\u0003J\u0010\u0010\u001c\u001a\u0004\u0018\u00010\u0003H\u00c6\u0003\u00a2\u0006\u0002\u0010\u0011JL\u0010\u001d\u001a\u00020\u00002\b\b\u0002\u0010\u0002\u001a\u00020\u00032\b\b\u0002\u0010\u0004\u001a\u00020\u00032\b\b\u0002\u0010\u0005\u001a\u00020\u00062\b\b\u0002\u0010\u0007\u001a\u00020\u00062\b\b\u0002\u0010\b\u001a\u00020\u00062\n\b\u0002\u0010\t\u001a\u0004\u0018\u00010\u0003H\u00c6\u0001\u00a2\u0006\u0002\u0010\u001eJ\u0013\u0010\u001f\u001a\u00020 2\b\u0010\u0016\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010!\u001a\u00020\u0006H\u00d6\u0001J\u0006\u0010\"\u001a\u00020\u0000J\t\u0010#\u001a\u00020$H\u00d6\u0001R\u0011\u0010\u0005\u001a\u00020\u0006\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000b\u0010\fR\u0011\u0010\b\u001a\u00020\u0006\u00a2\u0006\b\n\u0000\u001a\u0004\b\r\u0010\fR\u0011\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000e\u0010\u000fR\u0015\u0010\t\u001a\u0004\u0018\u00010\u0003\u00a2\u0006\n\n\u0002\u0010\u0012\u001a\u0004\b\u0010\u0010\u0011R\u0011\u0010\u0007\u001a\u00020\u0006\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0013\u0010\fR\u0011\u0010\u0004\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0014\u0010\u000f\u00a8\u0006%"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactsgraph/ConnectionEdge;", "", "fromContactId", "", "toContactId", "callCount", "", "smsCount", "emailCount", "lastInteraction", "(JJIIILjava/lang/Long;)V", "getCallCount", "()I", "getEmailCount", "getFromContactId", "()J", "getLastInteraction", "()Ljava/lang/Long;", "Ljava/lang/Long;", "getSmsCount", "getToContactId", "combine", "other", "component1", "component2", "component3", "component4", "component5", "component6", "copy", "(JJIIILjava/lang/Long;)Lcom/openclaw/androidecosystem/contacts/contactsgraph/ConnectionEdge;", "equals", "", "hashCode", "normalized", "toString", "", "contacts-app_debug"})
public final class ConnectionEdge {
    private final long fromContactId = 0L;
    private final long toContactId = 0L;
    private final int callCount = 0;
    private final int smsCount = 0;
    private final int emailCount = 0;
    @org.jetbrains.annotations.Nullable()
    private final java.lang.Long lastInteraction = null;
    
    public ConnectionEdge(long fromContactId, long toContactId, int callCount, int smsCount, int emailCount, @org.jetbrains.annotations.Nullable()
    java.lang.Long lastInteraction) {
        super();
    }
    
    public final long getFromContactId() {
        return 0L;
    }
    
    public final long getToContactId() {
        return 0L;
    }
    
    public final int getCallCount() {
        return 0;
    }
    
    public final int getSmsCount() {
        return 0;
    }
    
    public final int getEmailCount() {
        return 0;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Long getLastInteraction() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionEdge normalized() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionEdge combine(@org.jetbrains.annotations.NotNull()
    com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionEdge other) {
        return null;
    }
    
    public final long component1() {
        return 0L;
    }
    
    public final long component2() {
        return 0L;
    }
    
    public final int component3() {
        return 0;
    }
    
    public final int component4() {
        return 0;
    }
    
    public final int component5() {
        return 0;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Long component6() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionEdge copy(long fromContactId, long toContactId, int callCount, int smsCount, int emailCount, @org.jetbrains.annotations.Nullable()
    java.lang.Long lastInteraction) {
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