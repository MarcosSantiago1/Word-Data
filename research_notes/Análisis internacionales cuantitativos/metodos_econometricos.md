# Quantitative methods for cross-country (international comparative) statistical analysis

Scope: econometric and statistical methods for a country-year panel of about 217 countries, 2000-2024, joined by ISO3 (World Bank, WHO, V-Dem, WHR, ILOSTAT). The project already runs cross-sectional OLS (happiness on log GDP pc + life expectancy + control of corruption + health spending + Gini, n≈119), a logit for democracy, and a fixed-effects panel.

Note on sourcing: research ran under a budget of about 18 tool calls, mostly web searches whose results are abstracts, repository records and secondary documentation, not full texts. Items marked **[background, not verified this session]** come from standard textbook knowledge. They are not tied to a fetched source and are listed so the report writer can decide whether to keep them. The official linearmodels documentation host (bashtage.github.io) was blocked by the session's network settings, so the Python API details are not confirmed against the official docs.

---

## 1. Cross-sectional vs. pooled vs. panel designs (FE, RE, Hausman, two-way FE, robust/clustered/Driscoll-Kraay SEs, dynamic panels)

### Takeaway
With a country-year panel, the default workhorse is two-way fixed effects (country + year) with standard errors clustered by country. A cross-section like the n≈119 happiness OLS shows only associations between countries. TSCS data with many years and few units motivated Beck & Katz's panel-corrected SEs. Dynamic models with a lagged dependent variable bring in Nickell bias and the GMM "too many instruments" problem, so treat GMM as advanced.

