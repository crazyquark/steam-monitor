
from steam_web_api import Steam

from zoneinfo import ZoneInfo
from datetime import datetime
import asyncio
import signal

from config.secrets import STEAM_WEBAPI_KEY
from config.steam import users, check_interval_seconds, timezone
import db

steam = Steam(STEAM_WEBAPI_KEY)

prev_state = {}
prev_gameId = ''
prev_game = ''
start_time = None
end_time = None


def save_state():
    global prev_gameId
    global prev_game
    for user in users:
        if user in prev_state:
            db.store(dbname='state', data={
                'user': user,
                'game_id': prev_gameId,
                'game': prev_game,
                'prev_state': prev_state[user],
            })


def load_state():
    global prev_gameId
    global prev_game
    for user in users:
        state = db.get_data(user, 'state')
        if state:
            prev_gameId = state['game_id']
            prev_game = state['game']
            prev_state[user] = state['prev_state']


def check_status(user):
    global prev_gameId
    global prev_game
    global start_time
    global end_time

    tz = ZoneInfo(timezone)
    try:
        res = steam.users.search_user(user)
    except Exception as e:
        print(e)
        return

    # print(res)
    # logoff = datetime.fromtimestamp(
    #     res['player']['lastlogoff'], tz=tz)
    online = int(res['player']['personastate'])

    gameId = res['player']['gameid'] if 'gameid' in res['player'] else prev_gameId
    game = res['player']['gameextrainfo'] if 'gameextrainfo' in res['player'] else prev_game

    if not user in prev_state:
        prev_state[user] = {}

    # Could not get game info
    if online == 1 and not game:
        game = 'Steam'
        gameId = '-1'

    prev_online = prev_state[user][gameId] if gameId in prev_state[user] else 0
    if online == 1:
        if prev_online == 0:
            # Started game
            start_time = datetime.now(tz)
            db.store(dbname='activity', data={
                'user': user,
                'game_id': gameId,
                'game': game,
                'start_time': start_time
            })
        prev_state[user][gameId] = 1
        prev_gameId = gameId
        prev_game = game
    elif prev_online == 1:
        # Game end
        end_time = datetime.now(tz)
        db.store(dbname='activity', data={
            'user': user,
            'game_id': gameId,
            'game': prev_game,
            'end_time': end_time,
        })

        prev_state[user][gameId] = 0
        if start_time:
            db.store(dbname='session', data={
                'user': user,
                'game_id': gameId,
                'game': game,
                'start_time': start_time,
                'end_time': end_time,
                'duration': (end_time - start_time).total_seconds()
            })


async def check_user_loop():
    try:
        while True:
            for user in users:
                check_status(user)
            await asyncio.sleep(check_interval_seconds)
    except Exception as e:
        print(e)
        save_state()


def stop(signum, frame):
    asyncio.get_event_loop().stop()
    save_state()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    load_state()
    asyncio.run(check_user_loop())
