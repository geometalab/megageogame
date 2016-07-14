# -*- coding:utf-8 -*-
from flask import (Flask, render_template, request, jsonify)
import os
import psycopg2
import urlparse
from operator import itemgetter
from arcgis_scraper import ArcgisScraper
from geometry_calculator import GeometryHandler

APP = Flask(__name__)

SCRAPER = ArcgisScraper()
GEOMETRYHANDLER = GeometryHandler()
DATABASE_URL = (
    '''postgres://dgibhwjhbemyxu:rFqJwYnsX48PtWyR8LUgVHH0bE@ec2-54-228-219-2.eu-west-1.compute.amazonaws.com:5432/d6ln3gnquqodqq'''
)

urlparse.uses_netloc.append("postgres")
# URL = urlparse.urlparse(os.environ['DATABASE_URL'])

CONNECTION = psycopg2.connect(
     database="d6ln3gnquqodqq",
     user="dgibhwjhbemyxu",
     password="rFqJwYnsX48PtWyR8LUgVHH0bE",
     host="ec2-54-228-219-2.eu-west-1.compute.amazonaws.com",
     port="5432"
 )

CURSOR = CONNECTION.cursor()
QUERY_GET_LEVEL = ["http://services1.arcgis.com/6RDtDcHz3yZdtEVu/ArcGIS/rest/services/mgg2016_gamestate_m", "_sek1/FeatureServer/0/query?where"
                                                                       "=1%3D1&outFields=Status&f=pjson"]

QUERY_LEVEL_1 = [
    "http://services1.arcgis.com/6RDtDcHz3yZdtEVu/arcgis/rest/services/mgg2016_m1_sek1/FeatureServer/0/query?where=Gruppe%3D%27",
    '''%27&units=esriSRUnit_Meter&returnGeometry=true&outFields=Flaeche&f=pjson''']

QUERY_LEVEL_2 = [
    "http://services1.arcgis.com/6RDtDcHz3yZdtEVu/arcgis/rest/services/mgg2016_m2_sek1/FeatureServer/0/query?where=Gruppe%3D%27",
    '''%27&outFields=Nummer_Eingabe%2C+Nummer_Loesung&f=pjson&''']

QUERY_LEVEL_3 = [
    "http://services1.arcgis.com/6RDtDcHz3yZdtEVu/arcgis/rest/services/mgg2016_m3_sek1/FeatureServer/0/query?where=Gruppe%3D%27",
    '''%27&units=esriSRUnit_Meter&returnGeometry=true&f=pjson''']

QUERY_LEVEL_4 = [
    "http://services1.arcgis.com/6RDtDcHz3yZdtEVu/arcgis/rest/services/mgg2016_m4_sek1/FeatureServer/0/query?where=Gruppe%3D%27",
    '''%27&units=esriSRUnit_Meter&returnGeometry=true&f=pjson''']

QUERY_POINTS = "SELECT points FROM classes WHERE number = %s"
UPDATE_POINTS_QUERY = "UPDATE classes SET points = %s WHERE number = %s"
GET_PLAYER_QUERY = "SELECT points, name, match, state, former_place, trend from classes WHERE number = %s"

PLAYER_IDS = [
    'A1',
    'B1',
    'C1',
    'D1',
    'E1',
    'F1',
    'G1'
]
CLASS_NAMES = {'A1': 'Quarta C - Aargau', 'B1': 'Quarta 19a - Aargau', 'C1': 'Quarta 19b - Aargau', 'D1': '19d (Quarta) - Aargau', 'E1': '4r - Basel-Landschaft', 'F1':'VK7 - Zürich', 'G1': 'a1f - Zürich'}
VALID_LEVELS = [1, 2, 3, 4, 5, 6, 7]
VALID_STATES = ['weiss', 'schwarz']


@APP.route('/')
def show_site():
    return render_template('content.html')


@APP.route('/instruction')
def instructions():
    return render_template('instruction.html')


@APP.route('/input-level1')
def input_level1():
    classes = get_classes()
    return render_template('input-level1.html', classes=classes)