### Cited Findings
- Beck & Katz (1995, APSR 89(3):634-647), "What To Do (and Not To Do) with Time-Series Cross-Section Data", show that the Parks generalized least squares (FGLS) approach "produces standard errors that lead to extreme overconfidence, often underestimating variability by 50% or more". They propose "panel-corrected standard errors" (PCSE), which perform well in Monte Carlo analysis. Their analysis targets "temporally dominated" TSCS (few units, relatively long T). — [Cambridge/APSR abstract](https://www.cambridge.org/core/journals/american-political-science-review/article/abs/what-to-do-and-not-to-do-with-timeseries-crosssection-data/0E778B85AB008DAF8D13E0AC63505E37); [Caltech PDF](https://authors.library.caltech.edu/records/5q5x8-v1537/files/beck+katz95.pdf?download=1)
- Wilson & Butler (2007, Political Analysis 15(2):101-123), "A Lot More to Do", replicate eight TSCS papers in prominent journals. They find that "simple alternative specifications often lead to drastically different conclusions" and that Beck-Katz practice had hardened into an orthodoxy. — [WUSTL profile](https://profiles.wustl.edu/en/publications/a-lot-more-to-do-the-sensitivity-of-time-series-cross-section-ana/); [IDEAS](https://ideas.repec.org/a/cup/polals/v15y2007i02p101-123_00.html)
- In Python's `linearmodels`, `PanelOLS` supports entity and time effects (`EntityEffects`, `TimeEffects` in the formula) and clustered covariance via `fit(cov_type='clustered', cluster_entity=True)`. — [linearmodels PyPI 4.15](https://pypi.org/project/linearmodels/4.15/); [PyPI 3.0](https://pypi.org/project/linearmodels/3.0)
- Driscoll-Kraay SEs, which are robust to cross-sectional dependence plus serial correlation, are reported as available in linearmodels as a kernel covariance, e.g. `fit(cov_type="kernel", kernel="bartlett", bandwidth=5)`. This comes from a secondary skill page; the official docs could not be fetched to confirm it. — [secondary: claudskills linearmodels page](https://claudskills.com/skills/linearmodels/SKILL.md)
- Cluster-robust SEs presume many clusters. Standard asymptotic tests "can over-reject with few (5-30) clusters". Cameron, Gelbach & Miller (2008, REStat 90:417-427) propose the wild cluster bootstrap. — [NBER t0344 / CGM](https://www.nber.org/papers/t0344.pdf)
- The wild cluster bootstrap also has limits. MacKinnon & Webb find that t-tests and wild cluster bootstrap tests "fail when the number of treated clusters is small", and other work reports poor performance with fewer than about 11 clusters (Webb's 2014 modification addresses ≤12 clusters). — [QED WP 1364](https://ageconsearch.umn.edu/record/274690/files/qed_wp_1364.pdf); [QED WP 1315](https://ageconsearch.umn.edu/record/274640/files/qed_wp_1315.pdf)
- Dynamic panels: FE with a lagged dependent variable is biased downward (ρ̂ too low) because of Nickell bias, "especially when T is small". Difference/System GMM (Arellano-Bond / Blundell-Bond) instead use lagged levels as instruments. With large T, the instrument count "can explode". A suggested diagnostic is that a Difference-GMM ρ much lower than System-GMM ρ hints at weak instruments. — [PanelBox GMM docs (secondary)](https://panelbox.readthedocs.io/en/latest/user-guide/gmm/)
- Roodman (2009, Oxford Bulletin of Economics and Statistics 71(1):135-158), "A Note on the Theme of Too Many Instruments": Difference/System GMM can generate many instruments, which "overfit endogenous variables" and also weaken the Hansen J test of joint validity. This happens "by default" in common software. Re-examining Forbes (2000) on inequality and growth and Levine, Loayza & Beck (2000) on finance and growth, he finds results that look driven by previously undetected endogeneity. He recommends reporting the instrument count and testing robustness to reducing it. — [CGD WP 125 PDF](https://www.cgdev.org/sites/default/files/14256_file_Instruments.pdf); [IDEAS](https://ideas.repec.org/p/cgd/wpaper/125.html)
- **[background, not verified this session]** Nickell (1981) bias in FE with a lagged dependent variable is of order 1/T. With T≈25 (2000-2024) it is modest but non-zero, so a lagged-DV FE model is often acceptable when T is around 20-30 or more.
- **[background, not verified this session]** The Hausman test compares FE and RE. Rejection means RE's assumption that country effects are uncorrelated with regressors fails, so FE is preferred. In cross-country work it is almost always rejected. Many applied researchers skip RE or use the Mundlak / "within-between" (correlated random effects) approach, which adds country means of time-varying X to an RE model. linearmodels has `RandomEffects`, `BetweenOLS` and `FirstDifferenceOLS`; the classic Hausman statistic has to be computed by hand from FE and RE coefficient vectors.
- **[background, not verified this session]** HC3 heteroskedasticity-robust SEs (MacKinnon & White 1985; recommended for small n by Long & Ervin 2000, "Using heteroscedasticity consistent standard errors in the linear regression model", American Statistician) are available in statsmodels via `.fit(cov_type='HC3')`. They suit the n≈119 cross-section. A targeted search did not return Long & Ervin.

### Inferences
- For the user's ~217 × 25 panel, N is large and T moderate, which is the "panel" case, not Beck-Katz's "temporally dominated TSCS" case. Clustering by country (217 clusters) is reliable. PCSE and FGLS-Parks matter less. Driscoll-Kraay is a sensible robustness check for shocks common across countries (2008-09, COVID-2020).
- Country FE soak up slow-moving variables (institutions, culture, geography). Coefficients on near-constant regressors such as V-Dem democracy indices or Gini will be imprecise and identified only from within-country change. Beginners often misread a null FE coefficient as "no effect" when it really reflects little within-country variation. Report the within-SD of each regressor.
- Year FE are needed with 2000-2024 data because global shocks (2008, 2020) would otherwise confound trends.
- Treat Arellano-Bond/System GMM as advanced. With T≈25, FE with a lagged DV plus clustered SEs is a defensible and simpler choice.

### Gaps
- Could not fetch the official linearmodels docs (bashtage.github.io blocked) to confirm the `cov_type='kernel'` / `cluster_time` parameter names and defaults, or whether a built-in Hausman test exists.
- Did not retrieve Long & Ervin (2000) or the statsmodels HC3 documentation directly.
- No Python-native, well-maintained Arellano-Bond implementation was verified. PanelBox appeared in search, but its maturity was not assessed (pydynpd is another candidate, unverified).

---

## 2. Causal inference designs across countries (DiD and staggered adoption, synthetic control, IV, RDD, event studies)

### Takeaway
Since about 2020 the DiD literature has shown that the classic two-way FE "DiD" regression is biased when countries adopt a policy at different times and effects vary. Use Callaway-Sant'Anna-type estimators and event-study plots instead. Synthetic control (Abadie) is the standard design for one treated country, but replications show it can be fragile. Cross-country IV, with Acemoglu-Johnson-Robinson's settler mortality as the textbook case, rests on contestable instrument data and exclusion restrictions.

### Cited Findings
**Difference-in-differences (modern literature)**
- Roth, Sant'Anna, Bilinski & Poe (2023, Journal of Econometrics 235(2):2218-2244), "What's Trending in Difference-in-Differences?", organize the recent literature as relaxations of the canonical 2×2 DiD along three lines: (i) multiple periods with staggered timing, (ii) violations of parallel trends, (iii) alternative inference frameworks. — [arXiv 2201.01194](https://arxiv.org/pdf/2201.01194); [IDEAS](https://ideas.repec.org:443/a/eee/econom/v235y2023i2p2218-2244.html)
- Goodman-Bacon (2021): the TWFE DiD estimate is a weighted average of all 2×2 DiDs (the "Bacon decomposition"). — [Sant'Anna NY Fed slides, 2023](https://psantanna.com/files/nyfed.pdf)
- Under staggered timing with heterogeneous or dynamic effects, TWFE uses already-treated units as controls for later-treated units. These "forbidden comparisons" can get negative weights and bias the estimate. — [moderndid docs](https://moderndid.readthedocs.io/en/stable/user_guide/example_staggered_did.html); [diff-diff CallawaySantAnna docs](https://diff-diff.readthedocs.io/en/stable/api/_autosummary/diff_diff.CallawaySantAnna.html)
- Callaway & Sant'Anna (2021, Journal of Econometrics 225(2):200-230) estimate group-time effects ATT(g,t) using only never-treated or not-yet-treated units as controls, then aggregate them into event-study, group, calendar-time or overall effects. Pre-treatment ATT(g,t) near zero supports parallel trends. — [diff-diff docs](https://diff-diff.readthedocs.io/en/stable/api/_autosummary/diff_diff.CallawaySantAnna.html); [moderndid docs](https://moderndid.readthedocs.io/en/stable/user_guide/example_staggered_did.html)
- Modern estimators differ in which units serve as "clean controls" (never-treated, not-yet-treated, or last-treated) and in how many pre-periods they use. — [World Bank Development Impact blog](https://blogs.worldbank.org/en/impactevaluations/new-synthesis-and-key-lessons-recent-difference-differences-literature)
- Python implementations exist: `moderndid` and `diff-diff` (both document a CallawaySantAnna estimator). — [moderndid](https://moderndid.readthedocs.io/en/stable/user_guide/example_staggered_did.html); [diff-diff](https://diff-diff.readthedocs.io/en/stable/api/_autosummary/diff_diff.CallawaySantAnna.html); tutorial: [Mendez, Python DiD](https://carlos-mendez.rbind.io/post/python_did/)

**Synthetic control**
- Abadie (2021, Journal of Economic Literature 59(2):391-425), "Using Synthetic Controls: Feasibility, Data Requirements, and Methodological Aspects", gives practical guidance. It covers when synthetic control is reliable and when it may fail, contextual and data requirements, and robustness/diagnostic checks. Replication files are on openICPSR. — [IDEAS/JEL](https://ideas.repec.org/a/aea/jeclit/v59y2021i2p391-425.html); [NBER SI 2021 PDF](https://conference.nber.org/confer/2021/SI2021/Abadie_2021.pdf); [openICPSR](https://www.openicpsr.org/openicpsr/project/119933/view)
- Abadie, Diamond & Hainmueller (2015, AJPS 59(2):495-510), "Comparative Politics and the Synthetic Control Method", estimate that German reunification reduced West German GDP per capita by about $1,600 per year over 1990-2003. Synthetic West Germany is built from Austria, Japan, the Netherlands, Switzerland and the USA; the other 11 of 16 donor countries get zero weight. — [HKS record](https://www.hks.harvard.edu/publications/comparative-politics-and-synthetic-control-method); [mlsynth replication docs](https://mlsynth.readthedocs.io/en/latest/replications/vanillasc.html); [arXiv Bayesian SC reanalysis](https://arxiv.org/pdf/1910.06106)
- An I4R replication (Francis) calls the German result fragile. It depends on excluding poorly fitting donor countries. There is a mismatch between nominal-GDP data and the reported real-dollar figures; with the reported series, results stay significant only at p<0.10. Results are sensitive to the base year, and in a broader placebo exercise "only 8 out of 44 synthetic controls generate treatment effects with p < 0.10". — [IDEAS I4R DP 271](https://ideas.repec.org/p/zbw/i4rdps/271.html)
- The original synthetic control estimate lacked formal statistical inference; inference relies on placebo/permutation tests. — [arXiv 2108.13935](https://arxiv.org/pdf/2108.13935)
- Abadie & Gardeazabal (2003) on Basque terrorism is the first synthetic control application and is replicated in the same mlsynth docs. — [mlsynth replications](https://mlsynth.readthedocs.io/en/latest/replications/vanillasc.html)
- **[background, not verified this session]** Abadie & Gardeazabal (2003, AER) estimate roughly a 10% gap in Basque per capita GDP relative to a synthetic Basque Country built from other Spanish regions (mainly Catalonia and Madrid).

**Instrumental variables (AJR settler mortality)**
- Albouy's critique of Acemoglu, Johnson & Robinson (2001) raises three issues: high-mortality outliers; data for much of Latin America and Africa that is constructed or borrowed (he proposes dropping it); and the use of "campaign" (soldier) mortality, for which he proposes a dummy. AJR reply (NBER w16966; AER 2012) that limiting outliers "has no impact on our substantive results and if anything significantly strengthens them", that dropping Latin American and African data is arbitrary, and that the campaign dummy contradicts the historical record. — [NBER w16966](https://www.nber.org/papers/w16966); [AJR reply PDF](https://baselinescenario.com/wp-content/uploads/2009/09/reply-to-albouy-oct-2008-final-sept-2009.pdf)
- Auer (2007, SNB WP 2007-09) instruments settler mortality with a geographic disease model. He concludes that AJR's results reflect the early institution-building hypothesis "rather than measurement error". — [SNB WP 2007-09](https://snb.ch/en/mmr/papers/id/working_paper_2007_09)
- **[background, not verified this session]** Other common critiques of AJR: the exclusion restriction may fail because settler mortality could affect income today through disease environment or human capital (settlers brought education), not only through institutions (Glaeser et al. 2004, "Do Institutions Cause Growth?"). The first stage weakens once Albouy's corrections are applied.

**Event studies and RDD**
- Event-study plots (leads and lags around adoption) are the standard diagnostic for pre-trends, and Callaway-Sant'Anna aggregates naturally into event-time effects. — [diff-diff docs](https://diff-diff.readthedocs.io/en/stable/api/_autosummary/diff_diff.CallawaySantAnna.html); [eventstudytools explainer](https://www.eventstudytools.com/difference-in-differences-event-study)
- **[background, not verified this session]** Regression discontinuity is rarely possible in country-year data because few country-level policies switch on at a sharp numeric threshold. Exceptions include aid-eligibility income thresholds (e.g. IDA's GNI-per-capita cutoff) and close elections within countries. Most RDD work is subnational.

### Inferences
- For the user's data, candidate DiD questions are policies adopted by countries in different years (e.g. universal health coverage reforms, democratic transitions coded from V-Dem). These are staggered adoptions, so a plain `PanelOLS` with `EntityEffects + TimeEffects` and a treatment dummy is exactly the setup the modern literature warns about. Use Callaway-Sant'Anna or at least show a Bacon decomposition.
- Synthetic control fits single-country shocks visible in the panel (e.g. a specific country's crisis or reform). The German reunification replication shows the need to report donor weights, pre-period fit (RMSPE), placebo-in-space tests, and sensitivity to donor-pool choices.
- Cross-country IV is a classic but heavily contested design. Beginners should present IV mainly to show why identification is hard, not as a definitive estimate.

### Gaps
- Did not fetch the Callaway-Sant'Anna paper or the Goodman-Bacon paper directly. Details come from software documentation and slides.
- Did not retrieve Albouy's own text (AER 2012 comment) or an independent verdict on the Albouy-AJR debate.
- No verified source on the Basque 10% figure in this session.
- Other modern estimators (Sun & Abraham 2021, de Chaisemartin & D'Haultfœuille 2020, Borusyak-Jaravel-Spiess imputation, synthetic DiD by Arkhangelsky et al. 2021) were not verified this session but belong in the same literature.

---

## 3. Multilevel/hierarchical models and the small-number-of-countries problem

### Takeaway
Multilevel models (individuals in countries, e.g. Gallup World Poll / WVS microdata) estimate individual-level effects well. With the usual ~30 countries, country-level coefficients and cross-level interactions are unreliable (Bryan & Jenkins 2016). Recommendations for the minimum number of countries range from about 15 to 50 depending on model complexity.

### Cited Findings
- Bryan & Jenkins (2016, European Sociological Review 32(1):3-22), "Multilevel Modelling of Country Effects: A Cautionary Tale", use Monte Carlo simulation of multilevel linear and logit models. With many individuals per country but few countries, "analysts can reliably estimate individual-level effects but estimates of parameters summarising country effects are likely to be unreliable". Multilevel modelling "is no panacea". — [LSE Research Online](https://researchonline.lse.ac.uk/id/eprint/61357); [White Rose eprint](https://eprints.whiterose.ac.uk/93577/); [Essex repository](https://repository.essex.ac.uk/13410/)
- Typical multi-country survey datasets have about 30 countries, and usable numbers can be lower because of missing data. Later work notes that "there are still no clear rules of thumb regarding the minimum number of countries" and that recommendations range from 15 to 50 countries depending on model complexity. — [SSOAR record](https://www.ssoar.info/ssoar/handle/document/77112); [IFS Jenkins slides](https://ifs.org.uk/sites/default/files/output_url_files/Jenkins%252520slides.pdf)
- **[background, not verified this session]** Bryan & Jenkins recommend a simpler two-step alternative: estimate country-specific intercepts or slopes, then regress them on country characteristics. With few countries, Bayesian estimation or small-sample corrections (REML with Kenward-Roger df) is preferable. In Python, `statsmodels.MixedLM` fits linear random-intercept and random-slope models. Multilevel logit is better done in R (lme4) or with Bayesian tools (PyMC, bambi).

### Inferences
- The user's data are country-level aggregates, e.g. WHR's national ladder score, which is itself a Gallup country average. The design is ecological and multilevel models do not apply. To study individual happiness against country-level GDP or governance, the user would need Gallup World Poll microdata (licensed) or WVS/EVS microdata (free). With WVS waves (~60-90 countries) the country count is better than in the European surveys Bryan & Jenkins discuss.
- Small-N concerns also apply to the user's n≈119 OLS: five regressors are fine, but each extra governance index uses up degrees of freedom and adds collinearity.

### Gaps
- Did not fetch the Bryan & Jenkins full text for its exact simulation thresholds (e.g. performance at 10/20/30/50 countries).
- Did not verify statsmodels MixedLM documentation.

---

## 4. Specific pitfalls (endogeneity, OVB, multicollinearity of governance indices, Galton's problem, ecological fallacy, MNAR and imputation, outliers, PPP vs. market rates, logs, nonstationarity)

### Takeaway
Cross-country regressions face a set of known problems: reverse causality (e.g. GDP ↔ governance), highly collinear and perception-based governance indicators, spatial diffusion (Galton's problem), non-random missingness concentrated in poor or fragile states, and results driven by a few influential countries. Each has a standard remedy: lags plus FE or causal designs, composite indices or one indicator at a time, spatial diagnostics, Amelia-style multiple imputation for TSCS, and leave-one-out/influence diagnostics.

### Cited Findings
**Governance indices: collinearity and perception bias**
- Knack & Langbein (2010) use factor analysis on the six Worldwide Governance Indicators and find they "appear to be measuring the same broad concept" rather than six distinct dimensions. Kaufmann, Kraay & Mastruzzi dispute this. — [World Bank response](https://www.worldbank.org/content/dam/sites/govindicators/doc/KKMResponseEJDR2Final.pdf); [World Bank OKR](https://openknowledge.worldbank.org/entities/publication/1a3095cd-1ffa-5bf8-92c2-29ef82d8b993)
- Thomas (2010, European Journal of Development Research 22(1):31-54) questions the WGI's construct validity, asking whether researchers rely "on wrong data, rather than poor data". KKM reply that construct validity "is not a useful tool" for assessing the WGI. — [IDEAS](https://ideas.repec.org/a/pal/eurjdr/v22y2010i1p31-54.html); [World Bank response](https://www.worldbank.org/content/dam/sites/govindicators/doc/ResponseKL.pdf)
- Kurtz & Schrank (2007) argue the WGI are largely perceptual, so a strong economy can produce responses that affirm good governance. That is reverse causality built into the measure. — cited in [World Bank OKR / Knack-Langbein](https://openknowledge.worldbank.org/entities/publication/1a3095cd-1ffa-5bf8-92c2-29ef82d8b993)

**Galton's problem / spatial dependence**
- Galton's problem: observed cross-unit correlations may come from diffusion between units, not independent processes. Ignoring diffusion can overstate domestic determinants. — [V-Dem WP 119](https://www.v-dem.Net/media/publications/wp_119_final.pdf)
- Gleditsch & Ward (2006, International Organization) find that "international factors can exert a strong influence on the prospects for transitions to democracy" and that spatial clustering of democracy cannot be explained by domestic factors alone. — [PRIO record](https://www.prio.org/Publications/Publication/?x=3501)
- Ward & Gleditsch, *Spatial Regression Models* (2008), cover spatial lag and spatial error models with a democracy-development example. They treat spatial association as substantive, not a nuisance; Moran's I on residuals is the standard diagnostic. — [SAGE chapter PDF](https://in.sagepub.com/sites/default/files/upm-assets/21130_book_item_21130.pdf)
- Jahn (2006, International Organization) argues that many globalization/welfare-state studies do not adequately address Galton's problem. — [Cambridge record](https://resolve.cambridge.org/core/journals/international-organization/article/globalization-as-galtons-problem-the-missing-link-in-the-analysis-of-diffusion-patterns-in-welfare-state-development/A8268DB74C60F66EF52F061E197E70A9)

**Missing data in TSCS**
- Honaker & King (2010, AJPS 54(2):561-581), "What to Do About Missing Values in Time-Series Cross-Section Data", show that the best general imputation methods "work poorly with the time-series cross-section data structures common in these fields". They develop an MI model allowing "smooth time trends, shifts across cross-sectional units, and correlations over time and space", plus priors on individual missing cells from area-studies experts. — [King's site](https://gking.harvard.edu/publication/what-to-do-about-missing-values-in-time-series-cross-section-data/); [Harvard DASH PDF](https://dash.harvard.edu/bitstream/1/4100248/2/Honaker_MissingValues.pdf)
- Amelia II (Honaker, King & Blackwell, Journal of Statistical Software 45(7), 2011) implements this in R for cross-sectional data, single time series, or TSCS. — [JSS](https://www.jstatsoft.org/article/view/v045i07); [Amelia page](https://gking.harvard.edu/amelia/); [CRAN vignette](https://cran.r-project.org/web/packages/Amelia/vignettes/intro-mi.html)

**Outliers / influential countries**
- In the AJR-Albouy exchange, much of the dispute is about high-mortality outlier observations and which countries are included. Sample composition is a first-order issue in cross-country work. — [NBER w16966](https://www.nber.org/papers/w16966)
- The German synthetic control result is sensitive to which donor countries are excluded. — [I4R DP 271](https://ideas.repec.org/p/zbw/i4rdps/271.html)

**Background on remaining pitfalls [background, not verified this session]**
- *Endogeneity/reverse causality:* happiness ↔ health and GDP ↔ governance. Lagging regressors does not solve this (it shifts the problem when X is persistent). FE removes only time-invariant confounding.
- *Ecological fallacy* (Robinson 1950): country-level correlations, such as WHR ladder vs. GDP, do not imply the same relationship for individuals.
- *MNAR:* World Bank/WHO/ILOSTAT gaps cluster in fragile, conflict-affected and small states (e.g. South Sudan, Somalia, Venezuela after ~2014, North Korea), so listwise deletion pushes samples toward richer and more stable countries. MI (Amelia, or `IterativeImputer` / MICE in `statsmodels.imputation.mice`) assumes MAR, not MNAR, so MNAR calls for sensitivity analysis.
- *PPP vs. market exchange rates:* cross-country living-standard comparisons should use GDP per capita in PPP constant international dollars (World Bank `NY.GDP.PCAP.PP.KD`) rather than market-rate USD. Market rates understate real incomes in poor countries (the Balassa-Samuelson effect). ICP benchmark revisions (e.g. ICP 2017, ICP 2021 released 2024) can shift PPP levels.
- *Logs:* log GDP per capita is standard because the happiness-income relationship is roughly linear in log income (Stevenson & Wolfers 2008). A coefficient on ln(GDP) means Δy ≈ β/100 per 1% change. WHR's own model uses log GDP per capita PPP.
- *Nonstationarity:* in long macro panels (T≥30-40), trending series such as GDP and life expectancy can produce spurious regressions. Panel unit-root tests (Im-Pesaran-Shin, Pesaran CIPS) and first-differencing apply. With T=25 this is a moderate concern, and year FE or first differences mitigate it.
- *Multicollinearity check:* compute VIFs (`statsmodels.stats.outliers_influence.variance_inflation_factor`). V-Dem indices, WGI control of corruption, rule of law and government effectiveness typically correlate around r>0.85-0.9; use one, or a PCA composite.
- *Influence diagnostics:* `statsmodels` `OLSInfluence` gives Cook's distance, DFBETAS and leverage. Re-estimate leaving out one country or region at a time and with oil states and microstates excluded.

### Inferences
- In the user's happiness OLS, "control of corruption" (WGI, perception-based) plus log GDP pc plus life expectancy is a collinear set (rich countries score high on all three). Individual coefficients will be unstable, and corruption's coefficient may partly reflect income through perception bias.
- The ~217 → 119 drop in the OLS sample is itself a selection problem (Gini and WHR coverage are thin for small and fragile states). The report should recommend documenting which countries drop out and comparing complete-case results with MI results.
- Spatial and regional dependence among neighbouring countries means residuals are not independent even after clustering by country. Region FE or Moran's I on residuals is a cheap check, and Driscoll-Kraay SEs cover cross-sectional correlation in a panel.

### Gaps
- No verified source fetched this session on: PPP vs. market exchange rates, ecological fallacy, panel unit-root tests, log transformations, or VIF thresholds. These are all in the background bullets.
- No direct source found on WGI multicollinearity in regressions; Knack-Langbein's single-factor finding is the closest.
- No Python-native Amelia equivalent was verified. statsmodels MICE and scikit-learn IterativeImputer exist but do not model TSCS structure the way Amelia does (unverified).

---

## 5. Exploratory/unsupervised methods: clustering countries, PCA/factor analysis, convergence (beta, sigma)

### Takeaway
Beta and sigma convergence are the classic descriptive tools for country panels. The Barro "iron law" is about 2% per year of conditional convergence, and beta-convergence does not imply sigma-convergence. PCA and factor analysis are standard for compressing correlated governance indicators (Knack-Langbein found one dominant factor in the WGI). k-means and hierarchical clustering of countries are common and easy, but results depend on standardization, variable choice and k.

### Cited Findings
- Barro & Sala-i-Martin (1992) find conditional convergence of about 2% per year in a 98-country cross-section, conditioning on variables that hold constant countries' long-run characteristics. — [Barro (2012), NBER w18295 "Convergence and Modernization Revisited"](https://www.nber.org/system/files/working_papers/w18295/w18295.pdf)
- Barro (2012) reports about 1.7% per year in an 80-country panel since the 1960s and about 2.4% in a longer 34-country panel. The range 1.7-2.4% contains the "iron-law" 2%. — [NBER w18295](https://www.nber.org/papers/w18295)
- Sigma convergence means falling dispersion of incomes over time; beta convergence means poorer economies grow faster. Beta is necessary but not sufficient for sigma (acknowledged in Barro & Sala-i-Martin 1992, pp. 227-28). — [NBER w18295 PDF](https://www.nber.org/system/files/working_papers/w18295/w18295.pdf); [Mendez convergence slides](https://carlos-mendez.rbind.io/post/stata_convergence/slides/)
- Factor analysis of the six WGI dimensions suggests they measure one broad concept (Knack & Langbein 2010). This supports collapsing them into one composite (e.g. first principal component) instead of entering several at once. — [World Bank OKR](https://openknowledge.worldbank.org/entities/publication/1a3095cd-1ffa-5bf8-92c2-29ef82d8b993)
- **[background, not verified this session]** Python tools: `sklearn.decomposition.PCA`, `sklearn.cluster.KMeans`, `scipy.cluster.hierarchy` (Ward linkage), and silhouette scores for choosing k. Standardize variables first. The "club convergence" approach of Phillips & Sul (2007) is an advanced alternative that finds convergence clubs. Unconditional convergence across countries was absent in 1960-2000 but has appeared since the late 1990s/2000s (Patel, Sandefur & Subramanian 2021, "The new era of unconditional convergence", JDE). This is relevant because the user's 2000-2024 window falls in that period.

### Inferences
- For the user's panel, a simple beta-convergence regression (average annual growth of log GDP pc PPP 2000-2024 on log GDP pc in 2000) plus a sigma plot (cross-country SD of log GDP pc by year) is beginner-friendly and informative. The same idea extends to life expectancy or health spending.
- PCA on V-Dem/WGI governance variables addresses both the collinearity problem in section 4 and the "which governance measure" problem in section 6.

### Gaps
- No fetched source on k-means or hierarchical clustering applied to countries, or on Phillips-Sul club convergence.
- The Patel-Sandefur-Subramanian "unconditional convergence since ~2000" claim is background, not verified this session.

---

## 6. Robustness practices: specification curves, multiverse, extreme bounds (Leamer; Sala-i-Martin), out-of-sample validation

### Takeaway
Cross-country growth regressions brought the "model uncertainty" problem into the open. Levine & Renelt applied Leamer's extreme bounds and found almost nothing robust; Sala-i-Martin replaced the binary test with the full distribution of estimates; Bayesian model averaging followed. The modern version is specification curve / multiverse analysis (Simonsohn, Simmons & Nelson 2020), which reports results across all reasonable specifications with a joint test.

### Cited Findings
- Levine & Renelt (1992, AER) applied Leamer's extreme bounds analysis to cross-country growth regressions and concluded that very few, or no, variables are robust. — [Sala-i-Martin, UPF WP 201](https://econ-papers.upf.edu/papers/201.pdf)
- Sala-i-Martin (1997, AER Papers & Proceedings 87(2):178-183), "I Just Ran Two Million Regressions", proposes "assigning some level of confidence to each variable" and examining the whole distribution of coefficient estimates instead of extreme bounds. He concludes the picture is not "Nothing is Robust". The working paper circulated as "I Just Ran Four Million Regressions" (NBER 6252 / UPF 201). — [IDEAS (AER)](https://ideas.repec.org/a/aea/aecrev/v87y1997i2p178-83.html); [UPF WP 201](https://econ-papers.upf.edu/papers/201.pdf)
- Fernández, Ley & Steel (IMF WP, "We Just Averaged over Two Trillion Cross-Country Growth Regressions") use Bayesian model averaging. Their results broadly support Sala-i-Martin's more optimistic conclusion, though the variables they identify differ substantially. — [IMF WP](https://www.imf.org/en/Publications/WP/Issues/2016/12/30/We-Just-Averaged-over-Two-Trillion-Cross-Country-Growth-Regressions-3165)
- Simonsohn, Simmons & Nelson (2020, Nature Human Behaviour 4(11):1208-1214), "Specification curve analysis", report estimates for all reasonable specifications and combine them into a joint statistical test. Applied to three published findings, one was robust, one weak and one not robust at all. Code is at osf.io/9rvps. — [Nature Human Behaviour](https://link.springer.com/article/10.1038/s41562-020-0912-z); [IDEAS](https://ideas.repec.org/a/nat/nathum/v4y2020i11d10.1038_s41562-020-0912-z.html)
- Wilson & Butler (2007) show the same specification sensitivity in political-science TSCS. — [WUSTL](https://profiles.wustl.edu/en/publications/a-lot-more-to-do-the-sensitivity-of-time-series-cross-section-ana/)
- Roodman (2009) recommends reporting instrument counts and showing that GMM results survive fewer instruments, a robustness practice specific to dynamic panels. — [CGD WP 125](https://www.cgdev.org/sites/default/files/14256_file_Instruments.pdf)
- **[background, not verified this session]** Out-of-sample validation: hold out years (e.g. fit 2000-2018, predict 2019-2024) or regions, or use k-fold cross-validation grouped by country (`sklearn.model_selection.GroupKFold`) so the same country never sits in both train and test sets. Ordinary k-fold CV leaks country information in panels. Python options for specification curves include the `specification_curve` package (unverified), or a simple loop over combinations of controls, samples and SE types.

### Inferences
- For the happiness OLS, a feasible multiverse would vary the governance measure (WGI control of corruption vs. V-Dem corruption vs. a PCA composite), the GDP measure (PPP vs. market rate), the sample (all countries vs. excluding oil states and microstates), the year (one WHR year vs. a 3-year average) and the SE type (HC1 vs. HC3). Then plot the coefficient on log GDP pc across all of them.
- Reporting the full curve and the joint test is more credible than reporting one favored specification. This matters especially at n≈119, where adding or dropping a few countries changes estimates.

### Gaps
- Did not verify a maintained Python package for specification curve analysis.
- Did not fetch Leamer (1983/1985) directly; his role is attested only through Sala-i-Martin's paper.
- No fetched source on out-of-sample or grouped cross-validation in cross-country panels.
- General textbooks suggested in the brief (Wooldridge; Angrist & Pischke *Mostly Harmless Econometrics*; Cunningham *Causal Inference: The Mixtape*, free at mixtape.scunning.com; Huntington-Klein *The Effect*, free at theeffectbook.net) were not fetched this session. They are the standard beginner-to-intermediate references for FE, DiD, synthetic control, IV and RDD (both free books have chapters on each, Mixtape with Python code). URLs are given from background knowledge and were not verified.
