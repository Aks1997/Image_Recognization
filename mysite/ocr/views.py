from django.shortcuts import render, render_to_response
from PIL import Image, ImageDraw
import pytesseract
from .models import document
from .forms import DocumentForm
from django.http import HttpResponse
import time
import os

def list(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # to save the image in the database
            newdoc = document(docfile=request.FILES['docfile'])
            # newdoc.save()

            # get the coordinates from the form
            top_left_width= form.cleaned_data['top_left_width']
            top_left_height= form.cleaned_data['top_left_height']
            bottom_right_height = form.cleaned_data['bottom_right_height']
            bottom_right_width = form.cleaned_data['bottom_right_width']

            # get the all data in the database
            # documents = document.objects.all()
            # if using Windows Platform
            if(os.name=='nt'):
                pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'

            # To crop the Image
            image_original = Image.open(newdoc.docfile)
            image_copy = image_original.copy()
            temp = image_copy.crop(box=(top_left_width, top_left_height, bottom_right_width, bottom_right_height))
            data = pytesseract.image_to_string(temp)

            # to draw the box on the image_copy
            ImageDraw.Draw(image_original).rectangle([(top_left_width, top_left_height), (bottom_right_width, bottom_right_height)], fill=None, width=4)

            image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ocr/static/ocr/img/')
            image_original.save(image_path + "temp"+str(int(time.time()))+".png")
            path = "./ocr/static/ocr/img/" + "temp"+str(int(time.time()))+".png"

            if len(data) == 0:
                data = "No text!! :<"
            form = DocumentForm()
            return render(request, 'ocr/list.html', {'data':data, 'form':form, 'path':path})

    # if form is not valid or the request is get
    form = DocumentForm()
    return render(request, 'ocr/list.html', {'form':form})
