from django.db import models

# create your models here

class Movie(models.Model): 
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1500)
    image = models.ImageField(upload_to='movie/images/') 
    url = models.URLField(blank=True)
    genre = models.CharField(blank=True, max_length=250)
    year = models.IntegerField(blank=True, null=True)
    emb = models.BinaryField(blank=True, null=True)

    def __str__(self): 
        return self.title
