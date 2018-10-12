from django.db import models

# Create your models here.
class document(models.Model):
    docfile = models.FileField(upload_to="img/", blank=False)
    
