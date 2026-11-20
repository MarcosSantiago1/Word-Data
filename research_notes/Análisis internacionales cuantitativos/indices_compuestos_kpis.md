# Composite indices, rankings and KPIs for international country comparisons

> **Read this first: how sources are marked.** In this session web *search* worked but page *fetching* was blocked for almost every host (worldbank.org, sdgindex.org, worldhappiness.report and wikipedia.org all failed to resolve). So each citation carries one of two tags:
> - **[V]**: the claim was confirmed in this session by search-result text from that URL.
> - **[K]**: the claim comes from the canonical primary document named in the link. I know it well, but I could not re-open it in this session. Spot-check [K] items, especially exact numbers, before you publish. The URLs and DOIs on [K] items were also not re-checked in this session.
>
> All Python snippets were run in this session (numpy/pandas/scipy). The printed numbers come from those runs.
>
> **Context for the user's project.** The panel covers about 217 countries × 2000–2024 with ISO3 keys and these domains: demography, economy, health, suicide, public spending, happiness, democracy and governance. It already contains several of the indices discussed below (WHR ladder, V-Dem/EIU, WGI). The "Inferences" bullets say how each finding applies to the 5 multidimensional KPIs.

---

## 1. What are the standard steps of the OECD/JRC Handbook (2008) and JRC COIN guidance, including updates and the COINr / COINr-py tools?

### Takeaway
The 2008 OECD/JRC Handbook sets out a 10-step pipeline: framework → data selection → imputation → multivariate analysis → normalisation → weighting & aggregation → uncertainty/sensitivity → back to the data → links to other indicators → visualisation. The JRC Competence Centre on Composite Indicators and Scoreboards (COIN) still uses this pipeline. It runs it through its "10-step guide", statistical audits of major indices, and the R package **COINr**. I found no evidence that a Python port called "COINr-py"/"COINrpy" exists. PyPI returned 404 for `coinrpy`, and searches turned up nothing.

