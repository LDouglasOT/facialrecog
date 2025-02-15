from django.shortcuts import render

# Create your views here.
import numpy as np
import cv2
import base64
import insightface
from insightface.app import FaceAnalysis
from django.http import JsonResponse
from .models import Face, Parent
from rest_framework.decorators import api_view
from rest_framework.response import Response
import cv2
import numpy as np
import base64
from sklearn.metrics.pairwise import cosine_similarity
import re
from django.contrib.auth.backends import ModelBackend
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.forms.models import model_to_dict



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


from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
import numpy as np
from scipy.spatial.distance import cosine
from .models import Face  
 

THRESHOLD = 0.5  

@api_view(["POST"])
@parser_classes([MultiPartParser])
def train_face(request):
    """ Train and save face embeddings from multiple images """
    name = request.data.get("name")
    image_files = request.FILES.getlist('image')  # Allow multiple images
    phone = request.data.get("phone")
    if not name or not image_files:
        print("name and images are required")
        return Response({"error": "Name and images are required"}, status=400)

    embeddings = [] 
    match_count = 0  

    for image_file in image_files:
        img = img_to_numpy(image_file)
        if img is None:
            return Response({"error": f"Invalid image format for {image_file.name}"}, status=400)

        faces = app.get(img)  
        if len(faces) == 0:
            return Response({"error": f"No face detected in {image_file.name}"}, status=400)

        face_embedding = faces[0].embedding  
        embeddings.append(face_embedding)

    all_faces = Face.objects.all()
    for embedding in embeddings:
        for existing_face in all_faces:
            existing_embedding = np.frombuffer(existing_face.embedding, dtype=np.float32)
            similarity = 1 - cosine(existing_embedding, embedding)
            if similarity > THRESHOLD:
                match_count += 1
                break  

    if match_count >= len(embeddings) / 2:
        return Response({"message": "Face already registered", "match_count": match_count},status=404)

    # Save new embeddings
    for embedding in embeddings:
        face_obj = Face(name=phone, embedding=embedding.tobytes())
        face_obj.save()

    parent = Parent.objects.create(
        name=name,
        phone=phone
    )

    return Response({"message": "Faces trained successfully"})



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
        print("image is required")
        return Response({"error": "Image is required for recognition"}, status=400)

    # Convert image to numpy array
    img = img_to_numpy(image_file)
    if img is None:
        print("invalid image format")
        return Response({"error": "Invalid image format"}, status=400)

    # Detect face and extract embedding
    faces = app.get(img)  # Assuming app.get() detects faces and gives embeddings
    if len(faces) == 0:
        print("No face detected")
        return Response({"error": "No face detected"}, status=400)

    new_embedding = faces[0].embedding  # The embedding of the detected face

    # Get all stored face embeddings from the database
    stored_faces = Face.objects.all()

    # Compare new embedding with stored embeddings
    for stored_face in stored_faces:
        stored_embedding = np.frombuffer(stored_face.embedding, dtype=np.float32)

        similarity = compare_embeddings(new_embedding, stored_embedding)

        # If the similarity is above a threshold, we consider it a match
        if similarity > 0.7: 
            print(stored_face.name)
             # You can adjust the threshold value
            parent = Parent.objects.get(phone=stored_face.name)

            return Response({"message": "Face recognized", "parent": parent.name, "phone": parent.phone})

    # If no match is found
    print("no matching faces found")
    return Response({"error": "No matching face found"}, status=400)



class PhoneNumberAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            print("phone_number", username)
            print("password", password)
            users = CustomUser.objects.all()
            print(users)
            user = CustomUser.objects.get(phone_number=username)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            print("User does not exist")
            return None


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(data)
            phone_number = data.get("phone_number")
            password = data.get("password")

            user = authenticate(request, phone_number=phone_number, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return JsonResponse({
                    "message": "Login successful",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user": user.phone_number
                }, status=200)
            else:
                return JsonResponse({"error": "Invalid phone number or password"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
