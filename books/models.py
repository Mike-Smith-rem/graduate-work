from django.db import models


# Create your models here.
class Books(models.Model):
    name = models.CharField(max_length=30, blank=True, null=True)
    author = models.CharField(max_length=30, blank=True, null=True)


class Files(models.Model):
    name = models.CharField(max_length=30, blank=True, null=True)
    file = models.FileField(upload_to='files/')
