from typing import Iterable, Optional
from django.db import models

class Participant(models.Model):
    country = models.CharField(max_length=3, unique=True)
    artist = models.CharField(max_length=254)
    title = models.CharField(max_length=254)

    def __str__(self):
        return self.country
    
class Rank(models.Model):
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    participant = models.ForeignKey('Participant', on_delete=models.CASCADE)
    rank = models.IntegerField()

    def __str__(self):
        return f'{self.pk}: {self.player} - {self.participant} - {self.rank}'
    
class Player(models.Model):
    name = models.CharField(max_length=254, unique=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            super(Player, self).save(*args, **kwargs)
            participants = Participant.objects.all()
            index = 0
            for participant in participants:
                Rank.objects.create(player=self, participant=participant, rank=index)
                index += 1
        super(Player, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'