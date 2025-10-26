# Zalo Group Photo Album

This is an intelligent photo assistant that automatically organizes your photos by the people in them. It uses deep learning to find and group faces, saving you the manual effort of sorting through large photo collections.

## Key Features

- **Automatic Discovery & Clustering:** Point the app at a folder of photos, and it will automatically find all the unique people and group the photos they appear in.
- **Interactive Review Gallery:** After automatic clustering, you are presented with a web gallery where you can review the groups, name them, and correct any mistakes.
- **Specific Person Search:** Provide a few sample photos of a person, and the app will scan a directory to find all photos containing that person and create a dedicated album.
- **Chronological Timelines:** Each identified person gains a timeline view that orders their photos by capture time for easy storytelling and auditing.
- **Cross-Platform:** Works on Windows 11, macOS, and Ubuntu.
- **CPU & GPU Support:** Runs on standard laptops (CPU) and can leverage NVIDIA GPUs for significantly faster processing.

## Main Features (In Depth)

- Optional Google sign-in lets teams attach identity when credentials are present while keeping albums available anonymously; session details surface in the header and login UX adjusts accordingly (`app.py:52`, `app.py:143`, `templates/index.html:28`, `templates/login.html:11`).
- Automated “Cluster Discovery” detects faces with InsightFace, clusters embeddings with DBSCAN, and shows a review gallery the user can rename before export (`app.py:224`, `photo_processor.py:86`, `photo_processor.py:166`, `templates/gallery.html:34`).
- Album export copies original photos into per-person folders after the user saves their edits, keeping cluster metadata in sync for later sessions (`app.py:249`, `photo_processor.py:256`, `photo_processor.py:223`).
- Targeted “Search for Person” mode averages embeddings from uploaded samples, scans another directory for close matches, and builds a dedicated album (`app.py:173`, `photo_processor.py:280`, `templates/search.html:31`).
- Person timelines reuse cached cluster data to render chronological galleries and serve original photos only from whitelisted roots to prevent path traversal (`app.py:295`, `app.py:327`, `app.py:474`, `templates/timeline_index.html:32`).

## System Flow Overview

- App startup enables optional Google OAuth, prints a warning when credentials are missing, loads the InsightFace model once, and prepares an `output_albums/.cache` workspace for embeddings, crops, and assignments (`app.py:34`, `app.py:52`, `app.py:153`, `photo_processor.py:20`).
- Anonymous visitors can use every feature immediately; when Google sign-in is configured, successful callbacks stash profile details in the session and resume the original request (`app.py:173`, `app.py:506`, `app.py:576`, `templates/login.html:11`).
- In cluster discovery, the user submits a photo directory; the server extracts faces, stores crops and embeddings, computes clusters, and returns structured cluster data for the gallery UI (`app.py:224`, `photo_processor.py:86`, `photo_processor.py:148`, `photo_processor.py:180`).
- The gallery page lets users rename clusters and confirm; the front-end posts the edited clusters back to `/save_albums`, which copies originals into friendly-named folders and updates cached assignments for future timeline views (`templates/gallery.html:28`, `app.py:249`, `photo_processor.py:256`, `photo_processor.py:223`).
- The separate search workflow temporarily saves uploaded samples, logs progress to the page, compares embeddings across the target folder, and copies matches into a new album before cleaning its temp files (`app.py:173`, `app.py:205`, `photo_processor.py:280`).
- Timeline pages read cached assignments and face metadata, group photos by day using stored timestamps, and provide secure links to the original images while blocking requests that escape approved directories (`app.py:295`, `app.py:327`, `app.py:474`, `templates/timeline_detail.html:54`).

---

## Installation Guide

This guide uses the `conda` environment manager to ensure a consistent and isolated setup.

### Prerequisites

