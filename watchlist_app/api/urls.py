from django.urls import path, include
from rest_framework.routers import DefaultRouter

# from .views import movie_list, movie_detail
from .views import (
    WatchListSearch,
    WatchListAP,
    WatchListDetailAP,
    StreamPlatformAV,
    StreamPlatformDetailAV,
    # StreamPlatformVS,
    StreamPlatformMVS,
    ReviewList,
    ReviewDetail,
    ReviewCreate,
    UserReview,
)

router = DefaultRouter()
router.register("stream", StreamPlatformMVS, basename="streamplatform")

urlpatterns = [
    path("list/", WatchListAP.as_view(), name="movie-list"),
    path("<int:pk>/", WatchListDetailAP.as_view(), name="movie-detail"),
    path("", include(router.urls)),
    # testing purpose searc url
    path("listsearch/", WatchListSearch.as_view(), name="search-list"),
    # path("stream/", StreamPlatformAV.as_view(), name="stream"),
    # path(
    #     "stream/<int:pk>",
    #     StreamPlatformDetailAV.as_view(),
    #     name="streamplatform-detail",
    # ),
    # path(
    #     "review/<int:pk>",
    #     ReviewDetail.as_view(),
    #     name="review-detail",
    # ),
    # path("review/", ReviewList.as_view(), name="review-list"),
    path("<int:pk>/review-create", ReviewCreate.as_view(), name="review-create"),
    path(
        "<int:pk>/reviews/",
        ReviewList.as_view(),
        name="review-list",
    ),
    path("review/<int:pk>/", ReviewDetail.as_view(), name="review-detail"),
    path("reviews/", UserReview.as_view(), name="user-review-detail"),
]
