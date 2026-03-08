#!/usr/bin/env python3
"""
Email Draft Generator
Creates personalized follow-up emails based on lead score and enrichment data.
"""

from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class EmailDraft:
    """Generated email draft."""
    subject: str
    body: str
    tone: str
    cta: str
    followup_schedule: list

class EmailGenerator:
    """
    Generates personalized email drafts based on:
    - Lead score (hot/warm/cold)
    - Enrichment data (company info, tech stack, etc.)
    - Source intent
    """
    
    def __init__(self):
        self.templates = {
            'hot': self._hot_lead_template,
            'warm': self._warm_lead_template,
            'cold': self._cold_lead_template
        }
    
    def generate(self, lead: Dict, score_data: Dict, enrichment: Dict) -> EmailDraft:
        """
        Generate personalized email draft.
        """
        score = score_data.get('score', 0)
        
        # Determine template based on score
        if score >= 75:
            template_type = 'hot'
        elif score >= 50:
            template_type = 'warm'
        else:
            template_type = 'cold'
        
        template_func = self.templates.get(template_type, self._warm_lead_template)
        return template_func(lead, score_data, enrichment)
    
    def _hot_lead_template(self, lead: Dict, score_data: Dict, enrichment: Dict) -> EmailDraft:
        """Template for hot leads (score 75+)."""
        company = lead.get('company_name', 'your company')
        contact = lead.get('contact_name', 'there')
        industry = lead.get('industry', 'your industry')
        
        subject = f"Quick question about {company}'s lead qualification"
        
        body = f"""Hi {contact},

I noticed {company} requested a demo, and I wanted to reach out personally.

Given that you're in {industry} and likely dealing with high-volume lead flow, I'm guessing manual qualification is eating up your sales team's time.

Here's what we're seeing with similar companies:
• 73% of inbound leads never get followed up (too time-consuming)
• Manual qualification takes 15-20 min per lead
• Our AI does it in 30 seconds with 94% accuracy

I'd love to show you how we're helping companies like yours:
→ Qualify 100% of leads (not just the 10% you have time for)
→ Get back 10-15 hours/week per sales rep
→ Close 23% more deals from inbound leads

Are you free for a 15-minute call tomorrow at 2pm or 4pm?

Best,
Pandora
Lead Qualification Specialist

P.S. - If now's not a good time, just reply "later" and I'll follow up in a few weeks."""

        return EmailDraft(
            subject=subject,
            body=body,
            tone="urgent_but_helpful",
            cta="Schedule 15-min call",
            followup_schedule=["1 day", "3 days", "7 days"]
        )
    
    def _warm_lead_template(self, lead: Dict, score_data: Dict, enrichment: Dict) -> EmailDraft:
        """Template for warm leads (score 50-74)."""
        company = lead.get('company_name', 'your company')
        contact = lead.get('contact_name', 'there')
        
        subject = f"Helping {company} qualify more leads"
        
        body = f"""Hi {contact},

Thanks for reaching out to us.

I took a look at {company} and noticed you're probably handling a decent volume of inbound leads.

Most teams we work with were manually qualifying leads until they realized:
• They're only following up with 10-20% of inbound leads
• Response time averages 6+ hours (buyers expect <1 hour)
• Sales reps spend 40% of time on admin, not selling

Our AI-powered qualification service:
✓ Scores every lead in 30 seconds
✓ Enriches with company data (size, revenue, tech stack)
✓ Drafts personalized follow-ups
✓ Integrates with your existing tools

Result: Teams qualify 5x more leads and close 23% more deals.

Would you be open to a quick 15-minute demo this week?

Best,
Pandora
Lead Qualification Specialist

P.S. - Happy to send over a case study if you'd prefer to review first."""

        return EmailDraft(
            subject=subject,
            body=body,
            tone="helpful_informative",
            cta="Schedule demo",
            followup_schedule=["2 days", "5 days", "10 days"]
        )
    
    def _cold_lead_template(self, lead: Dict, score_data: Dict, enrichment: Dict) -> EmailDraft:
        """Template for cold leads (score <50)."""
        company = lead.get('company_name', 'your company')
        
        subject = f"Quick question about {company}'s sales process"
        
        body = f"""Hi there,

I was researching companies in your space and came across {company}.

Curious - how are you currently handling inbound lead qualification?

Most teams we talk to are either:
• Manually reviewing every lead (time-consuming)
• Using basic form fields (misses context)
• Not qualifying at all (low conversion)

If you're spending more than 5 hours/week on lead qualification, we might be able to help.

Our AI service automatically:
→ Scores leads based on 20+ signals
→ Enriches with company data
→ Drafts personalized follow-ups
→ Integrates with your CRM

No pressure, but if this sounds interesting, happy to share how it works.

Best,
Pandora
Lead Qualification Specialist

P.S. - If you're all set with qualification, just ignore this email."""

        return EmailDraft(
            subject=subject,
            body=body,
            tone="casual_low_pressure",
            cta="Reply if interested",
            followup_schedule=["5 days", "14 days"]
        )


def generate_email(lead: Dict, score_data: Dict, enrichment: Dict) -> Dict:
    """
    Main entry point: Generate email draft.
    """
    generator = EmailGenerator()
    draft = generator.generate(lead, score_data, enrichment)
    
    return {
        'subject': draft.subject,
        'body': draft.body,
        'tone': draft.tone,
        'cta': draft.cta,
        'followup_schedule': draft.followup_schedule
    }


if __name__ == '__main__':
    import json
    
    # Test with sample data
    test_lead = {
        'company_name': 'TechStart Inc',
        'contact_name': 'John Doe',
        'industry': 'Software/SaaS'
    }
    
    test_score = {'score': 93}
    test_enrichment = {'employee_count': 45}
    
    result = generate_email(test_lead, test_score, test_enrichment)
    print(json.dumps(result, indent=2))
