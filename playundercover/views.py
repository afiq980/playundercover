import re
import random
from random import shuffle
import ast
import json
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login
from django.template.context_processors import csrf
from django.contrib.auth.models import User
from models import Season, Pair, UserPair


def home(request):
    return render(request, 'index.html', {})


def login(request):
    return render(request, 'login.html', {})


def authentication(request):
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(username=email, password=password)

    def error_handle(error):
        c = {}
        c.update(csrf(request))
        return render(request, 'login.html', {'error_message': error})

    if user is not None:

        if user.is_active:
            auth_login(request, user)
            c = {}
            c.update(csrf(request))
            return redirect('home')
        else:
            c = {}
            c.update(csrf(request))
            error = 'Invalid username/password, please try again.'
            return error_handle(error)
    elif user is None:
        c = {}
        c.update(csrf(request))
        error = 'Invalid username/password, please try again.'
        return error_handle(error)


def register(request):
    return render(request, 'register.html', {})


def process_register(request):
    email = request.POST['email']
    password1 = request.POST['password1']
    password2 = request.POST['password2']

    def error_handle(error):
        c = {}
        c.update(csrf(request))
        return render(request, 'register.html', {'error_message': error})

    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        c = {}
        c.update(csrf(request))
        error = 'Invalid email address, please try again.'
        return error_handle(error)

    if User.objects.filter(username=email).exists():
        c = {}
        c.update(csrf(request))
        error = 'Email address already exist, please log in instead.'
        return error_handle(error)
    else:
        if password1 == password2:
            user = User.objects.create_user(email, email, password1)
            user.save()
        else:
            c = {}
            c.update(csrf(request))
            error = 'Passwords do not match, please try again.'
            return error_handle(error)
    return render(request, 'register.html', {})


def quickplay(request):
    return render(request, 'quickplay.html', {})


def register_players(request):
    player_names = request.POST.getlist('addmore[]')
    number_of_u = request.POST['uNumber']
    number_of_w = request.POST['wNumber']

    player_names = player_names[:-1] # because last item is an extra blank item in list

    player_assignment = assign_cuw(player_names, int(number_of_u), int(number_of_w))
    word_assignment = assign_word(request, player_assignment,None,None)

    player_assignment = json.dumps(player_assignment)
    word_assignment = json.dumps(word_assignment)

    return render(request, 'word-reveal.html', {"player_assignment":player_assignment,
                                                "word_assignment":word_assignment})


# returns list of lists - [[civilians],[undercover],[white]]
def assign_cuw(list_of_names, number_of_u, number_of_w):
    if len(list_of_names) <= number_of_u + number_of_w:
        return [[], [], []]

    civilian_list = []
    undercover_list = []
    white_list = []

    number_of_c = len(list_of_names) - number_of_u - number_of_w

    random.shuffle(list_of_names)

    for x in range(0, len(list_of_names)):
        if x < number_of_c:
            civilian_list.append(list_of_names.pop())
        elif x < number_of_c + number_of_u:
            undercover_list.append(list_of_names.pop())
        else:
            white_list.append(list_of_names.pop())

    return [civilian_list, undercover_list, white_list]


# returns list of lists - [[civilians words],[undercover words],[You are Mr White]]
def assign_word(request, cuw_assignment, difficulty_level, season_name):
    word_pair = get_pair(request, difficulty_level, season_name)

    word_pair_list = [word_pair.word1, word_pair.word2]

    word1_index = random.randint(0, 1)
    word2_index = 1-word1_index
    word1 = word_pair_list[word1_index]
    word2 = word_pair_list[word2_index]
    word3 = "You are Mr White"
    choose_pair_list = [word1, word2, word3]

    word_assignment = []
    for x in range(0,3):
        group_assignment = []
        for y in cuw_assignment[x]:
            group_assignment.append(choose_pair_list[x])
        word_assignment.append(group_assignment)

    return word_assignment


def get_pair(request, difficulty_level, season_name):
    current_user = None
    try:
        current_user = request.user
    except:
        pass

    if difficulty_level is None:
        difficulty_level = 0

    if difficulty_level is 0:
        pair_list = list(Pair.objects.filter(level__lte=3))
    else:
        pair_list = list(Pair.objects.filter(level__lte=difficulty_level))

    if season_name is not None:
        pair_list.filter(season=Season.objects.get(name=season_name))

    if current_user is not None:
        userpair_list = list(UserPair.objects.only("pair").all())
        choose_pair = list(set(pair_list) - set(userpair_list))

        return choose_pair[random.randint(0, len(choose_pair) - 1)]
    else:
        return pair_list[random.randint(0, len(pair_list) - 1)]


def turn_reveal(request):
    cuw_list_str = request.POST['player_assignment']
    cuw_list = ast.literal_eval(str(cuw_list_str.encode('utf-8')))

    uw_list = []
    uw_list.extend(cuw_list[1])
    uw_list.extend(cuw_list[2])

    played_names = get_player_turns(cuw_list)

    return render(request, 'turn-reveal.html', {"player_turns": played_names,
                                                "uw_list": uw_list})


def get_player_turns(cuw_list):
    total_number_of_players = len(cuw_list[0]) + len(cuw_list[1]) + len(cuw_list[2])

    played_names = []
    while len(played_names) != total_number_of_players:
        next_player = get_next_player(cuw_list, played_names)
        played_names.append(next_player)

    return played_names


# returns name of next player
def get_next_player(cuw_list, played_names):

    # remove the names of those that have played
    for played_name in played_names:
        for cuw_sub_list in cuw_list:
            try:
                cuw_sub_list.remove(played_name)
            except:
                pass

    # civilians are a few times more likely than undercover and whites to play next. White is least likely to play next.
    choose_list = []
    choose_list.extend(2 * cuw_list[0])
    choose_list.extend(cuw_list[1])
    choose_list.extend(cuw_list[2])
    decider = random.randint(0, len(choose_list) - 1)

    return choose_list[decider]


def player_elim_choose(request):
    return render(request, 'player-elim.html', {"player_turns": request.POST['player_turns'],
                                                "uw_list": request.POST['uw_list']})


def player_elim(request):
    player_list_str = request.POST['player_turns']
    player_list = ast.literal_eval(str(player_list_str.encode('utf-8')))
    player_to_elim = request.POST['player_to_elim']
    uw_list_str = request.POST['uw_list']
    uw_list = ast.literal_eval(str(uw_list_str.encode('utf-8')))

    player_list.remove(player_to_elim)

    if len(player_list) == 0:
        return render(request, 'index.html', {})
    else:
        for uw in uw_list:
            if uw in player_list:
                shuffle(player_list)
                return render(request, 'turn-reveal.html', {"player_turns": player_list,
                                                            "uw_list": request.POST['uw_list']})
        else:
            return render(request, 'index.html', {})