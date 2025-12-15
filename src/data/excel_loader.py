import pandas as pd
from typing import Dict


class ExcelDataLoader:
    """
    Robust Excel (.xlsb) loader for:
    - Transactional Sales table
    - Active Store pivot table
    - Column dictionary (headers)
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.engine = "pyxlsb"
        self.sheets = pd.ExcelFile(file_path, engine=self.engine).sheet_names

    # --------------------------------------------------
    # SALES HEADERS (DATA DICTIONARY)
    # --------------------------------------------------
    def load_sales_headers(self) -> pd.DataFrame:
        sheet = next(s for s in self.sheets if "header" in s.lower())

        df = pd.read_excel(
            self.file_path,
            sheet_name=sheet,
            engine=self.engine
        )

        df.columns = ["column", "description"]
        df = df.dropna(subset=["column"])

        return df.reset_index(drop=True)

    # --------------------------------------------------
    # SALES DATA (TRANSACTIONAL)
    # --------------------------------------------------
    def load_sales_data(self) -> pd.DataFrame:
        sheet = next(
            s for s in self.sheets
            if s.lower().strip() == "sales"
            or "2022" in s.lower()
        )

        raw = pd.read_excel(
            self.file_path,
            sheet_name=sheet,
            engine=self.engine,
            skiprows=1
        )

        headers = self.load_sales_headers()["column"].tolist()

        sales = raw.iloc[:, :len(headers)]
        sales.columns = headers
        sales = sales.dropna(how="all")

        # Type safety
        sales["Year"] = sales["Year"].astype(int)
        sales["Value"] = pd.to_numeric(sales["Value"], errors="coerce")
        sales["Month"] = sales["Month"].astype(str).str.upper()

        return sales.reset_index(drop=True)

    # --------------------------------------------------
    # ACTIVE STORE DATA (PIVOT MATRIX)
    # --------------------------------------------------
    def load_active_store_data(self) -> pd.DataFrame:
        """
        Pivot table → treat ANY non-null as active.
        We do NOT try to parse months/years here.
        """
        sheet = next(s for s in self.sheets if "active" in s.lower())

        raw = pd.read_excel(
            self.file_path,
            sheet_name=sheet,
            engine=self.engine,
            header=None
        )

        raw = raw.dropna(how="all")
        raw = raw.reset_index(drop=True)

        raw.rename(columns={raw.columns[0]: "Store"}, inplace=True)

        # Drop totals / blank rows
        raw = raw[
            ~raw["Store"]
            .astype(str)
            .str.contains("total|blank", case=False, na=False)
        ]

        return raw.reset_index(drop=True)

    # --------------------------------------------------
    # MASTER
    # --------------------------------------------------
    def load_all(self) -> Dict[str, pd.DataFrame]:
        return {
            "sales": self.load_sales_data(),
            "active_store": self.load_active_store_data(),
            "headers": self.load_sales_headers(),
        }
