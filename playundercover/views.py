import re
import random
from random import shuffle
import ast
import json
from copy import deepcopy
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.template.context_processors import csrf
from django.contrib.auth.models import User
from models import Season, Pair, UserPair, Namelist, CustomUser
from django.contrib.auth.decorators import login_required


def home(request):
    if request.user.is_authenticated():
        return render(request, 'index.html', {'logged_in': "true"})
    else:
        return render(request, 'index.html', {'logged_in': "false"})


def login(request):
    if request.user.is_authenticated():
        return home(request)
    else:
        return render(request, 'login.html', {})


def logout(request):
    if request.user.is_authenticated():
        auth_logout(request)
    return home(request)


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
    if request.user.is_authenticated():
        return home(request)
    else:
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
            # CustomUser.objects.create(user)
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

    if player_names[-1] == "":
        player_names = player_names[:-1] # because last item is an extra blank item in list

    if len(player_names) != len(set(player_names)):
        error_message = "Player names must be unique."
        return render(request, 'quickplay.html', {"error_message": error_message})

    if int(number_of_u) + int(number_of_w) >= len(player_names):
        error_message = "Total number of Undercovers and Mr Whites must be less than the number of players."
        return render(request, 'quickplay.html', {"error_message":error_message})

    if int(number_of_u) + int(number_of_w) == 0:
        error_message = "There must be at least 1 of either Undercover or Mr White."
        return render(request, 'quickplay.html', {"error_message":error_message})

    if int(number_of_u) < 0 or  int(number_of_w) < 0:
        error_message = "Number of Undercovers and/or Mr White cannot be negative."
        return render(request, 'quickplay.html', {"error_message":error_message})

    player_assignment = assign_cuw(player_names, int(number_of_u), int(number_of_w))
    word_assignment = assign_word(request, player_assignment,None,None)
    c_word = word_assignment[0][0]
    u_word = word_assignment[1][0]

    player_assignment = json.dumps(player_assignment)
    word_assignment = json.dumps(word_assignment)

    return render(request, 'word-reveal.html', {"player_assignment":player_assignment,
                                                "word_assignment":word_assignment,
                                                "c_word":c_word,
                                                "u_word":u_word})


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


def turn_reveal_single(request):
    cuw_list_str = request.POST['cuw_list']
    cuw_list = ast.literal_eval(str(cuw_list_str.encode('utf-8')))
    c_word = request.POST['c_word']
    u_word = request.POST['u_word']
    try:
        played_names_str = request.POST['played_names']
        played_names = ast.literal_eval(str(played_names_str.encode('utf-8')))
    except:
        played_names = []

    next_player = get_next_player(cuw_list, played_names)

    if next_player is not None:
        played_names.append(next_player)
        return render(request, 'turn-reveal.html', {"next_player": next_player,
                                                    "cuw_list": cuw_list,
                                                    "played_names": played_names,
                                                    "c_word": c_word,
                                                    "u_word": u_word})
    else:
        return render(request, 'player-elim.html', {"player_turns": played_names,
                                                    "cuw_list": cuw_list,
                                                    "c_word": c_word,
                                                    "u_word": u_word})



def turn_reveal(request):
    cuw_list_str = request.POST['player_assignment']
    cuw_list = ast.literal_eval(str(cuw_list_str.encode('utf-8')))

    uw_list = []
    uw_list.extend(cuw_list[1])
    uw_list.extend(cuw_list[2])

    played_names = get_player_turns(cuw_list)

    if played_names is not None:
        return render(request, 'turn-reveal-group.html', {"player_turns": played_names,
                                                          "uw_list": uw_list})
    else:
        return render(request, 'index.html', {"player_turns": played_names,
                                                          "uw_list": uw_list})


def get_player_turns(cuw_list):
    total_number_of_players = len(cuw_list[0]) + len(cuw_list[1]) + len(cuw_list[2])

    played_names = []
    while len(played_names) != total_number_of_players:
        next_player = get_next_player(cuw_list, played_names)
        if next_player is None:
            return None
        played_names.append(next_player)

    return played_names


