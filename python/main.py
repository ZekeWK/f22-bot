from mattermostdriver import Driver
import json

from secret import TOKEN
from configuration import *

def reactions_update(driver: Driver):
    reactions = driver.reactions.get_reactions_of_post(post_id = COURSE_REACTIONS_POST_ID)

    users = {}

    for reaction in reactions:
        if reaction["user_id"] not in users:
            users[reaction["user_id"]] = set()

        if reaction["emoji_name"] == "thermometer":
            users[reaction["user_id"]] |= COURSES["physics"]
        if reaction["emoji_name"] == "triangular_ruler":
            users[reaction["user_id"]] |= COURSES["math"]

    print(users)

async def event(data):
    print(data)

def main():
    driver = Driver({
        'url': 'mattermost.fysiksektionen.se',
        'basepath': '/api/v4',
        'verify': True,
        'scheme': 'https',
        'port': 443,
        'auth': None,
        'token': TOKEN,
        'keepalive': True,
        'keepalive_delay': 5,
        })

    driver.login()

#    print(driver.teams.get_team(team_id=TEAM_ID))

    reactions_update(driver)

#    driver.init_websocket(event)

    #driver.disconnect()

if __name__ == "__main__":
    main()
