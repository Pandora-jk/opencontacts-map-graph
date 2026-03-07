# 🚨 Security Incident Report - API Key Exposure

**Date:** 2026-03-03  
**Severity:** HIGH  
**Status:** Requires immediate action

---

## Incident Summary

**What happened:**  
Pandora (AI assistant) accidentally exposed the GROQ API key in a user-facing message while documenting the provider testing setup.

**Exposed credential:**  
- **Type:** GROQ API Key  
- **Pattern:** `[REDACTED_GROQ_KEY]`  
- **Exposure time:** 2026-03-03 ~08:30 UTC  
- **Exposed in:** Telegram message to user (@JKnopf)

**Root cause:**  
Failure to follow security best practice: "Never display API keys, even partially masked, in user-facing messages."

---

## Impact Assessment

### Files containing the exposed key:
```
/home/ubuntu/.openclaw/.env (current, should be rotated)
/home/ubuntu/.openclaw/workspace/INFRA-AUDIT-2026-03-03.md
/home/ubuntu/.openclaw/workspace/system/openclaw.json
/home/ubuntu/.openclaw/workspace/system/agents/main/agent/models.json
/home/ubuntu/.openclaw/workspace/tools/test-models.py
/home/ubuntu/.openclaw/workspace/API-PROVIDER-STATUS-2026-03-03.md
```

### Risk level: MEDIUM-HIGH
- Key was exposed in chat message (Telegram - encrypted but stored)
- Key exists in multiple workspace files
- No evidence of unauthorized use (yet)
- Free tier limits reduce financial risk, but usage quota could be consumed

---

## Immediate Actions Required

### 1. Rotate the GROQ API Key (URGENT)
```bash
# Step 1: Go to Groq console
# https://console.groq.com/keys

# Step 2: Revoke the old key (gsk_6E76...)

# Step 3: Generate a new key

# Step 4: Update the .env file
# Edit ~/.openclaw/.env and replace the GROQ key

# Step 5: Test the new key
python3 /home/ubuntu/.openclaw/workspace/tools/test-all-providers.py
```

### 2. Update Configuration Files
After generating the new key, update these files:
- `~/.openclaw/.env` (primary)
- `/home/ubuntu/.openclaw/workspace/system/agents/main/agent/models.json`
- `/home/ubuntu/.openclaw/workspace/tools/test-models.py` (if still needed)

### 3. Clean Up Exposed Key from Logs
The key appears in documentation files. Consider:
- Deleting or sanitizing `API-PROVIDER-STATUS-2026-03-03.md`
- Reviewing git history if repository is tracked
- Checking Telegram chat history (can't be deleted retroactively)

---

## Lessons Learned

### What went wrong:
1. API key was displayed in a user message (even though partially masked)
2. Key was written to multiple documentation files unnecessarily
3. Failed to follow the security principle: "Secrets are radioactive"

### What should have been done:
1. [OK] Test the API connection (this was correct)
2. [OK] Report success/failure status (correct)
3. [FAIL] Display any part of the API key (WRONG - should show only "Key present: ✓")
4. [FAIL] Write full key to documentation files (WRONG - use environment variable references only)

### Correct pattern for the future:
```
[OK] GOOD: "API Key: [Present] ✓"
[OK] GOOD: "API Key: Configured (gsk_***...***)"
[FAIL] BAD:  "API Key: [full_key_here]"
[FAIL] BAD:  Writing full key to markdown files
```

---

## Prevention Measures

### Immediate:
- [ ] Rotate the GROQ API key
- [ ] Remove full key from documentation files
- [ ] Add pre-commit hook to prevent API key commits

### Short-term:
- [ ] Update AI assistant instructions: "Never display API keys in messages"
- [ ] Modify test scripts to never output full keys
- [ ] Add validation to `.env` file to warn if keys are logged

### Long-term:
- [ ] Implement secret scanning in CI/CD
- [ ] Use Bitwarden secrets management for all API keys
- [ ] Regular security audits of workspace files

---

## Verification Commands

After rotation, verify the old key is no longer in use:
```bash
# Check if old key still exists in files
grep -r "OPENCLAW_GROQ_API_KEY" ~/.openclaw/

# Test new key works
python3 /home/ubuntu/.openclaw/workspace/tools/test-all-providers.py
```

---

## Timeline

| Time | Event |
|------|-------|
| 2026-03-03 08:25 UTC | API key exposed in Telegram message |
| 2026-03-03 08:30 UTC | Security incident identified |
| 2026-03-03 08:35 UTC | This incident report created |
| [Pending] | Key rotation completed |
| [Pending] | Cleanup verified |

---

## Contacts

- **Incident discovered by:** User (@JKnopf)
- **Incident reported to:** User (immediate notification)
- **Next review:** After key rotation

---

**Status:** [WARN] **AWAITING KEY ROTATION**  
**Priority:** HIGH - Rotate key within 24 hours  
**Risk:** Unauthorized usage of GROQ quota
