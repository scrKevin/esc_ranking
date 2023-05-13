import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Participant
from .forms import ParticipantForm
from .countries import countries

from .models import Player
from .models import Rank

def getCountryName(countryCode):
    for country in countries:
        if country['code'] == countryCode.upper():
            return country['name']
    return 'Unknown'

def create_view(request):
    form = ParticipantForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = ParticipantForm()
    context = {
        'form': form
    }
    return render(request, "create_view.html", context)

def list(request):
    participants = Participant.objects.values()
    list_result = [entry for entry in participants]
    return JsonResponse(list_result, safe=False)

def getCurrentRanking(playerName):
    player = Player.objects.get(name=playerName)
    ranks = Rank.objects.filter(player=player)
    ## for each rank, get the participant info and add it to json:
    list_result = []
    for rank in ranks:
        participant = Participant.objects.get(id=rank.participant.id)
        list_result.append({
            'id': participant.id,
            'country': participant.country,
            'countryName': getCountryName(participant.country),
            'artist': participant.artist,
            'title': participant.title,
            'rank': rank.rank
        })
    return list_result

def getPlayerRanking(request, playerName):
    list_result = getCurrentRanking(playerName)
    ## sort the list by rank:
    list_result.sort(key=lambda x: x['rank'])
    return JsonResponse(list_result, safe=False)

def currentRanking(request, playerName):
    ranking = getCurrentRanking(playerName)
    context = {
        'playerName': playerName
    }
    return render(request, "current_ranking.html", context)

def resultPage(request):
    return render(request, "results.html")

@csrf_exempt
def changeRanking(request, playerName):
    ## get the id and direction attributes from the POST body
    id = request.POST.get('id')
    direction = request.POST.get('direction')
    ## get the player:
    player = Player.objects.get(name=playerName)
    ranks = Rank.objects.filter(player=player)
    ## get the rank attribute of the rank with the given id:
    rank = Rank.objects.get(participant_id=id, player_id=player.pk)

    ## if direction == 'up' and rank.rank > 1
    ## swap ranks with the rank above
    if direction == 'up' and rank.rank >= 1:
        rankAbove = Rank.objects.get(player=player, rank=rank.rank-1)
        rankAbove.rank += 1
        rank.rank -= 1
        rankAbove.save()
        rank.save()

    ## if direction == 'down' and rank.rank < len(ranks)
    ## swap ranks with the rank below
    if direction == 'down' and rank.rank < len(ranks) - 1:
        rankBelow = Rank.objects.get(player=player, rank=rank.rank+1)
        rankBelow.rank -= 1
        rank.rank += 1
        rankBelow.save()
        rank.save()
    
    list_result = getCurrentRanking(playerName)
    ## sort the list by rank:
    list_result.sort(key=lambda x: x['rank'])
    return JsonResponse(list_result, safe=False)

def results(request):
    adminRanks = getCurrentRanking('admin')
    ## sort the list by rank in reverse order:
    adminRanks.sort(key=lambda x: x['rank'], reverse=True)
    print(adminRanks)
    ## get all players:
    players = Player.objects.all()
    ## add ranking to each player:
    for player in players:
        if player.name != 'admin': 
            player.ranking = getCurrentRanking(player.name)
            player.ranking.sort(key=lambda x: x['rank'])
            player.aggregateScore = 0

    roundNr = 0
    resultJson = []
    ## keep a dict for each player to store their previous ranking:
    previousRound = None

    ## for each player, compare their ranking to the admin ranking:
    for rank in adminRanks:
        round = {}
        round['roundNr'] = roundNr
        round['rank'] = rank['rank']
        round['country'] = rank['country']
        round['countryName'] = getCountryName(rank['country'])
        round['artist'] = rank['artist']
        round['title'] = rank['title']
        round['playerResults'] = []
        for player in players:
            if player.name != 'admin':
                for playerRank in player.ranking:
                    if playerRank['country'] == rank['country']:
                        roundScore = len(adminRanks) - abs(rank['rank'] - playerRank['rank'])
                        if roundNr == len(adminRanks) - 1 and roundScore == len(adminRanks):
                            roundScore *=2
                            print(f"{player.name} guessed winner correctly, double points!")

                        print(f'rank of {rank["country"]} is {rank["rank"]}, {player.name} guessed {playerRank["country"]} at {playerRank["rank"]}. Score: {roundScore}')
                        playerResult = {}
                        playerResult['previousRank'] = getPlayerRank(previousRound, player.name)
                        playerResult['playerName'] = player.name
                        playerResult['guessedRank'] = playerRank['rank']
                        playerResult['roundScore'] = roundScore
                        player.aggregateScore += roundScore
                        playerResult['aggregateScore'] = player.aggregateScore
                        round['playerResults'].append(playerResult)
        roundNr += 1
        ## sort the playerResults by aggregateScore:
        round['playerResults'].sort(key=lambda x: x['aggregateScore'], reverse=True)
        ## add currentRank to each playerResult:
        for playerResult in round['playerResults']:
            playerResult['currentRank'] = getPlayerRank(round, playerResult['playerName'])
        previousRound = round
        resultJson.append(round)
    print(resultJson)


    return JsonResponse(resultJson, safe=False)

def getPlayerRank(round, playerName):
    rank = 1
    if round == None:
        return -1
    for playerResult in round['playerResults']:
        if playerResult['playerName'] == playerName:
            return rank
        rank += 1
    return 0
    