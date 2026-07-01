# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
pip install -r requirements.txt
jupyter notebook
```

## Architecture

This is a two-notebook pipeline for Marketing Mix Modeling (MMM) using Google's Meridian library on synthetic data.

**Execution order matters**: Notebook 01 must run before Notebook 02, as it generates `data/synthetic_mmm.csv`.

### Notebooks

- `notebooks/01_synthetic_data_eda.ipynb` — Generates 104 weeks of synthetic weekly spend/revenue data, saves to `data/synthetic_mmm.csv`, and produces EDA charts in `outputs/`.
- `notebooks/02_meridian_model.ipynb` — Loads the CSV, fits a Bayesian MMM via Meridian MCMC, then produces ROI, decomposition, response curve, and budget optimisation outputs.

Both notebooks use `sys.path.insert(0, '..')` to import from `src/`.

### `src/transforms.py`

Reusable signal transforms used in both synthetic data generation and model interpretation:

- `adstock(x, decay)` — geometric carry-over
- `hill(x, ec, slope)` — diminishing returns saturation
- `adstock_hill(x, decay, ec, slope)` — convenience wrapper
- `normalise(x)` — min-max to [0, 1]
- `mape(actual, predicted)` — MAPE %
- `decompose_revenue(...)` — generates synthetic revenue with known ground-truth channel decomposition

### Data conventions

- All monetary values are in **£000s** (thousands of pounds).
- 9 canonical channels (in order): `tv`, `search`, `social`, `display`, `video`, `ooh`, `radio`, `email`, `affiliate`
- Spend columns follow the pattern `<channel>_spend` (e.g. `tv_spend`, `affiliate_spend`)
- Canonical channel colours (in order): `['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#e91e63', '#607d8b']`
- Channel parameters follow the `CHANNEL_PARAMS` dict pattern: `dict(coef, decay, ec, slope)`
- TV and OOH are **flighted** (not always-on) — their spend arrays contain zeros in dark weeks
- Baseline revenue includes a **trend** component (`1 + 0.003t`) and **holiday uplifts** (Christmas +30%, Easter +12%) on top of the sine-wave seasonality

### Meridian API (notebook 02)

Key classes used from the `meridian` library:

```python
from meridian.data import input_data as input_data_lib   # InputData
from meridian.model import meridian as meridian_model     # Meridian
from meridian.model import spec                           # ModelSpec
from meridian.analysis import optimizer                   # BudgetOptimizer
from meridian.analysis import analyzer                    # Analyzer
```

`InputData` expects:
- `kpi` and `media` / `media_spend` as `xr.DataArray` with dims `(geo, time)` and `(geo, time, media_channel)` respectively.
- Media impressions are normalised spend (divide by per-channel max).

MCMC is run with `mmm.sample_posterior(n_chains, n_adapt, n_burnin, n_keep, seed)`. The defaults in the notebook (`n_keep=1000`) are for quick iteration; increase for production runs.

### Output paths

Charts are saved from notebooks via `plt.savefig('../outputs/<name>.png', dpi=150)`. The `data/` and `outputs/` directories contain only `.gitkeep`; CSVs and PNGs are excluded by `.gitignore`.
