import logging
from src.order_report.config import ReportConfig
from src.order_report.loading import load_csv_data, save_to_csv
from src.order_report.processing import clean_order_data
from src.order_report.reporting import (
    aggregate_sales_by_dimension,
    create_overview_report,
    create_returns_report,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("=== Startar Order Report ===")

    # Initiera konfigurationsobjektet
    config = ReportConfig()
    config.ensure_output_dir_exists()

    try:
        # 1. Inläsning och validering
        raw_data = load_csv_data(config.input_file, config.required_columns)

        # 2. Databearbetning
        cleaned_data = clean_order_data(raw_data)

        # 3. Översiktsrapport
        overview_df = create_overview_report(cleaned_data)
        save_to_csv(overview_df, config.output_dir / "overview.csv")

        # 4. Försäljning per kategori
        sales_by_cat = aggregate_sales_by_dimension(
            cleaned_data, "product_category"
        )
        save_to_csv(sales_by_cat, config.output_dir / "sales_by_category.csv")

        # 5. Försäljning per region
        sales_by_region = aggregate_sales_by_dimension(cleaned_data, "region")
        save_to_csv(sales_by_region, config.output_dir / "sales_by_region.csv")

        # 6. Returer per kategori
        returns_by_cat = create_returns_report(cleaned_data)
        save_to_csv(
            returns_by_cat, config.output_dir / "returns_by_category.csv"
        )

        logger.info("=== Rapportgenereringen slutförd utan fel ===")

    except (FileNotFoundError, ValueError) as err:
        logger.error("Körningen avbröts på grund av ett känt fel: %s", err)
    except Exception as err:
        logger.critical("Ett oväntat fel uppstod: %s", err, exc_info=True)


if __name__ == "__main__":
    main()