#!/usr/bin/env python3
"""
CSV Cleaner for Knowledge Base Exports

This script cleans exported CSV files from the knowledge base app by:
- Removing HTML/XML tags from Title column (keeping only clean text)
- Extracting clean Summary from raw_text (removing all markup)
- Preserving Project, Topics, Date, and Source values
- Merging split multi-line task records
- Handling malformed XML tags
- Outputting a clean, Excel-friendly CSV

Usage:
    python clean_csv_export.py input.csv [output.csv]
    
    If output.csv is not specified, creates 'cleaned_<input_filename>.csv'
"""

import csv
import re
import sys
import html
from typing import List, Dict, Optional, Tuple
from pathlib import Path


# ============================================================================
# HTML/XML Tag Removal
# ============================================================================

def remove_html_tags(text: str) -> str:
    """
    Remove all HTML and XML tags from text, including:
    - Standard HTML tags: <div>, <span>, <p>, etc.
    - Confluence-specific tags: <ac:task>, <ac:task-id>, etc.
    - Malformed tags: <ac:task-bod>, <ac-tack-bodys>, etc.
    - Self-closing tags: <br/>, <hr/>, etc.
    - Comments: <!-- ... -->
    
    Args:
        text: Input string potentially containing HTML/XML tags
        
    Returns:
        Plain text with all tags removed
    """
    if not text or not isinstance(text, str):
        return ""
    
    # First, decode HTML entities (e.g., &rsquo; -> ', &nbsp; -> space)
    text = html.unescape(text)
    
    # Remove XML/HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Remove all XML/HTML tags (including malformed ones)
    # This regex matches <tag> or <tag attr="value"> or </tag> or <tag/>
    # Also handles malformed tags like <ac:task-bod> or <ac-tack-bodys>
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Remove any remaining XML/HTML artifacts
    text = re.sub(r'&[a-z]+;', '', text, flags=re.IGNORECASE)
    
    return text.strip()


