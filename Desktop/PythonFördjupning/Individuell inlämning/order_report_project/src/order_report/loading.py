import logging
from pathlib import Path
import pandas as pd
from src.order_report.validation import (
    validate_columns,
    validate_data_content,
)

logger = logging.getLogger(__name__)


def load_csv_data(file_path: Path, required_columns: set[str]) -> pd.DataFrame:
    """Läser in CSV-fil med felhantering och anropar valideringskontroller."""
    logger.info("Läser in data från: %s", file_path)

    if not file_path.exists():
        logger.error("Filen kunde inte hittas på sökvägen: %s", file_path)
        raise FileNotFoundError(f"Filen hittades inte: {file_path}")

    try:
        df = pd.read_csv(file_path)
    except Exception as err:
        logger.error("Kunde inte läsa eller tolka CSV-filen: %s", err)
        raise ValueError(
            f"Körningen avbröts – CSV-filen är defekt eller skadad: {err}"
        )

    logger.info("Inläsning klar. Antal rader: %d", len(df))

    # Validera struktur och datainnehåll
    validate_columns(df, required_columns)
    validate_data_content(df)

    return df


def save_to_csv(df: pd.DataFrame, output_path: Path) -> None:
    """Sparar en DataFrame till en CSV-fil."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info("Sparade rapport till: %s", output_path)
    except Exception as err:
        logger.error("Kunde inte spara filen till %s: %s", output_path, err)
        raise PermissionError(f"Misslyckades att skriva till fil: {err}")