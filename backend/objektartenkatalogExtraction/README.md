# ALKIS Building Function HTML to CSV Converter

This tool extracts building function data from the official ALKIS Objektartenkatalog HTML file and converts it into a structured CSV format for easier processing.

## Overview

The ALKIS (Amtliches Liegenschaftskatasterinformationssystem) standard defines various building functions through codes, names, and descriptions. This data is published in HTML format in the Objektartenkatalog.

This script parses the `AX_Gebaeudefunktion.html` file and extracts:
- **Code**: 4-digit function code (e.g., 1000, 1010, 2000)
- **Name**: Function name in German (e.g., "Wohngebäude", "Wohnhaus")
- **Description**: Detailed description of the function

## Requirements

- Python 3.7+
- beautifulsoup4

### Installation

Install the required dependency:

```bash
pip install beautifulsoup4
```

## Usage

### Basic Usage

1. Ensure `AX_Gebaeudefunktion.html` is in the same directory as `buildingFunctionHtmlToCsv.py`

2. Run the script:

```bash
python buildingFunctionHtmlToCsv.py
```

3. The script will create `building_functions.csv` in the same directory

### Output Format

The generated CSV file uses **semicolon (;)** as delimiter to avoid conflicts with commas in the description text:

```csv
code;name;description
1000;Wohngebäude;'Wohngebäude' ist ein Gebäude, das zum Wohnen genutzt wird.
1010;Wohnhaus;'Wohnhaus' ist ein Gebäude, in dem Menschen ihren Wohnsitz haben.
1020;Wohnheim;'Wohnheim' ist ein Gebäude, das nach seiner baulichen Anlage und Ausstattung zur Unterbringung von Studenten, Arbeitern u. a. bestimmt ist.
...
```

## File Descriptions

### buildingFunctionHtmlToCsv.py

Main conversion script with the following functions:

- **`extract_building_functions(html_file)`**: Main extraction function that parses the HTML and returns a list of building function dictionaries

- **`extract_name_from_div(div)`**: Extracts the function name from a table cell

- **`extract_description_from_div(div)`**: Extracts the function description from a table cell

- **`extract_code_from_div(div)`**: Extracts the 4-digit function code, handling formats like "1000 (G)"

- **`save_to_csv(functions, output_file)`**: Writes the extracted data to a CSV file

- **`main()`**: Main execution flow

### AX_Gebaeudefunktion.html

The source HTML file from the ALKIS Objektartenkatalog containing the building function table.

## HTML Structure

The script expects the following HTML structure:

```html
<table class="enum">
  <tbody>
    <tr class="enum">
      <th class="enum name">Bezeichnung</th>
      <th class="enum wert">Wert</th>
    </tr>
    <tr class="enum">
      <td class="enum name">
        <div class="wert">Wohngebäude
          <p class="indent smaller">'Wohngebäude' ist ein Gebäude, das zum Wohnen genutzt wird.</p>
        </div>
      </td>
      <td class="enum wert">
        <div class="wert">1000 (G)</div>
      </td>
    </tr>
    <!-- More rows... -->
  </tbody>
</table>
```

## Error Handling

The script includes robust error handling:

- **Missing HTML file**: Clear error message if input file not found
- **Invalid table structure**: Skips rows with incorrect format
- **Missing data**: Skips rows with missing codes or names
- **Progress reporting**: Shows progress every 50 entries
- **Full traceback**: Detailed error information if conversion fails

## Troubleshooting

### ImportError: No module named 'bs4'

Install BeautifulSoup4:
```bash
pip install beautifulsoup4
```