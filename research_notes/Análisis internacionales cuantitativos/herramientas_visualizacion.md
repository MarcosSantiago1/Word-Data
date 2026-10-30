# Tools, reproducible workflows and visualization/dashboard practices for quantitative cross-country analysis (Python-oriented, state as of Oct 2026)

> How this was checked (researcher note, 2026-10-30): package versions and release dates come from live queries to the PyPI JSON API (`https://pypi.org/pypi/<pkg>/json`) and the npm registry on 2026-10-30. The session could not reach some hosts: sdmx1.readthedocs.io, quarto.org, clauswilke.com, the CRAN DB and the GitHub API. Claims that rest on those hosts' canonical documentation, rather than on a page fetched in this session, are marked **[canonical ref, not fetched]**. Treat them as well-established but not re-verified here.

## 1. Python libraries (data access, analysis, composite indicators, mapping, viz, dashboards) and R equivalents

### Takeaway
The Python stack for a country-year panel is mature and actively maintained as of late 2026. The main data-access picks are wbgapi, sdmx1 (pandaSDMX has had no release since Feb 2023), owid-catalog and country_converter/pycountry. For analysis: pandas 3.x, DuckDB or polars, statsmodels, linearmodels and pyfixest. Charts: plotly or altair. Dashboards: Streamlit, Dash, Panel, Shiny for Python or Quarto. Two gaps stand out. There is no maintained Python port of COINr ("COINr-py" was not found on PyPI). Seaborn has had no release since January 2024.

### Cited Findings

