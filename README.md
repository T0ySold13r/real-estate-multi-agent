# Real Estate Multi-Agent Framework

> A multi-agent AI pipeline powered by **Claude** that automates the full real estate investment workflow — from finding distressed government auction properties to placing Section 8 tenants.
>
> [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
> [![Claude](https://img.shields.io/badge/AI-Claude%20Sonnet-orange.svg)](https://www.anthropic.com)
> [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
>
> ---
>
> ## What It Does
>
> This framework replicates the investment strategy popularized by tools like "Tranchi AI":
>
> ```
> Find $2K-$10K distressed property
>        ↓
>    Deep financial analysis (ARV, cash flow, ROI)
>        ↓
>    Build financing plan (personal loan → DSCR refi)
>        ↓
>    Prepare offer & bid strategy
>        ↓
>    Place Section 8 tenant → $500-$1,200/mo cash flow
>        ↓
>          Repeat
> ```
>
> ## Agent Architecture
>
> ```
> ┌─────────────────────────────────────────────────┐
> │  Agent 1: DealFinderAgent                       │
> │  Scans HUD, tax-deed, government auction sites  │
> │  Uses Claude to rank deals 1-10                 │
> └─────────────────────────────────────────────────┘
>                       ↓
> ┌─────────────────────────────────────────────────┐
> │  Agent 2: DealAnalyzerAgent                     │
> │  Estimates ARV, rehab cost, market rent         │
> │  Models DSCR refi + projects cash flow          │
> │  Outputs BUY / INVESTIGATE / PASS               │
> └─────────────────────────────────────────────────┘
>                       ↓
> ┌─────────────────────────────────────────────────┐
> │  Agent 3: FinancingAgent                        │
> │  Compares DSCR lenders (Kiavi, Visio, Lima One) │
> │  Builds step-by-step financing roadmap          │
> └─────────────────────────────────────────────────┘
>                       ↓
> ┌─────────────────────────────────────────────────┐
> │  Agent 4: OfferAgent                            │
> │  Calculates max bid to maintain target returns  │
> │  Drafts offer letters and bid strategy          │
> └─────────────────────────────────────────────────┘
>                       ↓
> ┌─────────────────────────────────────────────────┐
> │  Agent 5: TenantAgent                           │
> │  Finds local Housing Authority (PHA) contacts   │
> │  Calculates Section 8 FMR rents                 │
> │  Drafts rental listings, screening criteria     │
> └─────────────────────────────────────────────────┘
> ```
>
> ## Quick Start
>
> ### 1. Clone & Install
>
> ```bash
> git clone https://github.com/T0ySold13r/real-estate-multi-agent.git
> cd real-estate-multi-agent
>
> pip install -r requirements.txt
> playwright install chromium
> ```
>
> ### 2. Configure
>
> ```bash
> cp .env.example .env
> ```
>
> Edit `.env` and add your **Anthropic API key** (required):
>
> ```
> ANTHROPIC_API_KEY=sk-ant-...
> ```
>
> All other API keys are optional — the system uses Claude + demo data without them.
>
> ### 3. Run
>
> ```bash
> # Full pipeline (uses demo data if no live listings found)
> python main.py
>
> # Search specific states
> python main.py --states OH MI
>
> # Set max purchase price
> python main.py --max-price 5000
>
> # Analyze more deals
> python main.py --top-n 10
> ```
>
> ## Project Structure
>
> ```
> real-estate-multi-agent/
> ├── main.py                 # Orchestrator - runs the full pipeline
> ├── config.py               # All settings and financial assumptions
> ├── requirements.txt        # Python dependencies
> ├── .env.example            # Environment variable template
> │
> ├── agents/
> │   ├── __init__.py
> │   ├── deal_finder.py      # Agent 1: Scrapes auction sites
> │   ├── analyzer.py         # Agent 2: Financial analysis
> │   ├── financing.py        # Agent 3: Loan & lender matching
> │   ├── offer.py            # Agent 4: Offer letters & bid strategy
> │   └── tenant.py           # Agent 5: Section 8 tenant placement
> │
> └── reports/                # Auto-generated JSON deal reports
> ```
>
> ## Configuration
>
> Key settings in `.env`:
>
> | Variable | Default | Description |
> |---|---|---|
> | `ANTHROPIC_API_KEY` | required | Your Claude API key |
> | `TARGET_STATES` | `OH,MI,AL` | States to search |
> | `MAX_PURCHASE_PRICE` | `10000` | Max property price |
> | `MIN_MONTHLY_CASHFLOW` | `400` | Min cash flow target |
> | `MIN_CASH_ON_CASH` | `8` | Min CoC return % |
> | `SCAN_INTERVAL_HOURS` | `6` | Auto-scan frequency |
>
> ## Sample Output
>
> ```
> ╭──────────────────────────────────────────╮
> │    Real Estate Multi-Agent Framework     │
> │          Powered by Claude AI            │
> ╰──────────────────────────────────────────╯
>
> ──────── Agent 1: Deal Finder ────────
> [DealFinder] Searching 5 sources in ['OH', 'MI', 'AL']...
>   [+] HUD Homes: 0 listings found
>   [+] Bid4Assets: 0 listings found
>   [DealFinder] No live data - using demo deals.
>   [DealFinder] 4 ranked deals ready.
>
> ──────── Agent 2: Deal Analyzer ────────
>   [+] 2901 Lorain Ave:  BUY  (score=8.5, CF=$612/mo)
>   [+] 412 5th Ave S:    BUY  (score=7.9, CF=$543/mo)
>   [+] 1247 Elm Street:  INVESTIGATE (score=6.2, CF=$421/mo)
>
> ╭──────────────────── Best Deal Found ─────────────────────╮
> │ Top Deal:          2901 Lorain Ave, Cleveland, OH        │
> │ Asking Price:      $2,800                                │
> │ Estimated ARV:     $77,500                               │
> │ Monthly Cash Flow: $612                                  │
> │ Recommendation:    BUY                                   │
> │ Score:             8.5/10                                │
> ╰──────────────────────────────────────────────────────────╯
> ```
>
> ## Investment Strategy Explained
>
> This framework automates the **BRRRR + Section 8** strategy:
>
> 1. **Buy** a distressed government/tax-deed property for $2K-$10K
> 2. 2. **Rehab** using a personal loan (total all-in: ~$20K-$30K)
>    3. 3. **Refinance** with a DSCR loan (no income verification needed) at 75% LTV
>       4. 4. **Rent** to a Section 8 / HCV voucher holder (government pays rent)
>          5. 5. **Repeat** using the cash pulled out from the refinance
>            
>             6. > ⚠️ **Disclaimer**: Real estate investing involves significant risk. The financial projections in this tool are estimates only. Always verify ARV with a licensed appraiser, get professional title work, and consult a real estate attorney before purchasing. The claims made in social media posts about this strategy are often exaggerated.
>                >
>                > ## Extending the Framework
>                >
>                > ### Add a new data source
>                > Edit `config.py` → `AUCTION_SOURCES` list, then implement a scraper in `agents/deal_finder.py`.
>                >
>                > ### Add real property data APIs
>                > Add keys to `.env`:
>                > - **Zillow** (via RapidAPI) for ARV comps
>                > - - **RentCast** for rental market data
>                >   - - **ATTOM** for tax/ownership records
>                >    
>                >     - ### Add email/Slack alerts
>                >     - Set `SMTP_*` or `SLACK_WEBHOOK_URL` in `.env` — alerts fire automatically on new BUY recommendations.
>                >    
>                >     - ## License
>                >    
>                >     - MIT — see [LICENSE](LICENSE)
>
> ---
>
> *Built with [Claude](https://www.anthropic.com) by Anthropic*
