# Kanban - Android Ecosystem
**Priority: CRITICAL** - This is now the primary focus for the coding department.

Project scope: Android Contacts App with Material You dynamic colors, system theme support, and full CRUD operations.

## Backlog
- [ ] **Add contact photo support**
  - branch: `feature/contact-photos`
  - tests: photo display, placeholder avatar, tap to view
  - acceptance: photos display in list and details

- [ ] **Add contact sharing (vCard)**
  - branch: `feature/share-contact`
  - tests: vCard export, share intent
  - acceptance: can share contact via SMS/email/other apps

- [ ] **Add duplicate contact merging**
  - branch: `feature/merge-duplicates`
  - tests: detect duplicates, merge logic
  - acceptance: user can merge duplicate contacts

- [ ] **Dark mode optimization** (beyond system theme)
  - branch: `feature/dark-mode-optimization`
  - tests: manual theme toggle, persistent preference
  - acceptance: app respects system theme + manual override

## Ready
- [ ] **Setup GitHub repo for Obtanium auto-updates**
  - branch: `main` (production-ready releases)
  - tasks: 
    - Create GitHub Releases with APK assets
    - Add release notes with version changelog
    - Configure release signing for updates
    - Document Obtanium installation URL
    - Add auto-update metadata to APK
  - acceptance: 
    - APK downloadable from GitHub Releases
    - Obtanium can detect and install updates
    - Signed APKs for seamless updates
  - priority: CRITICAL

- [ ] **Verify Material You dynamic colors on device**
  - branch: `feature/material-you-verification`
  - tests: Android 12+ wallpaper colors, light/dark theme switching
  - acceptance: colors adapt to system wallpaper and theme

- [ ] **Fix test compilation errors**
  - branch: `bugfix/test-compilation-errors`
  - tests: all unit tests compile and pass
  - acceptance: ContactListItemTest, ContactMapViewModelTest, etc. compile successfully

## In Progress
- [x] **Enable Material You dynamic colors and system theme**
  - branch: `feature/material-you-dynamic-colors`
  - status: ✅ **COMPLETED** - APK built successfully
  - implementation: ContactsApplication class, dynamic color palette, light/dark themes
  - next: On-device verification

## Review
- [ ] **Material You implementation** - Needs independent reviewer
  - PR: #1
  - author: developer
  - reviewer: _pending assignment_
  - checklist:
    - [ ] Dynamic colors work on Android 12+
    - [ ] Light/dark theme follows system
    - [ ] Backward compatible with Android <12
    - [ ] No hardcoded colors in layouts

## Done
- [x] **Initial Android project setup**
  - Multi-module project (contacts-app, gallery-app, core-sdk)
  - Room database for local storage
  - ContactsContract integration

- [x] **Basic contact list UI**
  - ViewPager2 with tabs (All, Favorites, Groups, Map)
  - ContactAdapter with list display
  - Contact models and data layer

- [x] **Contact details view**
  - Full contact information display
  - Quick actions (call, message, email)
  - Group membership display

- [x] **Contact CRUD operations**
  - Create new contacts
  - Edit existing contacts
  - Delete contacts
  - Save to ContactsContract

- [x] **Search functionality**
  - Real-time search filter
  - Search by name, phone, email
  - Search bar in UI

- [x] **Favorites management**
  - Star/unstar contacts
  - Favorites tab filter
  - Real-time toggle

- [x] **Groups integration**
  - Display Android system groups
  - Filter contacts by group
  - Group navigation

- [x] **Material You dynamic colors**
  - System theme adaptation
  - Wallpaper-based colors (Android 12+)
  - Light/dark mode support
  - Backward compatible color palette

---

**Current Status:** 
- ✅ APK builds successfully with Material You support
- ⏳ Awaiting on-device verification
- ⏳ Test compilation fixes needed
- 📋 Independent review required before merge
