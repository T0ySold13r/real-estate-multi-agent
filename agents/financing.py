"""
agents/financing.py - Agent 3: Financing Agent
Compares DSCR lenders and builds step-by-step financing plans.
"""
import json
from dataclasses import dataclass
import anthropic, config
from .analyzer import AnalyzedDeal


@dataclass
class FinancingPlan:
    deal: AnalyzedDeal
    acquisition_strategy: str
    acquisition_amount: float
    acquisition_rate: float
    acquisition_term_months: int
    dscr_lender_options: list
    recommended_lender: str
    refi_timeline_days: int
    net_cash_after_refi: float
    monthly_debt_service: float
    financing_summary: str
    action_items: list


class FinancingAgent:
    DSCR_LENDERS = [
        {"name": "Kiavi", "min_loan": 75000, "max_ltv": 0.80, "rate_range": "7.5-9.5%", "notes": "Fast close 10-15 days"},
        {"name": "Visio Lending", "min_loan": 75000, "max_ltv": 0.80, "rate_range": "7.75-10%", "notes": "No min DSCR option"},
        {"name": "Lima One Capital", "min_loan": 50000, "max_ltv": 0.75, "rate_range": "8-11%", "notes": "Rehab-to-rent program"},
        {"name": "CoreVest Finance", "min_loan": 75000, "max_ltv": 0.75, "rate_range": "7.25-9%", "notes": "Best rates strong DSCR"},
        {"name": "RCN Capital", "min_loan": 50000, "max_ltv": 0.75, "rate_range": "8.5-11%", "notes": "Bridge-to-DSCR nationwide"},
    ]

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    def create_financing_plan(self, deals: list) -> list:
        targets = [d for d in deals if d.recommendation in ("BUY", "INVESTIGATE")]
        print(f"\n[Financing] Creating {len(targets)} financing plans...")
        plans = []
        for deal in targets:
            try:
                plan = self._build(deal)
                plans.append(plan)
                print(f"  [+] {deal.raw.address}: {plan.acquisition_strategy} | net ${plan.net_cash_after_refi:,.0f}")
            except Exception as e:
                print(f"  [-] {deal.raw.address}: {e}")
        return plans

    def _build(self, deal: AnalyzedDeal) -> FinancingPlan:
        total = deal.all_in_cost
        if total <= 15000: strat, rate, term = "personal_loan", 0.15, 36
        elif total <= 30000: strat, rate, term = "personal_loan", 0.12, 60
        else: strat, rate, term = "hard_money", 0.12, 12
        dscr_ratio = deal.estimated_rent / deal.monthly_mortgage if deal.monthly_mortgage else 0
        eligible = [l for l in self.DSCR_LENDERS if l["min_loan"] <= deal.dscr_loan_amount]
        lender = self._pick_lender(deal, eligible, dscr_ratio)
        net = deal.cash_pulled_out - deal.dscr_loan_amount * 0.03
        summary, steps = self._action_plan(deal, strat, lender, net)
        return FinancingPlan(
            deal=deal, acquisition_strategy=strat, acquisition_amount=total,
            acquisition_rate=rate, acquisition_term_months=term,
            dscr_lender_options=eligible, recommended_lender=lender,
            refi_timeline_days=90, net_cash_after_refi=net,
            monthly_debt_service=deal.monthly_mortgage,
            financing_summary=summary, action_items=steps,
        )

    def _pick_lender(self, deal, lenders, dscr) -> str:
        if not lenders: return "CoreVest Finance"
        ltext = "\n".join(f"- {l['name']}: {l['rate_range']} | {l['notes']}" for l in lenders)
        msg = self.client.messages.create(model=config.CLAUDE_MODEL, max_tokens=80,
            messages=[{"role": "user", "content":
                f"Best DSCR lender for ${deal.dscr_loan_amount:,.0f} loan, DSCR={dscr:.2f}:\n{ltext}\nOne line: 'Name - reason'"}])
        return msg.content[0].text.strip()

    def _action_plan(self, deal, strat, lender, net) -> tuple:
        prompt = (
            f"Write a 5-step financing action plan.\n"
            f"Deal: {deal.raw.address} | Buy: ${deal.raw.asking_price:,.0f} | "
            f"Rehab: ${deal.rehab_cost_estimate:,.0f} | ARV: ${deal.estimated_arv:,.0f}\n"
            f"Strategy: {strat} for acquisition, then DSCR refi with {lender}. "
            f"Target cash out: ${net:,.0f}\n"
            f'Return JSON: {{"summary":"2 sentence overview","action_items":["Step 1:...","Step 2:..."]}}'
        )
        msg = self.client.messages.create(model=config.CLAUDE_MODEL, max_tokens=400,
            messages=[{"role": "user", "content": prompt}])
        try:
            t = msg.content[0].text
            d = json.loads(t[t.find("{"):t.rfind("}") + 1])
            return d.get("summary", ""), d.get("action_items", [])
        except Exception:
            return (f"Acquire with {strat}, then DSCR refi with {lender}.", [
                f"1. Secure {strat} for ${deal.all_in_cost:,.0f}",
                f"2. Purchase at ${deal.raw.asking_price:,.0f}",
                f"3. Complete rehab (ARV target: ${deal.estimated_arv:,.0f})",
                f"4. Apply for DSCR refi: {lender}",
                f"5. Pull out ${net:,.0f} and repeat",
            ])
