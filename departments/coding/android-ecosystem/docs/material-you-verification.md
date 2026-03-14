# Material You Verification

Use the verification banner at the top of the contacts app to confirm the active theme state on a real device.

## What the banner shows

- Whether the device is Android 12+ and can use dynamic colors
- Whether the app is currently in light or dark theme
- The resolved primary and surface colors currently applied by the theme

## Device check flow

1. Install the branch build on an Android 12+ device.
2. Launch the app and note the banner values.
3. Change the wallpaper to something with a very different accent color.
4. Relaunch the app and confirm the primary color in the banner changes.
5. Toggle the system between light and dark theme and confirm the theme label plus surface color update.
6. Repeat once on an Android 11 or older device to confirm the banner reports the fallback palette path.

## Acceptance evidence

- Android 12+ screenshot before wallpaper change
- Android 12+ screenshot after wallpaper change
- Android 12+ screenshot in dark theme
- Android 11 or older screenshot showing fallback palette
