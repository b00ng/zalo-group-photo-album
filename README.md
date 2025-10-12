# Zalo Group Photo Album

This is an intelligent photo assistant that automatically organizes your photos by the people in them. It uses deep learning to find and group faces, saving you the manual effort of sorting through large photo collections.

## Key Features

- **Automatic Discovery & Clustering:** Point the app at a folder of photos, and it will automatically find all the unique people and group the photos they appear in.
- **Interactive Review Gallery:** After automatic clustering, you are presented with a web gallery where you can review the groups, name them, and correct any mistakes.
- **Specific Person Search:** Provide a few sample photos of a person, and the app will scan a directory to find all photos containing that person and create a dedicated album.
- **Cross-Platform:** Works on Windows 11, macOS, and Ubuntu.
- **CPU & GPU Support:** Runs on standard laptops (CPU) and can leverage NVIDIA GPUs for significantly faster processing.

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

#### Feature A: Cluster Discovery (Automatic Grouping)

This is the default mode. It's best for when you have a folder of photos and you want to discover everyone in it.

1.  On the "Cluster Discovery" page, enter the **full, absolute path** to the folder containing your photos.
2.  Click **"Create Albums"**.
3.  The application will process all the photos. When it's done, you will be redirected to the **Review Gallery**.
4.  In the gallery, you can see all the groups of faces the app found. **Rename the albums** by typing in the text boxes (e.g., change "Person 1" to "John Doe").
5.  Once you are happy with the names, click the **"Save Final Albums"** button at the top. The final, named albums will be created in the `output_albums` directory.

#### Feature B: Search for a Person

This mode is best for when you want to find all photos of one specific person.

1.  Click the **"Search for Person"** link in the navigation bar.
2.  On the search page, fill out the three fields:
    - **Upload Sample Photos:** Upload one or more clear photos of the person you want to find.
    - **Search Folder Path:** Enter the absolute path to the folder you want to search through.
    - **New Album Name:** Give the album a name (e.g., "Photos of Jane").
3.  Click **"Start Search & Create Album"**.
4.  The application will process the photos and show you a log on the page. The final album will be created directly in the `output_albums` directory.
