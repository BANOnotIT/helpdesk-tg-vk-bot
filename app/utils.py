import requests

phrase_settings = {
    'Pos1': 'a',
    'Level1': 60,
    'Pos2': 'n',
    'Level2': 10,
    'Pos3': 'i',
    'Level3': 60,
    'Pos4': 't',
    'Level4': 70,
}


def get_random_phrase():
    resp = requests.post('http://watchout4snakes.com/wo4snakes/Random/RandomPhrase', phrase_settings)

    return resp.text
