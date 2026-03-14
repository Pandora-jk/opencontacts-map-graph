package com.opencontacts.androidecosystem.contacts

data class ThemeVerificationSnapshot(
    val dynamicColorCapable: Boolean,
    val darkThemeEnabled: Boolean,
    val primaryColor: Int,
    val surfaceColor: Int,
)

fun formatColorHex(color: Int): String = String.format("#%06X", color and 0x00FFFFFF)

fun buildThemeVerificationSummary(snapshot: ThemeVerificationSnapshot): String {
    val dynamicColorLabel = if (snapshot.dynamicColorCapable) "Dynamic color ready" else "Fallback palette"
    val themeLabel = if (snapshot.darkThemeEnabled) "Dark theme" else "Light theme"
    return buildString {
        append(dynamicColorLabel)
        append(" • ")
        append(themeLabel)
        append(" • Primary ")
        append(formatColorHex(snapshot.primaryColor))
        append(" • Surface ")
        append(formatColorHex(snapshot.surfaceColor))
    }
}

fun buildThemeVerificationHint(snapshot: ThemeVerificationSnapshot): String {
    return if (snapshot.dynamicColorCapable) {
        "Change the wallpaper or toggle system light/dark theme, then reopen the app to confirm the colors update."
    } else {
        "This device is below Android 12, so the app is showing the fallback Material 3 palette instead of wallpaper-derived colors."
    }
}
