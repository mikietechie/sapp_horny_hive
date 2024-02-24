from django.db import models

class ProfileMeta(models.Model):
    fields = (
        "interest_music",
        "interest_cooking",
        "interest_dancing",
        "interest_gymnastics",
        "interest_fitness",
        "interest_sports",
        "interest_board_games",
        "interest_movies",
        "interest_technologies",
    )
    class Meta:
        abstract = True
    
    # interests
    interest_music = models.BooleanField(blank=True, null=True)
    interest_cooking = models.BooleanField(blank=True, null=True)
    interest_dancing = models.BooleanField(blank=True, null=True)
    interest_gymnastics = models.BooleanField(blank=True, null=True)
    interest_fitness = models.BooleanField(blank=True, null=True)
    interest_sports = models.BooleanField(blank=True, null=True)
    interest_board_games = models.BooleanField(blank=True, null=True)
    interest_movies = models.BooleanField(blank=True, null=True)
    interest_technologies = models.BooleanField(blank=True, null=True)
