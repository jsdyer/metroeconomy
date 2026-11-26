"""Publish Statistics Canada labour market results for each census metropolitan area."""
from html import escape
import json
from urllib.parse import urlencode
from result_pages import link, publish, table


def figure(value, index):
    if not isinstance(value, (int, float)):
        return "Suppressed" if value == "x" else "Unavailable"
    return f"{value:.1f}%" if index < 3 else f"{value:,}"


def publish_profiles(stage, tool):
    data = stage / "data"
    edition = json.loads((data / "summary.json").read_text())
    records = []
    for metro in edition["metros"]:
        code, name = metro["id"], metro["name"]
        series = json.loads((data / (code + ".json")).read_text())
        months = sorted(series, reverse=True)
        if not months or not any(isinstance(x, (int, float)) for row in series.values() for x in row):
            continue
        month, measures = months[0], edition["measures"]
        year, part = month.split("-")
        past = f"{int(year) - 1}-{part}"
        latest = series[month]
        previous = series.get(past, [None] * len(measures))
        title = f"{name} unemployment rate and employment statistics"
        intro = (f"Labour Force Survey estimates for the {name} metropolitan area in {metro['province']}, "
                 f"for the three months ending {month}.")
        if isinstance(latest[0], (int, float)):
            intro += f" The unemployment rate was {figure(latest[0], 0)}."
        rows = [(label, figure(latest[i], i), figure(previous[i], i)) for i, label in enumerate(measures)]
        body = table("Seasonally adjusted three-month averages", ["Indicator", month, past], rows)
        rows = [(m, figure(series[m][0], 0), figure(series[m][3], 3)) for m in months[:12]]
        body += table("Recent labour market history", ["Period ending", "Unemployment rate", "Employed people"], rows)
        query = urlencode({"left": code, "right": "205" if code == "933" else "933", "month": month})
        body += '<p>' + link(tool["url"] + "?" + query, "Compare this metro area with another city") + '</p>'
        body += (f'<h2>Reading these estimates</h2><p>The geography covers the full census metropolitan area. '
                 f'Consecutive estimates share two months. Counts are people and the rate uses the labour force as its denominator. '
                 f'The source can revise earlier estimates. Snapshot retrieved {escape(edition["retrieved"])}.</p>')
        if metro.get("smallSample"):
            body += '<p>Statistics Canada flags greater sampling variability for this area before September 2025.</p>'
        body += '<p>' + link(edition["source"], "Statistics Canada table 14-10-0459-01") + ' · '
        body += link('https://www.statcan.gc.ca/en/reference/licence', 'Statistics Canada Open Licence') + '</p>'
        body += '<p>' + link('/wagewindow/', 'Compare a wage change with provincial inflation') + '</p>'
        records.append((code, name, title, intro, body))
    publish(stage, tool, "cities", "Canadian unemployment and employment statistics by metro area",
            "Choose a census metropolitan area for its employment estimates, unemployment rate and year-over-year comparison.", records)
