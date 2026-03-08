#!/usr/bin/env python3
"""
AI-Powered Lead Qualification Service
Scores inbound leads based on firmographics + behavior signals.
"""

from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class Lead:
    """Represents an inbound lead."""
    company_name: str
    website: str
    contact_name: str
    email: str
    phone: Optional[str] = None
    company_size: Optional[str] = None  # e.g., "10-50", "50-200"
    industry: Optional[str] = None
    revenue: Optional[str] = None  # e.g., "$1M-$5M"
    source: Optional[str] = None  # e.g., "contact_form", "demo_request"
    message: Optional[str] = None
    
class LeadScorer:
    """
    Scores leads 0-100 based on:
    - Company size (employee count)
    - Industry fit
    - Revenue indicators
    - Source quality
    - Engagement signals
    """
    
    def __init__(self):
        # High-value industries (B2B SaaS, agencies, consultants)
        self.target_industries = [
            'software', 'saas', 'technology', 'digital agency', 
            'marketing agency', 'consulting', 'b2b', 'enterprise'
        ]
        
        # High-intent sources
        self.high_intent_sources = {
            'demo_request': 30,
            'pricing_page': 25,
            'contact_sales': 20,
            'contact_form': 15,
            'general': 5
        }
    
    def score(self, lead: Lead) -> dict:
        """
        Score a lead and return detailed breakdown.
        Returns: {score, breakdown, recommendation, next_action}
        """
        score = 0
        breakdown = {}
        
        # 1. Company Size Score (0-25 points)
        size_score = self._score_company_size(lead.company_size)
        breakdown['company_size'] = size_score
        score += size_score
        
        # 2. Industry Fit Score (0-25 points)
        industry_score = self._score_industry_fit(lead.industry)
        breakdown['industry_fit'] = industry_score
        score += industry_score
        
        # 3. Source Intent Score (0-30 points)
        source_score = self._score_source(lead.source)
        breakdown['source_intent'] = source_score
        score += source_score
        
        # 4. Engagement Signals (0-20 points)
        engagement_score = self._score_engagement(lead.message)
        breakdown['engagement'] = engagement_score
        score += engagement_score
        
        # Cap at 100
        score = min(score, 100)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(score, breakdown)
        next_action = self._determine_next_action(score, lead)
        
        return {
            'score': score,
            'breakdown': breakdown,
            'recommendation': recommendation,
            'next_action': next_action,
            'lead': lead
        }
    
    def _score_company_size(self, size: Optional[str]) -> int:
        """Score based on company size (employee count)."""
        if not size:
            return 10  # Default if unknown
        
        size_lower = size.lower()
        if '200' in size_lower or '500' in size_lower or 'enterprise' in size_lower:
            return 25  # Large company
        elif '50' in size_lower or '100' in size_lower:
            return 20  # Medium company
        elif '10' in size_lower or '20' in size_lower:
            return 15  # Small company
        elif '1' in size_lower or '5' in size_lower:
            return 10  # Very small
        else:
            return 10  # Unknown
    
    def _score_industry_fit(self, industry: Optional[str]) -> int:
        """Score based on industry match."""
        if not industry:
            return 12  # Default
        
        industry_lower = industry.lower()
        for target in self.target_industries:
            if target in industry_lower:
                return 25  # Perfect match
        
        # Partial matches
        if 'tech' in industry_lower or 'digital' in industry_lower:
            return 20
        elif 'service' in industry_lower or 'business' in industry_lower:
            return 15
        
        return 10  # Default
    
    def _score_source(self, source: Optional[str]) -> int:
        """Score based on lead source."""
        if not source:
            return 15  # Default
        
        source_lower = source.lower().replace(' ', '_')
        return self.high_intent_sources.get(source_lower, 15)
    
    def _score_engagement(self, message: Optional[str]) -> int:
        """Score based on message quality/engagement."""
        if not message:
            return 10  # Default
        
        message_lower = message.lower()
        score = 10  # Base score
        
        # High-intent keywords
        high_intent_keywords = [
            'urgent', 'asap', 'immediately', 'need help',
            'budget', 'price', 'cost', 'quote',
            'decision', 'buy', 'purchase', 'contract'
        ]
        
        for keyword in high_intent_keywords:
            if keyword in message_lower:
                score += 2
        
        # Length indicates engagement
        if len(message) > 100:
            score += 3
        elif len(message) > 50:
            score += 2
        
        return min(score, 20)
    
    def _generate_recommendation(self, score: int, breakdown: dict) -> str:
        """Generate human-readable recommendation."""
        if score >= 75:
            return "🔥 HOT LEAD - Immediate follow-up recommended"
        elif score >= 50:
            return "✅ QUALIFIED - Standard follow-up sequence"
        elif score >= 30:
            return "⚠️ NURTURE - Add to email nurture campaign"
        else:
            return "❌ LOW PRIORITY - Archive or long-term nurture"
    
    def _determine_next_action(self, score: int, lead: Lead) -> dict:
        """Determine specific next action for sales team."""
        if score >= 75:
            return {
                'action': 'immediate_call',
                'priority': 'high',
                'timeline': 'within 1 hour',
                'talking_points': [
                    f"Reference their interest in {lead.industry or 'our solution'}",
                    "Emphasize quick implementation",
                    "Offer demo within 24 hours"
                ]
            }
        elif score >= 50:
            return {
                'action': 'email_followup',
                'priority': 'medium',
                'timeline': 'within 24 hours',
                'talking_points': [
                    "Send case study in their industry",
                    "Offer 15-minute discovery call",
                    "Highlight ROI metrics"
                ]
            }
        else:
            return {
                'action': 'automated_nurture',
                'priority': 'low',
                'timeline': 'add to email sequence',
                'talking_points': [
                    "Send educational content",
                    "Monthly newsletter",
                    "Re-engage in 30 days"
                ]
            }


def score_lead(lead_data: dict) -> dict:
    """
    Main entry point: Score a lead from dictionary data.
    """
    lead = Lead(**lead_data)
    scorer = LeadScorer()
    result = scorer.score(lead)
    
    # Convert lead dataclass to dict for JSON serialization
    result['lead'] = {
        'company_name': lead.company_name,
        'website': lead.website,
        'contact_name': lead.contact_name,
        'email': lead.email,
        'phone': lead.phone
    }
    
    return result


if __name__ == '__main__':
    # Test with sample lead
    test_lead = {
        'company_name': 'TechStart Inc',
        'website': 'https://techstart.io',
        'contact_name': 'John Doe',
        'email': 'john@techstart.io',
        'phone': '+1-555-0123',
        'company_size': '10-50',
        'industry': 'Software/SaaS',
        'revenue': '$1M-$5M',
        'source': 'demo_request',
        'message': 'We need an urgent solution for lead qualification. Budget approved, looking to implement ASAP.'
    }
    
    result = score_lead(test_lead)
    print(json.dumps(result, indent=2))
