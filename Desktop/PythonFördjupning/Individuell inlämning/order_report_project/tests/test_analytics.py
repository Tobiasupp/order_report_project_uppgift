import pandas as pd
import pytest
from src.order_report.config import ReportConfig
from src.order_report.processing import clean_order_data
from src.order_report.reporting import (
    aggregate_sales_by_dimension,
    create_overview_report,
    create_returns_report,
)
from src.order_report.validation import (
    validate_columns,
    validate_data_content,
)


# ----------------------------------------------------------------------
# Fixtures för återanvändbar testdata
# ----------------------------------------------------------------------
@pytest.fixture
def sample_valid_df() -> pd.DataFrame:
    """Returnerar en giltig DataFrame för normalfalls-tester."""
    return pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "order_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
            "customer_id": [101, 102, 103],
            "region": [" north ", "south", None],
            "product_category": ["Electronics", " clothing ", "Electronics"],
            "quantity": [2, 1, "3"],
            "unit_price": [100.0, 50.0, None],  # median blir (100+50)/2 = 75.0
            "discount": [0.10, 0.0, None],
            "returned": ["False", "TRUE", "ja"],
        }
    )


# ----------------------------------------------------------------------
# 1. Tester för datastädning och beräkningar (processing.py)
# ----------------------------------------------------------------------
def test_clean_order_data_calculations(sample_valid_df: pd.DataFrame) -> None:
    """Testar beräkningar av order_value, discounted_value samt städning av typer."""
    cleaned = clean_order_data(sample_valid_df)

    # Kontrollera beräkningar för första raden: quantity=2, price=100.0, discount=0.10
    # order_value = 2 * 100 = 200.0
    # discounted_value = 200 * (1 - 0.10) = 180.0
    assert cleaned.loc[0, "order_value"] == 200.0
    assert cleaned.loc[0, "discounted_value"] == 180.0

    # Kontrollera textstädning (strip + title)
    assert cleaned.loc[0, "region"] == "North"
    assert cleaned.loc[2, "region"] == "Unknown"
    assert cleaned.loc[1, "product_category"] == "Clothing"

    # Kontrollera boolesk returhantering ("False" -> False, "TRUE" -> True, "ja" -> True)
    assert list(cleaned["returned"]) == [False, True, True]


def test_clean_order_data_missing_prices(
    sample_valid_df: pd.DataFrame,
) -> None:
    """Testar imputation av unit_price via medianvärde vid saknade/ogiltiga värden."""
    cleaned = clean_order_data(sample_valid_df)

    # Median för [100.0, 50.0] är 75.0. Rad 3 hade None -> ska ersättas med 75.0
    # quantity=3, price=75.0, discount=0.0 -> order_value = 225.0
    assert cleaned.loc[2, "unit_price"] == 75.0
    assert cleaned.loc[2, "order_value"] == 225.0


# ----------------------------------------------------------------------
# 2. Tester för validering (validation.py)
# ----------------------------------------------------------------------
def test_validate_columns_success(sample_valid_df: pd.DataFrame) -> None:
    """Normalfall: Inga undantag kastas när alla obligatoriska kolumner finns."""
    config = ReportConfig()
    try:
        validate_columns(sample_valid_df, config.required_columns)
    except ValueError:
        pytest.fail(
            "validate_columns kastade ValueError oavsiktligt för giltig data."
        )


def test_validate_columns_missing_column_raises_error() -> None:
    """Felscenario: Kasta ValueError om obligatorisk kolumn saknas."""
    config = ReportConfig()
    invalid_df = pd.DataFrame(
        {
            "order_id": [1],
            "region": ["North"],
            # Saknar övriga obligatoriska kolumner
        }
    )

    with pytest.raises(
        ValueError, match="Saknade obligatoriska kolumner i indata"
    ):
        validate_columns(invalid_df, config.required_columns)


# ----------------------------------------------------------------------
# 3. Tester för rapporter och aggregering (reporting.py)
# ----------------------------------------------------------------------
def test_create_overview_report(sample_valid_df: pd.DataFrame) -> None:
    """Testar generering av översiktsrapport med korrekta aggregerade summan/antal."""
    cleaned = clean_order_data(sample_valid_df)
    overview = create_overview_report(cleaned)

    metrics = dict(zip(overview["metric"], overview["value"]))

    assert metrics["order_count"] == 3
    assert metrics["return_count"] == 2
    # 180.0 (rad 1) + 50.0 (rad 2) + 225.0 (rad 3) = 455.0
    assert metrics["total_sales"] == 455.0


def test_aggregate_sales_by_dimension(sample_valid_df: pd.DataFrame) -> None:
    """Testar aggregering per kategori/region samt sortering."""
    cleaned = clean_order_data(sample_valid_df)

    # Aggregera på product_category
    category_report = aggregate_sales_by_dimension(cleaned, "product_category")

    # Electronics har 2 ordrar (180 + 225 = 405.0), Clothing har 1 order (50.0)
    # Rapport ska sorteras fallande på total_sales -> Electronics överst
    assert category_report.loc[0, "product_category"] == "Electronics"
    assert category_report.loc[0, "order_count"] == 2
    assert category_report.loc[0, "total_sales"] == 405.0


def test_create_returns_report(sample_valid_df: pd.DataFrame) -> None:
    """Testar returgrad per produktkategori."""
    cleaned = clean_order_data(sample_valid_df)
    returns_report = create_returns_report(cleaned)

    # Clothing har 1 order och 1 retur -> return_rate = 1.0
    # Electronics har 2 ordrar och 1 retur -> return_rate = 0.5
    assert returns_report.loc[0, "product_category"] == "Clothing"
    assert returns_report.loc[0, "return_rate"] == 1.0


def test_empty_dataframe_handling() -> None:
    """Edge case: Hantering av helt tom DataFrame med rätt kolumnstruktur."""
    empty_df = pd.DataFrame(
        columns=[
            "order_id",
            "order_date",
            "customer_id",
            "region",
            "product_category",
            "quantity",
            "unit_price",
            "discount",
            "returned",
        ]
    )

    cleaned = clean_order_data(empty_df)
    overview = create_overview_report(cleaned)

    metrics = dict(zip(overview["metric"], overview["value"]))

    assert metrics["total_sales"] == 0.0
    assert metrics["order_count"] == 0
    assert metrics["return_count"] == 0


def test_validate_data_content_warnings(caplog) -> None:
    """Testar att orimliga numeriska värden (t.ex. negativa priser) genererar en warning-logg."""
    df_invalid_values = pd.DataFrame(
        {
            "unit_price": [-10.0, 50.0],
            "quantity": [2, -1],
            "discount": [1.5, 0.1],  # 150% rabatt
        }
    )

    with caplog.at_level("WARNING"):
        validate_data_content(df_invalid_values)

    # Verifiera att rätt varningar skapats i loggen
    assert "negativt enhetspris" in caplog.text
    assert "negativ kvantitet" in caplog.text
    assert "orimlig rabatt" in caplog.text