# returns name of next player
def get_next_player(cuw_list, played_names):
    cuw_list_copy = deepcopy(cuw_list)

    # remove the names of those that have played
    for played_name in played_names:
        for cuw_sub_list in cuw_list_copy:
            try:
                cuw_sub_list.remove(played_name)
            except:
                pass

    # civilians are a few times more likely than undercover and whites to play next. White is least likely to play next.
    choose_list = []
    choose_list.extend(2 * cuw_list_copy[0])
    choose_list.extend(cuw_list_copy[1])
    choose_list.extend(cuw_list_copy[2])
    if len(choose_list) > 0:
        decider = random.randint(0, len(choose_list) - 1)
        return choose_list[decider]
    else:
        return None


def player_elim(request):
    players_to_elim = request.POST.getlist('players_to_elim')
    cuw_list_str = request.POST['cuw_list']
    cuw_list = ast.literal_eval(str(cuw_list_str.encode('utf-8')))
    c_word = request.POST['c_word']
    u_word = request.POST['u_word']

    player_list = []
    player_list.extend(cuw_list[0])
    player_list.extend(cuw_list[1])
    player_list.extend(cuw_list[2])
    player_list = json.dumps(player_list)

    # remove the names of players to elim
    for player_to_elim in players_to_elim:
        for cuw_sub_list in cuw_list:
            try:
                cuw_sub_list.remove(player_to_elim)
            except:
                pass

    if len(cuw_list[1]) == 0 and len(cuw_list[2]) == 0:
        winner_list = ""
        for i in range(0, len(cuw_list[0])):
            if i == len(cuw_list[0])-1 and i != 0:
                winner_list += "& "
                winner_list += cuw_list[0][i]
            elif len(cuw_list[0]) == 1:
                winner_list += cuw_list[0][i]
            else:
                winner_list += cuw_list[0][i] + ", "

        return render(request, 'gameover.html', {"winner_group": "CIVILIANS",
                                                 "winner_list": winner_list,
                                                 "c_word": c_word,
                                                 "u_word": u_word,
                                                 "player_list": player_list})
    elif len(cuw_list[0]) == 0:
        cuw_list[2].extend(cuw_list[1])
        winner_list = ""
        for i in range(0, len(cuw_list[2])):
            if i == len(cuw_list[2])-1 and i != 0:
                winner_list += "& "
                winner_list += cuw_list[2][i]
            elif len(cuw_list[2]) == 1:
                winner_list += cuw_list[2][i]
            else:
                winner_list += cuw_list[2][i] + ", "

        return render(request, 'gameover.html', {"winner_group": "UNDERCOVERS/MR WHITES",
                                                 "winner_list": winner_list,
                                                 "c_word": c_word,
                                                 "u_word": u_word,
                                                 "player_list": player_list})
    else:
        next_player = next_player = get_next_player(cuw_list, [])
        played_names = [next_player]
        return render(request, 'turn-reveal.html', {"next_player": next_player,
                                                    "cuw_list": cuw_list,
                                                    "played_names": played_names})


def replay(request):
    player_list = request.POST['player_list']
    player_list = ast.literal_eval(str(player_list.encode('utf-8')))
    player_list = json.dumps(player_list)

    return render(request, 'replay.html', {"player_list": player_list})


@login_required(login_url='')
def name_list(request):
    current_user = request.user
    custom_user = CustomUser.objects.get(user=current_user)
    namelist_objects = list(Namelist.objects.filter(custom_user=custom_user).values_list('name'))
    namelist = []
    for name_object in namelist_objects:
        namelist.append(str(name_object[0]))

    return render(request, 'player-list.html', {"name_list": namelist})


@login_required(login_url='')
def process_name_list(request):
    namelist = request.POST.getlist('addmore[]')
    current_user = request.user
    custom_user = CustomUser.objects.get(user=current_user)
    Namelist.objects.filter(custom_user=custom_user).delete()

    for name in namelist:
        if len(name) > 0:
            Namelist.objects.create(custom_user=custom_user, name=name)

    namelist_objects = list(Namelist.objects.filter(custom_user=custom_user).values_list('name'))

    namelist = []
    for name_object in namelist_objects:
        namelist.append(str(name_object[0]))

    message = "Name list updated."

    return render(request, 'player-list.html', {"name_list": namelist, "error_message": message})