from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import sys
import io
import shutil
from werkzeug.utils import secure_filename
from photo_processor import PhotoProcessor

app = Flask(__name__)

# --- CONFIGURATION ---
OUTPUT_DIR = "output_albums"

# --- INITIALIZATION ---
print("Loading InsightFace model, this may take a moment...")
# Pass the output directory to the processor so it knows where to create the .cache
processor = PhotoProcessor(output_path_base=OUTPUT_DIR)
print("Model loaded successfully.")


# --- ROUTES ---
@app.route('/')
def index():
    """Serves the main page where the user provides the input folder."""
    return render_template('index.html')

@app.route('/search')
def search():
    """Serves the new page for searching for a specific person."""
    return render_template('search.html')

@app.route('/run_search', methods=['POST'])
def run_search():
    """Handles the search form submission."""
    sample_files = request.files.getlist('sample_files')
    search_path = request.form.get('search_path')
    album_name = request.form.get('album_name')

    if not all([sample_files, search_path, album_name]):
        return render_template('search.html', status_message="Error: All fields are required.")

    if not os.path.isdir(search_path):
        return render_template('search.html', status_message=f"Error: Search directory not found.")

    # Save sample files to a temporary location within the cache
    sample_paths = []
    temp_sample_dir = os.path.join(processor.cache_path, "temp_samples")
    os.makedirs(temp_sample_dir, exist_ok=True)
    for file in sample_files:
        if file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(temp_sample_dir, filename)
            file.save(filepath)
            sample_paths.append(filepath)

    if not sample_paths:
        return render_template('search.html', status_message="Error: No valid sample files were uploaded.")

    # Capture print statements to show as a log
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        processor.search_for_person(sample_paths, search_path, album_name)
        status_message = captured_output.getvalue()
    except Exception as e:
        status_message = f"An unexpected error occurred: {e}\n"
        status_message += captured_output.getvalue()
    finally:
        sys.stdout = old_stdout
        # Clean up temp sample files
        shutil.rmtree(temp_sample_dir)

    return render_template('search.html', status_message=status_message)


@app.route('/process', methods=['POST'])
def process():
    """
    Handles the initial processing request for cluster discovery.
    """
    folder_path = request.form.get('folder_path')

    if not folder_path or not os.path.isdir(folder_path):
        return render_template('index.html', status_message=f"Error: Invalid folder path.")

    all_faces = processor.extract_faces(folder_path)
    if not all_faces:
        return render_template('index.html', status_message="No faces found in the provided directory.")

    labels = processor.cluster_faces(all_faces)
    cluster_data = processor.generate_cluster_ui_data(all_faces, labels)
    
    return render_template('gallery.html', clusters=cluster_data)

@app.route('/save_albums', methods=['POST'])
def save_albums():
    """
    Receives the corrected cluster data from the UI and saves the final albums.
    """
    corrected_clusters = request.json.get('clusters')
    
    try:
        with open(os.path.join(processor.cache_path, 'all_faces_data.json'), 'r') as f:
            all_faces_data = json.load(f)
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "Cache data not found. Please re-process images."}), 400

    PhotoProcessor.save_final_albums(corrected_clusters, all_faces_data, OUTPUT_DIR)
    
    return jsonify({"status": "success", "message": "Albums saved successfully!"})

@app.route('/output_albums/.cache/faces/<path:filename>')
def serve_cached_faces(filename):
    """Serves the cropped face images from the cache directory."""
    return send_from_directory(processor.faces_cache_path, filename)


# --- MAIN ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
