from flask import Flask, render_template, request, send_from_directory
import os
import tempfile
import zipfile
import urllib

app = Flask(__name__)

@app.route("/")
def index():
    """Render the index.html template."""
    return render_template('index.html')

@app.route("/download_pdf")
def download_pdf():
    """Download a PDF file."""
    path = request.args.get('path')
    if not path:
        app.logger.error("No path provided for PDF download.")
        return {"error": "No path provided for PDF download."}, 400
    filename = os.path.basename(path)
    directory = os.path.dirname(path)
    if not os.path.exists(os.path.join(directory, filename)):
        app.logger.error(f"PDF file does not exist: {filename}")
        return {"error": "PDF file does not exist."}, 404
    try:
        return send_from_directory(directory=directory, path=filename, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error downloading PDF: {e}")
        return {"error": "An error occurred while trying to download the PDF."}, 500

@app.route("/convert", methods=['POST'])
def convert_zip_to_pdf():
    """Convert a ZIP file to PDF."""
    app.logger.info("Received request to convert ZIP to PDF.")
    try:
        uploaded_file = request.files['zipFile']
        if uploaded_file.filename == '':
            raise ValueError("No file uploaded.")
        app.logger.info(f"Processing file: {uploaded_file.filename}.")
        temp_dir = tempfile.mkdtemp()
        app.logger.info(f"Temporary directory created at {temp_dir}.")
        zip_path = os.path.join(temp_dir, uploaded_file.filename)
        uploaded_file.save(zip_path)
        app.logger.info(f"ZIP file saved at {zip_path}.")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        app.logger.info("ZIP extraction completed.")
        os.remove(zip_path)
        app.logger.info(f"ZIP file {zip_path} removed.")
        app.logger.debug(f"Contents of {temp_dir}: {os.listdir(temp_dir)}")
        pdf_files = [os.path.join(root, file) for root, dirs, files in os.walk(temp_dir) for file in files if file.endswith(".pdf")]
        if not pdf_files:
            app.logger.error("No PDF files found in the uploaded ZIP.")
            return {"error": "No PDF files found in the uploaded ZIP. Please upload a ZIP containing PDF files."}, 400
        app.logger.info(f"Found {len(pdf_files)} PDF files.")
        table_content = "<table>"
        for pdf_file in pdf_files:
            pdf_name = os.path.basename(pdf_file)
            # Fixing the URL encoding issue for spaces in filenames
            pdf_link = "/download_pdf?path=" + urllib.parse.quote(temp_dir + '/' + pdf_name)
            table_content += f"<tr><td>{pdf_name}</td><td><a href='{pdf_link}' download='{pdf_name}'>Download</a></td></tr>"
        table_content += "</table>"
        app.logger.info("Generated table with download links for PDF files.")
        app.logger.debug(f"Final table content: {table_content}")
        return {"success": True, "table_content": table_content}, 200
    except Exception as e:
        app.logger.error(f"Error in /convert endpoint: {e}")
        return {"error": str(e)}, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)