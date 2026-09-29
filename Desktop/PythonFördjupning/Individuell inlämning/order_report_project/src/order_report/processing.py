import logging
import pandas as pd

logger = logging.getLogger(__name__)


def clean_order_data(df: pd.DataFrame) -> pd.DataFrame:
    """Tvättar och transformerar rådatan."""
    logger.info("Startar datastädning och transformering...")
    df = df.copy()

    # Textstädning
    df["region"] = (
        df["region"].fillna("Unknown").astype(str).str.strip().str.title()
    )
    df["product_category"] = (
        df["product_category"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .str.title()
    )

    # Numerisk städning
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1)

    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    median_price = df["unit_price"].median()
    df["unit_price"] = df["unit_price"].fillna(median_price)

    df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0)

    # Boolesk städning
    df["returned"] = (
        df["returned"]
        .fillna("false")
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "yes", "1", "ja"])
    )

    # Beräknade kolumner
    df["order_value"] = df["quantity"] * df["unit_price"]
    df["discounted_value"] = df["order_value"] * (1 - df["discount"])

    logger.info("Datastädning slutförd.")
    return df