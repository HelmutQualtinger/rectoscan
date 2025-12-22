# Rectoscan

A Python project for reordering PDF pages.

This README file provides an overview of the project, setup instructions, and usage guidelines.

## Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd rectoscan
    ```
2.  Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```


### Project Description

This project provides a graphical user interface (GUI) application, `reorder_pdf_gui.py`, built with Tkinter, that allows users to reorder pages within a PDF document. The primary function is to rearrange pages according to a specific rule: all odd-numbered pages are placed first in their natural ascending order (1, 3, 5, ...), followed by all even-numbered pages in reverse descending order (..., 8, 6, 4, 2). This is particularly useful for PDFs that may have been double-sided scanned in an interleaved format.

Additionally, the project includes a web application component served by `app.py`, allowing for PDF reordering through a web interface.

### Usage (GUI Application)

1.  **Ensure Dependencies are Installed:**
    Make sure you have followed the installation steps in the "Installation" section above, which includes installing `pypdf`.
    ```bash
    pipenv install pypdf
    ```

2.  **Run the Application:**
    Execute the GUI application from your activated virtual environment:
    ```bash
    python reorder_pdf_gui.py
    ```

3.  **File Selection:**
    *   The application will prompt you to select an input PDF file.
    *   It will then prompt you to specify where to save the reordered PDF, suggesting a default filename (e.g., `your_input_file-reordered.pdf`).

4.  **Processing:**
    Once the files are selected, the application will process the PDF and save the reordered version to your chosen output location.

## Scanning Two-Sided Pages with a Single-Sided Scanner (Corrected Workflow)

To scan double-sided documents using a single-sided scanner and have the back pages appended to the first scan, you can often use your scanner's software features that allow continuing a scan job or adding pages to an existing document. The goal is to produce a single PDF file with an interleaved page order, which can then be corrected.

1.  **Initiate Scan & Scan Front Sides:**
    *   Place your document stack in the scanner's feeder. Orient the pages so that the content intended for the *front* of each final page (e.g., pages 1, 3, 5, ...) is correctly positioned for scanning.
    *   Start the scanning process using your scanner's software. Look for an option to "Continue Scanning," "Add Pages," or similar, rather than "Save" or "Finish Scan."
    *   Scan all the pages. The software should append these scans to the first set of pages you scanned.

2.  **Flip and Scan Back Sides:**
    *   After scanning the front sides and selecting the option to continue scanning, take the *same stack of paper* and flip the entire stack. Ensure the pages are oriented so that the content intended for the *back* of each final page (e.g., pages 2, 4, 6, ...) is correctly positioned.
    *   Complete the scanning process. The software should append these "back" pages to the "front" pages, ideally resulting in a single PDF file.

3.  **Reorder the Resulting PDF:**
    *   The single PDF file you obtain will likely have pages in an interleaved order. For example, it might look like: `1, 3, 5, ..., 6, 4, 2, ...`.
    *   Use the `reorder_pdf_gui.py` script from this project to reorder this single, interleaved PDF into the standard sequential order (1, 2, 3, 4, ...). The script is designed precisely to correct this type of interleaved output.

**Note:** The exact wording and functionality for "Continue Scanning" or "Add Pages" will vary significantly depending on your scanner's model and its accompanying software. If your scanner software does not support appending scans to an existing document in this manner, you may need to revert to the method of creating two separate files and then reordering them.

## Web Container Usage

This project can be run as a web application within a Docker container. This allows for easy deployment and consistent execution across different environments.

### Prerequisites

*   Docker installed on your system.

### Building the Docker Image

Navigate to the root of the project directory (where the `Dockerfile` is located) and run the following command to build the Docker image:

```bash
docker build -t rectoscan-web .
```

This command tags the image as `rectoscan-web`.

### Running the Web Application

Once the image is built, you can run a container from it using the following command:

```bash
docker run -p 8000:8000 rectoscan-web
```

This command maps port 8000 on your host machine to port 8000 inside the container, where the web application is expected to be running (typically served by `app.py`).

### Accessing the Application

After starting the container, you can access the web interface by navigating to:

`http://localhost:8000`

in your web browser. The web interface will provide functionality to upload PDFs and reorder their pages.