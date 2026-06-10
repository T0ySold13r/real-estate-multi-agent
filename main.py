"""
main.py - Orchestrator for the Real Estate Multi-Agent Framework

Runs the full pipeline:
    Agent 1: DealFinderAgent    -> Find distressed properties
        Agent 2: DealAnalyzerAgent  -> Deep financial analysis
            Agent 3: FinancingAgent     -> Build financing plans
                Agent 4: OfferAgent         -> Prepare offer packages
                    Agent 5: TenantAgent        -> Tenant placement plans

                    Usage:
                        python main.py                    # Run full pipeline
                            python main.py --states OH MI     # Filter by states
                                python main.py --max-price 8000   # Set max purchase price
                                    python main.py --demo             # Use demo data only
                                    """
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

import config
from agents.deal_finder import DealFinderAgent
from agents.analyzer import DealAnalyzerAgent
from agents.financing import FinancingAgent
from agents.offer import OfferAgent
from agents.tenant import TenantAgent

console = Console()


def print_header():
      console.print(Panel.fit(
                "[bold cyan]Real Estate Multi-Agent Framework[/bold cyan]\n"
                "[dim]Powered by Claude AI[/dim]\n"
                f"[dim]Run started: {datetime.now().strftime('%Y-%m-%d %H:%M')}[/dim]",
                border_style="cyan",
      ))


def print_deal_table(analyzed_deals):
      """Print a summary table of analyzed deals."""
      table = Table(title="Deal Analysis Results", box=box.ROUNDED, show_header=True)
      table.add_column("Address", style="cyan", no_wrap=True)
      table.add_column("State", justify="center")
      table.add_column("Price", justify="right")
      table.add_column("ARV", justify="right")
      table.add_column("Cash Flow/mo", justify="right")
      table.add_column("CoC %", justify="right")
      table.add_column("Score", justify="center")
      table.add_column("Action", justify="center")

    for deal in analyzed_deals:
              r = deal.raw
              rec_color = {"BUY": "green", "INVESTIGATE": "yellow", "PASS": "red"}.get(deal.recommendation, "white")
              table.add_row(
                  f"{r.address[:25]}...",
                  r.state,
                  f"${r.asking_price:,.0f}",
                  f"${deal.estimated_arv:,.0f}",
                  f"${deal.net_monthly_cashflow:,.0f}",
                  f"{deal.cash_on_cash_return:.1f}%",
                  f"{deal.roi_score:.1f}/10",
                  f"[{rec_color}]{deal.recommendation}[/{rec_color}]",
              )
          console.print(table)


def print_financing_summary(plans):
      """Print financing plan summaries."""
      console.print("\n[bold yellow]Financing Plans[/bold yellow]")
      for plan in plans:
                console.print(Panel(
                              f"[cyan]{plan.deal.raw.address}, {plan.deal.raw.city}, {plan.deal.raw.state}[/cyan]\n"
                              f"Strategy: [yellow]{plan.acquisition_strategy}[/yellow] -> DSCR Refi\n"
                              f"Lender: {plan.recommended_lender}\n"
                              f"Net Cash Out: [green]${plan.net_cash_after_refi:,.0f}[/green]\n"
                              f"\n[bold]Action Items:[/bold]\n" +
                              "\n".join(f"  {step}" for step in plan.action_items[:5]),
                              title=f"Financing: {plan.deal.recommendation}",
                              border_style="yellow",
                ))


def print_offer_summary(offers):
      """Print offer package summaries."""
      console.print("\n[bold green]Offer Packages[/bold green]")
      for offer in offers:
                console.print(Panel(
                              f"[cyan]{offer.plan.deal.raw.address}[/cyan]\n"
                              f"Offer Amount: [green]${offer.offer_amount:,.0f}[/green] "
                              f"| Max Bid: ${offer.max_bid:,.0f}\n"
                              f"Auction Date: {offer.auction_deadline}\n\n"
                              f"[bold]Bid Strategy:[/bold]\n{offer.bid_strategy}\n\n"
                              f"[bold]Next Steps:[/bold]\n" +
                              "\n".join(f"  {step}" for step in offer.next_steps),
                              title="Offer Package",
                              border_style="green",
                ))


def print_tenant_summary(tenant_plans):
      """Print tenant placement plan summaries."""
      console.print("\n[bold magenta]Tenant Placement Plans[/bold magenta]")
      for plan in tenant_plans:
                console.print(Panel(
                              f"[cyan]{plan.offer.plan.deal.raw.address}[/cyan]\n"
                              f"Program: [yellow]{plan.target_program}[/yellow]\n"
                              f"Est. Rent: [green]${plan.estimated_rent:,.0f}/mo[/green] "
                              f"(FMR: ${plan.section8_fmr:,.0f})\n"
                              f"PHA: {plan.housing_authority}\n\n"
                              f"[bold]Rental Listing Draft:[/bold]\n{plan.rental_listing[:200]}...\n\n"
                              f"[bold]Timeline:[/bold]\n{plan.placement_timeline}",
                              title="Tenant Plan",
                              border_style="magenta",
                ))


