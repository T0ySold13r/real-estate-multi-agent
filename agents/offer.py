"""
agents/offer.py - Agent 4: Offer Agent
Drafts offer letters, calculates max bids, and defines bid strategies.
"""
from dataclasses import dataclass
import anthropic, config
from .financing import FinancingPlan


@dataclass
class OfferPackage:
    plan: FinancingPlan
    offer_amount: float
    max_bid: float
    offer_letter: str
    bid_strategy: str
    auction_deadline: str
    contact_info: str
    next_steps: list


class OfferAgent:
    """Agent 4 - prepares offer packages for approved deals."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    def prepare_offers(self, plans: list) -> list:
        print(f"\n[OfferAgent] Preparing {len(plans)} offers...")
        offers = []
        for plan in plans:
            try:
                offer = self._build(plan)
                offers.append(offer)
                print(f"  [+] {plan.deal.raw.address}: offer=${offer.offer_amount:,.0f} max=${offer.max_bid:,.0f}")
            except Exception as e:
                print(f"  [-] {plan.deal.raw.address}: {e}")
        return offers

    def _build(self, plan: FinancingPlan) -> OfferPackage:
        deal, raw = plan.deal, plan.deal.raw
        max_bid = (deal.estimated_arv * config.DSCR_LTV - deal.rehab_cost_estimate) * 0.90
        offer = min(raw.asking_price, max_bid)
        letter = self._letter(plan, offer)
        strategy = self._strategy(plan, offer, max_bid)
        steps = [
            f"1. Drive-by: {raw.address}",
            f"2. Title search (parcel: {raw.parcel_id or 'TBD'})",
            f"3. 2 contractor bids (budget ${deal.rehab_cost_estimate:,.0f})",
            f"4. Apply for {plan.acquisition_strategy}",
            f"5. Submit offer ${offer:,.0f} by {raw.auction_date or 'ASAP'}",
            f"6. Pre-qualify: {plan.recommended_lender.split(' - ')[0] if ' - ' in plan.recommended_lender else plan.recommended_lender}",
        ]
        return OfferPackage(plan=plan, offer_amount=offer, max_bid=max_bid,
            offer_letter=letter, bid_strategy=strategy,
            auction_deadline=raw.auction_date or "Contact seller",
            contact_info=f"Listing: {raw.listing_url}", next_steps=steps)

    def _letter(self, plan, amount) -> str:
        raw = plan.deal.raw
        msg = self.client.messages.create(model=config.CLAUDE_MODEL, max_tokens=300,
            messages=[{"role": "user", "content":
                f"Write a 150-word investor offer letter for {raw.address}, {raw.city} {raw.state}. "
                f"Offer: ${amount:,.0f}. Cash/financing ready, 30-day close, 10% earnest."}])
        return msg.content[0].text.strip()

    def _strategy(self, plan, offer, max_bid) -> str:
        msg = self.client.messages.create(model=config.CLAUDE_MODEL, max_tokens=100,
            messages=[{"role": "user", "content":
                f"2-sentence bid strategy: ask=${plan.deal.raw.asking_price:,.0f} "
                f"offer=${offer:,.0f} max=${max_bid:,.0f}. BRRRR+Section8."}])
        return msg.content[0].text.strip()
