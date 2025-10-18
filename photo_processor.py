import json
import os
import shutil
from datetime import datetime, timezone
from typing import List, Optional, Tuple

import cv2
import insightface
import numpy as np
from PIL import ExifTags, Image
from insightface.app import FaceAnalysis
from sklearn.cluster import DBSCAN


EXIF_DATETIME_KEYS = ["DateTimeOriginal", "DateTimeDigitized", "DateTime"]
EXIF_TAG_MAP = {v: k for k, v in ExifTags.TAGS.items() if isinstance(v, str)}


class PhotoProcessor:
    def __init__(self, output_path_base: str = "output_albums"):
        """
        Initializes the PhotoProcessor, loading the InsightFace model and setting up cache paths.
        """
        self.app = FaceAnalysis(providers=["CPUExecutionProvider"])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        self.output_path = output_path_base
        self.cache_path = os.path.join(self.output_path, ".cache")
        self.faces_cache_path = os.path.join(self.cache_path, "faces")
        self.faces_cache_file = os.path.join(self.cache_path, "all_faces_data.json")
        self.cluster_assignments_path = os.path.join(
            self.cache_path, "cluster_assignments.json"
        )
        os.makedirs(self.faces_cache_path, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Timestamp helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _read_exif_timestamp(image_path: str) -> Optional[str]:
        """Attempt to extract a timestamp from EXIF DateTime fields."""
        try:
            with Image.open(image_path) as img:
                exif_data = img._getexif() or {}
        except Exception:
            return None

        for key_name in EXIF_DATETIME_KEYS:
            tag_id = EXIF_TAG_MAP.get(key_name)
            if not tag_id:
                continue
            raw_value = exif_data.get(tag_id)
            if not raw_value:
                continue

            if isinstance(raw_value, bytes):
                try:
                    raw_value = raw_value.decode("utf-8")
                except Exception:
                    continue

            try:
                parsed = datetime.strptime(raw_value, "%Y:%m:%d %H:%M:%S")
                return parsed.isoformat(timespec="seconds")
            except ValueError:
                continue
        return None

    @staticmethod
    def _determine_photo_timestamp(image_path: str) -> Tuple[Optional[str], str]:
        """Determine the best available timestamp for a source photo."""
        exif_timestamp = PhotoProcessor._read_exif_timestamp(image_path)
        if exif_timestamp:
            return exif_timestamp, "exif"

        try:
            modified_time = datetime.fromtimestamp(
                os.path.getmtime(image_path), tz=timezone.utc
            )
            return modified_time.isoformat(timespec="seconds"), "file_modified"
        except Exception:
            return None, "unknown"

    # ------------------------------------------------------------------ #
    # Core processing
    # ------------------------------------------------------------------ #
    def extract_faces(self, input_path: str) -> List[dict]:
        """
        Extracts all faces from images in a directory, saves cropped faces, and returns face data.
        """
        print(f"Starting face extraction for directory: {input_path}")
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
        all_faces = []
        try:
            image_files = [
                os.path.join(input_path, f)
                for f in os.listdir(input_path)
                if os.path.splitext(f)[1].lower() in image_extensions
            ]
        except FileNotFoundError:
            print(f"Error: Input directory not found at {input_path}")
            return []

        print(f"Found {len(image_files)} images to process.")

        face_id_counter = 0
        for image_path in image_files:
            try:
                taken_at, timestamp_source = self._determine_photo_timestamp(image_path)
                img = cv2.imread(image_path)
                if img is None:
                    print(f"Could not read image: {image_path}")
                    continue

                faces = self.app.get(img)
                if not faces:
                    continue

                print(
                    f"Found {len(faces)} faces in: {os.path.basename(image_path)}"
                )
                for face in faces:
                    bbox = face.bbox.astype(int)
                    x1, y1, x2, y2 = bbox
                    cropped_face = img[y1:y2, x1:x2]

                    face_filename = f"face_{face_id_counter}.jpg"
                    face_filepath = os.path.join(self.faces_cache_path, face_filename)
                    cv2.imwrite(face_filepath, cropped_face)

                    all_faces.append(
                        {
                            "face_id": face_id_counter,
                            "embedding": face.embedding,
                            "original_path": image_path,
                            "face_image_path": face_filepath,
                            "taken_at": taken_at,
                            "timestamp_source": timestamp_source,
                        }
                    )
                    face_id_counter += 1
            except Exception as exc:
                print(f"An error occurred while processing {image_path}: {exc}")

        print(f"Total faces extracted: {len(all_faces)}")
        self.save_face_data(all_faces)
        return all_faces

    def save_face_data(self, all_faces: List[dict]) -> None:
        """Saves the extracted face data (including embeddings) to a JSON file in the cache."""
        serializable_faces = [
            {
                "face_id": face["face_id"],
                "embedding": face["embedding"].tolist(),
                "original_path": face["original_path"],
                "face_image_path": face["face_image_path"],
                "face_image_url": f"/output_albums/.cache/faces/{os.path.basename(face['face_image_path'])}",
                "taken_at": face.get("taken_at"),
                "timestamp_source": face.get("timestamp_source"),
            }
            for face in all_faces
        ]
        os.makedirs(self.cache_path, exist_ok=True)
        with open(self.faces_cache_file, "w") as cache_file:
            json.dump(serializable_faces, cache_file)

    def cluster_faces(self, all_faces: List[dict], eps: float = 0.5) -> np.ndarray:
        """Clusters faces based on their embeddings and returns the labels."""
        if not all_faces:
            return np.array([])

        embeddings = np.array([face["embedding"] for face in all_faces])
        clusterer = DBSCAN(metric="euclidean", eps=eps, min_samples=2)
        clusterer.fit(embeddings)
        cluster_count = len(set(clusterer.labels_)) - (
            1 if -1 in clusterer.labels_ else 0
        )
        print(f"Clustering complete. Found {cluster_count} clusters.")
        return clusterer.labels_

    def generate_cluster_ui_data(
        self, all_faces: List[dict], labels: np.ndarray
    ) -> List[dict]:
        """Generates a data structure of the clusters suitable for a UI."""
        clusters = {}
        cluster_assignments = {}

        for i, label in enumerate(labels):
            label = int(label)
            face_data = all_faces[i]

            if label not in clusters:
                default_name = (
                    f"Person {label + 1}" if label != -1 else "Unidentified"
                )
                clusters[label] = {
                    "cluster_id": label,
                    "name": default_name,
                    "faces": [],
                }
                cluster_assignments[label] = {
                    "cluster_id": label,
                    "name": default_name,
                    "face_ids": [],
                }

            clusters[label]["faces"].append(
                {
                    "face_id": face_data["face_id"],
                    "face_image_url": face_data.get("face_image_url")
                    or self._face_id_to_web_path(face_data),
                    "taken_at": face_data.get("taken_at"),
                    "timestamp_source": face_data.get("timestamp_source"),
                }
            )
            cluster_assignments[label]["face_ids"].append(face_data["face_id"])

        self._persist_cluster_assignments(cluster_assignments)
        return list(clusters.values())

    def _face_id_to_web_path(self, face_data: dict) -> str:
        return f"/output_albums/.cache/faces/{os.path.basename(face_data['face_image_path'])}"

    def _persist_cluster_assignments(self, cluster_assignments: dict) -> None:
        os.makedirs(self.cache_path, exist_ok=True)
        payload = {
            "clusters": list(cluster_assignments.values()),
            "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        try:
            with open(self.cluster_assignments_path, "w") as assignments_file:
                json.dump(payload, assignments_file)
        except Exception as exc:
            print(f"Failed to persist cluster assignments: {exc}")

    # ------------------------------------------------------------------ #
    # Data helpers for downstream routes
    # ------------------------------------------------------------------ #
    def load_all_faces_data(self) -> List[dict]:
        try:
            with open(self.faces_cache_file, "r") as cache_file:
                return json.load(cache_file)
        except FileNotFoundError:
            return []

    def load_cluster_assignments(self) -> List[dict]:
        try:
            with open(self.cluster_assignments_path, "r") as assignments_file:
                data = json.load(assignments_file)
                return data.get("clusters", [])
        except FileNotFoundError:
            return []

    # ------------------------------------------------------------------ #
    # Album persistence & search (unchanged behaviour)
    # ------------------------------------------------------------------ #
    @staticmethod
    def save_final_albums(cluster_data, all_faces_data, output_path_base):
        """Saves the final photo albums based on the (potentially corrected) cluster data."""
        print("Saving final albums...")
        face_map = {face["face_id"]: face for face in all_faces_data}

        for cluster in cluster_data:
            cluster_name = cluster.get("name", f"cluster_{cluster['cluster_id']}")
            # Sanitize cluster name for directory creation
            safe_cluster_name = "".join(
                c for c in cluster_name if c.isalnum() or c in (" ", "_")
            ).rstrip()
            cluster_dir = os.path.join(output_path_base, safe_cluster_name)
            os.makedirs(cluster_dir, exist_ok=True)

            image_paths_for_cluster = set()
            for face in cluster["faces"]:
                original_path = face_map[face["face_id"]]["original_path"]
                image_paths_for_cluster.add(original_path)

            print(f"Copying {len(image_paths_for_cluster)} photos to album: {safe_cluster_name}")
            for img_path in image_paths_for_cluster:
                shutil.copy(img_path, cluster_dir)

    def search_for_person(self, sample_paths, search_path, album_name, threshold=1.2):
        """
        Searches for a specific person in a directory of photos using sample images.
        """
        print("Step 1: Creating reference embedding from sample images...")
        reference_embeddings = []
        for sample_path in sample_paths:
            try:
                img = cv2.imread(sample_path)
                if img is None:
                    print(f"Warning: Could not read sample image {sample_path}")
                    continue
                faces = self.app.get(img)
                if not faces:
                    print(f"Warning: No faces found in sample image {sample_path}")
                    continue
                # Use the first face found in the sample image
                reference_embeddings.append(faces[0].embedding)
            except Exception as exc:
                print(f"An error occurred while processing sample {sample_path}: {exc}")

        if not reference_embeddings:
            print(
                "Error: Could not create a reference embedding. No faces found in sample images."
            )
            return

        # Average the embeddings to get a robust reference
        reference_embedding = np.mean(reference_embeddings, axis=0)
        print("Reference embedding created successfully.")

        print("\nStep 2: Searching for matches in the target directory...")
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
        matched_image_paths = set()

        try:
            image_files = [
                os.path.join(search_path, f)
                for f in os.listdir(search_path)
                if os.path.splitext(f)[1].lower() in image_extensions
            ]
        except FileNotFoundError:
            print(f"Error: Search directory not found at {search_path}")
            return

        for image_path in image_files:
            try:
                img = cv2.imread(image_path)
                if img is None:
                    continue

                faces = self.app.get(img)
                if not faces:
                    continue

                for face in faces:
                    distance = np.linalg.norm(face.embedding - reference_embedding)
                    if distance < threshold:
                        print(
                            f"Found a match in {os.path.basename(image_path)} (distance: {distance:.2f})"
                        )
                        matched_image_paths.add(image_path)
                        # Once a match is found in a photo, no need to check other faces in it
                        break
            except Exception as exc:
                print(f"An error occurred while processing {image_path}: {exc}")

        if not matched_image_paths:
            print("No matching photos were found.")
            return

        album_dir = os.path.join(self.output_path, album_name)
        os.makedirs(album_dir, exist_ok=True)

        print(f"\nStep 3: Saving matched photos to album '{album_name}'...")
        for img_path in matched_image_paths:
            shutil.copy(img_path, album_dir)
            print(f"Copied: {img_path}")
