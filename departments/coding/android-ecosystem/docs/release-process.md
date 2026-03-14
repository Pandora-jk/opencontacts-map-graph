# Contacts Release Process

1. Create a release keystore and keep the binary out of git.
2. Copy `keystore.properties.example` to `keystore.properties` for local signed builds.
3. Add these GitHub Actions secrets:
   - `CONTACTS_KEYSTORE_BASE64`
   - `CONTACTS_KEYSTORE_PASSWORD`
   - `CONTACTS_KEY_ALIAS`
   - `CONTACTS_KEY_PASSWORD`
4. Push feature branches normally to trigger `:apps:contacts:assembleDebug`.
5. Create and push a tag like `v1.0.0` to trigger the signed release APK job.
6. GitHub Releases will publish `contacts-vX.Y.Z.apk`, which Obtanium can track.

Local Gradle execution is currently blocked in this sandbox by socket restrictions, so GitHub Actions is the authoritative APK build path from this environment.
