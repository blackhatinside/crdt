# diagram/views.py
from django.shortcuts import render

def editor(request):
    return render(request, 'diagram/editor.html')