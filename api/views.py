from django.shortcuts import render

# Create your views here.
import numpy as np
import cv2
import base64
import insightface
from insightface.app import FaceAnalysis
from django.http import JsonResponse
from .models import Face
from rest_framework.decorators import api_view
from rest_framework.response import Response
import cv2
import numpy as np
import base64
from sklearn.metrics.pairwise import cosine_similarity
import re

# Initialize ArcFace Model
app = FaceAnalysis(name="buffalo_l")  # You can use "antelopev2" for better accuracy
app.prepare(ctx_id=-1)  # CPU (-1) or GPU (0)
import numpy as np
import cv2
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Face  # Assuming Face model exists

def img_to_numpy(image_file):
    try:
        # Read the image file as binary data
        image_bytes = image_file.read()

        # Convert binary data to a numpy array
        np_arr = np.frombuffer(image_bytes, np.uint8)

        # Decode the numpy array into an OpenCV image
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        return img
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None


@api_view(['POST'])
def train_face(request):
    """ Train and save face embeddings from multiple images """
    name = request.data.get("name")
    image_files = request.FILES.getlist('image')  # Allow multiple images
    print(request.FILES)

    if not name or not image_files:
        return Response({"error": "Name and images are required"}, status=400)

    embeddings = []  # To store embeddings of all images

    for image_file in image_files:
        img = img_to_numpy(image_file)
        if img is None:
            return Response({"error": f"Invalid image format for {image_file.name}"}, status=400)

        faces = app.get(img)  # Assuming app.get() detects faces in the image
        if len(faces) == 0:
            return Response({"error": f"No face detected in {image_file.name}"}, status=400)

        face_embedding = faces[0].embedding  # Assuming `embedding` is how the face is represented
        embeddings.append(face_embedding.tobytes())

    # Save the embeddings for each image
    for embedding in embeddings:
        face_obj = Face(name=name, embedding=embedding)
        face_obj.save()

    return Response({"message": "Faces trained successfully", "name": name})


def img_to_numpy(image_file):
    try:
        # Read the image file as binary data
        image_bytes = image_file.read()

        # Convert binary data to a numpy array
        np_arr = np.frombuffer(image_bytes, np.uint8)

        # Decode the numpy array into an OpenCV image
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        return img
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None


def compare_embeddings(new_embedding, stored_embedding):
    """ Compare two embeddings using cosine similarity """
    # Reshape embeddings to 2D arrays (required for sklearn's cosine_similarity)
    new_embedding = new_embedding.reshape(1, -1)
    stored_embedding = stored_embedding.reshape(1, -1)

    # Calculate cosine similarity
    similarity = cosine_similarity(new_embedding, stored_embedding)

    return similarity[0][0]  # Return the similarity score


@api_view(['POST'])
def recognize_face(request):
    """ Recognize a face from an image """
    image_file = request.FILES.get('image')
    print(request.FILES)

    if not image_file:
        return Response({"error": "Image is required for recognition"}, status=400)

    # Convert image to numpy array
    img = img_to_numpy(image_file)
    if img is None:
        return Response({"error": "Invalid image format"}, status=400)

    # Detect face and extract embedding
    faces = app.get(img)  # Assuming app.get() detects faces and gives embeddings
    if len(faces) == 0:
        return Response({"error": "No face detected"}, status=400)

    new_embedding = faces[0].embedding  # The embedding of the detected face

    # Get all stored face embeddings from the database
    stored_faces = Face.objects.all()

    # Compare new embedding with stored embeddings
    for stored_face in stored_faces:
        stored_embedding = np.frombuffer(stored_face.embedding, dtype=np.float32)

        similarity = compare_embeddings(new_embedding, stored_embedding)

        # If the similarity is above a threshold, we consider it a match
        if similarity > 0.7:  # You can adjust the threshold value
            return Response({"message": "Face recognized", "name": stored_face.name})

    # If no match is found
    return Response({"error": "No matching face found"}, status=400)