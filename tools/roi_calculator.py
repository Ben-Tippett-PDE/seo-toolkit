#!/usr/bin/env python3
"""
Marketing ROI Calculator
Built by Perth Digital Edge (https://perthdigitaledge.com.au)

Calculate return on investment for marketing campaigns with
detailed breakdowns including ROAS, profit margins, and break-even analysis.
"""

import argparse
import json
import sys

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False


def calculate_roi(investment, revenue, additional_costs=0):
    """Calculate marketing ROI metrics."""
    total_cost = investment + additional_costs
    profit = revenue - total_cost
    roi_percentage = ((revenue - total_cost) / total_cost) * 100 if total_cost > 0 else 0
    roas = revenue / investment if investment > 0 else 0
    profit_margin = (profit / revenue) * 100 if revenue > 0 else 0
    break_even = total_cost

    return {
        "investment": investment,
        "additional_costs": additional_costs,
        "total_cost": total_cost,
        "revenue": revenue,
        "profit": profit,
        "roi_percentage": round(roi_percentage, 2),
        "roas": round(roas, 2),
        "profit_margin": round(profit_margin, 2),
        "break_even": break_even,
        "is_profitable": profit > 0,
    }


def calculate_cpc_metrics(budget, cpc, conversion_rate, avg_order_value):
    """Calculate CPC and ad spend metrics."""
    clicks = budget / cpc if cpc > 0 else 0
    conversions = clicks * (conversion_rate / 100)
    revenue = conversions * avg_order_value
    cost_per_conversion = budget / conversions if conversions > 0 else 0
    roas = revenue / budget if budget > 0 else 0

    return {
        "daily_budget": budget,
        "cpc": cpc,
        "estimated_clicks": round(clicks),
        "conversion_rate": conversion_rate,
        "estimated_conversions": round(conversions, 1),
        "avg_order_value": avg_order_value,
        "estimated_revenue": round(revenue, 2),
        "cost_per_conversion": round(cost_per_conversion, 2),
        "roas": round(roas, 2),
        "monthly_budget": round(budget * 30, 2),
        "monthly_revenue": round(revenue * 30, 2),
        "monthly_profit": round((revenue - budget) * 30, 2),
    }


def print_roi_report(results):
    """Print ROI calculation results."""
    green = Fore.GREEN if HAS_COLOR else ""
    red = Fore.RED if HAS_COLOR else ""
    yellow = Fore.YELLOW if HAS_COLOR else ""
    reset = Style.RESET_ALL if HAS_COLOR else ""

    print(f"\n{'='*60}")
    print(f"  Marketing ROI Report â Perth Digital Edge")
    print(f"{'='*60}\n")

    print(f"  Investment:        ${results['investment']:,.2f}")
    if results['additional_costs'] > 0:
        print(f"  Additional Costs:  ${results['additional_costs']:,.2f}")
    print(f"  Total Cost:        ${results['total_cost']:,.2f}")
    print(f"  Revenue:           ${results['revenue']:,.2f}")
    print()

    colour = green if results['is_profitable'] else red
    print(f"  {colour}Profit/Loss:       ${results['profit']:,.2f}{reset}")
    print(f"  {colour}ROI:               {results['roi_percentage']}%{reset}")
    print(f"  ROAS:              {results['roas']}x")
    print(f"  Profit Margin:     {results['profit_margin']}%")
    print(f"  Break-even Point:  ${results['break_even']:,.2f}")
    print()

    if results['is_profitable']:
        print(f"  {green}â Campaign is profitable{reset}")
    else:
        print(f"  {red}â Campaign is not yet profitable{reset}")

    print(f"\n  Powered by Perth Digital Edge")
    print(f"  https://perthdigitaledge.com.au")
    print(f"{'='*60}\n")


def print_cpc_report(results):
    """Print CPC calculation results."""
    green = Fore.GREEN if HAS_COLOR else ""
    yellow = Fore.YELLOW if HAS_COLOR else ""
    reset = Style.RESET_ALL if HAS_COLOR else ""

    print(f"\n{'='*60}")
    print(f"  Ad Spend Planner â Perth Digital Edge")
    print(f"{'='*60}\n")

    print(f"  DAILY PROJECTIONS")
    print(f"  Budget:            ${results['daily_budget']:,.2f}")
    print(f"  Cost per Click:    ${results['cpc']:,.2f}")
    print(f"  Est. Clicks:       {results['estimated_clicks']:,}")
    print(f"  Conversion Rate:   {results['conversion_rate']}%")
    print(f"  Est. Conversions:  {results['estimated_conversions']}")
    print(f"  Avg Order Value:   ${results['avg_order_value']:,.2f}")
    print(f"  Est. Revenue:      ${results['estimated_revenue']:,.2f}")
    print(f"  Cost/Conversion:   ${results['cost_per_conversion']:,.2f}")
    print(f"  ROAS:              {results['roas']}x")
    print()
    print(f"  MONTHLY PROJECTIONS")
    print(f"  Monthly Budget:    ${results['monthly_budget']:,.2f}")
    print(f"  Monthly Revenue:   ${results['monthly_revenue']:,.2f}")

    colour = green if results['monthly_profit'] > 0 else yellow
    print(f"  {colour}Monthly Profit:    ${results['monthly_profit']:,.2f}{reset}")

    print(f"\n  Powered by Perth Digital Edge")
    print(f"  https://perthdigitaledge.com.au")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Marketing ROI Calculator by Perth Digital Edge (https://perthdigitaledge.com.au)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Calculator type")

    # ROI calculator
    roi_parser = subparsers.add_parser("roi", help="Calculate campaign ROI")
    roi_parser.add_argument("--investment", type=float, required=True, help="Total marketing investment ($)")
    roi_parser.add_argument("--revenue", type=float, required=True, help="Total revenue generated ($)")
    roi_parser.add_argument("--costs", type=float, default=0, help="Additional costs ($)")
    roi_parser.add_argument("--json", dest="json_file", help="Export to JSON")

    # CPC calculator
    cpc_parser = subparsers.add_parser("cpc", help="Calculate CPC & ad spend projections")
    cpc_parser.add_argument("--budget", type=float, required=True, help="Daily ad budget ($)")
    cpc_parser.add_argument("--cpc", type=float, required=True, help="Average cost per click ($)")
    cpc_parser.add_argument("--conversion-rate", type=float, default=2.5, help="Conversion rate %% (default: 2.5)")
    cpc_parser.add_argument("--aov", type=float, default=100, help="Average order value ($, default: 100)")
    cpc_parser.add_argument("--json", dest="json_file", help="Export to JSON")

    args = parser.parse_args()

    if not args.command:
        # Default to simple ROI mode for backward compatibility
        parser.add_argument("--investment", type=float, required=True)
        parser.add_argument("--revenue", type=float, required=True)
        args = parser.parse_args()
        results = calculate_roi(args.investment, args.revenue)
        print_roi_report(results)
        return

    if args.command == "roi":
        results = calculate_roi(args.investment, args.revenue, args.costs)
        print_roi_report(results)
    elif args.command == "cpc":
        results = calculate_cpc_metrics(args.budget, args.cpc, args.conversion_rate, args.aov)
        print_cpc_report(results)

    if hasattr(args, "json_file") and args.json_file:
        with open(args.json_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.json_file}")


if __name__ == "__main__":
    main()
