#!/usr/bin/env python3
"""HTML to CSV Converter for ALKIS Building Functions.

This script extracts building function data from the ALKIS Objektartenkatalog HTML file
and converts it into a structured CSV format.

The HTML contains a table with building function codes, names, and descriptions that
are used in the ALKIS (Amtliches Liegenschaftskatasterinformationssystem) standard.
"""

import csv
import re
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


def extract_building_functions(html_file: Path) -> List[Dict[str, str]]:
    """Extract building function data from HTML file.
    
    Parses the ALKIS Objektartenkatalog HTML file and extracts all building function
    entries from the table. Each entry contains a code, name, and description.
    
    Args:
        html_file: Path to the AX_Gebaeudefunktion.html file
        
    Returns:
        List of dictionaries with keys 'code', 'name', and 'description'
        
    Example:
        >>> functions = extract_building_functions(Path('AX_Gebaeudefunktion.html'))
        >>> functions[0]
        {'code': '1000', 'name': 'Wohngebäude', 'description': "'Wohngebäude' ist ..."}
    """
    print(f"Reading HTML file: {html_file}")
    
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the table containing building functions
    table = soup.find('table', class_='enum')
    if not table:
        raise ValueError("Could not find table with class 'enum' in HTML file")
    
    functions = []
    
    # Find all table rows (skip header row)
    rows = table.find_all('tr', class_='enum')
    print(f"Found {len(rows)} rows in table")
    
    for idx, row in enumerate(rows, start=1):
        # Skip header row (contains 'Bezeichnung' and 'Wert')
        if row.find('th'):
            continue
        
        # Extract data from columns
        columns = row.find_all('td', class_='enum')
        if len(columns) != 2:
            print(f"Warning: Row {idx} has {len(columns)} columns, expected 2. Skipping.")
            continue
        
        # Extract name and description from first column
        name_col = columns[0]
        name_div = name_col.find('div', class_='wert')
        if not name_div:
            print(f"Warning: Row {idx} has no name div. Skipping.")
            continue
        
        # Extract name (first text node before any <p> tags)
        name = extract_name_from_div(name_div)
        
        # Extract description (first <p> tag with class 'indent smaller')
        description = extract_description_from_div(name_div)
        
        # Extract code from second column
        code_col = columns[1]
        code_div = code_col.find('div', class_='wert')
        if not code_div:
            print(f"Warning: Row {idx} has no code div. Skipping.")
            continue
        
        code = extract_code_from_div(code_div)
        
        # Validate that we have all required fields
        if not code or not name:
            print(f"Warning: Row {idx} missing code or name. Skipping.")
            continue
        
        functions.append({
            'code': code,
            'name': name,
            'description': description or ''
        })
        
        # Print progress every 50 entries
        if len(functions) % 50 == 0:
            print(f"Processed {len(functions)} building functions...")
    
    print(f"Successfully extracted {len(functions)} building functions")
    return functions


def extract_name_from_div(div) -> Optional[str]:
    """Extract the name from a div.wert element.
    
    The name is the first text node in the div, before any <p> tags.
    
    Args:
        div: BeautifulSoup div element
        
    Returns:
        Cleaned name string or None if not found
    """
    # Get all direct text nodes (before any <p> tags)
    for child in div.children:
        if isinstance(child, str):
            name = child.strip()
            if name:
                return name
    return None


def extract_description_from_div(div) -> Optional[str]:
    """Extract the description from a div.wert element.
    
    The description is in the first <p> tag with classes 'indent smaller'.
    Normalizes whitespace and removes surrounding quotes.
    
    Args:
        div: BeautifulSoup div element
        
    Returns:
        Cleaned description string or None if not found
    """
    # Find first <p> with 'indent smaller' classes
    p_tags = div.find_all('p', class_='indent smaller')
    if p_tags:
        # Get the first <p> tag (this is the description)
        # Skip other <p> tags that might contain 'Grunddatenbestand' etc.
        description = p_tags[0].get_text(strip=True)
        
        # Normalize whitespace: replace multiple spaces, tabs, newlines with single space
        description = re.sub(r'\s+', ' ', description)
        
        # Remove surrounding quotes if present
        description = description.strip('"')
        
        return description
    return None


def extract_code_from_div(div) -> Optional[str]:
    """Extract the code from a div.wert element.
    
    The code is typically a 4-digit number, possibly followed by ' (G)'.
    This function extracts only the numeric code.
    
    Args:
        div: BeautifulSoup div element
        
    Returns:
        4-digit code string or None if not found
        
    Examples:
        '1000 (G)' -> '1000'
        '1010' -> '1010'
    """
    text = div.get_text(strip=True)
    
    # Extract the numeric code (4 digits)
    match = re.search(r'\b(\d{4})\b', text)
    if match:
        return match.group(1)
    return None


def save_to_csv(functions: List[Dict[str, str]], output_file: Path) -> None:
    """Save building functions to CSV file.
    
    Creates a CSV file with columns: code, name, description
    Uses semicolon (;) as delimiter to avoid issues with commas in descriptions.
    
    Args:
        functions: List of function dictionaries
        output_file: Path to output CSV file
    """
    print(f"\nWriting to CSV file: {output_file}")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['code', 'name', 'description'], delimiter=';')
        writer.writeheader()
        writer.writerows(functions)
    
    print(f"Successfully wrote {len(functions)} entries to {output_file}")


def main():
    """Main execution function.
    
    Reads the AX_Gebaeudefunktion.html file from the current directory,
    extracts building function data, and saves it to building_functions.csv
    """
    # Setup paths
    script_dir = Path(__file__).parent
    html_file = script_dir / 'AX_Gebaeudefunktion.html'
    output_file = script_dir / 'building_functions.csv'
    
    # Check if HTML file exists
    if not html_file.exists():
        print(f"Error: HTML file not found at {html_file}")
        print("Please ensure AX_Gebaeudefunktion.html is in the same directory as this script.")
        return 1
    
    try:
        # Extract building functions from HTML
        functions = extract_building_functions(html_file)
        
        if not functions:
            print("Error: No building functions were extracted")
            return 1
        
        # Save to CSV
        save_to_csv(functions, output_file)
        
        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Input file:  {html_file}")
        print(f"Output file: {output_file}")
        print(f"Total entries: {len(functions)}")
        print("\nFirst 3 entries:")
        for func in functions[:3]:
            print(f"  {func['code']} - {func['name']}")
        print("\nConversion completed successfully!")
        
        return 0
        
    except Exception as e:
        print(f"\nError during conversion: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
