from watchlist_app.models import WatchList, StreamPlatform, Review
from .serializers import WatchListSerializer, StreamPlatformSerializer, ReviewSerializer
from .permissions import IsAdminOrReadOnly, IsReviewUserOrReadOnly
from .throttling import ReviewCreateThrottle, ReviewListThrottle

# from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import (
    UserRateThrottle,
    AnonRateThrottle,
    ScopedRateThrottle,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .pagination import WatchListPagination, WatchListCursorPagination


class UserReview(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]

    serializer_class = ReviewSerializer
    # throttle_classes = [ReviewCreateThrottle]

    # def get_queryset(self):
    #     username = self.kwargs["username"]
    #     return Review.objects.filter(review_user__username=username)

    def get_queryset(self):
        username = self.request.query_params.get("username")
        return Review.objects.filter(review_user__username=username)


class ReviewCreate(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = ReviewSerializer
    throttle_classes = [ReviewCreateThrottle]

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
        pk = self.kwargs.get("pk")
        watchlist = WatchList.objects.get(id=pk)
        # print(watchlist)
        review_user = self.request.user

        review_queryset = Review.objects.filter(
            watchlist=watchlist, review_user=review_user
        )
        # print(review_queryset)
        if review_queryset.exists():
            raise ValidationError("you already have a review on this")

        if watchlist.number_rating == 0:
            watchlist.avg_rating = serializer.validated_data["rating"]
        else:
            watchlist.avg_rating = (
                watchlist.avg_rating + serializer.validated_data["rating"]
            ) / 2

        watchlist.number_rating = watchlist.number_rating + 1
        watchlist.save()

        serializer.save(watchlist=watchlist, review_user=review_user)


class ReviewList(generics.ListAPIView):
    # queryset = Review.objects.all()
    # permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    throttle_classes = [ReviewListThrottle, AnonRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["review_user__username", "active"]

    def get_queryset(self):
        pk = self.kwargs["pk"]
        return Review.objects.filter(watchlist_id=pk)


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewUserOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "review-detail"


# ------------------------------------------------- Generic Class based views with mixins --------------------------------


# class ReviewDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)


# class ReviewList(
#     mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
# ):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)

# ------------------------------------------------- Class based views ViewsSets --------------------------------


# class StreamPlatformMVS(viewsets.ReadOnlyModelViewSet):
class StreamPlatformMVS(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]

    queryset = StreamPlatform.objects.all()
    serializer_class = StreamPlatformSerializer


# ------------------------------------------------- Class based views ViewsSets --------------------------------


# class StreamPlatformVS(viewsets.ViewSet):
#     def list(self, request):
#         queryset = StreamPlatform.objects.all()
#         serializer = StreamPlatformSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = StreamPlatform.objects.all()
#         watchlist = get_object_or_404(queryset, pk=pk)
#         serializer = StreamPlatformSerializer(watchlist)
#         return Response(serializer.data)

#     def create(self, request):
#         serializer = StreamPlatformSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------- Class based views --------------------------------


class StreamPlatformAV(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        platform = StreamPlatform.objects.all()
        serializer = StreamPlatformSerializer(
            platform, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = StreamPlatformSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status.HTTP_400_BAD_REQUEST)


class StreamPlatformDetailAV(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return StreamPlatform.objects.get(id=pk)
        except StreamPlatform.DoesNotExist:
            return None

    def get(self, request, pk):
        stream = self.get_object(pk)
        if stream is None:
            return Response({"message": "Stream not found"}, status.HTTP_404_NOT_FOUND)

        serializer = StreamPlatformSerializer(stream, context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk):
        stream = self.get_object(pk)
        if stream is None:
            return Response({"message": "Stream not found"}, status.HTTP_404_NOT_FOUND)

        serializer = StreamPlatformSerializer(stream, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        stream = self.get_object(pk)
        if stream is None:
            return Response(
                {"message": "Stream not found"}, status=status.HTTP_404_NOT_FOUND
            )

        stream.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WatchListSearch(generics.ListAPIView):
    queryset = WatchList.objects.all()
    serializer_class = WatchListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "platform__name"]
    pagination_class = WatchListCursorPagination


class WatchListAP(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        movies = WatchList.objects.all()
        serializer = WatchListSerializer(movies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WatchListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class WatchListDetailAP(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return WatchList.objects.get(id=pk)
        except WatchList.DoesNotExist:
            return None

    def get(self, request, pk):
        movie = self.get_object(pk)
        if movie is None:
            return Response(
                {"message": "Movie not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = WatchListSerializer(movie)
        return Response(serializer.data)

    def put(self, request, pk):
        movie = self.get_object(pk)
        if movie is None:
            return Response(
                {"message": "Movie not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = WatchListSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        movie = self.get_object(pk)
        if movie is None:
            return Response(
                {"message": "Movie not found"}, status=status.HTTP_404_NOT_FOUND
            )

        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ------------------------------------------------- function based views --------------------------------

# @api_view(["GET", "POST"])
# def movie_list(request):
#     if request.method == "GET":
#         movies = Movie.objects.all()
#         serializer = MovieSerializer(movies, many=True)
#         return Response(serializer.data)

#     if request.method == "POST":
#         serializer = MovieSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["GET", "PUT", "DELETE"])
# def movie_detail(request, pk):
#     try:
#         movies = Movie.objects.get(id=pk)
#     except Movie.DoesNotExist:
#         return Response(
#             {"message": "Movie not found"}, status=status.HTTP_404_NOT_FOUND
#         )

#     if request.method == "GET":
#         serializer = MovieSerializer(movies)
#         return Response(serializer.data)

#     if request.method == "PUT":
#         serializer = MovieSerializer(movies, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     if request.method == "DELETE":
#         movies.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
