from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.permissions import IsAdminUser
from utils.cloudinary_service import upload_image


class ImageUploadView(APIView):
    """
    POST /api/admin/uploads/image/
    Generic image upload to Cloudinary. Returns URL and public_id.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        file = request.FILES.get("file") or request.FILES.get("image")
        if not file:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        folder = request.data.get("folder", "befa/uploads")
        result = upload_image(file, folder=folder)
        return Response(result, status=status.HTTP_201_CREATED)
