import numpy as np
import pandas as pd


def adstock(x: np.ndarray, decay: float = 0.5) -> np.ndarray:
    """Geometric adstock — models carry-over effect of media exposure.

    Args:
        x: Weekly spend or impressions array.
        decay: Retention rate per period (0 = no carry-over, 1 = permanent).
    """
    out = np.zeros_like(x, dtype=float)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = x[i] + decay * out[i - 1]
    return out


def hill(x: np.ndarray, ec: float = 0.5, slope: float = 2.0) -> np.ndarray:
    """Hill / saturation transform — models diminishing returns.

    Args:
        x: Input signal (post-adstock spend / impressions).
        ec: Half-saturation point; x value where output = 0.5.
        slope: Steepness of the curve (higher = more S-shaped).
    """
    return x ** slope / (ec ** slope + x ** slope)


def adstock_hill(
    x: np.ndarray,
    decay: float = 0.5,
    ec: float = 0.5,
    slope: float = 2.0,
) -> np.ndarray:
    """Convenience: apply adstock then Hill saturation in one call."""
    return hill(adstock(x, decay=decay), ec=ec, slope=slope)


def normalise(x: np.ndarray) -> np.ndarray:
    """Min-max normalise to [0, 1]."""
    rng = x.max() - x.min()
    return (x - x.min()) / rng if rng > 0 else np.zeros_like(x)


def mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Mean absolute percentage error (%)."""
    mask = actual != 0
    return float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)


def decompose_revenue(
    df: pd.DataFrame,
    spend_cols: list[str],
    channel_names: list[str],
    channel_params: list[dict],
    base_revenue: float,
    seasonality: np.ndarray,
    coefficients: list[float],
    noise_std: float = 20.0,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic revenue with known ground-truth decomposition.

    Each entry in channel_params should be a dict with keys:
        decay (float), ec (float), slope (float)

    Returns the original df with a 'revenue' column added.
    """
    rng = np.random.default_rng(seed)
    revenue = base_revenue * seasonality

    for col, params, coef in zip(spend_cols, channel_params, coefficients):
        transformed = adstock_hill(df[col].values, **params)
        revenue += coef * transformed

    revenue += rng.normal(0, noise_std, len(df))
    return df.assign(revenue=revenue)
