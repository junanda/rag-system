from typing import Dict, List, Any
from datetime import datetime

class TableToParagraphConverter:
    """Convert structured table data into narrative paragraphs."""
    
    def __init__(self):
        self.templates = {
            'capital_calls': self._capital_calls_template,
            'distributions': self._distributions_template,
            'adjustments': self._adjustments_template
        }
    
    def convert_tables_to_paragraphs(self, table_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, str]:
        """
        Convert all tables to paragraph format.
        
        Args:
            table_data: Dictionary containing capital_calls, distributions, and adjustments
        
        Returns:
            Dictionary with paragraph versions of each table type
        """
        paragraphs = {}
        
        for table_type, records in table_data.items():
            if table_type in self.templates and records:
                template_func = self.templates[table_type]
                paragraphs[table_type] = template_func(records)
            else:
                paragraphs[table_type] = ""
        
        return paragraphs
    
    def _capital_calls_template(self, records: List[Dict[str, Any]]) -> str:
        """Generate paragraph for capital calls."""
        if not records:
            return "No capital calls recorded during this period."
        
        intro = f"The fund executed {len(records)} capital call(s) during the reporting period. "
        
        call_descriptions = []
        for record in records:
            date = self._format_date(record.get('Date', ''))
            call_num = record.get('Call Number', 'N/A')
            amount = self._format_currency(record.get('Amount', 0))
            description = record.get('Description', 'No description provided')
            
            call_text = (
                f"On {date}, {call_num} was issued for {amount}, "
                f"designated for {description.lower()}."
            )
            call_descriptions.append(call_text)
        
        # Calculate total
        total_amount = sum(record.get('Amount', 0) for record in records)
        total_text = f" The cumulative capital called totaled {self._format_currency(total_amount)}."
        
        return intro + " ".join(call_descriptions) + total_text
    
    def _distributions_template(self, records: List[Dict[str, Any]]) -> str:
        """Generate paragraph for distributions."""
        if not records:
            return "No distributions were made during this period."
        
        intro = f"The fund made {len(records)} distribution(s) to investors during the reporting period. "
        
        dist_descriptions = []
        for record in records:
            date = self._format_date(record.get('Date', ''))
            dist_type = record.get('Type', 'N/A')
            amount = self._format_currency(record.get('Amount', 0))
            recallable = record.get('Recallable', 'N/A')
            description = record.get('Description', 'No description provided')
            
            recallable_text = "recallable" if recallable.lower() == 'yes' else "non-recallable"
            
            dist_text = (
                f"On {date}, a {recallable_text} {dist_type.lower()} distribution of {amount} "
                f"was processed, attributed to {description.lower()}."
            )
            dist_descriptions.append(dist_text)
        
        # Calculate totals
        total_amount = sum(record.get('Amount', 0) for record in records)
        recallable_count = sum(1 for r in records if r.get('Recallable', '').lower() == 'yes')
        
        summary = (
            f" Total distributions amounted to {self._format_currency(total_amount)}, "
            f"of which {recallable_count} distribution(s) were recallable."
        )
        
        return intro + " ".join(dist_descriptions) + summary
    
    def _adjustments_template(self, records: List[Dict[str, Any]]) -> str:
        """Generate paragraph for adjustments."""
        if not records:
            return "No adjustments were recorded during this period."
        
        intro = f"The fund recorded {len(records)} adjustment(s) during the reporting period. "
        
        adj_descriptions = []
        for record in records:
            date = self._format_date(record.get('Date', ''))
            adj_type = record.get('Type', 'N/A')
            amount = record.get('Amount', 0)
            description = record.get('Description', 'No description provided')
            
            # Determine if positive or negative adjustment
            direction = "increase" if amount > 0 else "decrease"
            abs_amount = self._format_currency(abs(amount))
            
            adj_text = (
                f"On {date}, a {adj_type.lower()} resulted in a {direction} of {abs_amount}, "
                f"related to {description.lower()}."
            )
            adj_descriptions.append(adj_text)
        
        # Calculate net adjustment
        net_adjustment = sum(record.get('Amount', 0) for record in records)
        net_direction = "increase" if net_adjustment >= 0 else "decrease"
        
        summary = (
            f" The net effect of all adjustments was a {net_direction} of "
            f"{self._format_currency(abs(net_adjustment))} in the fund's capital account."
        )
        
        return intro + " ".join(adj_descriptions) + summary
    
    def _format_date(self, date_str: str) -> str:
        """Format date string to readable format."""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%B %d, %Y')
        except:
            return date_str
    
    def _format_currency(self, amount: float) -> str:
        """Format number as currency."""
        if amount >= 1_000_000:
            return f"${amount/1_000_000:.1f} million"
        elif amount >= 1_000:
            return f"${amount/1_000:.1f} thousand"
        else:
            return f"${amount:,.2f}"
    
    def generate_full_report(self, table_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Generate a complete narrative report from all tables.
        
        Args:
            table_data: Dictionary containing all table data
        
        Returns:
            Complete narrative report as string
        """
        paragraphs = self.convert_tables_to_paragraphs(table_data)
        
        report_sections = []
        
        if paragraphs.get('capital_calls'):
            report_sections.append("## Capital Calls Summary\n" + paragraphs['capital_calls'])
        
        if paragraphs.get('distributions'):
            report_sections.append("\n\n## Distributions Summary\n" + paragraphs['distributions'])
        
        if paragraphs.get('adjustments'):
            report_sections.append("\n\n## Adjustments Summary\n" + paragraphs['adjustments'])
        
        return "\n".join(report_sections)