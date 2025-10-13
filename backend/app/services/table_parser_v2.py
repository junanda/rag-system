import pandas as pd
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TableParser:
    def __init__(self):
        self.table_keywords = {
            "capital_calls": ["capital call", "capital calls"],
            "distributions": ["distribution", "distributions"],
            "adjustments": ["adjustment", "adjustments"]
        }

    def _normalize(self, s: str) -> str:
        return " ".join(s.strip().lower().split()) if s else ""
    
    def table_classification(self, doc: any, stats: Dict[str, Any]) -> Dict[str, List]:
        all_tables = {"capital_calls": [], "distributions": [], "adjustments": []}
        
        for table in doc.tables:
            try:
                # Export table to pandas DataFrame
                df = table.export_to_dataframe(doc=doc)
                
                if df.empty:
                    continue

                # Identify table type from column headers
                table_type = self.identify_table_type_from_headers(df.columns.tolist())
                    
                if table_type != "unknown":
                    # Parse the DataFrame into records
                    records = self.parse_dataframe(df, table_type)
                    all_tables[table_type].extend(records)
                    stats["tables_extracted"] += 1
                    logger.info(f"Extracted {len(records)} records from {table_type} table")
                else:
                    logger.debug(f"Skipping unknown table with headers: {df.columns.tolist()}")
                        
            except Exception as e:
                logger.error(f"Error parsing table: {e}")
                stats["errors"].append(f"Table parsing error: {str(e)}")
        
        return all_tables

    def identify_table_type(self, caption: str) -> str:
        norm = self._normalize(caption)
        for key, keywords in self.table_keywords.items():
            if any(kw in norm for kw in keywords):
                return key
        return "unknown"

    def parse_table(self, table_data: List[List[str]], table_type: str) -> List[Dict[str, Any]]:
        if not table_data or len(table_data) < 2:
            return []

        headers = [h.strip() if h else f"col_{i}" for i, h in enumerate(table_data[0])]
        rows = table_data[1:]

        df = pd.DataFrame(rows, columns=headers)

        # Bersihkan kolom Amount
        if "Amount" in df.columns:
            df["Amount"] = (
                df["Amount"]
                .astype(str)
                .str.replace(r"[^\d.-]", "", regex=True)
                .replace("", "0")
                .astype(float)
            )

        return df.to_dict(orient="records")

    def parse_dataframe(self, df: pd.DataFrame, table_type: str) -> List[Dict[str, Any]]:
        """
        Parse a pandas DataFrame from Docling v2 table export.
        
        Args:
            df: DataFrame exported from table.export_to_dataframe()
            table_type: Type of table (capital_calls, distributions, adjustments)
            
        Returns:
            List of parsed records as dictionaries
        """
        if df.empty:
            return []
        
        # Normalize column names for easier matching
        df_norm = df.copy()
        df_norm.columns = [str(c).strip() for c in df.columns]
        
        # Clean Amount column if present
        amount_cols = [col for col in df_norm.columns if 'amount' in col.lower()]
        for col in amount_cols:
            df_norm[col] = (
                df_norm[col]
                .astype(str)
                .str.replace(r"[^\d.-]", "", regex=True)
                .replace("", "0")
            )
            try:
                df_norm[col] = df_norm[col].astype(float)
            except (ValueError, TypeError):
                logger.warning(f"Could not convert {col} to float")
        
        return df_norm.to_dict(orient="records")
    
    def identify_table_type_from_headers(self, headers: List[str]) -> str:
        """
        Identify table type from column headers.
        
        Args:
            headers: List of column names
            
        Returns:
            Table type (capital_calls, distributions, adjustments, or unknown)
        """
        lower_headers = [str(h).strip().lower() for h in headers]
        header_text = " ".join(lower_headers)

        # Strong heuristics based on common columns
        if any(k in lower_headers for k in ["call number", "call #"]) or "capital call" in header_text:
            return "capital_calls"

        if any(k in lower_headers for k in ["recallable"]) or "distribution" in header_text:
            return "distributions"
        
        if ("adjustment" in header_text or "adjustments" in header_text or any("adjust" in h for h in lower_headers) or ("type" in lower_headers and "amount" in lower_headers and "call number" not in lower_headers and "recallable" not in lower_headers)):
            return "adjustments"

        # Fallback to keyword-based detection
        for key, keywords in self.table_keywords.items():
            if any(kw in header_text for kw in keywords):
                return key

        return "unknown"