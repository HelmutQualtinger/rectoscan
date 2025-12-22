import os
import uuid # To generate unique filenames for uploads
from flask import Flask, request, redirect, url_for, render_template, render_template_string, send_from_directory, abort, flash
from werkzeug.utils import secure_filename
import pypdf

# --- Configuration ---
# Define folders for uploads and reordered files
UPLOAD_FOLDER = 'uploads'
REORDERED_FOLDER = 'reordered'
ALLOWED_EXTENSIONS = {'pdf'}
# Set a limit for maximum upload file size (e.g., 16MB)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REORDERED_FOLDER'] = REORDERED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
# A secret key is needed for session management (e.g., flashing messages)
app.secret_key = os.urandom(24) 

# Create upload and reordered folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REORDERED_FOLDER'], exist_ok=True)

# --- Helper Functions ---

def allowed_file(filename):
    """Checks if the filename has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def reorder_pdf_pages(input_pdf_path: str, output_pdf_path: str) -> tuple:
    """
    Reads a PDF in interleaved order (odd pages ascending, then even pages descending)
    and converts it back to sequential order (1, 2, 3, ..., n).
    Returns (True, None) on success, (False, error_message) on failure.
    """
    try:
        reader = pypdf.PdfReader(input_pdf_path)
        writer = pypdf.PdfWriter()
        num_pages = len(reader.pages)

        if num_pages == 0:
            return False, "Die PDF-Datei enthält keine Seiten."

        # Check if even number of pages, as per previous requirement context
        if num_pages % 2 != 0:
            return False, f"Die PDF-Datei muss eine gerade Anzahl von Seiten haben. Diese Datei hat {num_pages} Seiten."

        # Generate the interleaved order: odd pages ascending, then even pages descending
        interleaved_order = []
        # Add odd pages in their natural ascending order
        for i in range(1, num_pages + 1):
            if i % 2 != 0:
                interleaved_order.append(i)
        # Add even pages in their reverse descending order
        for i in range(num_pages, 0, -1):
            if i % 2 == 0:
                interleaved_order.append(i)

        # Create a mapping: logical page number -> position in the input file (0-indexed)
        position_map = {}
        for file_position, logical_page_num in enumerate(interleaved_order):
            position_map[logical_page_num] = file_position

        # Reconstruct the PDF in sequential logical order (1, 2, 3, ..., n)
        for desired_page_num in range(1, num_pages + 1):
            file_position = position_map[desired_page_num]
            page = reader.pages[file_position]
            writer.add_page(page)

        # Write the reordered PDF to the output file
        with open(output_pdf_path, "wb") as output_file:
            writer.write(output_file)

        return True, None # Indicate success

    except FileNotFoundError:
        error_msg = f"Eingabedatei nicht gefunden: {input_pdf_path}"
        print(f"Error: {error_msg}")
        return False, error_msg
    except pypdf.errors.PdfReadError as e:
        error_msg = f"PDF-Lesefehler: Die Datei ist möglicherweise beschädigt oder kein gültiges PDF. Fehlerdetails: {str(e)}"
        print(f"PDF Read Error: {e}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Fehler beim Umordnen: {str(e)}"
        print(f"An unexpected error occurred during PDF reordering: {e}")
        return False, error_msg

# --- HTML Template for Upload Form ---
# Using render_template_string for simplicity. Using raw string r"""...""" to prevent issues with backslashes.
UPLOAD_FORM_HTML = r"""
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>PDF Reorder Web Service</title>
    <style>
        body { font-family: sans-serif; margin: 20px; }
        .container { max-width: 700px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .flashes { list-style: none; padding: 0; margin-bottom: 15px; }
        .flashes li { padding: 10px; margin-bottom: 10px; border-radius: 4px; }
        .flashes li.error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .flashes li.success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        form { margin-top: 20px; }
        input[type=file] { margin-bottom: 10px; }
        input[type=submit] { background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        input[type=submit]:hover { background-color: #0056b3; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .download-link { margin-top: 20px; padding: 10px 15px; border: 1px solid #007bff; border-radius: 5px; display: inline-block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>PDF Reordering Service</h1>
        <p>Upload a PDF file (must have an even number of pages) to have its pages reordered.</p>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            <ul class=flashes>
            {% for category, message in messages %}
              <li class="{{ category }}">{{ message }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        
        <form method=post enctype=multipart/form-data action="{{ url_for('upload_file') }}">
          <input type=file name=file accept=".pdf">
          <br>
          <input type=submit value=Upload and Reorder>
        </form>
        
        {% if reordered_file_url %}
          <div class="download-link">
            <p><strong>File Reordered Successfully!</strong></p>
            <p><a href="{{ reordered_file_url }}" download>Download Reordered PDF</a></p>
          </div>
        {% endif %}
    </div>
</body>
</html>
"""
# --- Routes ---

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    reordered_file_url = None
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            # Generate a unique filename to avoid collisions and preserve original name structure
            unique_id = str(uuid.uuid4())[:8] # Use a shorter unique ID
            temp_upload_filename = f"{unique_id}_{original_filename}"
            temp_upload_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_upload_filename)
            
            try:
                file.save(temp_upload_path)

                # Define output path for the reordered file
                reordered_filename = f"reordered_{unique_id}_{original_filename}"
                output_pdf_path = os.path.join(app.config['REORDERED_FOLDER'], reordered_filename)

                # Reorder the PDF
                success, error_message = reorder_pdf_pages(temp_upload_path, output_pdf_path)

                if success:
                    flash(f'Datei "{original_filename}" erfolgreich hochgeladen und umgeordnet!', 'success')
                    # Construct URL for download
                    reordered_file_url = url_for('download_file', filename=reordered_filename)
                    # Optionally, remove the original uploaded file after successful reordering
                    # os.remove(temp_upload_path)
                else:
                    # Flash detailed error message from reorder_pdf_pages
                    flash(f'Fehler beim Umordnen von "{original_filename}": {error_message}', 'error')
                    # Optionally, remove the failed upload if it wasn't removed already
                    if os.path.exists(temp_upload_path):
                        os.remove(temp_upload_path)

            except Exception as e:
                # Catch any unexpected errors during file saving or processing
                flash(f'Ein unerwarteter Fehler ist aufgetreten: {str(e)}', 'error')
                # Clean up temp file if it exists and an error occurred
                if os.path.exists(temp_upload_path):
                    os.remove(temp_upload_path)

            # Render the template again, showing messages and the download link if successful
            return render_template('index.html', reordered_file_url=reordered_file_url)
        else:
            flash('Invalid file type. Please upload a PDF file.', 'error')
            return redirect(request.url)
            
    # If GET request, just show the upload form
    return render_template('index.html', reordered_file_url=None)

@app.route('/download/<filename>')
def download_file(filename):
    """Download a reordered PDF file."""
    # Validate filename to prevent directory traversal attacks
    if '..' in filename or filename.startswith('/'):
        abort(400)

    try:
        return send_from_directory(app.config['REORDERED_FOLDER'], filename, as_attachment=False)
    except FileNotFoundError:
        abort(404)

# --- Main execution (for running locally, not for Docker) ---
# This block is used when running the script directly (e.g., python app.py)
# It is not used when running with 'flask run'.
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
