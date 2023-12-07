from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from .serializers import RegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(["POST"])
def registeration_view(request):
    if request.method == "POST":
        serializer = RegistrationSerializer(data=request.data)

        data = {}

        if serializer.is_valid():
            account = serializer.save()
            data["username"] = account.username
            data["email"] = account.email
            data["message"] = "Registration successful"
            token = Token.objects.get(user=account).key
            data["token"] = token
            # refresh = RefreshToken.for_user(account)

            # data["token"] = {
            #     "refresh": str(refresh),
            #     "access": str(refresh.access_token),
            # }

            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = serializer.errors
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def logout_view(request):
    if request.method == "POST":
        request.user.auth_token.delete()
        return Response(
            {"message": "Successfully logged out"}, status=status.HTTP_200_OK
        )