def extract_task_body_content(text: str) -> str:
    """
    Extract content from task-body tags, handling both well-formed and malformed tags.
    Handles variations like:
    - <ac:task-body>...</ac:task-body>
    - <ac:task-bod>...</ac:task-bod>
    - <ac:task-bodusconan>...</ac:task-bodusconan>
    - <ac-tack-bodys>...</ac-tack-bodys>
    
    Args:
        text: Input string containing task body tags
        
    Returns:
        Extracted plain text content
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Decode HTML entities first
    text = html.unescape(text)
    
    # Try to match well-formed task-body tags
    patterns = [
        r'<ac:task-body[^>]*>(.*?)</ac:task-body>',  # Well-formed
        r'<ac:task-bod[^>]*>(.*?)</ac:task-bod[^>]*>',  # Malformed: task-bod
        r'<ac:task-bod[^>]*>(.*?)</ac-tack-bodys>',  # Malformed: mismatched closing
        r'<ac:task-bodusconan[^>]*>(.*?)</ac:task-bodusconan>',  # Very malformed
        r'<ac-tack-bodys[^>]*>(.*?)</ac-tack-bodys>',  # Malformed opening too
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            # Combine all matches and clean them
            content = ' '.join(matches)
            return remove_html_tags(content)
    
    # If no task-body tag found, try to extract any meaningful text
    return remove_html_tags(text)


def extract_title_from_summary(summary: str, max_length: int = 100) -> str:
    """
    Extract a clean title from summary text.
    Uses the first sentence or first N characters as title.
    
    Args:
        summary: Summary text to extract title from
        max_length: Maximum length for title
        
    Returns:
        Clean title string
    """
    if not summary:
        return ""
    
    # Remove all tags first
    cleaned = remove_html_tags(summary)
    
    if not cleaned:
        return ""
    
    # Try to extract first sentence (ending with . ! ?)
    sentence_match = re.match(r'^([^.!?]+[.!?])', cleaned)
    if sentence_match:
        title = sentence_match.group(1).strip()
        if len(title) <= max_length:
            return title
    
    # If no sentence ending found, use first N characters
    if len(cleaned) > max_length:
        # Try to break at word boundary
        truncated = cleaned[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.7:  # Only break if we're not too short
            return truncated[:last_space].strip() + "..."
        return truncated.strip() + "..."
    
    return cleaned.strip()


# ============================================================================
# Task Record Merging
# ============================================================================

def is_task_start(row: List[str]) -> bool:
    """
    Check if a row marks the start of a task record.
    Task records typically start with <ac:task> or similar tags.
    
    Args:
        row: List of cell values
        
    Returns:
        True if this row starts a task record
    """
    if not row or len(row) == 0:
        return False
    
    # Check all cells for task start tags
    row_text = ' '.join([str(cell) for cell in row if cell])
    return bool(re.search(r'<ac:task[>\s]', row_text, re.IGNORECASE))


def is_task_continuation(row: List[str]) -> bool:
    """
    Check if a row is a continuation of a task record.
    Continuation rows contain task-related tags like <ac:task-id>, <ac:task-body>, etc.
    
    Args:
        row: List of cell values
        
    Returns:
        True if this row continues a task record
    """
    if not row or len(row) == 0:
        return False
    
    # Check if any cell contains task-related tags
    row_text = ' '.join([str(cell) for cell in row if cell])
    task_patterns = [
        r'<ac:task-id>',
        r'<ac:task-uuid>',
        r'<ac:task-status>',
        r'<ac:task-body>',
        r'<ac:task-bod',  # Malformed variants
        r'</ac:task>',
        r'</ac-tack',  # Malformed closing
    ]
    
    return any(re.search(pattern, row_text, re.IGNORECASE) for pattern in task_patterns)


def extract_task_content(task_rows: List[List[str]]) -> str:
    """
    Extract meaningful content from a series of task rows.
    Combines task body content and removes all markup.
    
    Args:
        task_rows: List of rows that form a complete task record
        
    Returns:
        Cleaned task content as plain text
    """
    content_parts = []
    
    for row in task_rows:
        # Combine all cells in the row
        row_text = ' '.join([str(cell) for cell in row if cell])
        
        # Extract task body content (handles malformed tags)
        task_body_content = extract_task_body_content(row_text)
        if task_body_content:
            content_parts.append(task_body_content)
        else:
            # If no task-body tag, try to extract any meaningful text
            cleaned = remove_html_tags(row_text)
            # Skip if it's just tag names, IDs, or status
            if cleaned and not re.match(r'^(task|incomplete|complete|\d+|[a-f0-9-]{36})$', cleaned, re.IGNORECASE):
                # Skip UUIDs and task IDs
                if not re.match(r'^[a-f0-9-]{36}$', cleaned, re.IGNORECASE):
                    content_parts.append(cleaned)
    
    return ' '.join(content_parts).strip()


# ============================================================================
# Row Processing and Normalization
# ============================================================================

def normalize_cell_value(value: str, column_name: str, headers: List[str], row_data: Dict[str, str]) -> str:
    """
    Normalize a cell value based on its column type.
    Applies column-specific cleaning rules.
    
    Args:
        value: Raw cell value
        column_name: Name of the column (Title, Summary, Project, etc.)
        headers: All column headers (for context)
        row_data: Dictionary of all row values by column name (for cross-column logic)
        
    Returns:
        Normalized cell value
    """
    if not value or not isinstance(value, str):
        return ""
    
    column_lower = column_name.lower()
    
    # Title column: Remove all tags, extract clean title
    if column_lower == 'title':
        # If title contains tags, clean it completely
        cleaned = remove_html_tags(value)
        # If title is empty or just tags, try to extract from summary
        if not cleaned or len(cleaned) < 3:
            summary = row_data.get('summary', '') or row_data.get('Summary', '')
            if summary:
                cleaned = extract_title_from_summary(summary)
        return cleaned
    
    # Summary column: Remove all tags, extract task body content if present
    elif column_lower == 'summary':
        # First try to extract task body content (handles malformed tags)
        task_content = extract_task_body_content(value)
        if task_content:
            return task_content
        # Otherwise just remove all tags
        cleaned = remove_html_tags(value)
        # Preserve URLs
        urls = re.findall(r'https?://[^\s<>]+', value)
        if urls and not any(url in cleaned for url in urls):
            cleaned = f"{cleaned} {' '.join(urls)}"
        return cleaned
    
    # Topics column: Normalize separators, clean tags
    elif column_lower == 'topics':
        cleaned = remove_html_tags(value)
        # Normalize separators (semicolon, comma, pipe)
        cleaned = re.sub(r'[,;|]\s*', '; ', cleaned)
        # Remove empty topic entries
        topics = [t.strip() for t in cleaned.split(';') if t.strip()]
        return '; '.join(topics)
    
    # Project, Date, Source: Just remove tags, preserve value
    elif column_lower in ['project', 'date', 'source']:
        cleaned = remove_html_tags(value)
        # Remove any stray XML/HTML artifacts
        cleaned = re.sub(r'[<>]', '', cleaned)
        return cleaned.strip()
    
    # Default: Remove all tags
    else:
        return remove_html_tags(value)


def is_empty_row(row: List[str], headers: List[str]) -> bool:
    """
    Check if a row contains no meaningful information.
    A row is considered empty if all cells are empty or contain only markup.
    
    Args:
        row: List of cell values
        headers: List of column headers
        
    Returns:
        True if the row should be discarded
    """
    if not row:
        return True
    
    # Pad row to match header length
    while len(row) < len(headers):
        row.append("")
    
    # Check each cell
    for i, cell in enumerate(row[:len(headers)]):
        if not cell:
            continue
        
        cell_str = str(cell).strip()
        
        # Skip if cell is empty
        if not cell_str:
            continue
        
        # Skip if cell contains only tags (no actual text)
        text_without_tags = remove_html_tags(cell_str)
        # Also check if it's just task metadata (IDs, UUIDs, status)
        if text_without_tags and not re.match(r'^(task|incomplete|complete|\d+|[a-f0-9-]{36})$', text_without_tags, re.IGNORECASE):
            # Check if it's a UUID
            if not re.match(r'^[a-f0-9-]{36}$', text_without_tags, re.IGNORECASE):
                return False  # Found meaningful content
    
    return True  # No meaningful content found


# ============================================================================
# Main Processing Function
# ============================================================================

def process_csv(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Main function to process and clean a CSV file.
    
    Args:
        input_path: Path to input CSV file
        output_path: Path to output CSV file (optional)
        
    Returns:
        Path to the cleaned output file
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Determine output path
    if not output_path:
        output_path = input_file.parent / f"cleaned_{input_file.name}"
    else:
        output_path = Path(output_path)
    
    print(f"Reading CSV from: {input_path}")
    
    # Read input CSV
    rows = []
    headers = []
    
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        # Try to detect delimiter
        sample = f.read(1024)
        f.seek(0)
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter
        
        reader = csv.reader(f, delimiter=delimiter)
        
        # Read headers
        try:
            headers = next(reader)
            # Normalize header names (strip whitespace, handle BOM)
            headers = [h.strip().strip('\ufeff').strip('"') for h in headers]
            print(f"Found columns: {', '.join(headers)}")
        except StopIteration:
            raise ValueError("CSV file is empty or has no headers")
        
        # Read all rows
        for row in reader:
            rows.append(row)
    
    print(f"Read {len(rows)} data rows")
    
    # Process rows
    cleaned_rows = []
    i = 0
    
    while i < len(rows):
        current_row = rows[i]
        
        # Skip empty rows
        if is_empty_row(current_row, headers):
            i += 1
            continue
        
        # Check if this is the start of a task record
        if is_task_start(current_row):
            # Collect all rows that are part of this task
            task_rows = [current_row]
            i += 1
            
            while i < len(rows) and is_task_continuation(rows[i]):
                task_rows.append(rows[i])
                i += 1
            
            # Extract task content
            task_content = extract_task_content(task_rows)
            
            if task_content:
                # Create a new cleaned row
                cleaned_row = [""] * len(headers)
                
                # Build row data dictionary for cross-column logic
                row_data = {}
                for j, header in enumerate(headers):
                    if j < len(task_rows[0]):
                        row_data[header] = str(task_rows[0][j]) if task_rows[0][j] else ""
                
                # Process each column
                for j, header in enumerate(headers):
                    if j < len(task_rows[0]):
                        cell_value = str(task_rows[0][j]) if task_rows[0][j] else ""
                    else:
                        cell_value = ""
                    
                    # Special handling for Summary column - use extracted task content
                    if header.lower() == 'summary':
                        cleaned_row[j] = task_content
                    # Special handling for Title - extract from task content
                    elif header.lower() == 'title':
                        title = extract_title_from_summary(task_content)
                        cleaned_row[j] = title
                    else:
                        # Normalize other columns
                        cleaned_row[j] = normalize_cell_value(
                            cell_value, 
                            header, 
                            headers, 
                            row_data
                        )
                
                # Check if we should preserve Project, Topics, Date, Source from other rows
                # Look through all task rows for these values
                for task_row in task_rows[1:]:
                    for j, header in enumerate(headers):
                        if j < len(task_row) and task_row[j]:
                            header_lower = header.lower()
                            if header_lower in ['project', 'topics', 'date', 'source']:
                                value = str(task_row[j]).strip()
                                if value and not cleaned_row[j]:
                                    cleaned_row[j] = normalize_cell_value(
                                        value, 
                                        header, 
                                        headers, 
                                        row_data
                                    )
                
                cleaned_rows.append(cleaned_row)
            continue
        
        # Normal row processing
        # Build row data dictionary for cross-column logic
        row_data = {}
        for j, header in enumerate(headers):
            if j < len(current_row):
                row_data[header] = str(current_row[j]) if current_row[j] else ""
        
        cleaned_row = []
        for j, header in enumerate(headers):
            if j >= len(current_row):
                cleaned_row.append("")
                continue
            
            cell_value = str(current_row[j]) if current_row[j] else ""
            cleaned_value = normalize_cell_value(cell_value, header, headers, row_data)
            cleaned_row.append(cleaned_value)
        
        # Pad to match header length
        while len(cleaned_row) < len(headers):
            cleaned_row.append("")
        
        # Only add row if it has meaningful content
        if not is_empty_row(cleaned_row, headers):
            cleaned_rows.append(cleaned_row)
        
        i += 1
    
    print(f"Processed {len(cleaned_rows)} cleaned rows")
    
    # Write output CSV
    print(f"Writing cleaned CSV to: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        
        # Write headers
        writer.writerow(headers)
        
        # Write cleaned rows
        for row in cleaned_rows:
            writer.writerow(row)
    
    print(f"✅ Successfully created cleaned CSV: {output_path}")
    print(f"   Original rows: {len(rows)}")
    print(f"   Cleaned rows: {len(cleaned_rows)}")
    
    return str(output_path)


# ============================================================================
# Command Line Interface
# ============================================================================

def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python clean_csv_export.py <input.csv> [output.csv]")
        print("\nExample:")
        print("  python clean_csv_export.py export.csv")
        print("  python clean_csv_export.py export.csv cleaned_export.csv")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result_path = process_csv(input_path, output_path)
        print(f"\n✨ Done! Cleaned file saved to: {result_path}")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
