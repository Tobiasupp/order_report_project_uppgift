from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ReportConfig:
    """Innehåller projektets konfiguration och sökvägar."""

    base_dir: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent
    )
    input_file: Path = field(init=False)
    output_dir: Path = field(init=False)

    required_columns: set[str] = field(
        default_factory=lambda: {
            "order_id",
            "order_date",
            "customer_id",
            "region",
            "product_category",
            "quantity",
            "unit_price",
            "discount",
            "returned",
        }
    )

    def __post_init__(self) -> None:
        # Sätt sökvägar baserat på base_dir
        object.__setattr__(self, "input_file", self.base_dir / "data" / "orders.csv")
        object.__setattr__(self, "output_dir", self.base_dir / "output")

    def ensure_output_dir_exists(self) -> None:
        """Skapar output-mappen om den inte redan finns."""
        self.output_dir.mkdir(parents=True, exist_ok=True)