### Cited Findings
- The Handbook is by Nardo, Saisana, Saltelli, Tarantola, Hoffman and Giovannini, published by OECD/EC-JRC in 2008, titled *Handbook on Constructing Composite Indicators: Methodology and User Guide*. Its 10 steps are: (1) theoretical framework; (2) data selection; (3) imputation of missing data; (4) multivariate analysis; (5) normalisation; (6) weighting and aggregation; (7) uncertainty and sensitivity analysis; (8) back to the data (decomposing the index into its drivers); (9) links to other indicators; (10) visualisation of results. — [K] [OECD/JRC Handbook, doi:10.1787/9789264043466-en](https://doi.org/10.1787/9789264043466-en)
- The Handbook grew out of an earlier JRC technical report on tools for building composite indicators (Nardo et al. 2005, EUR 21682). That report argues that "a synergistic use of UA and SA [uncertainty and sensitivity analysis] is proven to be more powerful". — [V] [JRC EUR 21682 "Tools for Composite Indicators Building"](https://publications.jrc.ec.europa.eu/repository/bitstream/JRC31473/EUR%2021682%20EN.pdf)
- The JRC COIN hosts a toolkit page that lists COINr as its tool for building composite indicators. — [V] [JRC COIN – COINr page](https://knowledge4policy.ec.europa.eu/composite-indicators/toolkit_en/coinr_en); [V] [JRC COIN – COINr](https://knowledge4policy.ec.europa.eu/composite-indicators/coinr_en)
- COINr is "inspired by, and broadly follows the methodology of the JRC/OECD Handbook on Composite Indicators and the Competence Centre for Composite Indicators and Scoreboards, which also supported the development of the package". It covers indicator selection, denomination, imputation, data treatment (outliers), normalisation, weighting and aggregation. It also covers multivariate analysis, correlation plots, PCA shortcuts and global sensitivity analysis. Install it with `install.packages("COINr")`. — [V] [COINr README (CRAN mirror)](https://archive.linux.duke.edu/cran/web/packages/COINr/readme/README.html)
- COINr stores a whole index in one hierarchical object called a "coin". The current CRAN version is 1.1.14, maintained by William Becker. The pre-1.0 API is still available as the separate package **COINr6** (GitHub bluefoxr/COINr6). — [V] [COINr reference manual](https://archive.linux.duke.edu/cran/web/packages/COINr/refman/COINr.html); [V] [r-universe COINr](https://bluefoxr.r-universe.dev/COINr)
- COINr's reference publication: Becker, Caperna, Del Sorbo, Norlén, Papadimitriou & Saisana (2022), "COINr: An R package for developing composite indicators", *Journal of Open Source Software* 7(78), 4567. — [K] [JOSS doi:10.21105/joss.04567](https://doi.org/10.21105/joss.04567)
- JRC COIN carries out "statistical audits" of major international indices by invitation, for example the SDG Index (2019) and the Global Innovation Index (yearly). An audit runs two checks: (a) a correlation/PCA check of the conceptual structure; (b) a Monte Carlo uncertainty and sensitivity analysis of the ranks. — [K] [Papadimitriou, Neves & Becker (2019), JRC Statistical Audit of the SDG Index and Dashboards, JRC116857](https://publications.jrc.ec.europa.eu/repository/handle/JRC116857)
- A 2019 review by Greco, Ishizaka, Tasiou & Torrisi in *Social Indicators Research* 141:61–94 surveys the methodological framework of composite indices since the Handbook. It covers weighting, aggregation and robustness. — [V] [Greco et al. 2019, "On the Methodological Framework of Composite Indices"](https://pure.port.ac.uk/ws/files/8559735/On_the_methodological_framework_of_composite_indices.pdf)

### Inferences
- The 10 steps work as a checklist for the user's 5 KPIs. In beginner projects the steps most often skipped are 4 (check correlations/PCA within each KPI), 7 (rank uncertainty) and 8 (show which components drive each country's score).
- With no maintained Python COINr port, a Python user can rebuild the pipeline with pandas, scikit-learn (PCA, KNN imputation) and scipy, as in the snippets below. Another option is to call COINr from R via `rpy2`.

### Gaps
- I could not confirm whether a Python port named "COINr-py"/"COINrpy" exists, including under another name. PyPI `coinrpy` and `COINrpy` returned 404, and GitHub search results were empty. Treat it as non-existent unless the user has a link.
- I could not fetch the current JRC COIN pages to check whether a formal successor to the 2008 Handbook has been published (e.g., a revised guide by 2026). The JRC "10-step guide" and its online training material are the de facto updates. [K]

---

## 2. Normalisation, aggregation (compensability) and weighting: options and consequences

### Takeaway
Each choice is a value judgement that can change rankings:
- **Normalisation** sets the units and how outliers act.
- **Aggregation** sets how far a weak dimension can be offset by a strong one (compensability).
- **Weighting** sets the nominal importance of each indicator. *Nominal* weights are not the same as *effective* importance when indicators are correlated or have different variances.

### Cited Findings

**Normalisation (formulas):**
- **Min–max (rescaling):** `x' = (x − min)/(max − min)`, so x' lies in [0, 1]. It is sensitive to outliers and to the sample: adding or removing a country changes min and max. **z-score:** `x' = (x − mean)/sd`. It keeps relative distances, but an extreme value in one indicator weighs more in a sum. **Distance to target / reference:** `x' = x / x_target` or `(x − x_target)/x_target`. **Ranking:** `x' = rank(x)` is robust to outliers but discards interval information. **Categorical scales and "above/below the mean" are also options.** For "bad" indicators (e.g., suicide rate, mortality) you must flip the direction: `x' = (max − x)/(max − min)`. — [K] [OECD/JRC Handbook, Table 3 on normalisation methods](https://doi.org/10.1787/9789264043466-en)
- **Goalposts** are min–max with *fixed, external* bounds instead of the sample's own min and max. HDI example: life expectancy 20–85 years, expected years of schooling 0–18, mean years of schooling 0–15. Fixed bounds keep scores comparable over time and across samples. — [V] [Our World in Data – HDI indicator notes](https://ourworldindata.org/grapher/human-development-index-categories); [V] [UNDP HDR Technical Notes (data.un.org copy)](https://data.un.org/_Docs/HDR%20Technical%20Notes.pdf)

**Aggregation:**
- **Arithmetic mean** `CI = Σ wᵢ xᵢ` is *fully compensatory*: a one-unit loss in one indicator is exactly offset by `wᵢ/wⱼ` units in another. **Geometric mean** `CI = Π xᵢ^wᵢ` is *partially compensatory*: compensation is smaller when scores are low, and an unbalanced profile is penalised. Values must be strictly positive. **Non-compensatory multi-criteria methods** (e.g., Condorcet-type rankings) avoid compensation entirely. — [K] [OECD/JRC Handbook, ch. 6](https://doi.org/10.1787/9789264043466-en); [V] [Greco et al. 2019](https://pure.port.ac.uk/ws/files/8559735/On_the_methodological_framework_of_composite_indices.pdf)
- UNDP's own technical notes describe the switch to the geometric mean as producing *lower* index values. The largest changes fall on countries whose development is uneven across dimensions. — [V] [UNDP HDR Technical Notes](https://data.un.org/_Docs/HDR%20Technical%20Notes.pdf) (via search snippet)
- The **Mazziotta–Pareto Index** (Italian ISTAT's approach) is another partially compensatory option. It subtracts a penalty for imbalance: `MPI = M_z − S_z·cv`, where M is the mean of the standardised indicators, S their standard deviation and cv their coefficient of variation. — [K] [Mazziotta & Pareto (2016), *Social Indicators Research* 127:983–1003](https://doi.org/10.1007/s11205-015-0998-2)

**Weighting:**
- **Equal weights** are the most common choice and the easiest to explain. However, equal weights on correlated sub-indicators cause *implicit double-counting*. **Statistical weights:** PCA/factor analysis gives weights in proportion to the variance each factor explains (the Handbook's FA procedure: keep factors with eigenvalue > 1, rotate with varimax, use squared loadings scaled to unity). **Participatory weights:** budget allocation, where experts split 100 points, and the analytic hierarchy process (AHP). **Regression-based weights** and **conjoint analysis** are also options. — [K] [OECD/JRC Handbook, ch. 6](https://doi.org/10.1787/9789264043466-en)
- **Benefit of the Doubt (BoD)** is a DEA-based method. Each country gets its *own* most favourable weights, found by solving `max_w Σᵢ wᵢ y_ci s.t. Σᵢ wᵢ y_ji ≤ 1 ∀j, w ≥ 0`. A score of 1 means "no country does better under your own best weights". Weight restrictions are usually needed so that countries cannot ignore their weak dimensions. — [K] [Cherchye, Moesen, Rogge & Van Puyenbroeck (2007), "An introduction to 'benefit of the doubt' composite indicators", *Social Indicators Research* 82:111–145](https://doi.org/10.1007/s11205-006-9029-7)
- **Nominal weight ≠ importance.** Paruolo, Saisana & Saltelli (2013) measure each indicator's real influence with the *correlation ratio* (first-order sensitivity index) of the index on that indicator. Under nominally equal weights, the effective importances can be very unequal. — [V] [Paruolo, Saisana & Saltelli (2013), "Ratings and rankings: voodoo or science?", *JRSS A* 176(3)](https://www.andreasaltelli.eu/file/repository/rssa_1059.pdf); [K] [Becker, Saisana, Paruolo & Vandecasteele (2017), "Weights and importance in composite indicators: closing the gap", *Ecological Indicators* 80:12–22](https://doi.org/10.1016/j.ecolind.2017.03.056)
- Decancq & Lugo (2013) classify weighting schemes for multidimensional well-being into data-driven, normative and hybrid approaches. — [K] [Decancq & Lugo (2013), *Econometric Reviews* 32(1):7–34](https://doi.org/10.1080/07474938.2012.690641)

**Worked Python examples (run in this session):**
```python
import numpy as np, pandas as pd
from scipy.optimize import linprog

# Normalisation (df: rows=ISO3, cols=indicators; 'neg' = indicators where lower is better)
def minmax(s, lo=None, hi=None, higher_is_better=True):
    lo = s.min() if lo is None else lo;  hi = s.max() if hi is None else hi
    x = (s.clip(lo, hi) - lo) / (hi - lo)          # clip = goalpost censoring
    return x if higher_is_better else 1 - x
def zscore(s): return (s - s.mean()) / s.std()
def pct_rank(s): return s.rank(pct=True) * 100       # percentile rank 0-100

# Compensability: same arithmetic mean, different geometric mean
a = np.array([0.9, 0.9, 0.3]); b = np.array([0.7, 0.7, 0.7])
a.mean(), b.mean()                     # 0.70, 0.70
a.prod()**(1/3), b.prod()**(1/3)       # 0.624, 0.700 -> unbalanced profile penalised

# Benefit of the Doubt (DEA) with scipy
Y = np.array([[0.9,0.2,0.5],[0.6,0.6,0.6],[0.3,0.9,0.4],[0.5,0.5,0.9]])
for i in range(len(Y)):
    r = linprog(-Y[i], A_ub=Y, b_ub=np.ones(len(Y)), bounds=[(0,None)]*Y.shape[1])
    print(i, round(-r.fun,3), r.x.round(3))
# -> all 4 countries score 1.0 (each picks the weights favouring its strongest dimension)
#    a teaching example of why BoD needs weight restrictions (e.g. each w_i*y_i share >= 10%)
```

### Inferences
- **Panel data (2000–2024):** use *fixed goalposts*, for example defined once over the whole panel or from external targets, not min–max recomputed every year. Otherwise a country's score can change only because the best or worst country changed. This is the reason HDI and SDG Index use fixed bounds.
- **Skewed indicators** (GDP per capita, public spending in USD, suicide rates) need a log transform or winsorising/capping before min–max. Otherwise one or two outliers squeeze everyone else into a narrow band. The HDI logs income for this reason (see section 3).
- **Domains that should not compensate each other** (e.g., high GDP should not hide high suicide or poor governance): consider the geometric mean or Mazziotta–Pareto, and report the arithmetic version as a robustness check.

### Gaps
- The exact PCA/FA weighting recipe (eigenvalue > 1, varimax, squared loadings) is from memory of the Handbook [K]. I could not re-open it in this session.

---

## 3. How specific major indices are built

### Takeaway
Major indices span a spectrum:
- **Transparent goalpost-and-mean indices:** HDI, SDG Index, Social Progress Index, Better Life Index, Global Peace Index, EIU Democracy Index.
- **Counting-based poverty measures:** MPI (Alkire–Foster).
- **Latent-variable statistical models that report uncertainty:** V-Dem (Bayesian IRT) and WGI (unobserved components model).
- **The World Happiness Report** ranks a *single* survey item, the Cantril ladder. Its six "explanatory factors" are not used to build the ranking.

### Cited Findings

#### UNDP Human Development Index (HDI)
- **Current method (since HDR 2010).** Dimension index = `(actual − min)/(max − min)`. Goalposts: life expectancy 20–85; expected years of schooling 0–18; mean years of schooling 0–15. The education index is the arithmetic mean of the two schooling indices. HDI is the **geometric mean** of the three dimension indices. — [V] [Our World in Data HDI notes](https://ourworldindata.org/grapher/human-development-index-categories); [V] [UNDP HDR Technical Notes](https://data.un.org/_Docs/HDR%20Technical%20Notes.pdf)
- **Income** uses the natural log of GNI per capita (2017 PPP $). Goalposts are $100 and $75,000: `I_inc = (ln GNIpc − ln 100)/(ln 75000 − ln 100)`. The log reflects diminishing returns of income to capabilities. — [K] [UNDP HDR 2025 Technical Notes, via documentation page](https://hdr.undp.org/data-center/documentation-and-downloads)
- **Before 2010 (and why it changed).** HDI was the *arithmetic* mean of: life expectancy (goalposts 25–85); education (2/3 adult literacy + 1/3 gross enrolment); and log GDP per capita PPP ($100–$40,000). In 2010 UNDP replaced literacy/enrolment with mean and expected years of schooling, replaced GDP with GNI, and switched to the geometric mean. The stated reason was that the dimensions are imperfect substitutes: poor performance in one should not be linearly offset by another. — [K] [UNDP HDR 2010 Technical Note 1](https://hdr.undp.org/content/human-development-report-2010); the effect on index values is confirmed [V] in the [Technical Notes snippet](https://data.un.org/_Docs/HDR%20Technical%20Notes.pdf)
- The documentation page lists a 2025 HDR Technical Note alongside earlier editions. — [V] [UNDP documentation & downloads](https://hdr.undp.org/data-center/documentation-and-downloads)

**Worked example** (hypothetical country: LE = 75, EYS = 14, MYS = 9, GNI = $15,000):
```python
LE, EYS, MYS, GNI = 75, 14, 9, 15000
I_H = (LE-20)/(85-20)                                   # 0.8462
I_E = (min(EYS,18)/18 + min(MYS,15)/15) / 2             # (0.7778+0.6)/2 = 0.6889
I_I = (np.log(GNI)-np.log(100))/(np.log(75000)-np.log(100))  # 0.7569
HDI = (I_H*I_E*I_I)**(1/3)                              # 0.7613  (arithmetic mean would be 0.7640)
```

#### Inequality-adjusted HDI (IHDI)
- Each dimension is discounted by its Atkinson inequality measure with ε = 1: `A_x = 1 − (geometric mean of x)/(arithmetic mean of x)`, computed over the household-survey or life-table distribution of that dimension. Then `I*_x = (1 − A_x)·I_x`, `IHDI = (Π(1−A_x))^{1/3} · HDI`, and the "loss" from inequality is `1 − IHDI/HDI`. — [K] [UNDP HDR Technical Notes (IHDI section)](https://hdr.undp.org/data-center/documentation-and-downloads)
```python
x = np.array([2000, 5000, 10000, 40000.])               # incomes of 4 equal-size groups
A = 1 - np.exp(np.log(x).mean())/x.mean()               # Atkinson(eps=1) = 0.4419
```

#### Multidimensional Poverty Index (Alkire–Foster, OPHI/UNDP)
- MPI = H × A. **H** (incidence) is the share of people who are multidimensionally poor. **A** (intensity) is the average weighted share of deprivations among the poor. There are ten indicators in three dimensions: health (nutrition, child mortality); education (years of schooling, school attendance); living standards (cooking fuel, sanitation, drinking water, electricity, housing/flooring, assets). — [V] [UNDP HDR "Assessing multidimensional poverty"](https://hdr.undp.org/content/assessing-multidimensional-poverty-one-index-global-level); [V] [Our World in Data MPI](https://ourworldindata.org/grapher/multidimensional-poverty-index-mpi); [V] [Alkire et al., *Scientific Data* (2024), harmonised global MPI](https://www.nature.com/articles/s41597-024-04269-x)
- **Weights:** dimensions are equal at 1/3 each, so health and education indicators get 1/6 each and the six living-standard indicators 1/18 each. The poverty cutoff is **k = 1/3** of weighted deprivations. 20–33.3% counts as "vulnerable" and ≥ 50% as "severe". (An older 2010 UN briefing quoted a 30% cutoff. The 1/3 cutoff applies to current editions.) — [K] [OPHI Global MPI methodology](https://ophi.org.uk/global-mpi); [K] [Alkire & Foster (2011), *Journal of Public Economics* 95(7–8):476–487](https://doi.org/10.1016/j.jpubeco.2010.11.006); the 30% figure is [V] from the [2010 UN briefing](https://www.un.org/en/ga/second/65/docs/foster.pdf)
- 2025 global MPI (UNDP–OPHI, October 2025): 109 countries and 1,359 subnational regions, with about 1.1 billion of 6.3 billion people in acute multidimensional poverty. — [V] (search-result summary; primary: [OPHI](https://ophi.org.uk/global-mpi), [UNDP HDR MPI](https://hdr.undp.org/content/assessing-multidimensional-poverty-one-index-global-level))
```python
w = np.array([1/6]*4 + [1/18]*6)                        # 10 indicators
D = np.array([[1,0,1,0,1,1,0,0,1,0],                    # person x indicator deprivation (0/1)
              [0,0,0,0,1,0,0,0,0,0],
              [1,1,0,1,1,1,1,1,1,1],
              [0,0,1,0,0,0,0,0,0,0],
              [0,1,0,0,1,1,1,0,0,0]])
c = D @ w                     # deprivation scores: [0.5, 0.056, 0.833, 0.167, 0.333]
poor = c >= 1/3               # k = 1/3 ("dual cutoff": indicator cutoffs, then k)
H = poor.mean()               # 0.6
A = c[poor].mean()            # 0.5556
MPI = H*A                     # 0.3333 (= mean of censored c)
```
Note that person 5's score is exactly 1/3, so whether they are poor depends on `>=` vs `>`. MPI results are sensitive near k.

#### SDG Index and Dashboards (Sachs et al., SDSN Sustainable Development Report)
- Scores run 0–100 and are read as "% of the way to SDG achievement" (distance to target). The 2025 edition ranks **167** of the 193 UN member states, with Finland, Sweden and Denmark at the top. — [V] [UNRIC on SDR 2025](https://unric.org/en/sustainable-development-report-finland-sweden-and-denmark-top-the-2025-rankings/); [V] [SDR Methods chapter](https://dashboards.sdgindex.org/chapters/part-5-methods/)
- **Methodology changes:** SDR 2025 added a streamlined headline index (**SDGi**) built on 17 headline indicators, one per goal. It allows a consistent time series since 2015 with less missing-data bias. The methods page for the newer 2026 edition calls the headline index "**SDGhi**". The headline indicators were chosen for how well they track the full index and for their data coverage across countries and years. — [V] [SDR Methods chapter](https://dashboards.sdgindex.org/chapters/part-5-methods/); [V] [Tsinghua SDG summary of SDR 2025](https://thusdg.tsinghua.edu.cn/en/info/1141/1683.htm). *Naming conflict:* secondary 2025 sources say "SDGi", while the 2026 methods page says "SDGhi".
- **Comparability warning:** "SDG Index rankings and scores from one edition cannot be compared with the results from previous editions" because indicators and methods change. — [V] [SDR Methods chapter](https://dashboards.sdgindex.org/chapters/part-5-methods/)
- **Normalisation and aggregation:** `x' = 100·(x − lower)/(upper − lower)`, censored to [0, 100]. The *upper bound* is a target ("leave no one behind" absolute targets, science-based targets, or the average of the top 5 performers). The *lower bound* is the 2.5th percentile in early editions, later the average of the bottom 5 performers, so that outliers do not set the floor. Indicators are averaged arithmetically within each goal, and the 17 goals get **equal weights**. A country needs data for roughly ≥ 80% of indicators to be ranked. — [K] [Lafortune, Fuller, Moreno, Schmidt-Traub & Kroll (2018), SDG Index and Dashboards Detailed Methodological Paper](https://github.com/sdsna/2018GlobalIndex); [K] [Schmidt-Traub et al. (2017), *Nature Geoscience* 10:547–555](https://doi.org/10.1038/ngeo2985)
- **Dashboard (traffic lights):** each indicator gets green/yellow/orange/red from thresholds set by the authors. A goal's colour is the **average of the country's two worst-rated indicators** in that goal. This is deliberately non-compensatory: green requires both worst indicators to be green. Trend arrows (on track / moderately improving / stagnating / decreasing) compare recent annual growth with the rate needed to reach the green threshold by 2030. — [K] [Lafortune et al. 2018](https://github.com/sdsna/2018GlobalIndex); [K] [SDR Methods chapter](https://dashboards.sdgindex.org/chapters/part-5-methods/)

#### Social Progress Index (Social Progress Imperative)
- The index has 3 dimensions (Basic Human Needs; Foundations of Wellbeing; Opportunity), each with 4 components, for 12 in total. Each component has about 3–5 *outcome* indicators. Economic indicators (GDP) are deliberately left out, so that social progress can be compared *against* GDP. Indicators are scaled with "utopia/dystopia" goalposts. Component weights come from PCA/factor loadings (historically). Components are then averaged with equal weights. — [K] [Social Progress Imperative, methodology](https://www.socialprogress.org/)

#### OECD Better Life Index
- The index has 11 dimensions (housing, income, jobs, community, education, environment, civic engagement, health, life satisfaction, safety, work-life balance). Indicators are min–max normalised across OECD and partner countries and averaged within each dimension with equal weights. The OECD publishes **no official overall ranking**. Users set their own weights (0–5 per dimension) in an interactive tool. — [K] [OECD Better Life Index](https://www.oecdbetterlifeindex.org/)

#### Economist (EIU) Democracy Index
- The index uses 60 questions/indicators grouped into five categories: electoral process and pluralism; civil liberties; functioning of government; political participation; political culture. — [V] [Wikipedia – Economist Intelligence Unit](https://en.wikipedia.org/wiki/Economist_Intelligence_Unit)
- Indicators are mostly expert-scored 0 / 0.5 / 1, with public-opinion survey data where available. Each category is rescaled to 0–10, and the overall score is the simple average of the five. Regime types: full democracy > 8; flawed democracy 6–8; hybrid regime 4–6; authoritarian ≤ 4. Coding is by in-house analysts, and the full question-level data are not public. — [K] [EIU Democracy Index methodology appendix](https://www.eiu.com/n/campaigns/democracy-index-2024/)

#### V-Dem (Varieties of Democracy)
- V-Dem relies on many country experts. Its measurement model assumes **five or more coders per country-year-variable**. V-Dem gives indicators unique weights and combines them both additively and multiplicatively. — [V] [Lindberg et al., "The Methodology of Varieties of Democracy" (Coppedge)](https://sites.nd.edu/michael-coppedge/files/2019/07/LindbergEtalBMS2019.pdf); [V] [V-Dem Methodology v11.1](https://www.v-dem.net/static/website/img/refs/methodologyv111.pdf); [V] [Parliament of Canada "Measuring Democracy" (2024)](https://lop.parl.ca/staticfiles/PublicWebsite/Home/ResearchPublications/HillStudies/PDF/2024-03-E.pdf)
- **Bayesian ordinal IRT measurement model.** Experts' ordinal ratings (e.g., 0–4) are treated as noisy readings of a latent continuous trait. The model estimates expert-specific *thresholds*, which correct for scale-perception differences between experts, and *reliability*. Anchoring vignettes and bridge/lateral coders link experts across countries. Outputs are latent point estimates with credible intervals, built from posterior draws. — [K] [Pemstein et al., "The V-Dem Measurement Model", V-Dem Working Paper 21 (updated annually)](https://www.v-dem.net/media/publications/Working_Paper_21.pdf)
- **Aggregation into indices.** Electoral Democracy (polyarchy): `EDI = 0.5·(elected officials × clean elections × freedom of association × suffrage × freedom of expression) + 0.5·(1/8·elected officials + 1/4·clean elections + 1/4·assoc. + 1/8·suffrage + 1/4·expression)`. This is half multiplicative and half additive, a compromise on compensability. Liberal Democracy: `LDI = 0.25·EDI^1.585 + 0.25·LCI + 0.5·EDI^1.585·LCI`, where LCI is the liberal component index. Uncertainty is carried through the formulas by applying them to each posterior draw. — [K] [V-Dem Methodology / Codebook](https://www.v-dem.net/static/website/img/refs/methodologyv111.pdf)

#### World Bank Worldwide Governance Indicators (WGI)
- **Classic model (Kaufmann–Kraay–Mastruzzi).** An unobserved components model (UCM): each source k's rescaled score for country j is `y_jk = α_k + β_k (g_j + ε_jk)`. Here g_j ~ N(0,1) is latent governance and ε_jk ~ N(0, σ_k²) is source-specific error. The estimate of g_j is a weighted average of sources, with weights proportional to precision `1/σ_k²`, so noisier sources count less. Estimates are in standard-normal units (about −2.5 to +2.5) with a standard error for each country. The WGI also publishes **percentile ranks** with **90% confidence intervals**. Its guidance: differences whose intervals overlap should not be read as significant. — [K] [Kaufmann, Kraay & Mastruzzi (2010), "The Worldwide Governance Indicators: Methodology and Analytical Issues", WB Policy Research WP 5430](https://openknowledge.worldbank.org/handle/10986/3913)
- **2025 methodology revision (December 2025)**, documented in "The Worldwide Governance Indicators: Revised Methodology for Measuring Governance Using Perception Data". Changes:
  - adds an **absolute 0–100 governance score** anchored to fixed benchmark countries, published alongside the standard estimates;
  - changes the aggregation model so the **global average can change over time**; the old model fixed it at 0 every year, so only relative position was measured;
  - tightens data-source screening and adds new qualified sources, for **35 data sources** across the six dimensions (Voice & Accountability, Political Stability/Absence of Violence, Government Effectiveness, Regulatory Quality, Rule of Law, Control of Corruption);
  - realigns indicators with an institutional-functions framework;
  - recomputes the history back to 1996.
  The paper notes that its views are not necessarily endorsed by the Advisory Committee. — [V] [WGI 2025 Methodology Revision (PDF)](https://www.worldbank.org/content/dam/sites/govindicators/doc/The%20Worldwide%20Governance%20Indicators%202025%20Methodology%20Revision.pdf); [V] [WGI publication page](https://www.worldbank.org/en/publication/worldwide-governance-indicators); [V] [WDI series "Government Effectiveness – Governance score (0-100)", GOV_WGI_GE_SC](https://data.worldbank.org/indicator/GOV_WGI_GE_SC)
- The World Bank says the aggregate WGI scores are too coarse to guide specific reforms, and users should look at the disaggregated source indicators. — [V] [WGI publication page](https://www.worldbank.org/en/publication/worldwide-governance-indicators)

#### Global Peace Index (Institute for Economics & Peace)
- The index has 23 qualitative and quantitative indicators in three domains (Ongoing Domestic & International Conflict; Societal Safety & Security; Militarisation) and covers about 163 countries. Indicators are banded to 1–5, where lower is more peaceful, and weighted 1–5 by an expert panel. The overall score combines **internal peace (60%)** and **external peace (40%)**. Some indicators are EIU analyst scores, and missing data are imputed. — [K] [IEP Global Peace Index report, methodology annex](https://www.visionofhumanity.org/maps/)

#### World Happiness Report (WHR)
- The ranking uses the Gallup World Poll **Cantril ladder**, 0 (worst possible life) to 10 (best possible life), averaged over **3 years** (WHR 2025: 2022–2024; WHR 2026: 2023–2025, 147 countries). The authors say the 3-year average gives larger samples and more precise estimates, and it dampens one-off shocks. — [V] [WHR 2025 ch. 2](https://www.worldhappiness.report/ed/2025/caring-and-sharing-global-analysis-of-happiness-and-kindness/); [V] [WHR FAQ](https://www.worldhappiness.report/faq/); [V] [Gallup – WHR](https://www.gallup.com/analytics/349487/world-happiness-report.aspx)
- The **explanatory decomposition** is a pooled OLS regression on an unbalanced panel of national annual ladder means since 2005, with year fixed effects. Its six variables are log GDP per capita, social support, healthy life expectancy, freedom to make life choices, generosity and perceptions of corruption. The report notes that treating the mean ladder as average life satisfaction assumes the scale is **cardinal**. — [V] [WHR 2025 ch. 2](https://www.worldhappiness.report/ed/2025/caring-and-sharing-global-analysis-of-happiness-and-kindness/)
- **How to read the bar charts:** the ranking is the survey mean *only*. The six factors split each country's score into parts "explained" relative to **Dystopia**, a hypothetical country with the world's lowest value on every factor, plus "Dystopia + residual". Whiskers show 95% confidence intervals. About 1,000 respondents per country-year. — [K] [WHR Statistical Appendix / FAQ](https://www.worldhappiness.report/faq/)
- Critics argue the Cantril ladder wording primes respondents to think about wealth and power. — [V] [Nilsson et al., "The Cantril Ladder elicits thoughts about power and wealth" (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10834405/)

### Inferences
- The user's panel already holds the outputs of several of these indices. Putting V-Dem, EIU and WGI together in one KPI builds a composite of composites. These three are highly correlated, and WGI itself includes EIU and some V-Dem-type sources, so this double-counts "governance". Pick one per concept, or take their first principal component and report its loadings.
- **WGI series break:** the 2025 revision recalculated history to 1996. Mixing WGI data downloaded before and after December 2025 in one panel would create a break. Re-download the whole series, and choose explicitly between the old standard-normal estimate and the new 0–100 score. The old estimate is relative within each year; the new score is anchored.
- The WHR ladder is a single survey item with sampling error (CIs of roughly ±0.1–0.2 for typical samples [K]). Rank differences of a few places between neighbours are usually not significant.

### Gaps
- I could not re-open the 2025/2026 SDR methods page, so I have not confirmed the current lower-bound rule (2.5th percentile vs bottom-5 average) or the exact data-coverage threshold for ranking. Both come from earlier methodology papers [K].
- I could not verify whether the Social Progress Index changed its weighting (PCA) or aggregation in 2024–2026 editions.
- I could not confirm the GPI's current indicator count (23) and country count (163) for the 2025/2026 editions.
- I did not obtain the WGI 2025 benchmark countries or the exact 0–100 scaling formula; the search results did not include them.
- I could not confirm whether WHR 2025/2026 changed how it presents Dystopia, or the R² of the six-factor regression (historically about three-quarters of cross-country variance [K]).

---

## 4. Uncertainty and sensitivity analysis of rankings

### Takeaway
The standard method comes from Saisana, Saltelli & Tarantola (2005) and was adopted in the Handbook and in JRC audits:
1. Treat every modelling choice (imputation, normalisation, weights, aggregation, inclusion or exclusion of indicators) as an uncertain input.
2. Run Monte Carlo over those inputs.
3. Report each country's **median rank and a 90% (or 95%) rank interval**.
4. Use variance-based (Sobol) sensitivity indices to show which choice drives the uncertainty.

Statistical-model indices (WGI, V-Dem) give confidence or credible intervals directly.

### Cited Findings
- Saisana, Saltelli & Tarantola (2005), "Uncertainty and sensitivity analysis techniques as tools for the quality assessment of composite indicators", *JRSS Series A* 168(2):307–323. The paper argues that rankings depend on normalisation, weights and aggregation, and should be tested by Monte Carlo uncertainty analysis plus variance-based sensitivity analysis. — [V] [ResearchGate record](https://www.researchgate.net/publication/284100089_Uncertainty_and_sensitivity_analysis_as_tools_for_the_quality_assessment_of_composite_indicators); [V] [Tarantola, "State of the art on composite indicators"](https://www.uni-trier.de/fileadmin/fb4/projekte/SurveyStatisticsNet/KEI_UT_Tarantola.pdf)
- The first-order Sobol index `S_i = V[E(Y|X_i)]/V(Y)` gives the share of rank variance due to one input alone. The total index `S_Ti` adds that input's interactions. A new estimator for these indices was demonstrated on the e-Business Readiness composite indicator. — [V] [Saltelli et al., *Reliability Engineering & System Safety* (2005/6)](https://www.sciencedirect.com/science/article/abs/pii/S0951832005002243); formula [K] from the [Handbook, ch. 7](https://doi.org/10.1787/9789264043466-en)
- Paruolo, Saisana & Saltelli (2013) show how far nominal weights and indicator importance can diverge, and offer an importance measure for checking whether the index "means what it says". — [V] [JRSS A 176(3) PDF](https://www.andreasaltelli.eu/file/repository/rssa_1059.pdf)
- Høyland, Moene & Willumsen (2012) estimate rank uncertainty for the HDI and Doing Business with a Bayesian latent-variable model. Many countries' rank intervals span dozens of places. Their title calls this the "tyranny" of rankings. — [K] [Høyland, Moene & Willumsen (2012), "The tyranny of international index rankings", *Journal of Development Economics* 97(1):1–14](https://doi.org/10.1016/j.jdeveco.2011.01.007)
- WGI publishes 90% confidence intervals for percentile ranks and warns against over-interpreting small differences. V-Dem publishes credible intervals from posterior draws. — [K] [KKM 2010](https://openknowledge.worldbank.org/handle/10986/3913); [K] [V-Dem WP 21](https://www.v-dem.net/media/publications/Working_Paper_21.pdf)

**Worked Python example: Monte Carlo rank intervals (run in this session)**
```python
rng = np.random.default_rng(0)
Z  = pd.DataFrame(rng.normal(size=(8,4)), index=list("ABCDEFGH"))     # 8 countries x 4 indicators
mm = (Z - Z.min())/(Z.max() - Z.min())
ranks = []
for _ in range(2000):
    wt = rng.dirichlet(np.ones(4)*5)                    # random weights around equal (1/4 each)
    if rng.random() < 0.5:                              # random aggregation rule
        s = (mm*wt).sum(axis=1)                         # arithmetic
    else:
        s = np.exp((np.log(mm.clip(lower=0.01))*wt).sum(axis=1))   # geometric (floor avoids log 0)
    ranks.append(s.rank(ascending=False))
R = pd.concat(ranks, axis=1)
out = pd.DataFrame({"median": R.median(axis=1), "p05": R.quantile(.05, axis=1), "p95": R.quantile(.95, axis=1)})
# Output: B always rank 1; A, E, F share median 3 with 90% interval [2,4] -> not distinguishable
```
Extensions:
- add imputation (e.g., mean vs KNN), normalisation (min–max vs z vs rank) and "drop one indicator" as further random switches;
- for Sobol indices, use the `SALib` package (`SALib.sample.saltelli` / `SALib.analyze.sobol`) [K];
- for a simple "importance" check, compute R² of the index on each indicator, or the Pearson correlation of each indicator with the index.

### Inferences
- For the 5 KPIs: publish a median rank with a [p05, p95] interval for each country-year, and avoid the word "rank #k" when intervals overlap heavily. Compare years by the *change in score*, not the change in rank, because ranks shift when other countries move or the sample changes.
- A cheap robustness table goes a long way: equal vs PCA weights × arithmetic vs geometric × min–max vs z, plus Spearman ρ between the resulting rankings.

### Gaps
- I could not open the full text of Saisana et al. (2005), so the volume and page numbers are [K]. The default use of 90% vs 95% rank intervals varies between JRC audits.

---

## 5. Known criticisms of composite indices

### Takeaway
The criticisms recur across the literature:
- weights are arbitrary, and they imply trade-offs between dimensions that nobody would sign off if stated openly (Ravallion's "mashup" critique);
- correlated components cause double counting or redundancy (HDI vs income alone);
- data imputation inside indices can create "data" where there are none;
- rank volatility and false precision;
- the broader "beyond GDP" debate over whether a single number should replace a dashboard at all.

### Cited Findings
- **Ravallion, "Mashup Indices of Development"** (WB Policy Research WP 5432, Sept 2010; published in *World Bank Research Observer*, doi 10.1093/wbro/lkr009, 2012). Theory and practice give little guidance on how to build "mashup" indices. They appeal because they collapse many dimensions into one clean ranking and may reduce worries about measurement error in single components. Ravallion's recommendations include being explicit about trade-offs, testing robustness, and publishing the components (dashboards). — [V] [WPS 5432](https://documents1.worldbank.org/curated/en/454791468329342000/pdf/WPS5432.pdf); [V] [SSRN abstract](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1683903); [V] [scispace record with DOI](https://scispace.com/papers/mashup-indices-of-development-4xffyilizm); [V] [World Bank Research Digest Fall 2010](https://openknowledge.worldbank.org/server/api/core/bitstreams/4aa0fe2c-3641-588e-926d-07058aec83d2/content). The recommendations are [K].
- **"Troubling tradeoffs in the HDI"** (Ravallion, WP 5484, 2010; *Journal of Development Economics* 99(2), 2012). The post-2010 geometric HDI implies a monetary value of an extra year of life expectancy that rises steeply with income. Ravallion reports implied values of well under $1 per year of life in the poorest countries versus thousands of dollars in rich ones. He calls this an ethically troubling, hidden trade-off. — [V] existence of WP 5484 via [RePEc author page](https://ideas.repec.org/e/pra29.html); content [K] [Ravallion (2012), JDE 99(2):201–209](https://doi.org/10.1016/j.jdeveco.2012.01.007)
- **Redundancy:** early critics found the HDI highly correlated with its income component, raising the question of whether it adds information beyond GDP. — [K] [McGillivray (1991), "The Human Development Index: yet another redundant composite development indicator?", *World Development* 19(10)](https://doi.org/10.1016/0305-750X(91)90127-V); [K] [Kelley (1991), "The Human Development Index: 'Handle with care'", *Population and Development Review* 17(2)](https://doi.org/10.2307/1973733)
- **Weights:** rankings can depend heavily on normalisation, weights and aggregation, which motivated the uncertainty analysis in section 4. Nominal weights also differ from effective importance. — [V] [Saisana et al. 2005 (ResearchGate)](https://www.researchgate.net/publication/4993166_Uncertainty_and_Sensitivity_Techniques_as_Tools_for_the_Analysis_and_Validation_of_Composite_Indicators); [V] [Paruolo et al. 2013](https://www.andreasaltelli.eu/file/repository/rssa_1059.pdf); [V] [Greco et al. 2019](https://pure.port.ac.uk/ws/files/8559735/On_the_methodological_framework_of_composite_indices.pdf)
- **Comparability over time:** editions change indicators and methods. SDSN states that SDG Index scores and ranks cannot be compared across editions. UNDP recomputes HDI back-series in every report. WGI recomputed its history to 1996 in 2025. — [V] [SDR Methods](https://dashboards.sdgindex.org/chapters/part-5-methods/); [V] [WGI publication page](https://www.worldbank.org/en/publication/worldwide-governance-indicators)
- **"Beyond GDP":** the Stiglitz–Sen–Fitoussi Commission (2009) recommended dashboards of well-being measures, together with subjective well-being and sustainability measures, over a single summary index. That recommendation shaped the OECD's How's Life? framework and Better Life Index. — [K] [Report by the Commission on the Measurement of Economic Performance and Social Progress (2009)](https://ec.europa.eu/eurostat/documents/8131721/8131772/Stiglitz-Sen-Fitoussi-Commission-report.pdf)
- **Subjective measures:** the Cantril ladder wording may push respondents to think about wealth and power, which affects what "happiness rankings" capture. — [V] [PMC10834405](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10834405/)
- **Ranking-format criticism of the Doing Business successor:** critics argue B-READY keeps the ranking format that made Doing Business influential, and they question relying on a few lawyers to assess labour institutions. — [V] [Equal Times](https://www.equaltimes.org/the-b-ready-index-the-world-bank-s?lang=en)

### Inferences
- **Imputation risk in the user's panel:** suicide, happiness and public-spending series have gaps, especially for small states and early years. If a KPI imputes these, record an "imputed share" for each country-year and exclude or flag scores where, say, > 20–30% of inputs are imputed. This mirrors the SDG Index's ~80% coverage rule [K].
- Publish the dashboard of components next to every KPI, and say in plain words what trade-off the weights imply (e.g., "1 point of governance = 1 point of health").

### Gaps
- I could not open Ravallion's full texts, so the exact implied value-of-life figures are not cited and would need checking.
- I did not find a quantitative survey of how much imputation major indices use. GPI, SDG Index and SPI all document imputation, but I could not fetch the specific shares.

---

## 6. Other benchmarking techniques: distance-to-frontier, peer groups, percentile ranks, z-score and traffic-light dashboards

### Takeaway
Simpler benchmarks are often more honest than a full composite:
- **Distance-to-frontier:** the Doing Business score, used until DB2020. Doing Business was discontinued in 2021 over data irregularities and replaced by B-READY in October 2024.
- **Percentile ranks:** as WGI does.
- **Peer-group comparisons:** by income group, region, or nearest neighbours.
- **Threshold traffic-light dashboards:** the SDG Dashboard's "two worst indicators" rule.

### Cited Findings
- **Distance to frontier / "ease of doing business score".** For each indicator, `score = 100·(worst − y)/(worst − frontier)` for lower-is-better indicators, or `100·(y − worst)/(frontier − worst)` otherwise. The frontier is the best performance observed (over the 2005+ window), and "worst" is a fixed low percentile or bound set to limit outliers. Topic scores are simple averages, and the overall ranking sorts the average of the 10 topic scores. The DB2016–DB2018 editions renamed DTF to "ease of doing business score". — [K] [World Bank, Doing Business 2020, Methodology chapter](https://openknowledge.worldbank.org/handle/10986/32436)
- **Discontinuation.** Data irregularities came to light in 2020 and the World Bank paused the report. After a series of audits and reviews, including an external investigation by the law firm WilmerHale, it discontinued Doing Business in **September 2021**. The reviews reported that data for China (DB2018), Saudi Arabia, the UAE and Azerbaijan (DB2020) had been manipulated, with China's case involving pressure from senior management. — [V] [World Bank Group Timeline](https://timeline.worldbank.org/en/timeline/eventdetail/f4c63080-3245-4a4c-b370-d560df1e6291); [V] [VCI Legal summary](https://vci-legal.com/news/world-bank-cancels-doing-business-report)
- **B-READY (Business Ready)** is the successor. Its first edition came out on 3 October 2024, covering about 50 economies. It has 3 pillars (regulatory framework, public services, operational efficiency) across 10 topics in the life cycle of a firm, and many more indicators than Doing Business. It mixes expert questionnaires with firm surveys and publishes full data and a reproducibility package. — [V] [Site Selection Magazine](https://siteselection.com/new-world-bank-business-ready-rankings-offer-a-more-transparent-version-of-doing-business/); [V] [Pardee Wiki](https://pardeewiki.du.edu/index.php?title=Business_Ready_%28B-READY%29%2C_World_Bank); [V] [China Briefing](https://www.china-briefing.com/news/how-china-is-adapting-to-the-world-banks-b-ready-business-environment-benchmark/). *Conflict:* one planning source had targeted spring 2024 for release, and sources disagree on whether B-READY "ranks". It reports pillar scores (0–100) and quintile groupings, which critics see as a de facto ranking. — [V] [Equal Times](https://www.equaltimes.org/the-b-ready-index-the-world-bank-s?lang=en)
- **Percentile ranks with intervals:** WGI reports each country's percentile rank among all countries (0 = lowest, 100 = highest) with 90% confidence bands. — [K] [KKM 2010](https://openknowledge.worldbank.org/handle/10986/3913)
- **Traffic-light dashboards:** the SDG Dashboard sets green/yellow/orange/red thresholds for each indicator and rates a goal by the average of its two worst indicators. This keeps the *dashboard* non-compensatory while the *index* stays compensatory. — [K] [Lafortune et al. 2018](https://github.com/sdsna/2018GlobalIndex)

**Worked Python snippets for the user's panel**
```python
# panel: long df with columns iso3, year, indicator, value ; wide per year:
wide = panel.pivot_table(index=["iso3","year"], columns="indicator", values="value")

# 1) Percentile rank within each year (robust, easy to explain)
pct = wide.groupby(level="year").rank(pct=True) * 100

# 2) Peer-group z-score: compare each country only with its income group (or region) in the same year
#    meta: df indexed by iso3 with an 'income_group' column (e.g. World Bank classification)
grp = meta.reindex(wide.index.get_level_values("iso3"))["income_group"].values
z_peer = wide.groupby([wide.index.get_level_values("year"), grp]).transform(lambda s: (s - s.mean())/s.std())

# 3) Distance to frontier with fixed bounds over the whole panel (comparable over time)
def dtf(s, higher_is_better=True, lo_q=0.05, hi_q=0.95):
    worst, best = (s.quantile(lo_q), s.quantile(hi_q)) if higher_is_better else (s.quantile(hi_q), s.quantile(lo_q))
    return (100 * (s - worst) / (best - worst)).clip(0, 100)

# 4) SDG-style traffic light: thresholds per indicator, goal colour = mean of two worst
def light(score, g=80, y=60, o=40):      # on a 0-100 'distance to target' score
    return 3 if score >= g else 2 if score >= y else 1 if score >= o else 0   # 3=green ... 0=red
def goal_colour(scores):                 # scores: indicator scores of one country for one goal
    worst2 = sorted(light(s) for s in scores.dropna())[:2]
    return int(np.floor(np.mean(worst2)))  # floor = conservative rounding (author's choice, not SDSN's)
```

### Inferences
- For a beginner–intermediate project, a good default is a **dashboard first, composite second**:
  1. per-indicator percentile ranks or fixed-goalpost scores by year;
  2. a peer-group view (income group/region);
  3. only then the composite KPI, with a rank interval from section 4.
- Doing Business is the textbook case for **governance of the index itself**: documented data lineage, versioned methodology, a public reproducibility package and separation from political pressure. The user's notebook can copy this by freezing a methodology version per KPI and logging any changes.

### Gaps
- I could not fetch the DB2020 methodology to confirm the exact "worst" bound rule for each indicator. The DTF formula itself is standard [K].
- I could not verify B-READY's 2025/2026 coverage (number of economies) or whether later editions add an aggregate ranking.
- The `goal_colour` rounding in the snippet is an illustrative choice. I could not confirm SDSN's exact rounding rule for the "average of two worst" in the current edition.
