from typing import List, Dict
import re
from dataclasses import dataclass

@dataclass
class TableCell:
    text: str
    row: int
    col: int
    is_header: bool = False

@dataclass
class TableRow:
    cells: List[TableCell]
    is_header: bool = False

class TableExtractor:
    def __init__(self):
        self.amount_pattern = re.compile(r'\d+[\s.,]\d+(?:[\s.,]\d+)*(?:\s*(?:kr|NOK))?')
        self.quantity_pattern = re.compile(r'^\d+(?:[,.]\d+)?$')
    
    def detect_table_structure(self, lines: List[str]) -> List[List[str]]:
        """Detect potential table structure in text lines."""
        tables = []
        current_table = []
        
        for line in lines:
            # Check if line might be part of a table
            cells = self._split_into_cells(line)
            if len(cells) >= 2:  # Minimum 2 columns for a table
                if not current_table:
                    # Start new table
                    current_table = [cells]
                else:
                    # Continue existing table if structure matches
                    # Allow for some flexibility in column count
                    max_cols = max(len(row) for row in current_table)
                    if len(cells) >= max_cols - 1 and len(cells) <= max_cols + 1:
                        # Pad cells if necessary
                        while len(cells) < max_cols:
                            cells.append('')
                        current_table.append(cells)
                    else:
                        # Structure changed significantly, end current table
                        if len(current_table) >= 2:  # Minimum 2 rows
                            tables.append(current_table)
                        current_table = [cells]
            else:
                # Non-table line
                if current_table and len(current_table) >= 2:
                    tables.append(current_table)
                current_table = []
        
        # Add last table if exists
        if current_table and len(current_table) >= 2:
            tables.append(current_table)
        
        # Normalize table structure
        normalized_tables = []
        for table in tables:
            max_cols = max(len(row) for row in table)
            normalized_table = []
            for row in table:
                normalized_row = row + [''] * (max_cols - len(row))
                normalized_table.append(normalized_row)
            normalized_tables.append(normalized_table)
        
        return normalized_tables

    def _split_into_cells(self, line: str) -> List[str]:
        """Split a line into cells based on delimiters and spacing."""
        # First try splitting by common delimiters
        if '|' in line:
            cells = [cell.strip() for cell in line.split('|')]
        else:
            # Split by multiple spaces and preserve decimal numbers
            pattern = r'(?:\s{2,}|\t+)'
            cells = [cell.strip() for cell in re.split(pattern, line) if cell.strip()]
            
        # Handle decimal numbers (both . and , as decimal separators)
        final_cells = []
        for cell in cells:
            # Skip empty cells
            if not cell:
                continue
                
            # Check if the cell might be a decimal number with comma
            if ',' in cell and not re.search(r'[a-zA-Z]', cell):
                # Keep the number as is, don't split on comma
                final_cells.append(cell)
            else:
                final_cells.append(cell)
                
        return [cell for cell in final_cells if cell]

    def identify_columns(self, table: List[List[str]]) -> Dict[int, str]:
        """Identify column types based on content."""
        if not table or not table[0]:
            return {}
            
        column_types = {}
        num_columns = len(table[0])
        
        for col in range(num_columns):
            column_values = [row[col] for row in table[1:] if col < len(row)]
            
            # Check column contents
            amounts = sum(1 for val in column_values if self.amount_pattern.search(val))
            quantities = sum(1 for val in column_values if self.quantity_pattern.match(val))
            
            # Determine column type
            if amounts > len(column_values) * 0.5:
                column_types[col] = 'amount'
            elif quantities > len(column_values) * 0.5:
                column_types[col] = 'quantity'
            else:
                column_types[col] = 'description'
        
        return column_types

    def to_markdown(self, table: List[List[str]], column_types: Dict[int, str]) -> str:
        """Convert table to markdown format."""
        if not table:
            return ""
            
        # Create header
        header = table[0]
        markdown = "| " + " | ".join(header) + " |\n"
        markdown += "|" + "|".join("---" for _ in header) + "|\n"
        
        # Add rows
        for row in table[1:]:
            # Ensure row has same number of columns as header
            while len(row) < len(header):
                row.append("")
            
            # Format cells based on column type
            formatted_row = []
            for i, cell in enumerate(row):
                cell_type = column_types.get(i, 'text')
                if cell_type == 'amount':
                    # Right-align amounts
                    formatted_row.append(f"{cell:>}")
                else:
                    formatted_row.append(cell)
            
            markdown += "| " + " | ".join(formatted_row) + " |\n"
        
        return markdown

    def extract_tables(self, text: str) -> List[str]:
        """Extract and convert tables from text to markdown."""
        lines = text.split('\n')
        tables = self.detect_table_structure(lines)
        
        markdown_tables = []
        for table in tables:
            column_types = self.identify_columns(table)
            markdown_table = self.to_markdown(table, column_types)
            if markdown_table:
                markdown_tables.append(markdown_table)
        
        return markdown_tables
