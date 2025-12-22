# -*- coding: utf-8 -*-
"""
Tkinter GUI application script for selecting input and output PDF files,
reordering pages based on a general rule, and saving the result as a new PDF.

This script uses Tkinter's file dialogs for user interaction:
1. User selects an input PDF file (assumed to be in standard sequential order 1, 2, 3, ...).
2. A default output filename is generated (e.g., 'input-reordered.pdf').
3. User confirms or changes the output file path and name via a save dialog.
4. The script then reads the input PDF, reorders its pages according to the specified rule,
   and saves the reordered content to the specified output PDF file.

General Reordering Rule:
- Pages are reordered such that:
    1. All odd-numbered pages appear first, in their natural ascending order (1, 3, 5, ...).
    2. Then, all even-numbered pages appear, in their reverse descending order (..., 8, 6, 4, 2).
- This rule applies regardless of the total number of pages (as long as it's even, as per your previous clarification, though the code handles odd numbers too).

To use this script:
1. Ensure you have Python 3.13 installed.
2. Set up your environment using pipenv:
   a. Install pipenv globally if you haven't already:
      pip install pipenv
   b. Navigate to your project directory in the terminal:
      cd /Users/haraldbeker/PythonProjects/rectoscan
   c. Create a Pipfile and a virtual environment for Python 3.13:
      pipenv --python 3.13
   d. Activate the virtual environment:
      pipenv shell
   e. Install necessary libraries (like pypdf for PDF processing):
      pipenv install pypdf
3. Save the code below as a Python file (e.g., reorder_pdf_gui.py).
4. Run the script from your activated terminal:
   python reorder_pdf_gui.py

The script will guide you through selecting files and processing the PDF.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import pypdf # Make sure pypdf is installed

def select_input_pdf() -> str:
    """
    Opens a file dialog to select an input PDF file.
    Filters for PDF files.

    Returns:
        The absolute path to the selected input PDF file, or an empty string if cancelled.
    """
    # Tkinter dialogs can be called without explicitly creating a root window
    # if you don't need to interact with other Tkinter widgets.
    # However, if a root window is not created, Tkinter might create a default one
    # which could briefly flash on screen. Using root.withdraw() is a common practice
    # to prevent this flash.

    file_path = filedialog.askopenfilename(
        title="Select Input PDF File",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        defaultextension=".pdf"
    )
    return file_path

def select_output_pdf(initial_dir: str, initial_file: str) -> str:
    """
    Opens a file dialog to select the output PDF file path for saving.
    Defaults to a specified directory and filename.

    Args:
        initial_dir: The directory to start the dialog in.
        initial_file: The default filename to pre-fill.

    Returns:
        The absolute path for saving the output PDF, or an empty string if cancelled.
    """
    root = tk.Tk()
    root.withdraw() # Hide the main Tkinter window

    # Ensure initialdir is a valid directory path
    if not initial_dir or not os.path.isdir(initial_dir):
        initial_dir = os.getcwd() # Default to current working directory if invalid

    output_path = filedialog.asksaveasfilename(
        title="Save Reordered PDF As",
        initialdir=initial_dir,
        initialfile=initial_file,
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        defaultextension=".pdf"
    )
    return output_path

def generate_reordered_filename(input_filepath: str) -> str:
    """
    Generates the default output filename by appending '-reordered' to the basename
    of the input file, keeping the same directory and ensuring the extension is '.pdf'.

    Args:
        input_filepath: The path to the input PDF file.

    Returns:
        The default path for the reordered output PDF file. Returns an empty string
        if the input_filepath is empty or invalid.
    """
    if not input_filepath or not os.path.exists(input_filepath):
        return "" # Return empty string if input is invalid

    dir_name = os.path.dirname(input_filepath)
    base_and_ext = os.path.basename(input_filepath)
    basename, ext = os.path.splitext(base_and_ext)

    # Ensure the output extension is '.pdf' as requested by the user.
    if ext.lower() != '.pdf':
        ext = ".pdf" # Force output extension to be .pdf

    # Create the new basename by appending '-reordered'
    new_basename = f"{basename}-reordered"
    
    # Construct the full output file path
    output_filepath = os.path.join(dir_name, f"{new_basename}{ext}")
    
    return output_filepath

def reorder_pdf_pages_general_rule(input_pdf_path: str, output_pdf_path: str):
    """
    Reads a PDF in interleaved order (odd pages ascending, then even pages descending)
    and converts it back to sequential order (1, 2, 3, ..., n).

    This is useful for PDFs created by scanning a double-sided document on a single-sided
    scanner by flipping the stack halfway through.

    Input order assumed: 1, 3, 5, ..., n-1, n, n-2, ..., 4, 2
    Output order: 1, 2, 3, 4, ..., n

    Args:
        input_pdf_path: Path to the input PDF file (in interleaved order).
        output_pdf_path: Path where the reordered PDF will be saved.

    Raises:
        FileNotFoundError: If input file does not exist.
        pypdf.errors.PdfReadError: If the input file is not a valid PDF or is corrupted.
        ValueError: If the input PDF contains no pages or an odd number of pages.
        Exception: For other potential errors during processing.
    """
    if not os.path.exists(input_pdf_path):
        raise FileNotFoundError(f"Input file not found: {input_pdf_path}")

    try:
        reader = pypdf.PdfReader(input_pdf_path)
        writer = pypdf.PdfWriter()
        num_pages = len(reader.pages)

        # Check if the number of pages is even. Raise an error if it's odd.
        if num_pages % 2 != 0:
            raise ValueError("Input PDF must have an even number of pages for this reordering rule.")

        if num_pages == 0:
            raise ValueError(f"Input PDF file '{input_pdf_path}' contains no pages.")

        # Generate the interleaved order that the input file currently has
        interleaved_order = []

        # 1. Add odd pages in their natural ascending order
        for i in range(1, num_pages + 1):
            if i % 2 != 0:  # If page number is odd
                interleaved_order.append(i)

        # 2. Add even pages in their reverse descending order
        for i in range(num_pages, 0, -1):
            if i % 2 == 0:  # If page number is even
                interleaved_order.append(i)

        # Create a mapping: logical page number -> position in the input file (0-indexed)
        position_map = {}
        for file_position, logical_page_num in enumerate(interleaved_order):
            position_map[logical_page_num] = file_position

        # Read pages in sequential logical order (1, 2, 3, ..., n)
        # by finding where each page is located in the interleaved input file
        for desired_page_num in range(1, num_pages + 1):
            file_position = position_map[desired_page_num]
            page = reader.pages[file_position]
            writer.add_page(page)

        # Write the reordered PDF to the output file in binary write mode
        with open(output_pdf_path, "wb") as output_file:
            writer.write(output_file)

        print(f"Successfully reordered PDF saved to: {output_pdf_path}")

    except pypdf.errors.PdfReadError as e:
        raise pypdf.errors.PdfReadError(f"PDF reading error: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred during PDF reordering: {e}")

if __name__ == "__main__":
    print("Initializing GUI for PDF reordering process...")

    # 1. Select Input PDF File using Tkinter dialog
    input_pdf_path = select_input_pdf()

    if not input_pdf_path:
        messagebox.showerror("Error", "No input PDF file was selected. Exiting.")
        sys.exit(1)
    
    # 2. Generate the default output filename based on input path
    default_output_filename = generate_reordered_filename(input_pdf_path)
    
    # Determine the initial directory for the save dialog (use input file's directory)
    initial_save_dir = os.path.dirname(input_pdf_path) if input_pdf_path else os.getcwd()

    print(f"Input PDF selected: {input_pdf_path}")
    print("Opening save dialog to determine output file path...")

    # 3. Select Output PDF File location and name using Tkinter dialog
    output_pdf_path = select_output_pdf(
        initial_dir=initial_save_dir, 
        initial_file=os.path.basename(default_output_filename) # Use the derived name as the default
    )

    if not output_pdf_path:
        messagebox.showinfo("Operation Cancelled", "Output file selection was cancelled. Exiting.")
        sys.exit(0)
    
    print(f"Output PDF will be saved to: {output_pdf_path}")
    
    # 4. Perform PDF reordering and saving using the general rule
    try:
        reorder_pdf_pages_general_rule(input_pdf_path, output_pdf_path)
        messagebox.showinfo("Success", f"PDF reordered successfully!\n\nSaved to:\n{output_pdf_path}")
        print("PDF reordering process completed successfully.")
    except FileNotFoundError as fnf_error:
        messagebox.showerror("File Error", str(fnf_error))
        print(f"Error: {fnf_error}")
    except pypdf.errors.PdfReadError as pdf_error:
        messagebox.showerror("PDF Read Error", str(pdf_error))
        print(f"Error: {pdf_error}")
    except ValueError as val_error:
        messagebox.showerror("Processing Error", str(val_error))
        print(f"Error: {val_error}")
    except Exception as e:
        messagebox.showerror("An Unexpected Error Occurred", str(e))
        print(f"Error: {e}")

    print("\nScript finished.")
