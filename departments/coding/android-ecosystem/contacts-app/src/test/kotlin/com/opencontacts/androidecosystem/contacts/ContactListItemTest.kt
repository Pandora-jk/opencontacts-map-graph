package com.opencontacts.androidecosystem.contacts

import io.mockk.mockk
import io.mockk.verify
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ContactListItemTest {
    @Test
    fun render_usesDisplayNameAsTitle() {
        val model = ContactListItem().render(
            contact(id = "1", displayName = "Ada Lovelace", email = "ada@example.com")
        )

        assertEquals("Ada Lovelace", model.title)
    }

    @Test
    fun render_fallsBackToEmailWhenDisplayNameMissing() {
        val model = ContactListItem().render(
            contact(id = "1", displayName = null, email = "ada@example.com")
        )

        assertEquals("ada@example.com", model.title)
    }

    @Test
    fun render_fallsBackToPhoneWhenDisplayNameAndEmailMissing() {
        val model = ContactListItem().render(
            contact(id = "1", displayName = null, email = null, phoneNumbers = listOf("555-0100"))
        )

        assertEquals("555-0100", model.title)
    }

    @Test
    fun render_usesNoChannelsFallbackForSubtitle() {
        val model = ContactListItem().render(
            contact(id = "1", displayName = null, email = null, phoneNumbers = emptyList(), company = null)
        )

        assertEquals("No phone or email on file", model.subtitle)
        assertTrue(model.contentDescription.contains("Unknown contact"))
    }

    @Test
    fun performClick_invokesCallbackWithTrimmedId() {
        val callback = mockk<(ContactRecord) -> Unit>(relaxed = true)
        val item = ContactListItem(callback)

        item.performClick(contact(id = " 123 ", displayName = "Ada"))

        verify(exactly = 1) { callback(match { it.id == "123" && it.displayName == "Ada" }) }
    }

    @Test
    fun performClick_ignoresNullOrBlankContacts() {
        val callback = mockk<(ContactRecord) -> Unit>(relaxed = true)
        val item = ContactListItem(callback)

        item.performClick(null)
        item.performClick(contact(id = " "))

        verify(exactly = 0) { callback(any()) }
    }
}
