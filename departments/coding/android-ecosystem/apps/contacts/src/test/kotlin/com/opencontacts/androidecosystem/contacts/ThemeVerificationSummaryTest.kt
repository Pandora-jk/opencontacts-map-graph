package com.opencontacts.androidecosystem.contacts

import org.junit.Assert.assertEquals
import org.junit.Test

class ThemeVerificationSummaryTest {
    @Test
    fun formatColorHex_trimsAlphaChannel() {
        assertEquals("#112233", formatColorHex(0xFF112233.toInt()))
    }

    @Test
    fun buildThemeVerificationSummary_reportsDynamicDarkThemeValues() {
        val summary = buildThemeVerificationSummary(
            ThemeVerificationSnapshot(
                dynamicColorCapable = true,
                darkThemeEnabled = true,
                primaryColor = 0xFF5DDBC8.toInt(),
                surfaceColor = 0xFF191C1E.toInt(),
            ),
        )

        assertEquals(
            "Dynamic color ready • Dark theme • Primary #5DDBC8 • Surface #191C1E",
            summary,
        )
    }

    @Test
    fun buildThemeVerificationHint_reportsFallbackMessageBelowAndroid12() {
        val hint = buildThemeVerificationHint(
            ThemeVerificationSnapshot(
                dynamicColorCapable = false,
                darkThemeEnabled = false,
                primaryColor = 0xFFF5F1E8.toInt(),
                surfaceColor = 0xFFF5F1E8.toInt(),
            ),
        )

        assertEquals(
            "This device is below Android 12, so the app is showing the fallback Material 3 palette instead of wallpaper-derived colors.",
            hint,
        )
    }
}
