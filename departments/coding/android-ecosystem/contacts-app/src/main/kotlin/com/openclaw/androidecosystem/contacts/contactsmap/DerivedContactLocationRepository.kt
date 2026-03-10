package com.openclaw.androidecosystem.contacts.contactsmap

import com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlin.math.absoluteValue

class DerivedContactLocationRepository(
    private val contacts: Flow<List<ContactEntity>>,
    private val anchor: GeoCoordinate = GeoCoordinate(37.7749, -122.4194)
) : ContactLocationRepository {

    override fun observeLocations(): Flow<List<ContactLocation>> {
        return contacts.map { list ->
            list.flatMapIndexed { index, contact ->
                buildList {
                    add(createLocation(contact, index, LocationCategory.HOME, "Home"))
                    add(createLocation(contact, index + 1, LocationCategory.WORK, "Work"))
                    add(createLocation(contact, index + 2, LocationCategory.FREQUENT, "Frequent spot"))
                }
            }
        }
    }

    private fun createLocation(
        contact: ContactEntity,
        seed: Int,
        category: LocationCategory,
        labelPrefix: String
    ): ContactLocation {
        val latOffset = ((contact.id + seed).absoluteValue % 18) / 100.0
        val lonOffset = ((contact.displayName.hashCode() + seed).absoluteValue % 18) / 100.0
        val direction = if (seed % 2 == 0) 1 else -1
        return ContactLocation(
            contactId = contact.id,
            coordinate = GeoCoordinate(
                latitude = anchor.latitude + latOffset * direction,
                longitude = anchor.longitude - lonOffset * direction
            ),
            category = category,
            label = "$labelPrefix for ${contact.displayName}"
        )
    }
}
