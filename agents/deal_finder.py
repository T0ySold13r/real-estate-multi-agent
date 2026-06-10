"""
agents/deal_finder.py - Agent 1: Deal Finder
Scans government auction and tax-deed listings for distressed properties.
"""
import time, json, requests
from dataclasses import dataclass
from typing import Optional
import anthropic, config


@dataclass
class RawDeal:
      source: str
      address: str
      city: str
      state: str
      zip_code: str
      asking_price: float
      bedrooms: int
      bathrooms: float
      sqft: int
      property_type: str
      listing_url: str
      description: str
      auction_date: Optional[str] = None
      parcel_id: Optional[str] = None


class DealFinderAgent:
      """
          Agent 1 - Deal Finder
              Searches configured auction sources, filters by criteria,
                  and uses Claude to score and rank deals by investment potential.
                      """

    def __init__(self):
              self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
              self.session = requests.Session()
              self.session.headers.update({"User-Agent": config.USER_AGENT})

    def find_deals(self, states=None, max_price=None) -> list:
              """Search all sources and return ranked list of RawDeal objects."""
              states = states or config.TARGET_STATES
              max_price = max_price or config.MAX_PURCHASE_PRICE
              print(f"\n[DealFinder] Searching {len(config.AUCTION_SOURCES)} sources...")

        raw = []
        for source in config.AUCTION_SOURCES:
                      try:
                                        found = self._scrape_source(source, states, max_price)
                                        raw.extend(found)
                                        print(f"  [+] {source['name']}: {len(found)} listings")
                                        time.sleep(config.REQUEST_DELAY_SECONDS)
except Exception as e:
                print(f"  [-] {source['name']}: {e}")

        if not raw:
                      print("[DealFinder] No live data - using demo deals.")
                      raw = self._demo_deals(states, max_price)

        ranked = self._rank_with_claude(raw)
        print(f"[DealFinder] {len(ranked)} ranked deals ready.")
        return ranked

    # ── Scrapers ─────────────────────────────────────────────────────────────

    def _scrape_source(self, source, states, max_price):
              return {
                            "hud": self._scrape_hud,
                            "tax_deed": self._scrape_tax_deed,
                            "government": self._scrape_govsales,
              }.get(source["type"], lambda *a: [])(source, states, max_price)

    def _scrape_hud(self, source, states, max_price):
              deals = []
              for state in states:
                            try:
                                              r = self.session.get(
                                                                    "https://www.hudhomestore.gov/Listing/PropertySearchResult.aspx",
                                                                    params={"sState": state, "nMaxPrice": int(max_price)},
                                                                    timeout=config.REQUEST_TIMEOUT,
                                              )
                                              if r.status_code == 200:
                                                                    deals.extend(self._parse_hud(r.text, state, source["name"]))
                            except Exception as e:
                                              print(f"    HUD {state}: {e}")
                                      return deals

    def _scrape_tax_deed(self, source, states, max_price):
              try:
                            r = self.session.get(
                                              f"{source['url']}auctions/type/tax-deed",
                                              timeout=config.REQUEST_TIMEOUT,
                            )
                            if r.status_code == 200:
                                              return self._parse_generic(r.text, states, max_price, source["name"])
              except Exception as e:
                            print(f"    TaxDeed: {e}")
                        return []

    def _scrape_govsales(self, source, states, max_price):
              try:
                            r = self.session.get(
                                              f"{source['url']}search?category=real-estate",
                                              timeout=config.REQUEST_TIMEOUT,
                            )
                            if r.status_code == 200:
                                              return self._parse_generic(r.text, states, max_price, source["name"])
    except Exception as e:
            print(f"    GovSales: {e}")
        return []

    def _parse_hud(self, html, state, name): return []   # TODO: BeautifulSoup impl
    def _parse_generic(self, html, states, max_price, name): return []  # TODO

    # ── Demo data ─────────────────────────────────────────────────────────────

    def _demo_deals(self, states, max_price):
              deals = [
                  RawDeal("HUD (Demo)", "1247 Elm St", "Cleveland", "OH", "44105",
                                              4500, 3, 1.0, 1200, "SFR", "https://hudhomestore.gov/demo/1",
                                              "Tax-foreclosed SFR. ARV $65-75K. Section 8 $950-1100/mo.",
                                              "2026-07-15", "OH-CUY-001"),
                  RawDeal("Bid4Assets (Demo)", "834 Michigan Ave", "Detroit", "MI", "48210",
                                              3200, 2, 1.0, 980, "SFR", "https://bid4assets.com/demo/2",
                                              "Tax-deed. ARV ~$55K. Section 8 FMR $875/mo.",
                                              "2026-07-20", "MI-WAY-002"),
                  RawDeal("GovSales (Demo)", "412 5th Ave S", "Birmingham", "AL", "35205",
                                              5000, 3, 2.0, 1450, "SFR", "https://govsales.gov/demo/3",
                                              "Seized property. Good bones. ARV ~$80K. Sec 8 $1050-1200/mo.",
                                              "2026-07-25", "AL-JEF-003"),
                  RawDeal("RealtyTrac (Demo)", "2901 Lorain Ave", "Cleveland", "OH", "44113",
                                              2800, 4, 1.5, 1600, "SFR", "https://realtytrac.com/demo/4",
                                              "Pre-foreclosure. ARV $70-85K. High-demand rental corridor.",
                                              "2026-08-01", "OH-CUY-004"),
    ]
        return [d for d in deals if d.state in states and d.asking_price <= max_price]

    # ── Claude ranking ────────────────────────────────────────────────────────

    def _rank_with_claude(self, deals):
              if not deals:
                            return []
                        listing_text = "\n\n".join(
                                      f"#{i+1}: {d.address}, {d.city} {d.state} | ${d.asking_price:,.0f} | "
                                      f"{d.bedrooms}BD/{d.sqft}sqft\n{d.description}"
                                      for i, d in enumerate(deals)
                        )
        prompt = (
                      f"Rank these {len(deals)} distressed properties for the BRRRR + Section 8 strategy.\n"
                      f"Buy under ${config.MAX_PURCHASE_PRICE:,.0f}, rehab, DSCR refi, place Section 8 tenant.\n"
                      f"Target cash flow: ${config.MIN_MONTHLY_CASHFLOW:,.0f}+/mo.\n\n{listing_text}\n\n"
                      "Return JSON array sorted by score desc:\n"
                      '[{"deal_index":1,"score":8,"reasoning":"...","red_flags":"...","estimated_arv":70000}]'
        )
        msg = self.client.messages.create(
                      model=config.CLAUDE_MODEL,
                      max_tokens=config.MAX_TOKENS,
                      messages=[{"role": "user", "content": prompt}],
        )
        try:
                      text = msg.content[0].text
                      data = json.loads(text[text.find("["):text.rfind("]") + 1])
                      ranked = []
                      for r in data:
                                        idx = r["deal_index"] - 1
                                        if 0 <= idx < len(deals):
                                                              deals[idx].description += f"\n[Score:{r['score']}/10] {r['reasoning']}"
                                                              ranked.append(deals[idx])
                                                      return ranked
except Exception:
            return deals
