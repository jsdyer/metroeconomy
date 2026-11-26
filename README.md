# Metro Economy

Compare the labour markets of two Canadian census metropolitan areas using seven indicators from Statistics Canada’s monthly Labour Force Survey. [Open Metro Economy](https://coolcode.ca/metroeconomy/).

<!-- coolcode:guide -->
Compare Halifax with Vancouver or Abbotsford–Mission. Pick a month to see how many people were working or looking for work and how their share of the labour force changed. Share the selected comparison or download the underlying monthly estimates.
<!-- /coolcode:guide -->

[Browse employment statistics by metro area](https://coolcode.ca/metroeconomy/cities/). The offline Pages build writes a dated HTML result for each qualifying record and lists it in the project sitemap. New records are published with the next successful data build.

## Reading the figures

Statistics Canada publishes seasonally adjusted three-month moving averages. The October estimate summarizes August through October. Consecutive estimates share two months. Year-over-year changes compare the selected period with the same ending month a year earlier.

Employment, unemployment, labour force and population are estimated numbers of people. The population base is people 15 and older in the survey population. Employment and participation rates use that population as their denominator. The unemployment rate uses the labour force. A change from 6% to 7% is one percentage point. Smaller changes can reflect sampling variability. The app reports descriptive differences, without a test of statistical significance. The geography is the full metropolitan area on 2021 boundaries, which can include neighbouring municipalities. The app flags areas for which Statistics Canada cautions about smaller samples before September 2025.

## Source and reuse

[Statistics Canada, Table 14-10-0459-01](https://doi.org/10.25318/1410045901-eng), Labour force characteristics by census metropolitan area, three-month moving average, seasonally adjusted. Distributed under the [Statistics Canada Open Licence](https://www.statcan.gc.ca/en/reference/licence). The original CSV stores counts in thousands, rounded to the nearest hundred people. Metro Economy converts the unit to people and retains the published percentage precision. Missing and suppressed estimates have no numeric value in the download. Source flags appear in the status column. The source may revise past estimates.

## Collection and publishing

The checked-in snapshot makes the explorer usable immediately. The refresh workflow checks the official bulk ZIP each Friday and replaces the snapshot when an observation, coverage or metadata changes. The recorded retrieval date belongs to the saved edition. `data/summary.json.checked_at` records each successful online source check, including unchanged data, and is used by the watchdog. Older snapshots use their known retrieval day at midnight UTC until the next online check; offline builds never substitute the current time. A changed snapshot triggers the Pages build, including the [complete CSV](https://coolcode.ca/metroeconomy/data/metro-economy.csv) and structured dataset metadata. A failed download leaves the published site in place.

Run `python3 scripts/collect.py` to retrieve the current release, or pass `--zip PATH` to process a saved official archive. Run `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests`, and `python3 scripts/build.py` before publishing `dist/`.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. The independent scheduler on our Linux server triggers overdue refreshes and checks published freshness; its code and current target list live in [the hub repository](https://github.com/jsdyer/jsdyer.github.io/tree/main/services/refresh-watchdog). The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->

Source requests are bounded by time and size. If the primary HTTPS client has a transport error or a 403/429/server response, the collector tries the same public URL with curl (installed on GitHub runners; optional locally). TLS verification remains enabled. A successful download and the existing data validation must both pass before a successful check is recorded. If both fail, the previous publication keeps its original dates.