def save_results(analyzed_deals, financing_plans, offers, tenant_plans):
      """Save pipeline results to a JSON report."""
      reports_dir = Path("reports")
      reports_dir.mkdir(exist_ok=True)
      timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
      report_path = reports_dir / f"pipeline_run_{timestamp}.json"

    report = {
              "run_timestamp": timestamp,
              "summary": {
                            "deals_found": len(analyzed_deals),
                            "buy_recommendations": sum(1 for d in analyzed_deals if d.recommendation == "BUY"),
                            "financing_plans": len(financing_plans),
                            "offers_prepared": len(offers),
                            "tenant_plans": len(tenant_plans),
              },
              "deals": [
                            {
                                              "address": f"{d.raw.address}, {d.raw.city}, {d.raw.state}",
                                              "asking_price": d.raw.asking_price,
                                              "arv": d.estimated_arv,
                                              "monthly_cashflow": d.net_monthly_cashflow,
                                              "coc_return": d.cash_on_cash_return,
                                              "score": d.roi_score,
                                              "recommendation": d.recommendation,
                            }
                            for d in analyzed_deals
              ],
    }

    with open(report_path, "w") as f:
              json.dump(report, f, indent=2)

    console.print(f"\n[dim]Report saved to: {report_path}[/dim]")
    return report_path


def run_pipeline(states=None, max_price=None, demo=False):
      """Run the full multi-agent pipeline."""
      print_header()

    # Override config if args provided
      if states:
                config.TARGET_STATES = states
            if max_price:
                      config.MAX_PURCHASE_PRICE = max_price

    # ── Agent 1: Find Deals ────────────────────────────────────────────
    console.print("\n[bold cyan]Agent 1: Searching for distressed properties...[/bold cyan]")
    finder = DealFinderAgent()
    raw_deals = finder.find_deals(demo=demo)
    console.print(f"  [green]Found {len(raw_deals)} potential deals[/green]")

    if not raw_deals:
              console.print("[red]No deals found. Try adjusting search parameters.[/red]")
              return

    # ── Agent 2: Analyze Deals ────────────────────────────────────────
    console.print("\n[bold cyan]Agent 2: Analyzing deals with Claude AI...[/bold cyan]")
    analyzer = DealAnalyzerAgent()
    analyzed_deals = []
    for deal in raw_deals:
              console.print(f"  Analyzing: {deal.address[:40]}...", end="")
              result = analyzer.analyze(deal)
              analyzed_deals.append(result)
              color = {"BUY": "green", "INVESTIGATE": "yellow", "PASS": "red"}.get(result.recommendation, "white")
              console.print(f" [{color}]{result.recommendation}[/{color}]")

    print_deal_table(analyzed_deals)

    # Filter to BUY + INVESTIGATE for further processing
    actionable = [d for d in analyzed_deals if d.recommendation in ("BUY", "INVESTIGATE")]
    console.print(f"\n[yellow]{len(actionable)} deals proceeding to financing...[/yellow]")

    if not actionable:
              console.print("[red]No actionable deals. Exiting pipeline.[/red]")
              return

    # ── Agent 3: Build Financing Plans ───────────────────────────────
    console.print("\n[bold cyan]Agent 3: Building financing plans...[/bold cyan]")
    fin_agent = FinancingAgent()
    financing_plans = []
    for deal in actionable:
              console.print(f"  Planning financing for: {deal.raw.address[:40]}...")
              plan = fin_agent.build_plan(deal)
              financing_plans.append(plan)

    print_financing_summary(financing_plans)

    # ── Agent 4: Prepare Offers ───────────────────────────────────────
    console.print("\n[bold cyan]Agent 4: Preparing offer packages...[/bold cyan]")
    offer_agent = OfferAgent()
    offers = []
    for plan in financing_plans:
              console.print(f"  Preparing offer for: {plan.deal.raw.address[:40]}...")
              offer = offer_agent.prepare_offer(plan)
              offers.append(offer)

    print_offer_summary(offers)

    # ── Agent 5: Tenant Placement ─────────────────────────────────────
    console.print("\n[bold cyan]Agent 5: Building tenant placement plans...[/bold cyan]")
    tenant_agent = TenantAgent()
    tenant_plans = []
    for offer in offers:
              console.print(f"  Planning tenant placement for: {offer.plan.deal.raw.address[:40]}...")
              plan = tenant_agent.build_plan(offer)
              tenant_plans.append(plan)

    print_tenant_summary(tenant_plans)

    # ── Save Results ──────────────────────────────────────────────────
    save_results(analyzed_deals, financing_plans, offers, tenant_plans)

    # ── Final Summary ─────────────────────────────────────────────────
    console.print("\n" + "="*60)
    console.print(Panel.fit(
              f"[bold green]Pipeline Complete![/bold green]\n"
              f"Deals analyzed:     [cyan]{len(analyzed_deals)}[/cyan]\n"
              f"BUY recommendations:[green]{sum(1 for d in analyzed_deals if d.recommendation == 'BUY')}[/green]\n"
              f"Offers prepared:    [cyan]{len(offers)}[/cyan]\n"
              f"Tenant plans:       [cyan]{len(tenant_plans)}[/cyan]",
              border_style="green",
    ))


def main():
      parser = argparse.ArgumentParser(
                description="Real Estate Multi-Agent Framework",
                formatter_class=argparse.RawDescriptionHelpFormatter,
      )
      parser.add_argument(
          "--states",
          nargs="+",
          default=None,
          help="Target states (e.g. OH MI AL). Defaults to config.TARGET_STATES",
      )
      parser.add_argument(
          "--max-price",
          type=float,
          default=None,
          help="Maximum purchase price. Defaults to config.MAX_PURCHASE_PRICE",
      )
      parser.add_argument(
          "--demo",
          action="store_true",
          help="Use demo/mock data instead of live scraping",
      )
      args = parser.parse_args()

    try:
              run_pipeline(
                            states=args.states,
                            max_price=args.max_price,
                            demo=args.demo,
              )
except KeyboardInterrupt:
          console.print("\n[yellow]Pipeline interrupted by user.[/yellow]")
          sys.exit(0)
except Exception as e:
          console.print(f"\n[red]Pipeline error: {e}[/red]")
          raise


if __name__ == "__main__":
      main()
  
