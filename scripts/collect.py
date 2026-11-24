"""Extract the seven seasonally adjusted CMA series from Statistics Canada 14-10-0459."""
import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal
import io
import json
from pathlib import Path
import re
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DOWNLOAD = "https://www150.statcan.gc.ca/n1/tbl/csv/14100459-eng.zip"
SOURCE = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410045901"
MEASURES = ["Unemployment rate", "Employment rate", "Participation rate",
            "Employment", "Unemployment", "Labour force", "Population"]


def extract(z):
    meta = csv.reader(io.TextIOWrapper(z.open("14100459_MetaData.csv"), encoding="utf-8-sig"))
    small = {r[1] for r in meta if len(r) >= 7 and r[0] == "1" and "16" in r[6].split(";")}
    cities, series = {}, {}
    reader = csv.DictReader(io.TextIOWrapper(z.open("14100459.csv"), encoding="utf-8-sig"))
    for row in reader:
        if row["Statistics"] != "Estimate" or row["Data type"] != "Seasonally adjusted":
            continue
        match = re.fullmatch(r"2021S0503(\d{1,3})", row["DGUID"])
        if not match or row["Labour force characteristics"] not in MEASURES:
            continue
        code = match[1].zfill(3)
        geo, period = row["GEO"], row["REF_DATE"]
        if not re.fullmatch(r"\d{4}-(?:0[1-9]|1[0-2])", period):
            raise ValueError(f"Unexpected reference month {period}")
        name, province = geo.rsplit(", ", 1)
        cities[code] = {"id": code, "name": name, "province": province, "smallSample": geo in small}
        cell = series.setdefault(code, {}).setdefault(period, {})
        index = MEASURES.index(row["Labour force characteristics"])
        if index in cell:
            raise ValueError(f"Duplicate {code} {period} {index}")
        expected = "Percent" if index < 3 else "Persons in thousands"
        if row["UOM"] != expected:
            raise ValueError(f"Unexpected unit {row['UOM']}")
        value = row["VALUE"]
        if not value:
            cell[index] = row["STATUS"] or None
        else:
            number = Decimal(value)
            if number < 0 or (index < 3 and number > 100):
                raise ValueError(f"Invalid value {number}")
            if row["STATUS"]:
                raise ValueError(f"Review newly flagged numeric estimate: {row['STATUS']}")
            cell[index] = float(number) if index < 3 else int(number * 1000)

    if not {"001", "205", "932", "933"}.issubset(cities):
        raise ValueError("Expected metropolitan areas missing")
    dates = sorted({month for values in series.values() for month in values})
    records = {}
    for code, periods in series.items():
        records[code] = {}
        for month, cell in sorted(periods.items()):
            if len(cell) != len(MEASURES):
                raise ValueError(f"Incomplete set of indicators in {code}, {month}")
            records[code][month] = [cell[i] for i in range(len(MEASURES))]
    index = {"source": SOURCE, "start": dates[0], "through": dates[-1], "count": len(cities),
             "months": dates, "measures": MEASURES, "metros": sorted(cities.values(), key=lambda c: c["name"])}
    return index, records


def save(index, records, destination, checked_at=None):
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / "summary.json"
    old = json.loads(path.read_text()) if path.exists() else {}
    if old and (old["through"] > index["through"] or {m["id"] for m in old["metros"]} - set(records)):
        raise ValueError("Earlier release or missing geography; keeping the existing snapshot")
    modified = False
    for code, data in records.items():
        target = destination / f"{code}.json"
        body = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
        if not target.exists() or target.read_text() != body:
            target.write_text(body, encoding="utf-8")
            modified = True
    if modified or {k: v for k, v in old.items() if k not in ("retrieved", "checked_at")} != index:
        index["retrieved"] = datetime.now(timezone.utc).date().isoformat()
    else:
        index["retrieved"] = old["retrieved"]
    if checked_at:
        index["checked_at"] = checked_at
    elif not modified and old.get("checked_at"):
        index["checked_at"] = old["checked_at"]
    path.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"{index['count']} metropolitan areas, {index['start']} to {index['through']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", type=Path, help="Read a previously downloaded official ZIP")
    args = parser.parse_args()
    if args.zip:
        archive = args.zip
    else:
        with urlopen(DOWNLOAD, timeout=90) as response:
            archive = io.BytesIO(response.read())
    with zipfile.ZipFile(archive) as z:
        summary, series = extract(z)
    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds") if not args.zip else None
    save(summary, series, ROOT / "web/data", checked_at=checked_at)
