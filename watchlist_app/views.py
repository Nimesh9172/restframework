# from .models import Movie
# from django.http import JsonResponse


# # Create your views here.
# def movie_list(request):
#     movies = Movie.objects.all()
#     data = {"movie": list(movies.values())}
#     return JsonResponse(data, safe=False)


# def movie_detail(request, pk):
#     movie = Movie.objects.get(pk=pk)
#     data = list(movie.values())
#     return JsonResponse(data, safe=False)
