import os
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from sklearn.cluster import DBSCAN
import shutil
import json

class PhotoProcessor:
    def __init__(self, output_path_base="output_albums"):
        """
        Initializes the PhotoProcessor, loading the InsightFace model and setting up cache paths.
        """
        self.app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        self.output_path = output_path_base
        self.cache_path = os.path.join(self.output_path, ".cache")
        self.faces_cache_path = os.path.join(self.cache_path, "faces")
        os.makedirs(self.faces_cache_path, exist_ok=True)

    def extract_faces(self, input_path):
        """
        Extracts all faces from images in a directory, saves cropped faces, and returns face data.
        """
        print(f"Starting face extraction for directory: {input_path}")
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        all_faces = []
        try:
            image_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if os.path.splitext(f)[1].lower() in image_extensions]
        except FileNotFoundError:
            print(f"Error: Input directory not found at {input_path}")
            return []
            
        print(f"Found {len(image_files)} images to process.")

        face_id_counter = 0
        for image_path in image_files:
            try:
                img = cv2.imread(image_path)
                if img is None:
                    print(f"Could not read image: {image_path}")
                    continue
                
                faces = self.app.get(img)
                if not faces:
                    continue

                print(f"Found {len(faces)} faces in: {os.path.basename(image_path)}")
                for face in faces:
                    bbox = face.bbox.astype(int)
                    x1, y1, x2, y2 = bbox
                    cropped_face = img[y1:y2, x1:x2]
                    
                    face_filename = f"face_{face_id_counter}.jpg"
                    face_filepath = os.path.join(self.faces_cache_path, face_filename)
                    cv2.imwrite(face_filepath, cropped_face)

                    all_faces.append({
                        'face_id': face_id_counter,
                        'embedding': face.embedding,
                        'original_path': image_path,
                        'face_image_path': face_filepath
                    })
                    face_id_counter += 1
            except Exception as e:
                print(f"An error occurred while processing {image_path}: {e}")
        
        print(f"Total faces extracted: {len(all_faces)}")
        self.save_face_data(all_faces)
        return all_faces

    def save_face_data(self, all_faces):
        """Saves the extracted face data (including embeddings) to a JSON file in the cache.
        """
        serializable_faces = [
            {
                'face_id': face['face_id'],
                'embedding': face['embedding'].tolist(),
                'original_path': face['original_path'],
                'face_image_path': face['face_image_path']
            } for face in all_faces
        ]
        with open(os.path.join(self.cache_path, 'all_faces_data.json'), 'w') as f:
            json.dump(serializable_faces, f)

    def cluster_faces(self, all_faces, eps=0.5):
        """Clusters faces based on their embeddings and returns the labels.
        """
        if not all_faces:
            return np.array([])

        embeddings = np.array([face['embedding'] for face in all_faces])
        clusterer = DBSCAN(metric="euclidean", eps=eps, min_samples=2)
        clusterer.fit(embeddings)
        print(f"Clustering complete. Found {len(set(clusterer.labels_)) - (1 if -1 in clusterer.labels_ else 0)} clusters.")
        return clusterer.labels_

    def generate_cluster_ui_data(self, all_faces, labels):
        """Generates a data structure of the clusters suitable for a UI.
        """
        clusters = {}
        # Create a web-accessible path for the cached faces
        # This assumes the cache folder will be served as a static directory
        web_cache_path = os.path.join("static", os.path.basename(self.cache_path), "faces")

        for i, label in enumerate(labels):
            label = int(label)
            face_data = all_faces[i]
            web_face_path = os.path.join(web_cache_path, os.path.basename(face_data['face_image_path'])).replace("\\", "/")

            if label not in clusters:
                clusters[label] = {
                    "cluster_id": label,
                    "name": f"Person {label + 1}" if label != -1 else "Unidentified",
                    "faces": []
                }
            clusters[label]['faces'].append({
                'face_id': face_data['face_id'],
                'face_image_url': web_face_path
            })
        return list(clusters.values())

    @staticmethod
    def save_final_albums(cluster_data, all_faces_data, output_path_base):
        """Saves the final photo albums based on the (potentially corrected) cluster data.
        """
        print("Saving final albums...")
        face_map = {face['face_id']: face for face in all_faces_data}

        for cluster in cluster_data:
            cluster_name = cluster.get('name', f"cluster_{cluster['cluster_id']}")
            # Sanitize cluster name for directory creation
            safe_cluster_name = "".join(c for c in cluster_name if c.isalnum() or c in (' ', '_')).rstrip()
            cluster_dir = os.path.join(output_path_base, safe_cluster_name)
            os.makedirs(cluster_dir, exist_ok=True)

            image_paths_for_cluster = set()
            for face in cluster['faces']:
                original_path = face_map[face['face_id']]['original_path']
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
            except Exception as e:
                print(f"An error occurred while processing sample {sample_path}: {e}")

        if not reference_embeddings:
            print("Error: Could not create a reference embedding. No faces found in sample images.")
            return

        # Average the embeddings to get a robust reference
        reference_embedding = np.mean(reference_embeddings, axis=0)
        print("Reference embedding created successfully.")

        print("\nStep 2: Searching for matches in the target directory...")
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        matched_image_paths = set()
        
        try:
            image_files = [os.path.join(search_path, f) for f in os.listdir(search_path) if os.path.splitext(f)[1].lower() in image_extensions]
        except FileNotFoundError:
            print(f"Error: Search directory not found at {search_path}")
            return

        for image_path in image_files:
            try:
                img = cv2.imread(image_path)
                if img is None: continue
                
                faces = self.app.get(img)
                if not faces: continue

                for face in faces:
                    distance = np.linalg.norm(face.embedding - reference_embedding)
                    if distance < threshold:
                        print(f"Found a match in {os.path.basename(image_path)} (distance: {distance:.2f})")
                        matched_image_paths.add(image_path)
                        # Once a match is found in a photo, no need to check other faces in it
                        break 
            except Exception as e:
                print(f"An error occurred while processing {image_path}: {e}")

        print(f"\nStep 3: Saving album... Found {len(matched_image_paths)} matching photos.")
        if not matched_image_paths:
            print("No matching photos found.")
            return

        # Sanitize album name for directory creation
        safe_album_name = "".join(c for c in album_name if c.isalnum() or c in (' ', '_')).rstrip()
        album_dir = os.path.join(self.output_path, safe_album_name)
        os.makedirs(album_dir, exist_ok=True)

        for img_path in matched_image_paths:
            shutil.copy(img_path, album_dir)
        
        print(f"Album '{safe_album_name}' created successfully in '{self.output_path}'.")

if __name__ == '__main__':
    print("Photo Processor module updated with search feature and loaded.")
