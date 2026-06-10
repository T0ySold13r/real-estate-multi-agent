"""
agents/analyzer.py - Agent 2: Deal Analyzer
Deep financial analysis: ARV estimation, DSCR modeling, cash flow projection.
"""
import json, math
from dataclasses import dataclass
from typing import Optional
import anthropic, config
from .deal_finder import RawDeal


@dataclass
class AnalyzedDeal:
      raw: RawDeal
      estimated_arv: float
      rehab_cost_estimate: float
      all_in_cost: float
      dscr_loan_amount: float
      cash_pulled_out: float
      monthly_mortgage: float
      estimated_rent: float
      vacancy_loss: float
      monthly_expenses: float
      net_monthly_cashflow: float
      cash_on_cash_return: float
      annual_cashflow: float
      roi_score: float
      recommendation: str   # BUY / INVESTIGATE / PASS
    analysis_summary: str
    risks: str


class DealAnalyzerAgent:
      """
          Agent 2 - Deal Analyzer
              Produces detailed AnalyzedDeal reports with financial projections
                  and BUY/PASS/INVESTIGATE recommendations.
                      """

    def __init__(self):
              self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    def analyze_deals(self, deals: list, top_n: int = 5) -> list:
              print(f"\n[Analyzer] Analyzing top {min(top_n, len(deals))} deals...")
              analyzed = []
              for deal in deals[:top_n]:
                            try:
                                              result = self._analyze_single(deal)
                                              analyzed.append(result)
                                              print(f"  [+] {deal.address}: {result.recommendation} "
                                                    f"(score={result.roi_score:.1f}, CF=${result.net_monthly_cashflow:,.0f}/mo)")
except Exception as e:
                print(f"  [-] {deal.address}: {e}")
        analyzed.sort(key=lambda x: x.roi_score, reverse=True)
        buys = len([a for a in analyzed if a.recommendation == "BUY"])
        print(f"[Analyzer] Done. {buys} BUY recommendations.")
        return analyzed

    def _analyze_single(self, deal: RawDeal) -> AnalyzedDeal:
              arv, rehab, rent = self._estimate_with_claude(deal)
              all_in = deal.asking_price + rehab
              loan_amount = arv * config.DSCR_LTV
              cash_pulled = loan_amount - all_in
              r = config.DSCR_INTEREST_RATE / 12
              n = config.DSCR_LOAN_TERM_YEARS * 12
              monthly_mortgage = loan_amount * (r * (1 + r)**n) / ((1 + r)**n - 1) if r > 0 else loan_amount / n
              vacancy_loss = rent * config.VACANCY_RATE
              expenses = (monthly_mortgage + vacancy_loss + rent * config.PROPERTY_MGMT_RATE
                          + rent * config.MAINTENANCE_RATE + config.INSURANCE_ANNUAL / 12
                          + arv * config.PROPERTY_TAX_RATE / 12)
              cashflow = rent - expenses
              coc = (cashflow * 12 / max(all_in - loan_amount, 1)) * 100
              score = self._score(cashflow, coc, cash_pulled, deal)
              rec = self._recommend(cashflow, coc, score)
              summary, risks = self._summarize(deal, arv, rehab, cashflow, cash_pulled, rec)
              return AnalyzedDeal(
                  raw=deal, estimated_arv=arv, rehab_cost_estimate=rehab,
                  all_in_cost=all_in, dscr_loan_amount=loan_amount,
                  cash_pulled_out=cash_pulled, monthly_mortgage=monthly_mortgage,
                  estimated_rent=rent, vacancy_loss=vacancy_loss,
                  monthly_expenses=expenses, net_monthly_cashflow=cashflow,
                  cash_on_cash_return=coc, annual_cashflow=cashflow * 12,
                  roi_score=score, recommendation=rec,
                  analysis_summary=summary, risks=risks,
              )

    def _estimate_with_claude(self, deal: RawDeal) -> tuple:
              market = config.TARGET_MARKETS.get(deal.state, {})
              prompt = (
                  f"Estimate conservative values for this distressed property.\n"
                  f"Property: {deal.address}, {deal.city}, {deal.state}\n"
                  f"Type: {deal.bedrooms}BD/{deal.bathrooms}BA, {deal.sqft}sqft\n"
                  f"Price: ${deal.asking_price:,.0f} | Notes: {deal.description[:300]}\n"
                  f"Market: {market.get('notes', '')}\n\n"
                  f'Return JSON: {{"arv": 0, "rehab_cost": 0, "section8_rent": 0}}'
              )
              msg = self.client.messages.create(
                  model=config.CLAUDE_MODEL, max_tokens=256,
                  messages=[{"role": "user", "content": prompt}]
              )
              try:
                            text = msg.content[0].text
                            d = json.loads(text[text.find("{"):text.rfind("}") + 1])
                            return float(d["arv"]), float(d["rehab_cost"]), float(d["section8_rent"])
except Exception:
            return deal.sqft * 50, deal.sqft * config.REHAB_COST_PER_SQFT, 850.0

    def _score(self, cashflow, coc, cash_pulled, deal) -> float:
              s = 5.0
              if cashflow >= 800: s += 2.0
elif cashflow >= 600: s += 1.5
elif cashflow >= 400: s += 1.0
elif cashflow >= 200: s += 0.5
elif cashflow < 0: s -= 2.0
        if coc >= 20: s += 1.5
elif coc >= 15: s += 1.0
elif coc >= 10: s += 0.5
elif coc < 5: s -= 1.0
          if cash_pulled > 5000: s += 1.0
elif cash_pulled > 0: s += 0.5
          if deal.asking_price <= 3000: s += 0.5
                    return max(1.0, min(10.0, s))

    def _recommend(self, cashflow, coc, score) -> str:
              if cashflow >= config.MIN_MONTHLY_CASHFLOW and coc >= config.MIN_CASH_ON_CASH and score >= 6.5:
                            return "BUY"
elif cashflow >= config.MIN_MONTHLY_CASHFLOW * 0.7 and score >= 5.0:
            return "INVESTIGATE"
        return "PASS"

    def _summarize(self, deal, arv, rehab, cashflow, cash_pulled, rec) -> tuple:
              prompt = (
                            f"Summarize this RE deal in 2 sentences, then list 2-3 risks.\n"
                            f"{deal.address} | Buy: ${deal.asking_price:,.0f} | ARV: ${arv:,.0f} | "
                            f"Rehab: ${rehab:,.0f} | CF: ${cashflow:,.0f}/mo | Cash out: ${cash_pulled:,.0f} | {rec}\n"
                            f'Return JSON: {{"summary": "...", "risks": "..."}}'
              )
              msg = self.client.messages.create(
                  model=config.CLAUDE_MODEL, max_tokens=256,
                  messages=[{"role": "user", "content": prompt}]
              )
              try:
                            text = msg.content[0].text
                            d = json.loads(text[text.find("{"):text.rfind("}") + 1])
                            return d.get("summary", ""), d.get("risks", "")
except Exception:
            return f"{rec}: ${cashflow:,.0f}/mo cash flow.", "Verify ARV with local agent."
