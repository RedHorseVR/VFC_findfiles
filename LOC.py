#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path
from tabulate import tabulate

def count_lines(file_path):
    """
    Count lines in a file. Consecutive blank lines count as a single line.
    
    Args:
        file_path (str): Path to the file
    
    Returns:
        int: Number of lines
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            
        # Handle consecutive blank lines
        count = 0
        prev_blank = False
        
        for line in lines:
            is_blank = line.strip() == ""
            
            if is_blank:
                if not prev_blank:
                    count += 1
                    prev_blank = True
            else:
                count += 1
                prev_blank = False
                
        return count
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return 0

def find_text_files(directory, extensions):
    """
    Recursively find text files with specified extensions in a directory.
    
    Args:
        directory (str): The directory to search in
        extensions (list): List of file extensions to look for
    
    Returns:
        dict: A dictionary with directories as keys and lists of (file, line_count) tuples as values
    """
    result = {}
    
    for root, dirs, files in os.walk(directory):
        text_files = []
        for file in files:
            for ext in extensions:
                if file.endswith(ext):
                    file_path = os.path.join(root, file)
                    line_count = count_lines(file_path)
                    text_files.append((file, line_count))
                    break
        
        if text_files:
            result[root] = text_files
    
    return result

def print_file_tables(file_dict):
    """
    Print a table for each directory showing the text files found and their line counts.
    
    Args:
        file_dict (dict): Dictionary with directories as keys and lists of (file, line_count) tuples as values
    """
    grand_total_files = 0
    grand_total_lines = 0
    
    for directory, files in file_dict.items():
        print(f"\nFiles in {directory}:")
        
        # Prepare table data
        table_data = []
        dir_total_lines = 0
        
        for i, (file, line_count) in enumerate(files):
            table_data.append([i+1, file, line_count])
            dir_total_lines += line_count
        
        # Add directory totals
        table_data.append(["", f"TOTAL ({len(files)} files)", dir_total_lines])
        
        # Update grand totals
        grand_total_files += len(files)
        grand_total_lines += dir_total_lines
        
        # Print table
        print(tabulate(table_data, headers=["#", "Filename", "Lines"], tablefmt="grid"))
    
    # Print grand totals
    print("\nGRAND TOTAL:")
    print(tabulate([["TOTAL", f"{grand_total_files} files", f"{grand_total_lines} lines"]], 
                   headers=["", "Files", "Lines"], tablefmt="grid"))

def main():
    parser = argparse.ArgumentParser(description="Find text files with specified extensions recursively")
    parser.add_argument("directory", help="Directory to search in")
    parser.add_argument("--extensions", "-e", nargs="+", default=[".txt", ".html", ".py", ".css"],
                        help="File extensions to search for (default: .txt .html .py .css)")
    
    args = parser.parse_args()
    
    # Ensure extensions have dots if not provided
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in args.extensions]
    
    # Check if directory exists
    if not os.path.isdir(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist", file=sys.stderr)
        return 1
    
    # Find the files
    file_dict = find_text_files(args.directory, extensions)
    
    if not file_dict:
        print(f"No files with extensions {', '.join(extensions)} found in {args.directory}")
        return 0
    
    # Print the tables
    print_file_tables(file_dict)
    return 0

if __name__ == "__main__":
    sys.exit(main())