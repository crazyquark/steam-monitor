
from steam_web_api import Steam

from zoneinfo import ZoneInfo
from datetime import datetime
import asyncio

from config.secrets import STEAM_WEBAPI_KEY
from config.steam import users, check_interval_seconds, timezone
import db

steam = Steam(STEAM_WEBAPI_KEY)

prev_state = {}
prev_gameId = ''
start_time = None
end_time = None


def save_state():
    global prev_gameId
    for user in users:
        if user in prev_state:
            db.store(dbname='state', data={
                'user': user,
                'game_id': prev_gameId,
                'prev_state': prev_state[user],
            })


def load_state():
    global prev_gameId
    for user in users:
        state = db.get_data(user, 'state')
        if state:
            prev_gameId = state['game_id']
            prev_state[user] = state['prev_state']


def check_status(user):
    global prev_gameId
    global start_time
    global end_time

    tz = ZoneInfo(timezone)
    res = steam.users.search_user(user)
    # print(res)
    # logoff = datetime.fromtimestamp(
    #     res['player']['lastlogoff'], tz=tz)
    online = int(res['player']['personastate'])

    gameId = res['player']['gameid'] if 'gameid' in res['player'] else prev_gameId
    game = res['player']['gameextrainfo'] if 'gameextrainfo' in res['player'] else ''

    if not user in prev_state:
        prev_state[user] = {}

    # Could not retrieve game info, so just log online time on Steam
    if not game and online == 1:
        gameId = '-1'
        game = 'Steam'

    prev_online = prev_state[user][gameId] if gameId in prev_state[user] else 0
    if game:
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
    elif prev_online == 1:
        # Game end
        end_time = datetime.now(tz)
        db.store(dbname='activity', data={
            'user': user,
            'game_id': gameId,
            'game': game,
            'end_time': end_time,
        })

        prev_state[user][gameId] = 0
        if start_time:
            db.store(dbname='session', data={
                'user': user,
                'game_id': gameId,
                'start_time': start_time,
                'duration': (end_time - start_time).total_seconds()
            })


async def check_user_loop():
    try:
        while True:
            for user in users:
                check_status(user)
            await asyncio.sleep(check_interval_seconds)
    except:
        save_state()

if __name__ == '__main__':
    load_state()
    asyncio.run(check_user_loop())
