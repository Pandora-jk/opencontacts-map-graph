# Android Contacts App - Nightly Improvement Sprint

## Mission
Transform the basic contacts app into a fully functional app that matches industry standards (Google Contacts, Samsung Contacts, iOS Contacts) by implementing missing core features.

## Timeline
- **Start:** Tonight (2026-03-11 evening)
- **Complete:** Tomorrow morning (2026-03-12)
- **Delivery:** New APK with all improvements

## Phase 1: Competitive Analysis (Evening)

### Benchmark Apps to Study
1. **Google Contacts** (Android standard)
2. **Samsung Contacts** (OEM standard)
3. **iOS Contacts** (Apple standard)

### Key Features to Match
| Feature | Priority | Status |
|---------|----------|--------|
| Contact list with search | P0 | ❌ Missing |
| Contact photos | P0 | ❌ Missing |
| Quick actions (call/message/email) from list | P0 | ❌ Missing |
| Contact creation | P0 | ❌ Missing |
| Contact editing | P0 | ❌ Missing |
| Contact deletion | P0 | ❌ Missing |
| Favorites management (star/unstar) | P0 | ❌ Missing |
| Contact sharing (vCard) | P1 | ❌ Missing |
| Duplicate merging | P2 | ⏸️ Future |
| Contact groups management (create/edit) | P1 | ❌ Missing |
| Smooth scrolling & performance | P0 | ❌ Needs work |
| Pull-to-refresh | P1 | ❌ Missing |
| Dark mode support | P2 | ⏸️ Future |
| Contact sync status | P2 | ⏸️ Future |

## Phase 2: Implementation Plan (Overnight)

### P0 Features (Must Have)

#### 1. Search Functionality
- Search bar at top of each tab
- Real-time filtering as user types
- Search by: name, phone, email, company

#### 2. Contact Photos
- Display contact photo in list
- Display photo in details
- Placeholder avatar if no photo
- Tap to view full photo

#### 3. Quick Actions in List
- Call button on each list item
- Message button on each list item
- Optional: Email button

#### 4. Create Contact
- Floating action button (FAB)
- Form with all fields:
  - First name, Last name
  - Phone (multiple)
  - Email (multiple)
  - Address
  - Company, Job title
  - Groups
  - Photo
- Save to ContactsContract

#### 5. Edit Contact
- Edit button in details view
- Same form as create
- Update existing contact
- Cancel option

#### 6. Delete Contact
- Delete option in details (menu or button)
- Confirmation dialog
- Remove from ContactsContract

#### 7. Favorites Toggle
- Star icon in list item
- Star icon in details view
- Toggle on/off
- Update in real-time

#### 8. Performance Improvements
- Async contact loading (coroutines)
- Pagination (load 50 at a time)
- DiffUtil for smooth updates
- Loading spinners

## Phase 3: Testing Checklist

### Manual Testing (On Device)
- [ ] App launches without crash
- [ ] Contact list loads quickly (<2s for 100 contacts)
- [ ] Search works in real-time
- [ ] Tap contact → opens details
- [ ] Tap call → opens dialer with number
- [ ] Tap message → opens SMS with number
- [ ] Tap email → opens email app
- [ ] Tap address → opens maps
- [ ] Create new contact → saves successfully
- [ ] Edit contact → updates successfully
- [ ] Delete contact → removes successfully
- [ ] Toggle favorite → star appears/disappears
- [ ] Groups tab shows actual groups
- [ ] Tap group → shows filtered contacts
- [ ] Back navigation works correctly
- [ ] No frame skips during scrolling
- [ ] Photos display correctly
- [ ] All fields visible in details

### Performance Targets
- Cold start: <2s
- Contact list load: <2s for 100 contacts
- Scroll: 60fps (no frame skips)
- Search: <100ms response
- Contact open: instant

## Success Criteria
By morning, the app should:
1. ✅ Match basic functionality of Google Contacts
2. ✅ Have zero crashes in core flows
3. ✅ Load and scroll smoothly
4. ✅ Allow full CRUD operations on contacts
5. ✅ Support search across all fields
6. ✅ Display photos and all contact fields
7. ✅ Support favorites toggling
8. ✅ Work reliably on device
9. ✅ **All changes reviewed and approved** (see REVIEW_PROCESS.md)

## Review Requirements
- **All PRs must be reviewed** by an independent developer before merging
- Critical bugs (crash fixes) require security review
- Performance changes require profiler verification
- Run: `python3 ../tools/assign-reviewer.py <PR#> <author>` to assign reviewer

## Files to Modify
- `ContactListFragment.kt` - Add search, quick actions
- `ContactAdapter.kt` - Add photo, buttons, star toggle
- `ContactDetailsActivity.kt` - Add edit, delete, star toggle
- `ContactMapViewModel.kt` - Add async loading, search, CRUD operations
- New: `CreateContactActivity.kt` - Create new contact
- New: `EditContactActivity.kt` - Edit existing contact
- New: `ContactSearchView.kt` - Search bar component
- `activity_main.xml` - Add search bar, FAB
- `layout` files - Update with new UI elements

## Deliverable
New APK: `contacts-app-debug-v2.apk` with all P0 features implemented and tested.
