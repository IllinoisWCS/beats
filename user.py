from config import config
from db import Session, BannedUser
import requests
import json
import threading

CROWD_SERVER = config.get('Crowd', 'server')
CROWD_APPLICATION_NAME = config.get('Crowd', 'application_name')
CROWD_PASSWORD = config.get('Crowd', 'password')

CROWD_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}


def get_user(username):
    r = requests.get(
        'http://' + CROWD_SERVER + '/crowd/rest/usermanagement/1/user',
        params={'username': username},
        headers=CROWD_HEADERS,
        auth=(CROWD_APPLICATION_NAME, CROWD_PASSWORD)
    )
    return r


def create_session(username, password):
    """Return Crowd session or instance of BannedUser if user is banned"""
    r = requests.post(
        'http://' + CROWD_SERVER + '/crowd/rest/usermanagement/1/session',
        data=json.dumps({'username': username, 'password': password}),
        headers=CROWD_HEADERS,
        auth=(CROWD_APPLICATION_NAME, CROWD_PASSWORD)
    )
    if r.status_code == requests.codes.created:
        ban_details = get_ban_details(username)
        if ban_details is not None:
            return ban_details
    return r


def get_session(token):
    r = requests.get(
        'http://%s/crowd/rest/usermanagement/1/session/%s' % (
            CROWD_SERVER, token),
        headers=CROWD_HEADERS,
        auth=(CROWD_APPLICATION_NAME, CROWD_PASSWORD))
    if r.status_code == requests.codes.ok:
        threading.Thread(target=validate_session, args=(token,)).start()
    return r


def validate_session(token):
    r = requests.post(
        'http://%s/crowd/rest/usermanagement/1/session/%s' % (
            CROWD_SERVER, token),
        data=json.dumps({}),
        headers=CROWD_HEADERS,
        auth=(CROWD_APPLICATION_NAME, CROWD_PASSWORD))
    return r


def delete_session(token):
    r = requests.delete(
        'http://%s/crowd/rest/usermanagement/1/session/%s' % (
            CROWD_SERVER, token),
        headers=CROWD_HEADERS,
        auth=(CROWD_APPLICATION_NAME, CROWD_PASSWORD))
    return r


def valid_session(token):
    session = get_session(token)
    user = session.json()['user']['name']
    return (session.status_code == requests.codes.ok and
            get_ban_details(user) is None)


def get_ban_details(user):
    """Returns instance of BannedUser if user is banned, or None otherwise"""
    session = Session()
    ban_details = session.query(BannedUser).filter_by(username=user).first()
    session.commit()
    return ban_details
