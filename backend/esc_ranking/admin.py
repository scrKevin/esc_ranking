from django.contrib import admin

from .models import Participant
from .models import Player
from .models import Rank

admin.site.register(Participant)
admin.site.register(Player)
admin.site.register(Rank)