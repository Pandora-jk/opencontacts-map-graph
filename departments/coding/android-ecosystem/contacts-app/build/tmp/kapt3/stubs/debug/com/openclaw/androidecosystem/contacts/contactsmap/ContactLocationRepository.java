package com.openclaw.androidecosystem.contacts.contactsmap;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\u0018\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\bf\u0018\u00002\u00020\u0001J\u0014\u0010\u0002\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00050\u00040\u0003H&\u00a8\u0006\u0006"}, d2 = {"Lcom/openclaw/androidecosystem/contacts/contactsmap/ContactLocationRepository;", "", "observeLocations", "Lkotlinx/coroutines/flow/Flow;", "", "Lcom/openclaw/androidecosystem/contacts/contactsmap/ContactLocation;", "contacts-app_debug"})
public abstract interface ContactLocationRepository {
    
    @org.jetbrains.annotations.NotNull()
    public abstract kotlinx.coroutines.flow.Flow<java.util.List<com.openclaw.androidecosystem.contacts.contactsmap.ContactLocation>> observeLocations();
}