@APP.route('/input-level2')
def input_level2():
    return render_template('input-level2.html')


@APP.route('/input-level3')
def input_level3():
    return render_template('input-level3.html')


@APP.route('/input-level4')
def input_level4():
    return render_template('input-level4.html' )


@APP.route('/input-level5')
def input_level5():
    return render_template('input-level5.html')


@APP.route('/input-level6')
def input_level6():
    classes = get_classes()
    return render_template('input-level6.html', classes=classes)


@APP.route('/admin')
def tryLogin():
    return render_template('login.html')


@APP.route('/login', methods=['GET', 'POST'])
def login():
    name = request.json['name']
    password = request.json['password']
    classes = get_classes()
    if name == 'geo' and password == '22322':
        return render_template('admin-board.html', classes=classes)


@APP.route('/_admin_relative_submit')
def relative_submit():
    class_name = request.args.get('class_num', 0, type=int)
    estimate = request.args.get('points')
    if class_name == 0:
        return jsonify(result="Bitte wähle eine Klasse aus")
    try:
        estimate = int(estimate)
    except ValueError:
        return jsonify(result="Deine Eingabe war keine Zahl")
    CURSOR.execute(
        QUERY_POINTS,
        (PLAYER_IDS[class_name-1],)
    )
    points = CURSOR.fetchone()[0]
    CURSOR.execute(
        UPDATE_POINTS_QUERY,
        (estimate + points, PLAYER_IDS[class_name-1])
    )
    CONNECTION.commit()
    return jsonify(result="Deine Eingabe war erfolgreich")


@APP.route('/seed_classes')
def seed():
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, 'classes.txt')) as f:
        content = f.readlines()
        for line in content:
            CURSOR.execute(line.rstrip())
        CONNECTION.commit()
    return jsonify(result='''Super''')


@APP.route('/_level_selected')
def level_selected():
    curr_level = int(request.args.get('current_level'))
    level_chosen = int(request.args.get('level_chosen'))
    return elements_for_manual_mode(curr_level, level_chosen)


def elements_for_manual_mode(curr_level, clicked_level):
    stats = get_classes_in_statistics(clicked_level)
    header = get_instruction_header(curr_level, clicked_level)
    instruction_panel_text = get_instruction(clicked_level)
    map_iframe = get_map(clicked_level)
    return jsonify(
        stats=stats,
        header=header,
        instruction=instruction_panel_text,
        map=map_iframe
    )


@APP.route('/_update_level')
def update():
    curr_level = int(request.args.get('current_level'))
    curr_state = request.args.get('current_state')
    if not curr_level in VALID_LEVELS:
        curr_level = 0
    instruction_panel_text = get_instruction(curr_level)
    instruction_panel_heading = ''
    if curr_level == 0:
        map_iframe = get_map(1)
        instruction_panel_heading = 'A game with 7 levels'
    elif curr_level == 1 and (curr_state == 'weiss' or curr_state == 'schwarz'):
        map_iframe = get_map(1)
    else:
        map_iframe = get_map(curr_level)
    return jsonify(
        instruction_panel_heading=instruction_panel_heading,
        instruction=instruction_panel_text,
        map=map_iframe
    )


@APP.route('/_get_current_ranking')
def update_ranking():
    curr_level = int(request.args.get('current_level'))
    stats = get_classes_in_statistics(curr_level)
    ranking = get_ranking()
    return jsonify(
        ranking=ranking,
        instruction=stats
    )


@APP.route('/_get_current_level')
def get_current_level():
    curr_level = int(request.args.get('current_level'))
    if not curr_level == 0:
        pre_query = str(curr_level).join(QUERY_GET_LEVEL)
        curr_layer = SCRAPER.get_json(pre_query)
        state = curr_layer['features'][0]['attributes']['Status']
        if state != 'schwarz' and state in VALID_STATES:
            return jsonify(level=curr_level, state=state)
    for i in range(1, 8):
        if i != curr_level:
            query = str(i).join(QUERY_GET_LEVEL)
            curr_layer = SCRAPER.get_json(query)
            state = curr_layer['features'][0]['attributes']['Status']
            if state != 'schwarz' and state in VALID_STATES:
                return jsonify(level=i, state=state)
    if curr_level in VALID_LEVELS:
        return jsonify(level=curr_level, state=3)
    else:
        return jsonify(level=0, state=0)


