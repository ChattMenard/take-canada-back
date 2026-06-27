#!/usr/bin/env python3
"""Batch-fetch World Bank indicators for Veritas evidence base."""
import json
import urllib.request
import urllib.error
from pathlib import Path
from time import sleep

BASE_URL = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"
OUTDIR = Path("/home/x99/Desktop/FUCK/EVIDENCE_COLLECTED/WORLD_BANK_DATA")
OUTDIR.mkdir(parents=True, exist_ok=True)

COUNTRIES = "CAN;USA;NOR;SWE;DNK;FRA;DEU;GBR;AUS;JPN;NLD;FIN"

INDICATORS = {
    "GC.TAX.TOTL.GD.ZS": "Tax_revenue_percent_GDP",
    "GC.TAX.YPKG.RV.ZS": "Income_profits_capital_gains_tax_percent_revenue",
    "GC.TAX.GSRV.RV.ZS": "Goods_services_tax_percent_revenue",
    "SI.POV.GINI": "Gini_index",
    "NE.TRD.GNFS.ZS": "Trade_percent_GDP",
    "GC.XPN.TOTL.GD.ZS": "Government_expense_percent_GDP",
    "SE.XPD.TOTL.GD.ZS": "Education_expenditure_percent_GDP",
    "EG.ELC.FOSL.ZS": "Electricity_fossil_fuels_percent",
    "EG.ELC.RNEW.ZS": "Electricity_renewables_percent",
    "NY.GDP.PCAP.CD": "GDP_per_capita_current_USD",
    "SP.POP.TOTL": "Total_population",
    "SL.UEM.TOTL.ZS": "Unemployment_total_percent",
    "FP.CPI.TOTL.ZG": "Inflation_consumer_prices_annual_percent",
    "NE.IMP.GNFS.ZS": "Imports_goods_services_percent_GDP",
    "NE.EXP.GNFS.ZS": "Exports_goods_services_percent_GDP",
}


def fetch(indicator: str, name: str) -> dict:
    url = f"{BASE_URL}?date=2000:2024&format=json&per_page=500"
    url = url.format(countries=COUNTRIES, indicator=indicator)
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        # data[0] is pagination metadata, data[1] is the records
        records = data[1] if len(data) > 1 else []
        # Sort by country then year ascending
        records.sort(key=lambda r: (r.get("country", {}).get("value", ""), r.get("date", "")))
        return {"indicator": indicator, "name": name, "count": len(records), "records": records}
    except urllib.error.HTTPError as e:
        return {"indicator": indicator, "name": name, "error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"indicator": indicator, "name": name, "error": str(e)}


def main():
    results = {}
    for indicator, name in INDICATORS.items():
        print(f"Fetching {indicator} ({name})...")
        results[name] = fetch(indicator, name)
        sleep(0.3)  # be polite to the API

    # Save raw JSON
    raw_path = OUTDIR / "world_bank_raw.json"
    with open(raw_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Raw data saved: {raw_path}")

    # Build a summary CSV (latest year per country per indicator)
    summary_rows = ["indicator,country,country_code,year,value"]
    for name, payload in results.items():
        if "error" in payload:
            print(f"  SKIP {name}: {payload['error']}")
            continue
        # Group by country, take latest non-null year
        by_country = {}
        for r in payload.get("records", []):
            cc = r.get("country", {}).get("id", "")
            cname = r.get("country", {}).get("value", "")
            year = r.get("date", "")
            val = r.get("value")
            if val is None:
                continue
            key = (cc, cname)
            if key not in by_country or year > by_country[key]["year"]:
                by_country[key] = {"year": year, "value": val}
        for (cc, cname), data in by_country.items():
            summary_rows.append(f"{name},{cname},{cc},{data['year']},{data['value']}")

    csv_path = OUTDIR / "world_bank_summary.csv"
    with open(csv_path, "w") as f:
        f.write("\n".join(summary_rows) + "\n")
    print(f"Summary CSV saved: {csv_path}")

    # Print a quick preview
    print("\n--- Latest values per indicator for CAN ---")
    for name, payload in results.items():
        if "error" in payload:
            continue
        can_records = [r for r in payload.get("records", []) if r.get("country", {}).get("id") == "CAN" and r.get("value") is not None]
        if can_records:
            latest = max(can_records, key=lambda r: r.get("date", ""))
            print(f"  {name}: {latest['value']} ({latest['date']})")
        else:
            print(f"  {name}: no data")


if __name__ == "__main__":
    main()
