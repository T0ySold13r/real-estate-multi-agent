"""
agents/tenant.py - Agent 5: Tenant Finder
Identifies Section 8 / HCV programs, calculates FMR rents, drafts listings.
"""
from dataclasses import dataclass
import anthropic, config
from .offer import OfferPackage


@dataclass
class TenantPlan:
    offer: OfferPackage
    target_program: str
    housing_authority: str
    estimated_rent: float
    section8_fmr: float
    rental_listing: str
    screening_criteria: str
    management_options: list
    placement_timeline: str


class TenantAgent:
    """
    Agent 5 - Tenant Finder
    Finds local Housing Authorities, calculates Section 8 FMR rents,
    drafts rental listings, and recommends property management options.
    """

    FMR_DATA = {
        ("OH", "Cleveland"): {1: 850, 2: 975, 3: 1125, 4: 1275},
        ("OH", "Akron"):     {1: 800, 2: 950, 3: 1100, 4: 1250},
        ("MI", "Detroit"):   {1: 875, 2: 1000, 3: 1175, 4: 1325},
        ("AL", "Birmingham"):{1: 825, 2: 975, 3: 1150, 4: 1300},
        ("AL", "Huntsville"):{1: 950, 2: 1100, 3: 1300, 4: 1450},
    }

    PHA_DATA = {
        "OH": {
            "Cleveland": "Cuyahoga Metropolitan Housing Authority (CMHA) - 216-348-5000 - cmha.net",
            "Akron": "Akron Metropolitan Housing Authority - 330-762-9631 - akronhousing.org",
        },
        "MI": {
            "Detroit": "Detroit Housing Commission - 313-877-8000 - detroithousingcommission.org",
        },
        "AL": {
            "Birmingham": "Housing Authority of Birmingham District - 205-521-0600 - habd.org",
            "Huntsville": "Housing Authority of Huntsville - 256-539-0774 - hahousing.org",
        },
    }

    PM_DATA = {
        "OH": ["Realty Trust Group - rentaltrust.com", "Howard Hanna PM - howardhanna.com"],
        "MI": ["JMZ Management - jmzmanagement.com", "Beanstalk RE Solutions - beanstalk-res.com"],
        "AL": ["Renters Warehouse Birmingham - renterswarehouse.com", "RPM Birmingham - rpm-birmingham.com"],
    }

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    def create_tenant_plans(self, offers: list) -> list:
        """Create tenant placement plans for all properties."""
        print(f"\n[TenantAgent] Creating plans for {len(offers)} properties...")
        plans = []
        for offer in offers:
            try:
                plan = self._build_plan(offer)
                plans.append(plan)
                print(f"  [+] {offer.plan.deal.raw.address}: "
                      f"Sec8 @ ${plan.estimated_rent:,.0f}/mo")
            except Exception as e:
                print(f"  [-] {offer.plan.deal.raw.address}: {e}")
        return plans

    def _build_plan(self, offer: OfferPackage) -> TenantPlan:
        raw = offer.plan.deal.raw
        fmr = self._get_fmr(raw.state, raw.city, raw.bedrooms)
        premium = config.TARGET_MARKETS.get(raw.state, {}).get("avg_section8_premium", 1.0)
        rent = fmr * premium
        pha = self._get_pha(raw.state, raw.city)
        listing = self._draft_listing(raw, rent)
        pm = self.PM_DATA.get(raw.state, ["TurboTenant.com or Avail.co (DIY)"])
        pm.append("TurboTenant.com or Avail.co (free DIY option)")
        timeline = (
            "Week 1-2: Contact PHA, get on approved landlord list\n"
            "Week 2-3: Schedule HQS inspection\n"
            "Week 3-4: Pass inspection, list on Zillow/HousingList\n"
            "Week 4-8: Screen applicants, select voucher holder\n"
            "Week 8-10: Sign lease, first PHA rent check\n"
            "Total: 6-10 weeks from rehab completion"
        )
        screening = (
            "Section 8 Screening:\n"
            "- Valid HCV voucher required\n"
            "- Income verified by PHA\n"
            "- Credit: 580+ preferred\n"
            "- No violent felonies in 5 yrs\n"
            "- No evictions in 3 yrs\n"
            "- 2 landlord references"
        )
        return TenantPlan(
            offer=offer, target_program="Section 8 / Housing Choice Voucher",
            housing_authority=pha, estimated_rent=rent, section8_fmr=fmr,
            rental_listing=listing, screening_criteria=screening,
            management_options=pm, placement_timeline=timeline,
        )

    def _get_fmr(self, state, city, beds) -> float:
        for (s, c), rents in self.FMR_DATA.items():
            if s == state and city.startswith(c):
                return float(rents.get(min(beds, 4), 900))
        return float({"OH": 950, "MI": 1000, "AL": 975}.get(state, 900))

    def _get_pha(self, state, city) -> str:
        for city_key, contact in self.PHA_DATA.get(state, {}).items():
            if city.startswith(city_key):
                return contact
        return f"Search HUD.gov for PHA in {city}, {state}"

    def _draft_listing(self, raw, rent) -> str:
        msg = self.client.messages.create(
            model=config.CLAUDE_MODEL, max_tokens=200,
            messages=[{"role": "user", "content":
                f"Write a 3-sentence rental listing. Section 8 accepted.\n"
                f"{raw.bedrooms}BD/{raw.bathrooms}BA at {raw.address}, {raw.city} {raw.state}\n"
                f"Rent: ${rent:,.0f}/mo. Mention Section 8 prominently."}]
        )
        return msg.content[0].text.strip()