def get_classes_in_statistics(curr_level):
    data_array = []

    if curr_level == 1 or curr_level == 3 or curr_level == 4:
        scrape_query = ""
        select_old_points = ""
        update_level_score = ""
        if curr_level == 1:
            scrape_query = QUERY_LEVEL_1
            select_old_points = "SELECT points FROM level1 WHERE class = %s"
            update_level_score = "UPDATE level1 SET points = %s WHERE class = %s"
        if curr_level == 3:
            scrape_query = QUERY_LEVEL_3
            select_old_points = "SELECT numb FROM level3 WHERE class = %s"
            update_level_score = "UPDATE level3 SET numb = %s WHERE class = %s"
        if curr_level == 4:
            scrape_query = QUERY_LEVEL_4
            select_old_points = "SELECT socks FROM level4 WHERE class = %s"
            update_level_score = "UPDATE level4 SET socks = %s WHERE class = %s"
        for player_id in PLAYER_IDS:
            level_points = 0
            features = SCRAPER.get_json(player_id.join(scrape_query))['features']
            if curr_level == 1:
                if(len(features)) > 0:
                    level_points = features[0]['attributes']['Flaeche']
            else:
                level_points = len(features) * 2
            CURSOR.execute(select_old_points, (player_id,))
            old_points = CURSOR.fetchone()[0]
            CURSOR.execute(QUERY_POINTS, (player_id,))
            curr_points = CURSOR.fetchone()[0]
            new_points = level_points - old_points + curr_points
            if old_points < level_points:
                CURSOR.execute(UPDATE_POINTS_QUERY, (new_points, player_id))
                CURSOR.execute(update_level_score, (level_points, player_id))
            data_array.append({"name": player_id, "points": level_points})

    else:
        for player_id in PLAYER_IDS:
            CURSOR.execute(QUERY_POINTS, (player_id,))
            points = CURSOR.fetchone()[0]
            data_array.append({"name": player_id, "points": points})
    CONNECTION.commit()
    return data_array


def get_classes():
    classes = []
    CURSOR.execute("SELECT name FROM classes ORDER BY number")
    for current_class in CURSOR.fetchall():
        classes.append(current_class[0])
    return classes


def get_ranking():
    classes = []
    for player_id in PLAYER_IDS:
        CURSOR.execute(GET_PLAYER_QUERY, (player_id,))
        result = CURSOR.fetchone()
        curr_class = {
            'class_id': player_id,
            'points': result[0],
            'class_name': result[1],
            'match': result[2],
            'state': result[5],
            'former_place': result[3],
            'old_trend': result[4]
        }
        classes.append(curr_class)

    classes = sorted(classes, key=itemgetter('points'))
    classes.reverse()
    curr_places = []
    for curr_class in classes:
        class_text = (
            CLASS_NAMES[curr_class['class_id']] +
            '<div class="points_ranking" style="float: right;" >' +
            str(curr_class['points']) +
            ' points' +
            '</div>'
        )
        curr_places.append(class_text)
    return curr_places


def get_instruction(level):
    CURSOR.execute(
        "SELECT instruction FROM instructions WHERE level = %s",
        (level,))
    return CURSOR.fetchone()[0]


def get_map(level):
    CURSOR.execute(
        "SELECT map_link FROM maps WHERE level = %s",
        (level,))
    return CURSOR.fetchone()[0]


def get_instruction_header(current_level, level):
    if current_level > level:
        return 'Passed'
    elif current_level < level:
        return 'Not Started'
    else:
        return 'Playing'


if __name__ == '__main__':
    APP.run()
