"""Create the complete CSV and describe its public download on the landing page."""
import csv
import json
from pathlib import Path


def publish_dataset(stage: Path):
    data = stage / "data"
    index = json.loads((data / "summary.json").read_text())
    with (data / "metro-economy.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["end_month", "cma", "geography", "province", "indicator", "unit", "value", "source_status"])
        for metro in index["metros"]:
            records = json.loads((data / (metro["id"] + ".json")).read_text())
            for month, values in records.items():
                for i, (measure, value) in enumerate(zip(index["measures"], values, strict=True)):
                    numeric = isinstance(value, (int, float))
                    writer.writerow([month, metro["id"], metro["name"], metro["province"], measure,
                                     "percent" if i < 3 else "persons",
                                     value if numeric else "", "" if numeric else value or "unavailable"])
    url = "https://coolcode.ca/metroeconomy/"
    dataset = {
        "@context": "https://schema.org", "@type": "Dataset", "@id": url+"#dataset", "url": url,
        "name": "Metro Economy — monthly Canadian metropolitan labour market estimates",
        "description": f"Seven seasonally adjusted three-month moving average labour market indicators for {index['count']} Canadian census metropolitan areas, derived from Statistics Canada Labour Force Survey table 14-10-0459-01.",
        "creator": {"@type": "Organization", "name": "CoolCode", "url": "https://coolcode.ca/"},
        "isBasedOn": "https://doi.org/10.25318/1410045901-eng",
        "license": "https://www.statcan.gc.ca/en/reference/licence", "spatialCoverage": "Canada",
        "temporalCoverage": index['start'] + "/" + index['through'], "dateModified": index["retrieved"],
        "variableMeasured": index["measures"],
        "distribution": {"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": url+"data/metro-economy.csv"}
    }
    label = f"{index['count']} metro areas · {index['start']} to {index['through']} · Snapshot retrieved {index['retrieved']}"
    return label, json.dumps(dataset, ensure_ascii=False).replace("<", "\\u003c")
