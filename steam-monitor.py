
from steam_web_api import Steam

from zoneinfo import ZoneInfo
from datetime import datetime
import asyncio

from config.secrets import STEAM_WEBAPI_KEY
import db

users = ['crazyquark']
steam = Steam(STEAM_WEBAPI_KEY)
wait_time = 60

prev_state = {}


def check_status(user):
    tz = ZoneInfo('Europe/Bucharest')
    res = steam.users.search_user(user)
    # print(res)
    # logoff = datetime.fromtimestamp(
    #     res['player']['lastlogoff'], tz=tz)
    # online = int(res['player']['personastate'])

    gameId = res['player']['gameid'] if 'gameid' in res['player'] else ''
    game = res['player']['gameextrainfo'] if 'gameextrainfo' in res['player'] else ''

    prev_online = prev_state[user][gameId] if user in prev_state and gameId in prev_state[user] else 0
    if gameId:
        if prev_online == 0:
            # Started game
            start_time = datetime.now(tz)
            db.store(data={
                'user': user,
                'game_id': gameId,
                'game': game,
                'start_time': start_time
            })

        prev_state[user][gameId] = 1
    elif prev_state == 1:
        # Game end
        end_time = datetime.now(tz)
        db.store(date={
            'user': user,
            'game_d': gameId,
            'game': game,
            'end_time': end_time,
        })

        prev_state[user][gameId] = 0


async def check_user_loop():
    while True:
        for user in users:
            check_status(user)
        await asyncio.sleep(wait_time)


if __name__ == '__main__':
    asyncio.run(check_user_loop())
