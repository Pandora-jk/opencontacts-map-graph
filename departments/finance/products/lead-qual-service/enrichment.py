#!/usr/bin/env python3
"""
Lead Enrichment Module
Enriches leads with additional data from APIs (Clearbit, Hunter, etc.)
"""

import requests
from typing import Optional, Dict
from dataclasses import dataclass

@dataclass
class EnrichedLead:
    """Extended lead with enrichment data."""
    original_lead: dict
    employee_count: Optional[int] = None
    annual_revenue: Optional[str] = None
    tech_stack: list = None
    social_profiles: dict = None
    funding_stage: Optional[str] = None
    last_funding_amount: Optional[str] = None
    competitors: list = None
    confidence_score: float = 0.0
    
class LeadEnricher:
    """
    Enriches leads with external data.
    Currently uses mock data (no API keys configured).
    Ready for Clearbit/Hunter integration when keys available.
    """
    
    def __init__(self, clearbit_key: Optional[str] = None, hunter_key: Optional[str] = None):
        self.clearbit_key = clearbit_key
        self.hunter_key = hunter_key
        self.use_mock = not clearbit_key and not hunter_key
    
    def enrich(self, lead: dict) -> EnrichedLead:
        """
        Enrich a lead with additional data.
        """
        if self.use_mock:
            return self._mock_enrich(lead)
        
        # Real enrichment (when API keys available)
        return self._api_enrich(lead)
    
    def _mock_enrich(self, lead: dict) -> EnrichedLead:
        """
        Mock enrichment for testing/demo purposes.
        Simulates what real APIs would return.
        """
        # Extract domain from email or website
        email = lead.get('email', '')
        website = lead.get('website', '')
        domain = self._extract_domain(email or website)
        
        # Mock data based on domain
        mock_data = self._get_mock_data(domain)
        
        return EnrichedLead(
            original_lead=lead,
            employee_count=mock_data.get('employee_count'),
            annual_revenue=mock_data.get('annual_revenue'),
            tech_stack=mock_data.get('tech_stack', []),
            social_profiles=mock_data.get('social_profiles', {}),
            funding_stage=mock_data.get('funding_stage'),
            last_funding_amount=mock_data.get('last_funding_amount'),
            competitors=mock_data.get('competitors', []),
            confidence_score=0.85  # Mock confidence
        )
    
    def _api_enrich(self, lead: dict) -> EnrichedLead:
        """
        Real enrichment using Clearbit/Hunter APIs.
        """
        email = lead.get('email', '')
        
        # Clearbit enrichment
        clearbit_data = self._clearbit_enrich(email) if self.clearbit_key else {}
        
        # Hunter enrichment
        hunter_data = self._hunter_enrich(email) if self.hunter_key else {}
        
        # Combine data
        enriched = EnrichedLead(
            original_lead=lead,
            employee_count=clearbit_data.get('metrics', {}).get('employees'),
            annual_revenue=clearbit_data.get('metrics', {}).get('annualRevenue'),
            tech_stack=clearbit_data.get('tech', []),
            social_profiles=clearbit_data.get('site', {}).get('siteProfiles', {}),
            funding_stage=clearbit_data.get('funding', {}).get('stage'),
            last_funding_amount=clearbit_data.get('funding', {}).get('lastRoundAmount'),
            competitors=[],
            confidence_score=0.95
        )
        
        return enriched
    
    def _clearbit_enrich(self, email: str) -> dict:
        """Enrich using Clearbit API."""
        if not self.clearbit_key:
            return {}
        
        try:
            response = requests.get(
                f'https://person.clearbit.com/v2/combined/find',
                params={'email': email},
                auth=(self.clearbit_key, ''),
                timeout=5
            )
            return response.json() if response.ok else {}
        except:
            return {}
    
    def _hunter_enrich(self, email: str) -> dict:
        """Enrich using Hunter API."""
        if not self.hunter_key:
            return {}
        
        try:
            response = requests.get(
                'https://api.hunter.io/v2/account',
                params={'api_key': self.hunter_key},
                timeout=5
            )
            return response.json() if response.ok else {}
        except:
            return {}
    
    def _extract_domain(self, text: str) -> str:
        """Extract domain from email or URL."""
        if '@' in text:
            return text.split('@')[1].lower()
        elif '://' in text:
            return text.split('://')[1].split('/')[0].lower()
        return text.lower()
    
    def _get_mock_data(self, domain: str) -> dict:
        """Generate realistic mock data based on domain."""
        # Simple heuristic: tech companies = higher values
        is_tech = any(kw in domain for kw in ['tech', 'soft', 'ai', 'data', 'cloud'])
        
        return {
            'employee_count': 45 if is_tech else 20,
            'annual_revenue': '$5M-$10M' if is_tech else '$1M-$5M',
            'tech_stack': ['React', 'Node.js', 'AWS'] if is_tech else ['WordPress', 'Google Workspace'],
            'social_profiles': {
                'linkedin': f'https://linkedin.com/company/{domain.split(".")[0]}',
                'twitter': f'https://twitter.com/{domain.split(".")[0]}'
            },
            'funding_stage': 'Series A' if is_tech else 'Bootstrapped',
            'last_funding_amount': '$5M' if is_tech else None,
            'competitors': ['competitor1.com', 'competitor2.com'] if is_tech else []
        }


def enrich_lead(lead: dict) -> dict:
    """
    Main entry point: Enrich a lead and return result.
    """
    enricher = LeadEnricher()
    enriched = enricher.enrich(lead)
    
    return {
        'original_lead': enriched.original_lead,
        'employee_count': enriched.employee_count,
        'annual_revenue': enriched.annual_revenue,
        'tech_stack': enriched.tech_stack,
        'social_profiles': enriched.social_profiles,
        'funding_stage': enriched.funding_stage,
        'last_funding_amount': enriched.last_funding_amount,
        'competitors': enriched.competitors,
        'confidence_score': enriched.confidence_score
    }


if __name__ == '__main__':
    import json
    
    # Test with sample lead
    test_lead = {
        'company_name': 'TechStart Inc',
        'website': 'https://techstart.io',
        'contact_name': 'John Doe',
        'email': 'john@techstart.io'
    }
    
    result = enrich_lead(test_lead)
    print(json.dumps(result, indent=2))