**Data access**
- **wbgapi** 1.0.14 (released 2026-02-27) is described as "a comprehensive interface to the World Bank's data and metadata". It is the World Bank's own API client and covers WDI and the other WB databases. — [PyPI wbgapi](https://pypi.org/project/wbgapi/)
- Alternatives: **wbdata** 1.1.0 (2025-10-05, docs at wbdata.readthedocs.io) and **world_bank_data** 0.1.4 (2024-09-28, less active). — [PyPI wbdata](https://pypi.org/project/wbdata/); [PyPI world_bank_data](https://pypi.org/project/world_bank_data/)
- **pandas-datareader** 0.11.1 (2026-06-24) is still released, so it is maintained again after a long gap. It is "pandas-compatible data readers, formerly a component of pandas" (sources include FRED, World Bank, OECD, Eurostat). — [PyPI pandas-datareader](https://pypi.org/project/pandas-datareader/)
- **sdmx1** 2.28.0 (2026-10-18, requires Python ≥3.11) implements SDMX 2.1 (ISO 17369:2013) and **3.0**. It can "explore and retrieve data available from SDMX-REST web services operated by providers including the World Bank, International Monetary Fund, Eurostat, OECD, and United Nations", read and write SDMX-ML, SDMX-JSON and SDMX-CSV, and convert to pandas. It is imported as `import sdmx`. Copyright runs "2014–2026". — [PyPI sdmx1](https://pypi.org/project/sdmx1/)
- **pandaSDMX**: last release 1.10.0 on 2023-02-25, SDMX 2.1 only. sdmx1 describes itself as a fork of pandaSDMX (itself a fork of pysdmx). No formal deprecation notice was found, but the release cadence shows sdmx1 is the de facto successor. — [PyPI pandaSDMX](https://pypi.org/project/pandaSDMX/); [PyPI sdmx1 2.15.0](https://pypi.org/project/sdmx1/2.15.0); [khaeru/sdmx](https://www.github.com/khaeru/sdmx)
- **owid-catalog** 1.3.0 (2026-10-19) provides "core data types for managing OWID data (Dataset, Table, Variable)". It is published from `lib/catalog` in the owid/etl repo. — [PyPI owid-catalog](https://pypi.org/project/owid-catalog/); [owid/etl](https://github.com/owid/etl)
- **country_converter (coco)** 1.3.2 (2025-10-22) converts "country names between different classification schemes" (ISO2/ISO3, UN M49, WB/IMF/OECD membership, regex name matching). **pycountry** 26.2.16 (2026-02-17) provides ISO 3166 country and subdivision data, ISO 4217 currency data and translations. — [PyPI country_converter](https://pypi.org/project/country_converter/); [PyPI pycountry](https://pypi.org/project/pycountry/)

**Analysis / storage / econometrics**
- **pandas 3.1.0** (2026-10-22), **polars 2.1.0** (2026-10-25), **DuckDB 2.0.0** (2026-10-21, "in-process database"). — [PyPI pandas](https://pypi.org/project/pandas/); [PyPI polars](https://pypi.org/project/polars/); [PyPI duckdb](https://pypi.org/project/duckdb/)
- pandas 3.0 made Copy-on-Write the default behaviour and introduced a default string dtype. Older chained-assignment tutorial code (`df[col][mask] = x`) no longer modifies the original frame. — [pandas 3.0 release notes](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html) **[canonical ref, not fetched]**
- **statsmodels 0.15.0** (2026-08-27), **linearmodels 7.1** (2026-10-16; "Linear Panel, Instrumental Variable, Asset Pricing, and System Regression models", i.e. PanelOLS with entity/time effects, RandomEffects, BetweenOLS, FirstDifferenceOLS) and **pyfixest 0.60.0** (2026-06-11; "fast high dimensional fixed effect estimation following syntax of the fixest R package"). — [PyPI statsmodels](https://pypi.org/project/statsmodels/); [PyPI linearmodels](https://pypi.org/project/linearmodels/); [PyPI pyfixest](https://pypi.org/project/pyfixest/)
- **scikit-learn 1.9.1** (2026-09-10) handles clustering and PCA of country profiles. **PyMC 6.3.2** (2026-09-08) and **Bambi 0.21.0** (2026-09-10, formula-based Bayesian multilevel models such as `y ~ x + (1|country)`). — [PyPI scikit-learn](https://pypi.org/project/scikit-learn/); [PyPI pymc](https://pypi.org/project/pymc/); [PyPI bambi](https://pypi.org/project/bambi/)
- **ydata-profiling 4.18.4** (2026-04-22) produces automatic EDA reports for a DataFrame. — [PyPI ydata-profiling](https://pypi.org/project/ydata-profiling/)
- **sqlite-utils 4.2.1** (2026-08-13; "CLI tool and Python library for manipulating SQLite databases") and **Datasette 0.65.5** (2026-09-17; "explore and publish data") are directly relevant to a SQLite-based project. Datasette turns the .db file into a browsable, queryable web interface and JSON API. — [PyPI sqlite-utils](https://pypi.org/project/sqlite-utils/); [PyPI datasette](https://pypi.org/project/datasette/)

**Composite indicators**
- **COINr** is an **R** package (CRAN 1.1.14; R-universe build April 2026) by William Becker et al. (JOSS 2022). It covers imputation, normalisation, weighting, aggregation, sensitivity analysis and plotting, and stores indicator sets as a hierarchical "coin" object. — [COINr CRAN manual](https://stat.ethz.ch/CRAN/web/packages/COINr/refman/COINr.html); [r-universe](https://bluefoxr.r-universe.dev/packages); [JOSS paper](https://www.theoj.org/joss-papers/joss.04567/10.21105.joss.04567.pdf)
- No package named `coinrpy`, `COINrpy` or `coinr` exists on PyPI (queried 2026-10-30). The JOSS COINr paper names **CIF** as a Python library for composite indicators. — [JOSS paper](https://www.theoj.org/joss-papers/joss.04567/10.21105.joss.04567.pdf); PyPI queries returned 404 for those names.

**Mapping**
- **geopandas 1.2.0** (2026-09-28), **mapclassify 2.11.0** (2026-08-11; "classification schemes for choropleth maps", e.g. quantiles, Fisher-Jenks, natural breaks) and **cartopy 0.26.0** (2026-09-17; projections with matplotlib). — [PyPI geopandas](https://pypi.org/project/geopandas/); [PyPI mapclassify](https://pypi.org/project/mapclassify/); [PyPI cartopy](https://pypi.org/project/cartopy/)
- **Natural Earth** draws boundaries by their **de facto** status (whoever controls the territory) and also shows disputed areas so users can adapt them. Since **version 5 (Dec 2021)** it offers optional "point-of-view" (POV/worldview) layers that give de jure boundaries for several dozen countries. Admin-0 has 512 unique 3-character codes, including 272 "country" codes and 103 disputed-territory codes. The 5.1.x releases fixed the POV shapefile exports. The stated rationale: "a school teacher should be able to teach geography with maps based on Natural Earth data without worrying about legal compliance issues". — [Natural Earth disputed boundaries policy](https://www.naturalearthdata.com/about/disputed-boundaries-policy/); [Admin 0 – Countries point-of-views](https://www.naturalearthdata.com/?p=5118); [Admin 0 – Breakaway, disputed areas](https://www.naturalearthdata.com/?p=402)

**Visualization**
- **plotly 7.1.0** (2026-09-15), **Vega-Altair 6.3.0** (2026-09-15; "declarative statistical visualization"), **matplotlib 3.11.2** (2026-09-11), **plotnine 0.15.8** (2026-08-14; ggplot2 grammar in Python) and **great-tables 1.1.0** (2026-10-15; publication-quality tables from Posit). — [PyPI plotly](https://pypi.org/project/plotly/); [PyPI altair](https://pypi.org/project/altair/); [PyPI matplotlib](https://pypi.org/project/matplotlib/); [PyPI plotnine](https://pypi.org/project/plotnine/); [PyPI great-tables](https://pypi.org/project/great-tables/)
- **seaborn 0.13.2** is still the latest release, dated 2024-01-25. It still works, but it is the one major viz library here without a release in more than 2.5 years. — [PyPI seaborn](https://pypi.org/project/seaborn/)
- **owid-grapher-py 0.3.5** (2026-07-29) renders OWID-style charts in Jupyter. It is MIT-licensed, and its docs call it "experimental". — [PyPI owid-grapher-py](https://pypi.org/project/owid-grapher-py/); [OWID Grapher Python docs](https://owid-docs.readthedocs.io/projects/owid-grapher-py/en/latest/)
- **hvplot 0.12.2** (2025-12-18) is a high-level plotting API on HoloViews. — [PyPI hvplot](https://pypi.org/project/hvplot/)

**Dashboards**
- Python app frameworks (latest versions): **Streamlit 1.66.1** (2026-10-21), **Dash 4.5.0** (2026-10-29, by Plotly), **Panel 1.10.0** (2026-10-23, HoloViz), **Shiny for Python 1.9.0** (2026-10-29, Posit), **Vizro 1.0.0** (2026-10-20, McKinsey's low-code layer on Dash, now at 1.0), **marimo 0.25.2** (2026-10-19; reactive notebooks that can run as apps) and **Voilà 0.5.13** (2026-09-04; notebooks as apps). — [PyPI streamlit](https://pypi.org/project/streamlit/); [PyPI dash](https://pypi.org/project/dash/); [PyPI panel](https://pypi.org/project/panel/); [PyPI shiny](https://pypi.org/project/shiny/); [PyPI vizro](https://pypi.org/project/vizro/); [PyPI marimo](https://pypi.org/project/marimo/); [PyPI voila](https://pypi.org/project/voila/)
- **Quarto** (quarto-cli 1.10.19, 2026-10-06 on PyPI) is a "scientific and technical publishing system built on Pandoc". — [PyPI quarto-cli](https://pypi.org/project/quarto-cli/)
- Quarto dashboards (introduced in Quarto 1.4) are built from `.qmd` or `.ipynb` files with Python, R or Observable JS. Components include value boxes, cards, rows/columns, tabsets and sidebars. A dashboard can be static HTML (deployable to GitHub Pages) or interactive via Shiny or OJS. — [Quarto Dashboards docs](https://quarto.org/docs/dashboards/) **[canonical ref, not fetched — host blocked]**
- **Observable Framework**: latest npm release **1.13.4 on 2026-03-02**, with no newer release through Oct 2026. It is a free, open-source static site generator for data apps. "Data loaders" in any language (Python, SQL, R) build data snapshots at build time, and the site is then redeployed. — [npm registry @observablehq/framework](https://registry.npmjs.org/@observablehq/framework); [Observable Framework](https://observablehq.com/framework/); [Observable 2.0 release notes](https://observablehq.com/release-notes/2024-02-15-observable-2-0)
- **Evidence** (SQL + Markdown BI-as-code): latest npm release `@evidence-dev/evidence` **40.1.8 on 2026-02-06**, with no releases since. — [npm registry @evidence-dev/evidence](https://registry.npmjs.org/@evidence-dev/evidence)

**R equivalents (where R dominates)**
- **vdemdata** (official V-Dem R package, GitHub-only: `devtools::install_github("vdeminstitute/vdemdata")`) ships the latest V-Dem dataset plus helper functions. The repository describes it as a "development version". Third-party mirrors (bobfromspace/vdemdata v10, xmarquez/vdem v11.1) are outdated. — [V-Dem data archive](https://www.v-dem.net/dsarchive.html); [gittrend vdeminstitute/vdemdata](https://gittrend.io/repo/vdeminstitute/vdemdata); [xmarquez/vdem](https://github.com/xmarquez/vdem)
- The **WDI** (World Bank), **countrycode** (Arel-Bundock), **fixest** (Bergé; high-dimensional FE) and **plm** (panel models) R packages are the R standard. pyfixest explicitly mirrors fixest syntax. — [PyPI pyfixest](https://pypi.org/project/pyfixest/); R package CRAN pages **[canonical ref, not fetched — CRAN DB blocked]**

### Inferences
- For this user's stack (Colab, which runs Python 3.11+ in 2026): `wbgapi` (WDI) + `sdmx1` (IMF/OECD/Eurostat/ILO) + `owid-catalog` or OWID CSV downloads, with `country_converter` as the single place that harmonises ISO3 keys before anything is written to SQLite. sdmx1's ≥3.11 requirement is satisfied on current Colab.
- DuckDB can query the existing SQLite file directly (via its sqlite extension), so moving to DuckDB for heavy aggregations needs no migration. Polars is optional at about 5,400 rows (217 × 25), where pandas is more than enough.
- For a beginner-to-intermediate panel: start with `linearmodels.PanelOLS` (entity and time effects, clustered SEs) or `pyfixest`, whose syntax matches the dominant R/fixest literature. Reserve Bambi/PyMC for an optional multilevel chapter.
- Composite KPIs: without a Python COINr, implement the steps manually in pandas following the OECD/JRC Handbook pipeline (normalise → weight → aggregate → sensitivity). This is also more didactic. Running COINr in R once to cross-check results is an option.
- Dashboard choice for a GitHub-centric beginner:
  - **Streamlit**: simplest Python-only app, with free hosting on Streamlit Community Cloud.
  - **Quarto dashboard**: static, lives in the same repo as the docs, publishes to GitHub Pages, and pairs naturally with the didactic documentation.
  - **Dash/Vizro**: if plotly-centric callbacks are needed.
  - Observable Framework and Evidence are JS/Node-based, and their release cadence slowed in 2026, so they are less suitable for a Python-first beginner.

### Gaps
- No PyPI package called COINr-py was found. Neither CIF's maintenance status nor its PyPI name was verified.
- Current CRAN versions of WDI, countrycode, fixest, plm and wbstats could not be retrieved (CRAN DB host blocked).
- Whether Observable Framework and Evidence are formally in maintenance mode could not be confirmed. Only release dates were observed (GitHub API not accessible).
- The sdmx1 per-source list and docs (sdmx1.readthedocs.io) were blocked. Its source list is cited only via the PyPI description.

## 2. Reproducibility: project structure, data versioning, orchestration, data testing, codebooks, scheduled updates

### Takeaway
A mature, lightweight reproducible pattern for a single-person ETL in 2026 has five parts. (1) A cookiecutter-style layout separating raw, interim and processed data. (2) A DAG of small scripts (Makefile, Snakemake or a plain Python `run_all.py`; Kedro, Dagster and Prefect if it grows). (3) Schema tests with pandera (or pointblank or Great Expectations). (4) A machine-readable codebook (Frictionless `datapackage.json` or YAML metadata à la OWID). (5) A GitHub Actions cron job that rebuilds and commits or publishes data. OWID's open ETL is the reference implementation of this pattern at scale.

### Cited Findings
- **pandera 0.35.0** (2026-10-25): "a light-weight and flexible data validation and testing tool for statistical data" (DataFrame schemas with column types, ranges and uniqueness checks; works with pandas and polars). — [PyPI pandera](https://pypi.org/project/pandera/)
- **Great Expectations (GX Core) 1.24.1** (2026-10-22): "Always know what to expect from your data". Heavier and more enterprise-oriented. — [PyPI great-expectations](https://pypi.org/project/great-expectations/)
- **pointblank 1.1.1** (2026-10-15, Posit): "Find out if your data is what you think it is". Produces HTML validation reports, which suit didactic docs. — [PyPI pointblank](https://pypi.org/project/pointblank/)
- **DVC 3.67.1** (2026-03-31): "Git for data scientists – manage your code and data together". dvc-data 3.18.3 (2026-02-27). — [PyPI dvc](https://pypi.org/project/dvc/); [PyPI dvc-data](https://pypi.org/project/dvc-data/)
- **frictionless 5.21.0** (2026-10-15): "data management framework for Python that provides functionality to describe, extract, validate and transform tabular data" (Data Package / Table Schema standards). — [PyPI frictionless](https://pypi.org/project/frictionless/)
- Orchestrators (latest versions): **Snakemake 9.27.1** (2026-10-21; "reproducible and scalable data analyses"), **Kedro 1.7.0** (2026-09-28), **Prefect 3.9.0** (2026-10-21) and **Dagster 1.13.27** (2026-10-26). — [PyPI snakemake](https://pypi.org/project/snakemake/); [PyPI kedro](https://pypi.org/project/kedro/); [PyPI prefect](https://pypi.org/project/prefect/); [PyPI dagster](https://pypi.org/project/dagster/)
- **OWID ETL** (`owid/etl`, MIT license) is "the compute graph for Our World in Data's data processing". Its tagline is "There is no extract, there is no load, there is only transform".
  - Top-level folders: `etl`, `lib`, `dag`, `snapshots`, `tests`, `schemas`, `apps`, `docs`.
  - It uses `pyproject.toml` + `uv.lock` (uv-managed) and is tested on Python 3.11–3.14.
  - Buildkite CI runs unit tests, public dataset builds and a nightly full rebuild. The repo has about 17.8k commits.
  - It also contains `AGENTS.md`/`CLAUDE.md` and an `owid_mcp` folder, i.e. it is set up for AI-agent-assisted development.
  — [owid/etl GitHub](https://github.com/owid/etl); docs at [docs.owid.io/projects/etl](https://docs.owid.io/projects/etl/)
- The OWID ETL docs describe a staged channel design: `snapshot` (raw file plus provenance metadata, `.dvc` files) → `meadow` (minimal cleaning) → `garden` (harmonised country names, metadata in YAML) → `grapher` (loaded into the chart DB). Dependencies are declared in a DAG YAML. — [OWID ETL docs](https://docs.owid.io/projects/etl/) **[canonical ref, not fetched; README fetch did not describe channels]**
- **Cookiecutter Data Science v2** lays out a standard structure: `data/raw`, `data/interim` and `data/processed` (raw treated as immutable), plus `notebooks/`, `references/` (data dictionaries) and `reports/figures`. — [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/) **[canonical ref, not fetched]**
- GitHub Actions supports `on: schedule: - cron: '...'` (UTC; minimum interval 5 minutes). In public repositories, scheduled workflows are automatically disabled after 60 days without repository activity. — [GitHub Docs – events that trigger workflows (schedule)](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#schedule) **[canonical ref, not fetched]**

### Inferences
- A recommended minimal structure for the user's repo:
  - `data/raw/` (API snapshots with download date, never edited)
  - `data/processed/panel.sqlite`
  - `src/etl/{extract,transform,load}.py`
  - `src/schemas.py` (pandera)
  - `codebook/variables.yaml` or `datapackage.json`
  - `notebooks/` (didactic, numbered `01_…`, `02_…`)
  - `dashboard/` (Streamlit app or Quarto dashboard)
  - `.github/workflows/update.yml`
- A cheap provenance scheme that mirrors OWID's snapshot idea without needing DVC: store each raw API pull as a dated Parquet/CSV plus a small JSON with source URL, indicator code, retrieval date and license. DVC is worthwhile only once raw files exceed what Git handles comfortably (tens of MB). At around 5k rows × N indicators, plain Git or Git LFS usually suffices.
- Useful pandera checks for a country-year panel:
  - unique (iso3, year) key
  - year between 2000 and 2024
  - iso3 values in the reference country list
  - percentages within 0–100
  - non-negative GDP per capita
  - an explicit missingness threshold per indicator
- The codebook should record for each KPI: definition, formula, unit, source indicator code(s), aggregation rule (population-weighted vs simple mean for regional aggregates) and imputation policy. The OWID and Frictionless metadata models are good templates.
- For scheduled updates: a weekly or monthly cron in GitHub Actions that runs the ETL, runs the pandera tests, commits the updated SQLite/Parquet (or creates a release) and rebuilds the static dashboard to GitHub Pages. Any repo commit (including the bot's own) avoids the 60-day auto-disable.

### Gaps
- The exact OWID channel naming and metadata schema could not be re-verified from a fetched page (docs host not fetched).
- Comparative benchmarks of pandera vs GX vs pointblank for teaching use were not found. The recommendation is judgment-based.

## 3. Exemplary public projects and the design choices that make them effective

### Takeaway
The best cross-country tools share five design patterns: (a) one canonical chart with **chart/map/table** views, (b) user-selected countries with sensible defaults, (c) a time slider with fixed axes, (d) prominent sources, metadata and **downloads (CSV/SVG/PNG)**, and (e) shareable URL state. OWID Grapher is the clearest open-source embodiment. Gapminder adds animated multivariate bubbles on a log income axis. OECD BLI adds user-defined weights for composite indices. V-Dem and Global Data Lab show the value of offering uncertainty-aware and subnational data.

### Cited Findings
- **OWID Grapher (redesign, 18 Oct 2023)**:
  - Chart, map and table views are switched with buttons. The table view gives summary statistics over a range of years selected with the timeline slider. Clicking a country on the map opens its chart.
  - "Edit countries and regions" entity selector.
  - "Align axis scales" switch and **small multiples** via the settings menu.
  - The data source is shown prominently on every chart, with a "Learn more about this data" overlay.
  - Download menu offering SVG/PNG and CSV, plus an embed snippet.
  - Shared links preview the exact chart configuration (tab, timespan, countries). Full-screen mode.
  — [OWID: Redesigning our interactive data visualizations](https://ourworldInData.org/redesigning-our-interactive-data-visualizations)
- Grapher code is open source (MIT). OWID charts, data and text are CC BY, but third-party source data keeps the original providers' terms (e.g. WHO, UN, World Bank). — [OWID FAQ](https://OurWorldInData.Org/faqs); [owid/owid-grapher](https://github.com/owid/owid-grapher); [The OWID Grapher](https://ourworldindata.org/owid-grapher)
- **Gapminder / Trendalyzer** was created by Hans, Ola and Anna Rosling (2003); Google later acquired it as the Motion Chart. It encodes income (log x-axis), life expectancy (y), population (bubble size) and region (colour), animates over years and keeps axes fixed across frames. In Python, Plotly reproduces it with `px.scatter(..., log_x=True, size='pop', color='continent', animation_frame='year', animation_group='country')`. — [Wikipedia: Trendalyzer](https://en.wikipedia.org/wiki/Trendalyzer); [UC3M CSSLab Gapminder chart](https://csslab.uc3m.es/dataviz/projects/gapminder/); [Plotly animation notebook](https://nbviewer.org/github/jonmmease/plotly.py_release_notebooks/blob/master/notebooks/v3.7.0/animation_updates.ipynb)
- Robertson et al. (InfoVis 2008), "Effectiveness of Animation in Trend Visualization", compared Gapminder-style animation, traces and small multiples. Animation was the least effective for *analysis* (slower, more errors) but enjoyed for *presentation*. — [Robertson, Fernandez, Fisher, Lee, Stasko 2008 (PDF)](https://faculty.cc.gatech.edu/~stasko/papers/infovis08-anim.pdf) (finding summarised from the paper; PDF not re-fetched in this session)
- **OECD Better Life Index** (Moritz Stefaner with Raureif and 9elements, 2011) shows 11 well-being dimensions for about 40 countries as "flowers".
  - Users re-weight dimensions and the ranking updates live. The weighted petal "become[s] broader and more saturated".
  - Stefaner chose flowers for visual coherence and friendly branding after testing many designs.
  - Critics (Storytelling with Data, FlowingData commenters) noted that petal lengths are hard to compare.
  - The same principle was carried into OECD Regional Well-Being.
  — [truth & beauty: OECD BLI](https://truth-and-beauty.net/projects/oecd-better-life-index); [FlowingData 2011](https://flowingdata.com/2011/05/24/better-life-index-measures-well-being-across-countries/); [Storytelling with Data](https://www.storytellingwithdata.com/blog/2011/06/oecd-better-life-initative); [OECD Regional Well-Being](https://truth-and-beauty.net/projects/oecd-regional-wellbeing)
- **V-Dem Graphing Tools**: an online platform "for making data visualization intuitive, accessible and easy to use", including a mapping tool and PanDem. All data and graphs are open and free to use. A Danish MFA manual describes the tools as covering more than 300 indicators. — [V-Dem Graphing Tools](https://www.v-dem.net/graphingtools.html); [Danida V-Dem tools manual](https://um.dk/en/-/media/websites/umen/danida/partnerships/research/manual-for-v-dem-online-tools.ashx)
- **Global Data Lab (Radboud University)**: the Subnational HDI database by Smits & Permanyer (Scientific Data 2019) covered 1,625 regions in 161 countries for 1990–2017. Later versions are reported at about 1,855 regions in 168 countries. GDL also hosts a Subnational Gender Development Index. — [Smits & Permanyer 2019, PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6413757); [GDL Subnational HD](https://globaldatalab.org/sgdi/); [UNDP HDR on SHDI](https://hdr.undp.org/en/content/subnational-human-development-index-moving-beyond-country-level-averages)

### Inferences
- Design choices worth copying in the user's dashboard:
  - **Chart, map and table views of the same indicator** (OWID).
  - **Country picker with region presets** and defaults (e.g. the user's region plus world aggregate).
  - **Year slider with fixed axes**.
  - **Linear/log toggle** for income-type variables.
  - **"Sources & method" panel** per KPI that links to the codebook.
  - **CSV download** of the filtered data.
  - **URL query parameters** for shareable state (Streamlit `st.query_params` or Quarto/OJS).
- Use a Gapminder bubble chart as an *engaging entry point*. Provide small multiples or line charts for *analytic* comparison, as the Robertson et al. finding supports.
- For composite KPIs, an OECD-BLI-style "your weights" slider is a strong didactic device. It makes students see that rankings depend on normative weighting choices.
- Global Data Lab is a reminder to flag that national averages hide within-country inequality. This is a useful "limitations" section for the socioeconomic conclusions.

### Gaps
- No formally published "OWID design principles" document was found. The OWID findings come from the 2023 redesign post, and later Grapher changes (2024–2026, e.g. mobile redesign) were not verified.
- No primary World Bank Data Viz / DataBank design documentation was retrieved.
- Gapminder Foundation primary design documentation was not fetched.

## 4. Visualization best practices for country comparisons (and accessibility)

### Takeaway
For cross-country panels, the strongest defaults are:
- line charts or **small multiples** for trajectories
- **slope or dumbbell charts** for two-period change
- **sorted dot/bar plots** (not tables of ranks) for rankings, with uncertainty where available
- **log scales** for income and other multiplicative variables

Use choropleths only for normalized rates, with classed colour scales, an equal-area projection and a stated boundary policy. Avoid dual axes, rainbow palettes and colour-only encodings, and use colour-blind-safe palettes with sufficient contrast.

### Cited Findings
- Choropleths work best for rates, percentages or per-capita values, because raw totals favour large or populous areas. — [Storytelling with Data: what is a choropleth map?](https://www.storytellingwithdata.com/blog/what-is-a-choropleth-map)
- Map raw counts only when the goal is to show *how much* exists. Data already expressed per capita, as a percent or as a ratio needs no further standardization. — [Axis Maps Cartography Guide: standardizing data](https://www.axismaps.com/guide/standardizing-data)
- Choropleths are poor for precise value reading. — [think.design: choropleth](https://think.design/services/data-visualization-data-design/choropleth/)
- Datawrapper Academy covers palette choice for choropleths (sequential vs diverging, number of classes). Lisa Charlotte Rost's Datawrapper post discusses when to use choropleths and when not to. — [Datawrapper Academy: what to consider when creating choropleth maps](https://www.datawrapper.de/academy/what-to-consider-when-creating-choropleth-maps); [Map Room summary](https://www.maproomblog.com/2018/04/advice-on-choropleth-maps/); [FlowingData: choropleth design considerations](https://flowingdata.com/2018/03/28/choropleth-map-design-considerations)
- A log axis gives equal distances for equal *relative* changes. This is why Gapminder plots income on log x with readable breaks (1k, 10k, 100k). — [UC3M CSSLab Gapminder](https://csslab.uc3m.es/dataviz/projects/gapminder/)
- mapclassify provides classification schemes for choropleths (quantiles, equal interval, Fisher-Jenks, etc.). Classing choices change the visual story. — [PyPI mapclassify](https://pypi.org/project/mapclassify/)
- Claus Wilke, *Fundamentals of Data Visualization* (O'Reilly 2019, free online), has relevant chapters on:
  - "Color pitfalls" (rainbow scales, not designing for colour-vision deficiency; recommends Okabe-Ito)
  - "The principle of proportional ink" (bars must start at zero)
  - "Visualizing uncertainty" (error bars, graded intervals)
  - "Visualizing geospatial data" (projections; cartograms as an alternative to area bias)
  - "Multi-panel figures" (small multiples)
  - "Visualizing trends"
  — [Wilke, Fundamentals of Data Visualization](https://clauswilke.com/dataviz/) **[canonical ref, not fetched — host blocked]**
- Edward Tufte popularized **small multiples** (*Envisioning Information*, 1990) and the data-ink ratio (*The Visual Display of Quantitative Information*, 1983). Alberto Cairo, *How Charts Lie* (W. W. Norton, 2019), covers truncated or dual axes, unnormalized maps and spurious correlations. — [Tufte books](https://www.edwardtufte.com/tufte/books_vdqi); [Cairo, How Charts Lie](https://www.albertocairo.com/) **[canonical refs, not fetched]**
- WCAG 2.x Success Criterion 1.4.11 (Non-text Contrast) requires 3:1 contrast for graphical objects needed to understand content. SC 1.4.1 (Use of Color) forbids colour as the only means of conveying information. — [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) **[canonical ref, not fetched]**
- Natural Earth's de facto default boundaries plus optional worldview layers (see section 1) are the practical answer to disputed-border issues on world maps. — [Natural Earth disputed boundaries policy](https://www.naturalearthdata.com/about/disputed-boundaries-policy/)

### Inferences
- A practical rule set for the user's dashboard and docs:
  1. Default to time-series lines with a highlighted focus country against grey peers, or to small multiples by region with shared y-axes (OWID's "Align axis scales").
  2. For 2000 vs 2024 comparisons, use slope or dumbbell charts sorted by change.
  3. For rankings, use a sorted dot plot with the value shown, not just the rank number, because ranks exaggerate tiny differences. Add intervals where the source gives them (e.g. V-Dem posterior intervals).
  4. Put GDP per capita, income and similar on a log scale with labelled breaks, and explain it in the docs ("each gridline = ×10").
  5. Choropleths: only rates or per-capita values. Use classed sequential palettes (mapclassify quantiles or Fisher-Jenks, 5–7 classes) or a diverging palette around a meaningful midpoint. Use an equal-area or compromise projection (Equal Earth or Robinson via geopandas `to_crs`) instead of Web Mercator. Pair with a bar or dot chart, because small states vanish on maps. State the boundary policy (Natural Earth de facto) in a footnote.
  6. Never use dual y-axes. Use two aligned panels, or index both series to 100 in a base year.
  7. Use colour-blind-safe palettes (Okabe-Ito for categories; viridis/cividis or ColorBrewer sequential), check them with a CVD simulator, use redundant encodings (labels, markers), add alt-text and data tables, and respect WCAG contrast.
  8. Always show source, units, base year (constant vs current USD, PPP) and the date of data retrieval.

### Gaps
- The full text of the Datawrapper "when to use choropleths" post and specific Datawrapper rules on dual axes were not retrieved.
- Equal Earth's availability as a named CRS in geopandas/pyproj (EPSG:8857) is known from PROJ docs but was not verified this session.

## 5. Didactic resources (English and Spanish) for beginner–intermediate learners

### Takeaway
English resources are abundant and free: QuantEcon, McKinney's *Python for Data Analysis* (free online 3rd ed.), *The Effect* (Huntington-Klein), Wilke's book, and the OWID Teaching Hub. In Spanish, the verifiable options found were the World Bank's Open Learning Campus open-data courses. CEPAL-branded Python courses could not be verified.

### Cited Findings
- **OWID Teaching Hub** ("Teaching with OWID") is a resource hub for global development education. It encourages students to explore data through interactive charts, and OWID surveys teachers about classroom use. — [OWID Teaching](https://ourworldindata.org/teaching); [OWID: how to use Our World in Data](https://ourworldindata.org/how-to-use-our-world-in-data)
- **World Bank Open Learning Campus – Spanish open-data courses**: "Datos Abiertos para Usuarios de Datos", "para Productores de Datos" and "para Encargados de Formular Políticas". The users course covers definitions, sourcing and licensing, scraping and cleaning, basic analysis and visualization, and storytelling. — [WB OLC course 36389](https://www.worldbank.org/en/olc/course/36389); [36388](https://www.worldbank.org/en/olc/course/36388); [36387](https://www.worldbank.org/en/olc/course/36387)
- The World Bank's data-for-development course engaged about 21,000 learners. The WB Data Use and Literacy Program publishes data-literacy materials. — [WB Data Blog](https://blogs.worldbank.org/en/opendata/demand-data-literacy-world-banks-data-development-course-engages-21000-data-enthusiasts); [WB Data Use and Literacy Program](https://www.worldbank.org/en/programs/data-use-and-literacy-program/publications)
- A World Bank programme in Paraguay trained more than 160 government officials in Python and R at three levels. — [desarrollo.edu.py](https://desarrollo.edu.py/?p=4900)
- **QuantEcon** offers free Python lecture series, including "A First Course in Quantitative Economics with Python" with cross-country income-distribution and growth examples. — [QuantEcon intro](https://intro.quantecon.org/) **[canonical ref, not fetched]**
- **Wes McKinney, *Python for Data Analysis*, 3rd ed. (2022)** is free online ("Open Access" HTML) and covers pandas groupby, reshaping and time series. — [wesmckinney.com/book](https://wesmckinney.com/book/) **[canonical ref, not fetched; note pandas 3.x changes postdate it]**
- **Nick Huntington-Klein, *The Effect*** is free online. It covers causal inference including fixed effects (Ch. 16) and difference-in-differences, with code in R, Stata and Python. — [theeffectbook.net](https://theeffectbook.net/) **[canonical ref, not fetched]**
- Plotly's Gapminder animation notebook is a ready-made teaching example. — [nbviewer Plotly animation](https://nbviewer.org/github/jonmmease/plotly.py_release_notebooks/blob/master/notebooks/v3.7.0/animation_updates.ipynb)

### Inferences
- Suggested learning path to embed in the project docs:
  1. McKinney chapters 5–10 (pandas, cleaning, groupby), with a note on pandas 3 Copy-on-Write
  2. the OWID/Gapminder visual literacy examples
  3. Wilke's colour, uncertainty and geospatial chapters
  4. QuantEcon's cross-country income chapters
  5. *The Effect* Ch. 16 before any panel fixed-effects regression
- For Spanish-speaking learners, pair the WB OLC Spanish courses (concepts) with the project's own Spanish notebooks (code). Writing the didactic documentation in Spanish fills a real gap found in this research.

### Gaps
- No CEPAL/ILPES course specifically on Python for cross-country analysis could be verified. CEPALSTAT's API and its Python client status were not researched (out of scope / not found).
- No Spanish translation of *The Effect* or *Fundamentals of Data Visualization* was verified. No Spanish edition of McKinney's 3rd ed. was verified.
- The current World Bank "Data Literacy Program" course catalog and its 2026 status were not confirmed beyond the pages cited.
