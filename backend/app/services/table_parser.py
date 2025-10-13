
import logging
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime
from decimal import Decimal

import pandas as pd
from docling.document_converter import DocumentConverter

from app.schemas.transaction import CapitalCallCreate, DistributionCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentParser:
    """
    A class to extract structured data and text from documents using the docling library.

    This parser identifies tables based on specific headers (e.g., "Capital Call", "Distribution"),
    parses the table rows, and maps them to corresponding Pydantic schemas. It also extracts
    text paragraphs for vector storage and includes error handling for parsing issues.
    """

    TABLE_HEADER_MAPPING = {
        "capital call": CapitalCallCreate,
        "distribution": DistributionCreate,
    }

    def __init__(self, file_path: str, fund_id: int):
        """
        Initializes the DocumentParser with the path to the document and the fund ID.

        Args:
            file_path (str): The path to the document file to be parsed.
            fund_id (int): The ID of the fund associated with this document.
        """
        self.file_path = file_path
        self.fund_id = fund_id
        try:
            self.converter = DocumentConverter()
            conv_res = self.converter.convert(file_path)
            self.doc = conv_res.document
        except Exception as e:
            logger.error(f"Error converting document {file_path}: {e}")
            self.doc = None

    def parse(self) -> Tuple[Dict[str, List[Any]], str]:
        """
        Parses the document to extract structured data from tables and unstructured text.

        Returns:
            Tuple[Dict[str, List[Any]], str]: A tuple containing:
                - A dictionary of extracted data, with keys as table types (e.g., "capital_calls")
                  and values as lists of Pydantic schema objects.
                - A string containing all the extracted paragraph text.
        """
        if not self.doc:
            return {}, ""

        extracted_data = {
            "capital_calls": [],
            "distributions": [],
        }
        
        paragraphs_text = self._extract_paragraphs()
        
        tables = self.doc.tables
        for table in tables:
            self._parse_table(table, extracted_data)

        return extracted_data, paragraphs_text

    def _extract_paragraphs(self) -> str:
        """Extracts document text as Markdown for downstream vector storage."""
        try:
            # Docling v2 provides markdown export directly from the DoclingDocument
            return self.doc.export_to_markdown()
        except Exception:
            # Fallback: no paragraphs available
            return ""

    def _parse_table(self, table: Any, extracted_data: Dict[str, List[Any]]):
        """
        Parses a single table to identify its type and extract its data.

        Args:
            table (Any): The table object from Docling v2.
            extracted_data (Dict[str, List[Any]]): The dictionary to populate with extracted data.
        """
        # Use pandas DataFrame exported from table for robust parsing
        try:
            df: pd.DataFrame = table.export_to_dataframe()
        except Exception as e:
            logger.error(f"Failed to export table to DataFrame: {e}")
            return

        header_text = " ".join([str(col).lower() for col in df.columns])
        
        for header_keyword, schema in self.TABLE_HEADER_MAPPING.items():
            if header_keyword in header_text:
                if schema == CapitalCallCreate:
                    key = "capital_calls"
                else:
                    key = "distributions"

                try:
                    records = self._parse_table_rows_df(df, schema)
                    extracted_data[key].extend(records)
                    logger.info(f"Successfully parsed {len(records)} records from a '{header_keyword}' table.")
                except Exception as e:
                    logger.error(f"Error parsing table with header '{header_keyword}': {e}")

    # The _get_table_header_text method is no longer needed with DataFrame-based parsing.


    def _parse_table_rows_df(self, df: pd.DataFrame, schema: Any) -> List[Any]:
        """Parses a DataFrame exported from a Docling table into schema objects."""
        records: List[Any] = []
        # Normalize headers to lowercase for matching
        lower_cols = [str(c).lower().strip() for c in df.columns]
        df_norm = df.copy()
        df_norm.columns = lower_cols

        for _, row in df_norm.iterrows():
            row_data = {k: (str(v) if not pd.isna(v) else None) for k, v in row.to_dict().items()}

            try:
                if schema == CapitalCallCreate:
                    mapped_data = {
                        "fund_id": self.fund_id,
                        "call_date": self._parse_date(row_data.get("date") or row_data.get("call date")),
                        "amount": self._parse_decimal(row_data.get("amount")),
                        "call_type": row_data.get("type") or row_data.get("call type"),
                        "description": row_data.get("description"),
                    }
                elif schema == DistributionCreate:
                    mapped_data = {
                        "fund_id": self.fund_id,
                        "distribution_date": self._parse_date(row_data.get("date") or row_data.get("distribution date")),
                        "amount": self._parse_decimal(row_data.get("amount")),
                        "distribution_type": row_data.get("type") or row_data.get("distribution type"),
                        "is_recallable": self._parse_bool(row_data.get("recallable")),
                        "description": row_data.get("description"),
                    }
                else:
                    continue

                filtered_data = {k: v for k, v in mapped_data.items() if v is not None}
                records.append(schema(**filtered_data))
            except (ValueError, TypeError, KeyError) as e:
                logger.warning(f"Skipping row due to parsing error: {e}. Row data: {row_data}")

        return records

    def _parse_date(self, date_str: str) -> datetime.date:
        """Parses a string into a date object."""
        if not date_str:
            raise ValueError("Date string is empty")
        # Add more robust date parsing if formats vary
        try:
            return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        except ValueError:
            return datetime.strptime(date_str.strip(), "%m/%d/%Y").date()


    def _parse_decimal(self, decimal_str: str) -> Decimal:
        """Parses a string into a Decimal object."""
        if not decimal_str:
            raise ValueError("Decimal string is empty")
        # Remove common currency symbols and commas
        cleaned_str = decimal_str.replace("$", "").replace(",", "").strip()
        return Decimal(cleaned_str)

    def _parse_bool(self, bool_str: str) -> bool:
        """Parses a string into a boolean."""
        if not bool_str:
            return False
        return bool_str.lower().strip() in ["true", "yes", "1"]

# Example Usage (for demonstration purposes):
if __name__ == '__main__':
    # This is a dummy file path. Replace with a real PDF/DOCX file for testing.
    # You would also need to have the 'docling' library installed.
    # pip install docling
    dummy_file_path = "../files/Sample_Fund_Performance_Report.pdf"
    fund_id = 1

    # Create a dummy file for testing if it doesn't exist
    # try:
    #     with open(dummy_file_path, "w") as f:
    #         f.write("This is a dummy file.")
    # except IOError:
    #     # This will fail if the path is invalid, which is expected for this example.
    #     pass
    if not os.path.exists(dummy_file_path):
        raise FileNotFoundError(f"File not found: {dummy_file_path}")

    parser = DocumentParser(dummy_file_path, fund_id)
    if parser.doc:
        extracted_data, paragraphs = parser.parse()
        
        print("--- Extracted Structured Data ---")
        print(extracted_data)
        
        print("\n--- Extracted Paragraphs for Vector Storage ---")
        print(paragraphs)

