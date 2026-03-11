# Android Contacts App - Critical Bug Fix Plan

## Issue Report (2026-03-11)
**Severity:** CRITICAL - App crashes on core functionality  
**Reported by:** User testing on device  
**Logcat available:** Yes (see memory/2026-03-11.md for full logs)

## Bugs Identified

### 1. Contact Tap Crash (CRITICAL)
**Symptom:** App crashes when tapping a contact  
**Error:** `ActivityNotFoundException` or similar  
**Root Cause:** Likely still an Intent issue or Activity not properly registered  
**Status:** INVESTIGATING - Previous fix didn't resolve it

### 2. Groups Navigation Overlay Bug (HIGH)
**Symptom:** Clicking a group shows contacts "just above the other stuff" with "two text above each other"  
**Expected:** Groups should replace the current view or open in a proper separate screen  
**Root Cause:** Fragment replacement logic in `ContactGroupsFragment` is using wrong container ID or not removing existing fragments  
**Current behavior:** `parentFragmentManager.beginTransaction().replace(R.id.fragment_container, fragment)`  
**Issue:** The `R.id.fragment_container` may not exist or the ViewPager2 is still showing

### 3. Performance Issues (MEDIUM)
**Symptom:** "Skipped 300+ frames" during contact loading  
**Log evidence:** `Choreographer: Skipped 333 frames! The application may be doing too much work on its main thread`  
**Root Cause:** Loading all contacts synchronously on main thread  
**Fix needed:** Move contact loading to background thread (coroutines/ViewModel)

## Action Items for Dev Team

### Immediate (Today)
1. **Debug Contact Tap Crash**
   - Re-run app with logcat attached
   - Verify `ContactDetailsActivity` is in manifest
   - Check if Intent has correct package name
   - Test with simple toast first to isolate issue

2. **Fix Groups Navigation**
   - Option A: Use proper fragment container within ViewPager2 tab
   - Option B: Open group contacts in ContactDetailsActivity-style full screen
   - Option C: Use ViewPager2 with dynamic fragment replacement
   - **Recommended:** Show group contacts in same list view, hide bottom nav temporarily

3. **Performance Optimization**
   - Add pagination to contact loading (load 50 at a time)
   - Use coroutines for background processing
   - Add loading spinner during load

### This Week
4. **Add proper contact detail view** with:
   - Full name, phone, email, groups
   - Edit contact button
   - Add to favorites toggle
   - Share contact option

5. **Add search functionality**
   - Search bar at top
   - Filter contacts by name/phone

6. **Add contact editing**
   - Edit name, phone, groups
   - Save changes back to ContactsContract

## Technical Notes

### Current Architecture
- MainActivity: Hosts ViewPager2 with 4 tabs
- ContactListFragment: Shows list of contacts (All/Favorites/Groups mode)
- ContactGroupsFragment: Shows system groups
- ContactMapFragment: Placeholder for map view
- ContactDetailsActivity: Full-screen contact details (crashing)

### Known Issues
- Fragment container ID mismatch
- Main thread blocking on contact queries
- No pagination for large contact lists
- Back stack not properly managed for group navigation

### Files to Modify
- `ContactGroupsFragment.kt` - Fix navigation logic
- `ContactListFragment.kt` - Add pagination, improve performance
- `ContactMapViewModel.kt` - Add async loading with coroutines
- `activity_main.xml` - Verify fragment container exists
- `AndroidManifest.xml` - Verify Activity registration

## Testing Checklist
- [ ] App launches without crash
- [ ] Tapping contact opens full-screen details (no overlay)
- [ ] Tapping group shows filtered contacts (proper navigation)
- [ ] Back button works correctly
- [ ] No frame skips during contact loading
- [ ] Call button opens phone dialer
- [ ] Message button opens SMS app
- [ ] Favorites shows only starred contacts
- [ ] All tab shows all contacts
- [ ] Groups tab shows actual Android groups

## Success Criteria
- Zero crashes on contact tap
- Clean navigation (no overlays, proper back stack)
- <100ms frame time during contact loading
- Smooth scrolling with 1000+ contacts
