from django.db import models


# Create your models here.

GENDER_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Feminino'),
    ('O', 'Outro'),
    ('N', 'Prefiro não dizer'),
]

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30)
    firstName = models.CharField('Nome', blank=True, max_length=30)
    lastName = models.CharField('Sobrenome', blank=True, max_length=30)
    gender = models.CharField('Gênero', blank=True, max_length=1, choices = GENDER_CHOICES)
    email = models.EmailField(max_length=254, unique=True)
    senha = models.CharField(max_length=15)

class Song(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    artist = models.CharField(max_length=30)
    gender = models.CharField(max_length=15)

class SongList(models.Model):

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='songlist')
    song1 = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True, blank=True, related_name='songlist_1')
    song2 = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True, blank=True, related_name='songlist_2')
    song3 = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True, blank=True, related_name='songlist_3')
    song4 = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True, blank=True, related_name='songlist_4')
    song5 = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True, blank=True, related_name='songlist_5')

    def get_songs(self):

        songs = []
        for song in [self.song1, self.song2, self.song3, self.song4, self.song5]:

            if song is not None:

                songs.append(song)

        return songs