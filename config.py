"""
config.py - Centralized configuration for the Real Estate Multi-Agent Framework
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Anthropic ────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
MAX_TOKENS = 4096

# ── Property Data APIs ───────────────────────────────────────────────────────
ZILLOW_API_KEY = os.getenv("ZILLOW_API_KEY", "")
ATTOM_API_KEY = os.getenv("ATTOM_API_KEY", "")
RENTCAST_API_KEY = os.getenv("RENTCAST_API_KEY", "")
WALKSCORE_API_KEY = os.getenv("WALKSCORE_API_KEY", "")

# ── Database ─────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./deals.db")

# ── Notifications ────────────────────────────────────────────────────────────
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# ── Deal Search Criteria ─────────────────────────────────────────────────────
TARGET_STATES = os.getenv("TARGET_STATES", "OH,MI,AL").split(",")
MAX_PURCHASE_PRICE = float(os.getenv("MAX_PURCHASE_PRICE", "10000"))
MIN_CASH_ON_CASH = float(os.getenv("MIN_CASH_ON_CASH", "8"))
MIN_MONTHLY_CASHFLOW = float(os.getenv("MIN_MONTHLY_CASHFLOW", "400"))
SCAN_INTERVAL_HOURS = int(os.getenv("SCAN_INTERVAL_HOURS", "6"))

# ── Financial Assumptions ────────────────────────────────────────────────────
REHAB_COST_PER_SQFT = 15          # Light rehab cost estimate
ARV_MULTIPLIER = 0.75             # Conservative ARV % to use
DSCR_LTV = 0.75                   # DSCR loan LTV (75%)
DSCR_INTEREST_RATE = 0.08         # Estimated DSCR rate
DSCR_LOAN_TERM_YEARS = 30
VACANCY_RATE = 0.08               # 8% vacancy assumption
PROPERTY_MGMT_RATE = 0.10         # 10% management fee
MAINTENANCE_RATE = 0.05           # 5% of rent for maintenance
INSURANCE_ANNUAL = 1200           # Annual insurance estimate
PROPERTY_TAX_RATE = 0.012         # 1.2% annual property tax

# ── Scraping ─────────────────────────────────────────────────────────────────
REQUEST_TIMEOUT = 30
REQUEST_DELAY_SECONDS = 2         # Polite delay between requests
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
            )

            # ── Auction / Data Sources ───────────────────────────────────────────────────
            AUCTION_SOURCES = [
                {
                        "name": "GovSales",
                                "url": "https://www.govsales.gov/",
                                        "type": "government",
                                            },
                                                {
                                                        "name": "HUD Homes",
                                                                "url": "https://www.hudhomestore.gov/",
                                                                        "type": "hud",
                                                                            },
                                                                                {
                                                                                        "name": "Auction.com",
                                                                                                "url": "https://www.auction.com/",
                                                                                                        "type": "auction",
                                                                                                            },
                                                                                                                {
                                                                                                                        "name": "RealtyTrac",
                                                                                                                                "url": "https://www.realtytrac.com/",
                                                                                                                                        "type": "foreclosure",
                                                                                                                                            },
                                                                                                                                                {
                                                                                                                                                        "name": "Bid4Assets",
                                                                                                                                                                "url": "https://www.bid4assets.com/",
                                                                                                                                                                        "type": "tax_deed",
                                                                                                                                                                            },
                                                                                                                                                                            ]
                                                                                                                                                                            
                                                                                                                                                                            # ── Target Markets ───────────────────────────────────────────────────────────
                                                                                                                                                                            TARGET_MARKETS = {
                                                                                                                                                                                "OH": {
                                                                                                                                                                                        "cities": ["Cleveland", "Akron", "Toledo", "Dayton"],
                                                                                                                                                                                                "notes": "Low price-to-rent ratio, landlord-friendly laws",
                                                                                                                                                                                                        "avg_section8_premium": 1.1,
                                                                                                                                                                                                            },
                                                                                                                                                                                                                "MI": {
                                                                                                                                                                                                                        "cities": ["Detroit", "Flint", "Pontiac", "Saginaw"],
                                                                                                                                                                                                                                "notes": "Tax-deeded inventory, Section 8 above market",
                                                                                                                                                                                                                                        "avg_section8_premium": 1.15,
                                                                                                                                                                                                                                            },
                                                                                                                                                                                                                                                "AL": {
                                                                                                                                                                                                                                                        "cities": ["Birmingham", "Huntsville", "Mobile", "Montgomery"],
                                                                                                                                                                                                                                                                "notes": "Low property tax, Section 8 above market",
                                                                                                                                                                                                                                                                        "avg_section8_premium": 1.2,
                                                                                                                                                                                                                                                                            },
                                                                                                                                                                                                                                                                            }
