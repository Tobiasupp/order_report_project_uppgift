import logging
import pandas as pd
from src.order_report.config import ReportConfig

logger = logging.getLogger(__name__)


def validate_columns(df: pd.DataFrame, required_columns: set[str]) -> None:
    """Kontrollerar att alla nödvändiga kolumner finns i DataFrame."""
    logger.info("Validerar kolumner i indata...")
    missing = required_columns - set(df.columns)

    if missing:
        logger.error("Validering misslyckades. Saknade kolumner: %s", missing)
        raise ValueError(f"Saknade obligatoriska kolumner i indata: {missing}")

    logger.info("Validering av kolumner genomfördes utan fel.")


def validate_data_content(df: pd.DataFrame) -> None:
    """Kontrollerar datakvalitet, orimliga värden och tom data."""
    logger.info("Validerar datakvalitet och värdegränser...")

    # 1. Kontrollera om datan är helt tom
    if df.empty:
        logger.warning(
            "Inläst CSV-fil är tom. Inga rader finns att bearbeta."
        )
        return

    # 2. Kontrollera negativa priser eller kvantiteter
    invalid_prices = df[df["unit_price"] < 0]
    if not invalid_prices.empty:
        logger.warning(
            "Hittade %d rader med negativt enhetspris. Dessa bör granskas.",
            len(invalid_prices),
        )

    invalid_quantities = df[df["quantity"] < 0]
    if not invalid_quantities.empty:
        logger.warning(
            "Hittade %d rader med negativ kvantitet. Dessa bör granskas.",
            len(invalid_quantities),
        )

    # 3. Kontrollera orimliga rabatter (t.ex. < 0% eller > 100%)
    invalid_discounts = df[(df["discount"] < 0) | (df["discount"] > 1.0)]
    if not invalid_discounts.empty:
        logger.warning(
            "Hittade %d rader med orimlig rabatt (utanför 0-100%%).",
            len(invalid_discounts),
        )

    logger.info("Datakvalitetsvalidering klar.")