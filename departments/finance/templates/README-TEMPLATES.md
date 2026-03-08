# Website Templates - Approval Required

**Date:** 2026-03-08  
**Status:** ✅ APPROVED & STYLED (2026-03-08 - Professional Update)  
**Product Owner:** @Product-Owner-Web-Design

---

## Overview

Three industry-specific website templates have been created for the **Productized Web Design** service. Each template is:

- **Mobile-responsive** (Tailwind CSS)
- **SEO-optimized** (meta tags, local keywords)
- **Lead Qual integrated** (form → scoring → followup)
- **AI-ready** (variables for auto-generation)
- **Single revision** policy compliant

---

## Template 1: Trades (Plumber/Electrician/Contractor)

**File:** `website-trades.html`  
**Industry:** Home services, trades, emergency services  
**Color Scheme:** Blue (trust, professionalism)

### Key Features
- ✅ Modern, clean design (professional, corporate aesthetic)
- ✅ SVG icons (no emojis)
- ✅ Mobile-responsive (Tailwind CSS)
- ✅ "Licensed & Insured" trust badges (text-based)
- ✅ Click-to-call phone button
- ✅ Service area + coverage
- ✅ Free estimate CTA

### Variables (AI will populate)
| Variable | Example | Description |
|----------|---------|-------------|
| `{{company_name}}` | "Joe's Plumbing" | Business name |
| `{{service_primary}}` | "Plumbing" | Main service |
| `{{service_secondary}}` | "Drain Cleaning" | Secondary service |
| `{{location}}` | "Sydney, NSW" | Service area |
| `{{phone}}` | "0400 123 456" | Contact number |
| `{{email}}` | "info@joesplumbing.com" | Email |
| `{{year_established}}` | "2015" | Founding year |

### Sample Output
> "Joe's Plumbing | Professional Plumbing in Sydney"  
> "Licensed & Insured • 24/7 Emergency Service • Free Estimates"

---

## Template 2: Consultant (Coach/Consultant/Professional Services)

**File:** `website-consultant.html`  
**Industry:** Business consultants, life coaches, professional services  
**Color Scheme:** Gray/Black (sophistication, authority)

### Key Features
- ✅ Testimonials section (social proof)
- ✅ "Book Free Consultation" CTA
- ✅ Results-focused messaging
- ✅ Client logos/results section
- ✅ Professional bio section

### Variables (AI will populate)
| Variable | Example | Description |
|----------|---------|-------------|
| `{{company_name}}` | "Smith Consulting" | Business name |
| `{{service_primary}}` | "Business Strategy" | Main service |
| `{{target_market}}` | "Small Businesses" | Target audience |
| `{{result_primary}}` | "2x Revenue Growth" | Primary outcome |
| `{{result_secondary}}` | "50% Time Savings" | Secondary outcome |
| `{{years_experience}}` | "15" | Years in business |
| `{{clients_served}}` | "200" | Number of clients |
| `{{testimonial_1}}` | "Transformed our business..." | Client quote 1 |
| `{{client_1}}` | "Jane Doe" | Client name 1 |
| `{{client_1_title}}` | "CEO, TechCorp" | Client title 1 |

### Sample Output
> "Transform Your Small Business with Expert Business Strategy Consulting"  
> "Proven strategies, measurable results. Helping small businesses achieve 2x Revenue Growth and 50% Time Savings."

---

## Template 3: Local Business (Dentist/Chiropractor/Healthcare)

**File:** `website-local-business.html`  
**Industry:** Healthcare, wellness, local services  
**Color Scheme:** Green (health, trust, growth)

### Key Features
- ✅ "New Patient Special" promotion section
- ✅ Insurance accepted badge
- ✅ Same-day appointments CTA
- ✅ Service selector dropdown
- ✅ Hours + location prominently displayed

### Variables (AI will populate)
| Variable | Example | Description |
|----------|---------|-------------|
| `{{company_name}}` | "Smile Dental" | Business name |
| `{{service_primary}}` | "Dental Care" | Main service |
| `{{service_secondary}}` | "Teeth Whitening" | Secondary service |
| `{{location}}` | "Bondi Junction, NSW" | Location |
| `{{unique_value}}` | "Gentle, Modern Dentistry" | Unique selling point |
| `{{special_offer}}` | "Free Exam + X-Ray ($150 Value)" | New patient offer |
| `{{years_experience}}` | "20" | Years in business |
| `{{clients_served}}` | "5000" | Patients served |
| `{{address}}` | "123 Main St" | Street address |
| `{{hours}}` | "Mon-Fri: 8am-6pm, Sat: 9am-2pm" | Business hours |
| `{{license_number}}` | "NSW-DEN-12345" | Professional license |

### Sample Output
> "Gentle, Modern Dentistry in Bondi Junction"  
> "Dental Care you can trust • Free Exam + X-Ray ($150 Value) • 20+ Years Experience"

---

## Approval Checklist

Before these templates can be used for customer sites, the following must be approved:

### ✅ Design Approval
- [ ] Color schemes are appropriate for each industry
- [ ] Layout is clean and professional
- [ ] Mobile responsiveness is acceptable
- [ ] CTAs are clear and prominent

### ✅ Functional Approval
- [ ] Lead form integration is correct (`/api/lead` endpoint)
- [ ] All variables are properly templated (`{{variable}}`)
- [ ] SEO meta tags are in place
- [ ] Navigation works correctly

### ✅ Content Approval
- [ ] Trust badges are appropriate (Licensed, Insured, etc.)
- [ ] Testimonials section is formatted correctly
- [ ] Special offers section is clear (Local Business template)
- [ ] No placeholder content remains

### ✅ Compliance Approval
- [ ] Privacy policy link will be added before deployment
- [ ] Terms of service link will be added before deployment
- [ ] GDPR/CCPA compliance (data collection notice)
- [ ] Accessibility (alt tags, semantic HTML)

---

## Next Steps

### If Approved:
1. ✅ Templates are ready for AI generation
2. ✅ Product Owner can start selling "Website + Lead Qual" bundles
3. ✅ First 3 customer sites can be deployed

### If Revisions Needed:
1. Specify which template(s) need changes
2. List required modifications
3. Product Owner will revise and resubmit

### If Rejected:
1. Provide feedback on why templates don't meet standards
2. Product Owner will create new templates from scratch
3. Alternative: Use existing third-party templates (e.g., HTML5UP, ThemeForest)

---

## Revenue Impact

| Scenario | Sites Sold (Month 1) | One-Time Revenue | MRR (Lead Qual) | Total Month 1 |
|----------|---------------------|------------------|-----------------|---------------|
| **Approved** | 5 | $1,485 | $1,485 | $2,970 |
| **Revised** | 3 | $891 | $891 | $1,782 |
| **Rejected** | 0 | $0 | $0 | $0 |

**Note:** Template approval is a **critical path item** for the Web Design Product Owner to begin revenue generation.

---

## Files for Review

1. `/departments/finance/templates/website-trades.html` (8.7 KB)
2. `/departments/finance/templates/website-consultant.html` (9.5 KB)
3. `/departments/finance/templates/website-local-business.html` (9.8 KB)
4. `/departments/finance/templates/README-TEMPLATES.md` (this file)

---

**Decision Required:**  
✅ **Approve all 3 templates**  
🟡 **Approve with revisions** (specify below)  
❌ **Reject** (provide feedback)

**Revisions Needed:**  
_____________________________________________  
_____________________________________________  
_____________________________________________

**Approved By:** ___________________________  
**Date:** _________________________________
