import json
import os
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer


class SharedMemory:
    """Class to manage shared memory for the travel planning workflow"""

    def __init__(self, memory_dir="memory"):
        self.memory_dir = memory_dir
        self.memory_file = os.path.join(memory_dir, "shared_memory.json")
        self.vectors_file = os.path.join(memory_dir, "vectors.npy")
        self._ensure_memory_dir()
        self._load_model()
        self._ensure_files()

    def _ensure_memory_dir(self):
        """Ensure the memory directory exists"""
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)

    def _ensure_files(self):
        """Ensure the memory files exist"""
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                json.dump([], f)
        if not os.path.exists(self.vectors_file):
            np.save(self.vectors_file, np.array([]))

    def _load_model(self):
        """Load the sentence transformer model"""
        model_path = "all-mpnet-base-v2"
        self.model = SentenceTransformer(model_path)

    def read_memory(self):
        """Read shared memory from file"""
        with open(self.memory_file, 'r') as f:
            return json.load(f)

    def write_memory(self, agent_name, prompt, answer):
        """Write to shared memory with vector encoding"""
        # Read existing memory and vectors
        memory = self.read_memory()
        vectors = np.load(self.vectors_file, allow_pickle=True).tolist()

        # Create new memory item
        new_item = {
            "agent": agent_name,
            "prompt": prompt,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }

        # Encode combined text to vector
        combined_text = f"{prompt} {answer}"
        vector = self.model.encode(combined_text).tolist()

        # Append to memory and vectors
        memory.append(new_item)
        vectors.append(vector)

        # Save to files
        with open(self.memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
        np.save(self.vectors_file, np.array(vectors))

    def search_memory(self, query, agent_name=None, top_k=3):
        """Search shared memory for relevant information using vector similarity"""
        memory = self.read_memory()
        vectors = np.load(self.vectors_file, allow_pickle=True).tolist()

        if not memory or not vectors:
            return []

        # Encode query to vector
        query_vector = self.model.encode(query)

        # Calculate cosine similarity for each memory item
        results = []
        for i, (item, vector) in enumerate(zip(memory, vectors)):
            if agent_name and item["agent"] != agent_name:
                continue

            # Calculate cosine similarity
            similarity = self._calculate_similarity(query_vector, np.array(vector))

            if similarity > 0:
                results.append((similarity, item))

        # Sort by similarity score and return top_k results
        results.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in results[:top_k]]

    def _calculate_similarity(self, vector1, vector2):
        """Calculate cosine similarity between two vectors"""
        if np.linalg.norm(vector1) == 0 or np.linalg.norm(vector2) == 0:
            return 0
        return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))


# Create a global instance
shared_memory = SharedMemory()