You must have Anaconda or Miniconda installed on your system.
- **Windows/macOS:** Download from the [official Anaconda website](https://www.anaconda.com/download).
- **Ubuntu:** Follow the [official installation guide](https://docs.anaconda.com/free/anaconda/install/linux/).

### Setup Steps

1.  **Clone the Repository:**
    First, clone this project to your local machine.
    ```bash
    git clone https://github.com/your-username/zalo-group-photo-album.git
    cd zalo-group-photo-album
    ```

2.  **Create a Conda Environment:**
    Create a new, clean environment for this project. We recommend Python 3.10.
    ```bash
    conda create -n photoalbum python=3.10 -y
    ```

3.  **Activate the Environment:**
    You must activate the environment every time you work on the project.
    ```bash
    conda activate photoalbum
    ```

4.  **Install Dependencies:**
    Install all the required Python libraries from the `requirements.txt` file using `pip`.
    ```bash
    pip install -r requirements.txt
    ```
    This will download and install all necessary packages, including Flask, scikit-learn, and InsightFace.

### Optional Google Sign-In

Google OAuth is optional. Configure it when you want users to identify themselves; otherwise the app runs anonymously.

1. **(Optional) Create Google OAuth Credentials:**  
   - Visit the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
   - Create an OAuth 2.0 Client ID of type **Web application**.
   - Add authorized redirect URIs, including `http://localhost:8080/auth/google/callback` for local development.
2. **(Optional) Configure Environment Variables:**  
   When all variables are present, the app enables the Google sign-in experience. Missing values simply disable the login button.
   ```bash
   export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
   export GOOGLE_CLIENT_SECRET="your-secret"
   export GOOGLE_REDIRECT_URI="http://localhost:8080/auth/google/callback"
   export FLASK_SECRET_KEY="set-a-random-secret"
   ```
3. **Restart the Server:**  
   Restart any running Flask process after updating the environment variables so the changes take effect. Without credentials, the server logs a warning that Google sign-in is disabled and continues to run.

### (Optional) GPU Acceleration Setup

For a significant performance increase, you can configure the application to use an NVIDIA GPU.

1.  **Prerequisites:**
    - An NVIDIA GPU with the latest drivers installed.
    - The NVIDIA CUDA Toolkit installed on your system.

2.  **Install GPU-enabled ONNX Runtime:**
    The `insightface` library uses ONNX Runtime. The `requirements.txt` file installs the CPU version by default. To upgrade, run the following commands:
    ```bash
    pip uninstall onnxruntime
    pip install onnxruntime-gpu
    ```

3.  **Update the Code:**
    In the `photo_processor.py` file, change the following line in the `__init__` method:
    ```python
    # From:
    self.app = FaceAnalysis(providers=['CPUExecutionProvider'])
    # To:
    self.app = FaceAnalysis(providers=['CUDAExecutionProvider'])
    ```

---

## User Guide

### 1. Running the Application

1.  **Activate the environment:**
    ```bash
    conda activate photoalbum
    ```
2.  **Run the Flask web server:**
    ```bash
    flask run --host=0.0.0.0 --port=8080
    ```
3.  **Open your web browser** and navigate to the URL shown in the terminal (e.g., `http://127.0.0.1:8080`).

### 2. Using the Features

The application has two main modes, accessible from the navigation bar at the top of the page.

Signing in with a Google account is optional. When enabled and authenticated, the signed-in account is displayed in the upper-right corner with a sign-out action.

#### Feature A: Cluster Discovery (Automatic Grouping)

This is the default mode. It's best for when you have a folder of photos and you want to discover everyone in it.

1.  On the "Cluster Discovery" page, enter the **full, absolute path** to the folder containing your photos.
2.  Optionally adjust **Clustering Similarity (eps)** or **Minimum Samples** when you want tighter or looser grouping; leave the defaults (0.5 and 2) for behaviour that matches prior releases.
3.  Click **"Create Albums"**.
4.  The application will process all the photos. When it's done, you will be redirected to the **Review Gallery**.
5.  In the gallery, you can see all the groups of faces the app found. **Rename the albums** by typing in the text boxes (e.g., change "Person 1" to "John Doe").
6.  Once you are happy with the names, click the **"Save Final Albums"** button at the top. The final, named albums will be created in the `output_albums` directory.

#### Feature B: Search for a Person

This mode is best for when you want to find all photos of one specific person.

1.  Click the **"Search for Person"** link in the navigation bar.
2.  On the search page, fill out the three fields:
    - **Upload Sample Photos:** Upload one or more clear photos of the person you want to find.
    - **Search Folder Path:** Enter the absolute path to the folder you want to search through.
    - **New Album Name:** Give the album a name (e.g., "Photos of Jane").
3.  Click **"Start Search & Create Album"**.
4.  The application will process the photos and show you a log on the page. The final album will be created directly in the `output_albums` directory.

#### Feature C: Person Timelines

After running clustering, open **Person Timelines** from the navigation bar to browse a chronological gallery for each identified person.

1. Select a person to open their timeline detail page.
2. Photos are grouped by day. Thumbnails use the detected face crop; click any item to open the original photo in a new tab.
3. The header displays the total photo count and the overall date range when timestamps are available.
4. Timelines update automatically when you re-run clustering or rename clusters in the review gallery.

#### Feature D: Group Existing Faces

Use this when you already have cropped faces and `all_faces_data.json` from a previous run and only need to rebuild grouped photo folders.

1. Open **Group Existing Faces** from the navigation bar.
2. Enter the original photo directory and the faces cache directory (must contain `all_faces_data.json`).
3. Optionally set a custom output folder name plus clustering similarity or minimum samples; leave blank to reuse the defaults (0.5 and 2).
4. Click **"Group Faces"** to cluster the cached embeddings and copy the referenced photos into per-person subfolders under `output_albums/<chosen-or-generated-name>/`.

#### Run Cluster Discovery from the Command Line

You can execute the entire extraction → clustering → album export pipeline without starting Flask. This is useful for automated jobs or remote servers.

1. **Install dependencies** (inside a virtual environment if you prefer):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Run the pipeline with Python** (replace the paths and tuning parameters as needed):
   ```bash
   python - <<'PY'
   from photo_processor import PhotoProcessor

   photos_dir = "/absolute/path/to/photos"
   output_dir = "output_albums_cli"

   processor = PhotoProcessor(output_path_base=output_dir)
   faces = processor.extract_faces(photos_dir)
   if not faces:
       raise SystemExit("No faces detected; nothing to cluster.")

   labels = processor.cluster_faces(faces, eps=0.5, min_samples=2)
   clusters = processor.generate_cluster_ui_data(faces, labels)
   PhotoProcessor.save_final_albums(clusters, faces, output_dir)

   print(f"Created grouped albums in: {output_dir}")
   PY
   ```
3. **Customize clustering behaviour** by editing the `eps` (similarity threshold) and `min_samples` arguments before rerunning the script.
4. **Review the results**: grouped folders will appear under `output_dir`, each containing the original photos for that cluster. Cached face crops and metadata live in `output_dir/.cache/`.

---

## Manual Verification Checklist

Use Google test credentials (or a dedicated workspace test account) to verify the optional authentication flow:

1. **Startup Without Credentials:** Launch the server without Google OAuth environment variables and confirm it logs a warning but still serves the app.
2. **Anonymous Access Works:** Visit `http://localhost:8080/` in a private browser window and verify you stay on the main page with an optional “Sign in with Google” link when OAuth is configured.
3. **Anonymous Timeline Access:** Navigate to `/timeline` and `/timeline/<id>` without signing in to confirm the pages load normally.
4. **Successful Sign-In (Optional):** After providing credentials, click **Continue with Google**, complete the OAuth consent screen, and verify that the home page shows your Google name/avatar in the header.
5. **State Mismatch Handling:** Start the login flow, then manually remove the `state` parameter from the callback URL before submitting. Confirm you return to the login page with an error message.
6. **Sign-Out:** Click **Sign out** and confirm you return to the login page (when enabled) or the main page (when login is disabled) and the header no longer shows account info.
7. **EXIF Timestamp Extraction:** Upload a photo with a known EXIF `DateTimeOriginal` value and confirm the person’s timeline groups the image under the expected day and shows the correct time.
8. **Filesystem Fallback:** Upload a photo without EXIF metadata and ensure the timeline still lists it (labelled with the fallback timestamp source).
9. **Secure Photo Serving:** Copy a timeline photo link, edit the URL to target a disallowed path, and confirm the server responds with HTTP 403.
10. **Reuse Cached Faces (Success):** Point the Group Existing Faces flow at a photo directory and matching cache (containing `all_faces_data.json`) and confirm grouped albums plus the success summary are created.
11. **Reuse Cached Faces (Validation):** Run the flow with a cache missing `all_faces_data.json` or referencing files outside the supplied photo directory and ensure a clear error is displayed without creating output.
12. **CLI Cluster Discovery:** Execute the command-line workflow using a sample album, adjust `eps`/`min_samples`, and confirm grouped folders and cache artifacts are written to the specified output directory.
