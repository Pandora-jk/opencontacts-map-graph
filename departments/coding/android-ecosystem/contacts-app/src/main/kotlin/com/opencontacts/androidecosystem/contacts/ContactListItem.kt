package com.opencontacts.androidecosystem.contacts

class ContactListItem(
    private val onClick: (ContactRecord) -> Unit = {},
) {
    fun render(contact: ContactRecord): ContactListItemModel {
        val title = contact?.displayName?.trim().takeUnless { it.isNullOrEmpty() }
            ?: contact.email?.trim().takeUnless { it.isNullOrEmpty() }
            ?: contact.phoneNumbers.firstOrNull { it.trim().isNotEmpty() }?.trim()
            ?: "Unknown contact"
        val subtitle = contact.company?.trim().takeUnless { it.isNullOrEmpty() }
            ?: contact.email?.trim().takeUnless { it.isNullOrEmpty() }
            ?: contact.phoneNumbers.firstOrNull { it.trim().isNotEmpty() }?.trim()
            ?: "No phone or email on file"

        return ContactListItemModel(
            title = title,
            subtitle = subtitle,
            contentDescription = "Contact row for $title",
            isFavorite = contact.isFavorite,
        )
    }

    fun performClick(contact: ContactRecord?) {
        val normalizedId = contact?.id?.trim().orEmpty()
        if (normalizedId.isEmpty()) {
            return
        }
        onClick(contact.copy(id = normalizedId))
    }
}
