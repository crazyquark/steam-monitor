
from steam_web_api import Steam

from zoneinfo import ZoneInfo
from datetime import datetime

from config.secrets import STEAM_WEBAPI_KEY

steam = Steam(STEAM_WEBAPI_KEY)

res = steam.users.search_user('crazyquark')
print(res)
logoff = datetime.fromtimestamp(
    res['player']['lastlogoff'], tz=ZoneInfo('Europe/Bucharest'))
online = res['player']['personastate']
gameid = res['player']['gameid'] if 'gameid' in res['player'] else ''
game = res['player']['gameextrainfo'] if 'gameextrainfo' in res['player'] else ''
print(logoff)
print(online)
print(gameid)
print(game)
