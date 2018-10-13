from __future__ import print_function
from django.shortcuts import render, render_to_response
from PIL import Image, ImageDraw
import pytesseract
from .models import document
from .forms import DocumentForm
from django.http import HttpResponse
import time
import numpy as np
import cv2
import os

path = "./ocr/static/ocr/img/" + "temp"+str(int(time.time()))

def getImages(urls):
    count=1
    new_images = []
    image = cv2.imread(urls)
    grayScale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sigma = 0.33
    v = np.median(grayScale)
    low = int(max(0, (1.0 - sigma) * v))
    high = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(grayScale, low, high)
    (_, cnts, _) = cv2.findContours(edged,
                                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    def detectShape(cnt):
        shape = 'unknown'
        peri = cv2.arcLength(c, True)
        vertices = cv2.approxPolyDP(c, 0.04 * peri, True)
        if len(vertices) == 3:
            shape = 'triangle'
        elif len(vertices) == 4:
            x, y, width, height = cv2.boundingRect(vertices)
            aspectRatio = float(width) / height
            if aspectRatio >= 0.95 and aspectRatio <= 1.05:
                shape = "square"
            else:
                shape = "rectangle"
        elif len(vertices) == 5:
            shape = "pentagon"
        else:
            shape = "circle"
        return shape
    for c in cnts:
        shape = detectShape(c)
        if shape =="rectangle":
            x,y,w,h = cv2.boundingRect(c)
            if w>20 and h>20:
                new_img=image[y:y+h,x:x+w]
                cv2.imwrite(path + str(count) + '.png', new_img)
                print(path)
                if str(path) not in new_images:
                    new_images.append(path + str(count) + '.png')
                    count +=1
                print(new_images)
    return new_images

def list(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        # image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ocr/static/ocr/img/')
        if form.is_valid():
            # to save the image in the database
            newdoc = document(docfile=request.FILES['docfile'])
            newdoc.save()

            if(os.name=='nt'):
                pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'

            # To crop the Image
            print(str(newdoc.docfile))
            new_images_path = []
            data = []
            try:
                new_images_path=getImages('./ocr/static/ocr/' + str(newdoc.docfile))
            except:
                data.append('Reupload the Image')
                form = DocumentForm()
                return render(request, 'ocr/list.html', {'data':data, 'form':form, 'path':'./ocr/static/ocr/'+ str(newdoc.docfile)})

            for i in range(len(new_images_path)):
                data1 = pytesseract.image_to_string(new_images_path[i])
                if len(data1)>0:
                    data.append(data1)
            form = DocumentForm()
            if(len(data)==0):
                data.append('No text!! :<')
            data.reverse()
            return render(request, 'ocr/list.html', {'data':data, 'form':form, 'path':'./ocr/static/ocr/'+ str(newdoc.docfile)})

    # if form is not valid or the request is get
    form = DocumentForm()
    return render(request, 'ocr/list.html', {'form':form})
