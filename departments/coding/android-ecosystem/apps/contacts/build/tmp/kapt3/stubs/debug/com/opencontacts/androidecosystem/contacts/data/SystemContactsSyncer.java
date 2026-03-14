package com.opencontacts.androidecosystem.contacts.data;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0012\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\b\n\u0002\b\u0002\b\u00e6\u0080\u0001\u0018\u00002\u00020\u0001J\u000e\u0010\u0002\u001a\u00020\u0003H\u00a6@\u00a2\u0006\u0002\u0010\u0004\u00a8\u0006\u0005"}, d2 = {"Lcom/opencontacts/androidecosystem/contacts/data/SystemContactsSyncer;", "", "syncContacts", "", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "contacts_debug"})
public abstract interface SystemContactsSyncer {
    
    @org.jetbrains.annotations.Nullable
    public abstract java.lang.Object syncContacts(@org.jetbrains.annotations.NotNull
    kotlin.coroutines.Continuation<? super java.lang.Integer> $completion);
}