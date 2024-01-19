from django.shortcuts import render

def error_429_view(request, exception):
    return render(request, '429.html', status=429)