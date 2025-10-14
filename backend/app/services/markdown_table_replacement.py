import re
from typing import Dict

class MarkdownTableReplacer:
    """Replace markdown tables with narrative paragraphs while keeping headers."""
    
    def __init__(self):
        # Mapping table headers to dictionary keys
        self.table_mapping = {
            'capital calls': 'capital_calls',
            'distributions': 'distributions',
            'adjustments': 'adjustments'
        }
    
    def replace_tables_with_paragraphs(
        self, 
        markdown_text: str, 
        paragraphs: Dict[str, str]
    ) -> str:
        """
        Replace markdown tables with narrative paragraphs.
        
        Args:
            markdown_text: Original markdown text with tables
            paragraphs: Dictionary with table_type: paragraph_text
        
        Returns:
            Modified markdown with tables replaced by paragraphs
        """
        lines = markdown_text.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this is a table header (## Something)
            if line.startswith('##'):
                # Extract header text
                header_text = line.replace('#', '').strip().lower()
                
                # Check if this header matches any table type
                table_type = self._get_table_type(header_text)
                
                if table_type and table_type in paragraphs:
                    # Add the header
                    result_lines.append(lines[i])
                    result_lines.append('')  # Empty line after header
                    
                    # Skip the table content
                    i = self._skip_table(lines, i + 1)
                    
                    # Add the paragraph
                    result_lines.append(paragraphs[table_type])
                    result_lines.append('')  # Empty line after paragraph
                else:
                    # Not a table header we want to replace, keep as is
                    result_lines.append(lines[i])
                    i += 1
            else:
                # Regular line, keep as is
                result_lines.append(lines[i])
                i += 1
        
        # Clean up multiple consecutive empty lines
        cleaned_result = self._clean_empty_lines(result_lines)
        
        return '\n'.join(cleaned_result)
    
    def _get_table_type(self, header_text: str) -> str:
        """
        Identify table type from header text.
        
        Args:
            header_text: Lowercase header text
        
        Returns:
            Table type key or None
        """
        for key, value in self.table_mapping.items():
            if key in header_text:
                return value
        return None
    
    def _skip_table(self, lines: list, start_idx: int) -> int:
        """
        Skip all lines that belong to a table.
        
        Args:
            lines: List of all lines
            start_idx: Starting index to check
        
        Returns:
            Index of first non-table line
        """
        i = start_idx
        in_table = False
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Empty line
            if not line:
                if in_table:
                    # Empty line after table might mean end of table
                    # But check next line to be sure
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not next_line.startswith('|'):
                            # Next line is not table, so we're done
                            return i + 1
                i += 1
                continue
            
            # Check if this is a table line (starts and ends with |)
            if re.match(r'^\s*\|.*\|\s*$', line):
                in_table = True
                i += 1
                continue
            
            # Check if this is a table separator (| --- | --- |)
            if re.match(r'^\s*\|\s*[-:]+\s*\|', line):
                in_table = True
                i += 1
                continue
            
            # If we were in a table and hit non-table line, we're done
            if in_table:
                return i
            
            # Not a table line and we haven't seen table yet, keep looking
            i += 1
        
        return i
    
    def _clean_empty_lines(self, lines: list) -> list:
        """
        Remove excessive empty lines (max 1 consecutive empty line).
        
        Args:
            lines: List of lines
        
        Returns:
            Cleaned list of lines
        """
        cleaned = []
        prev_empty = False
        
        for line in lines:
            is_empty = not line.strip()
            
            if is_empty:
                if not prev_empty:
                    cleaned.append(line)
                prev_empty = True
            else:
                cleaned.append(line)
                prev_empty = False
        
        # Remove leading and trailing empty lines
        while cleaned and not cleaned[0].strip():
            cleaned.pop(0)
        
        while cleaned and not cleaned[-1].strip():
            cleaned.pop()
        
        return cleaned
    
    def replace_tables_smart(
        self, 
        markdown_text: str, 
        paragraphs: Dict[str, str],
        keep_header: bool = True
    ) -> str:
        """
        Smart replacement that handles various markdown structures.
        
        Args:
            markdown_text: Original markdown text
            paragraphs: Dictionary with paragraphs
            keep_header: Whether to keep the section header
        
        Returns:
            Modified markdown
        """
        result = markdown_text
        
        # Process each table type
        for header_key, dict_key in self.table_mapping.items():
            if dict_key not in paragraphs:
                continue
            
            # Pattern to match section header + table
            # Matches: ## Header ... (table content) ... until next ## or end
            pattern = (
                r'(##\s*' + re.escape(header_key) + r'[^\n]*\n)'  # Header
                r'((?:.*\n)*?)'  # Content before table
                r'(\|[^\n]+\|(?:\n\|[^\n]+\|)*)'  # Table
                r'(\n|$)'  # End
            )
            
            if keep_header:
                # Replace table with paragraph, keep header
                replacement = r'\1\n' + paragraphs[dict_key] + r'\4'
            else:
                # Replace entire section with just paragraph
                replacement = paragraphs[dict_key] + r'\4'
            
            result = re.sub(
                pattern, 
                replacement, 
                result, 
                flags=re.IGNORECASE | re.MULTILINE
            )
        
        return result


# Example usage
if __name__ == "__main__":
    # Sample markdown
    markdown_text = """## Tech Ventures Fund III

    ## Quarterly Performance Report - Q4 2024

    Fund Name: Tech Ventures Fund III
    GP: Tech Ventures Partners
    Vintage Year: 2023
    Fund Size: $100,000,000
    Report Date: December 31, 2024

    ## Capital Calls

    | Date       | Call Number   | Amount     | Description          |
    |------------|---------------|------------|----------------------|
    | 2023-01-15 | Call 1        | $5,000,000 | Initial Capital Call |
    | 2023-06-20 | Call 2        | $3,000,000 | Follow-on Investment |
    | 2024-03-10 | Call 3        | $2,000,000 | Bridge Round Funding |
    | 2024-09-15 | Call 4        | $1,500,000 | Additional Capital   |

    ## Distributions

    | Date       | Type              | Amount     | Recallable   | Description            |
    |------------|-------------------|------------|--------------|------------------------|
    | 2023-12-15 | Return of Capital | $1,500,000 | No           | Exit: TechCo Inc       |
    | 2024-06-20 | Income            | $500,000   | No           | Dividend Payment       |
    | 2024-09-10 | Return of Capital | $2,000,000 | Yes          | Partial Exit: DataCorp |
    | 2024-12-20 | Income            | $300,000   | No           | Year-end Distribution  |

    ## Adjustments

    | Date       | Type                    | Amount    | Description                        |
    |------------|-------------------------|-----------|------------------------------------|
    | 2024-01-15 | Recallable Distribution | -$500,000 | Recalled distribution from Q4 2023 |
    | 2024-03-20 | Capital Call Adjustment | $100,000  | Management fee adjustment          |
    | 2024-07-10 | Contribution Adjustment | -$50,000  | Expense reimbursement              |

    ## Performance Summary

    Total Capital Called: $11,500,000
    Total Distributions: $4,300,000
    Net Paid-In Capital (PIC): $11,050,000"""

    # Sample paragraphs
    paragraphs = {
        'capital_calls': 'The fund executed 4 capital call(s) during the reporting period. On January 15, 2023, Call 1 was issued for $5.0 million, designated for initial capital call. On June 20, 2023, Call 2 was issued for $3.0 million, designated for follow-on investment. On March 10, 2024, Call 3 was issued for $2.0 million, designated for bridge round funding. On September 15, 2024, Call 4 was issued for $1.5 million, designated for additional capital. The cumulative capital called totaled $11.5 million.',
        'distributions': 'The fund made 4 distribution(s) to investors during the reporting period. On December 15, 2023, a non-recallable return of capital distribution of $1.5 million was processed, attributed to exit: techco inc. On June 20, 2024, a non-recallable income distribution of $500.0 thousand was processed, attributed to dividend payment. On September 10, 2024, a recallable return of capital distribution of $2.0 million was processed, attributed to partial exit: datacorp. On December 20, 2024, a non-recallable income distribution of $300.0 thousand was processed, attributed to year-end distribution. Total distributions amounted to $4.3 million, of which 1 distribution(s) were recallable.',
        'adjustments': "The fund recorded 3 adjustment(s) during the reporting period. On January 15, 2024, a recallable distribution resulted in a decrease of $500.0 thousand, related to recalled distribution from q4 2023. On March 20, 2024, a capital call adjustment resulted in a increase of $100.0 thousand, related to management fee adjustment. On July 10, 2024, a contribution adjustment resulted in a decrease of $50.0 thousand, related to expense reimbursement. The net effect of all adjustments was a decrease of $450.0 thousand in the fund's capital account."
    }
    
    # Initialize replacer
    replacer = MarkdownTableReplacer()
    
    # Replace tables with paragraphs
    result = replacer.replace_tables_with_paragraphs(markdown_text, paragraphs)
    
    print("=" * 80)
    print("ORIGINAL MARKDOWN (with tables)")
    print("=" * 80)
    print(markdown_text[:500] + "...\n")
    
    print("=" * 80)
    print("MODIFIED MARKDOWN (tables replaced with paragraphs)")
    print("=" * 80)
    print(result)