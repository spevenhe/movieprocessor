from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):
    poster = models.CharField(blank=True,max_length=500)
    name = models.CharField(max_length=200)
    score = models.CharField(max_length=20)
    release_time = models.CharField(blank=True,max_length=50)
    ratings_number = models.CharField(max_length=20)
    director = models.CharField(max_length=200)
    star = models.CharField(max_length = 200)
    movie_length = models.CharField(max_length = 30)
    movie_type = models.CharField(max_length=200)
    storyline = models.CharField(max_length = 400)
    trailer_embed_link = models.CharField(max_length=400)
  
    
    def __unicode__(self):
        return 'id=' + str(self.id) + ',name="' + self.name + '"'

class Comment(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    post_id = models.CharField(max_length=200)
    comment_time = models.DateTimeField(default=None)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    username = models.CharField(max_length=200,default=None)

    def __str__(self):
        return 'text="' + self.text + '"'

# Create your models here.
class Post(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    post_time = models.DateTimeField()
    username = models.CharField(max_length=200)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rate = models.CharField(max_length = 1)

    def __str__(self):
        return 'text="' + self.text + '"'

class Product(models.Model):
    product_picture = models.FileField(blank=True)
    name = models.CharField(max_length=200)
    movie = models.CharField(max_length=200)
    link = models.CharField(max_length=400)

    def __unicode__(self):
        return 'id=' + str(self.id) + ',name="' + self.name + '"'


class MovieFans(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    profile_picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)
    favorite = models.CharField(max_length = 400)
    # I think we may need a char list of the movie name and use the list to get each movie
    recommand_movie_list = models.CharField(max_length = 400)
    rating_history = models.CharField(max_length = 4000)
    watching_histpry = models.ManyToManyField(Movie)
    shopping_history = models.CharField(max_length = 400)

    def __unicode__(self):
        return 'id=' + str(self.id) + ',favorite="' + self.favorite + '"'

    def isMovieRated(self,id):
        idAndScore = self.rating_history.split(',')
        ratedID = []
        for i in range(0,len(idAndScore)-1):
            ratedID+=[idAndScore[i].split(':')[0]]
        for rID in ratedID:
            if(id == rID):
                return True
        return False

    def get_rated_movie(self,id):
        if(self.isMovieRated(id)==False):
            return
        idAndScore = self.rating_history.split(',')
        ratedIDAndScore = {}
        for i in range(0,len(idAndScore)-1):
            ratedIDAndScore[idAndScore[i].split(':')[0]] = idAndScore[i].split(':')[1]
        if(str(id) in ratedIDAndScore):
            return ratedIDAndScore[str(id)]
        
    def add_rated_movie(self,movieID,score):
        self.rating_history = self.rating_history+movieID+':'+score+','
        return





# Create your models here.
