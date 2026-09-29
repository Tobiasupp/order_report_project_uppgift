import logging
import pandas as pd

logger = logging.getLogger(__name__)


def create_overview_report(df: pd.DataFrame) -> pd.DataFrame:
    """Genererar övergripande nyckeltal."""
    logger.info("Skapar översiktsrapport (overview)...")
    total_sales = round(df["discounted_value"].sum(), 2)
    number_of_orders = df["order_id"].nunique()
    number_of_returns = int(df["returned"].sum())

    return pd.DataFrame(
        {
            "metric": ["total_sales", "order_count", "return_count"],
            "value": [total_sales, number_of_orders, number_of_returns],
        }
    )


def aggregate_sales_by_dimension(
    df: pd.DataFrame, group_col: str
) -> pd.DataFrame:
    """Återanvändbar funktion för aggregering per dimension (kategori/region)."""
    logger.info("Skapar försäljningsrapport grupperat på: %s", group_col)
    result = df.groupby(group_col, as_index=False).agg(
        order_count=("order_id", "nunique"),
        total_sales=("discounted_value", "sum"),
        returns=("returned", "sum"),
    )

    result["total_sales"] = result["total_sales"].round(2)
    result["return_rate"] = (
        result["returns"] / result["order_count"]
    ).round(3)

    return result.sort_values("total_sales", ascending=False).reset_index(
        drop=True
    )


def create_returns_report(df: pd.DataFrame) -> pd.DataFrame:
    """Beräknar returgrad per produktkategori."""
    logger.info("Skapar returrapport per produktkategori...")
    returns = df.groupby("product_category", as_index=False).agg(
        order_count=("order_id", "nunique"),
        returns=("returned", "sum"),
    )

    returns["return_rate"] = (
        returns["returns"] / returns["order_count"]
    ).round(3)

    return returns.sort_values("return_rate", ascending=False).reset_index(
        drop=True
    )