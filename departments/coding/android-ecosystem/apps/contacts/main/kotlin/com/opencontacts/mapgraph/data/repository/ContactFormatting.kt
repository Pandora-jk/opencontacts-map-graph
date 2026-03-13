package com.opencontacts.mapgraph.data.repository

internal fun normalizePhoneNumber(phone: String?): String? {
    val digits = phone.orEmpty().filter(Char::isDigit)
    return digits.ifBlank { null }
}

internal fun formatStructuredAddress(
    street: String?,
    city: String?,
    state: String?,
    postalCode: String?,
    country: String?,
): String? {
    val locality = listOfNotNull(
        city?.takeUnless(String::isBlank),
        state?.takeUnless(String::isBlank),
    ).joinToString(", ")
    val postal = postalCode?.takeUnless(String::isBlank)
    val head = listOfNotNull(
        street?.takeUnless(String::isBlank),
        locality.takeUnless(String::isBlank),
    ).joinToString(", ")
    val combined = buildString {
        if (head.isNotBlank()) {
            append(head)
        }
        if (postal != null) {
            if (isNotEmpty()) {
                append(' ')
            }
            append(postal)
        }
        val cleanCountry = country?.takeUnless(String::isBlank)
        if (cleanCountry != null) {
            if (isNotEmpty()) {
                append(", ")
            }
            append(cleanCountry)
        }
    }.trim().trimEnd(',')
    return combined.ifBlank { null }
}
