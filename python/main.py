from mattermostdriver import Driver
from threading import Thread
import json

from secret import TOKEN
from configuration import *

def remove_channel_member(driver, channel_id, user_id):
    driver.channels.remove_channel_member(channel_id, user_id)

def add_channel_member(driver, channel_id, user_id):
    driver.channels.add_user(channel_id, {"user_id": user_id})

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

    threads = []
    users_in_channels = {}
    for channel in COURSE_CHANNEL_IDS:
        thread = users_in_channels[channel] = driver.channels.get_channel_members(COURSE_CHANNEL_IDS[channel])

    for channel in COURSE_CHANNEL_IDS:
        for user_in_channel in users_in_channels[channel]:
            if user_in_channel["user_id"] not in users or channel not in users[user_in_channel["user_id"]]:
                if user_in_channel["user_id"] == driver.client.userid:
                    continue
                print(f"Removing '{user_in_channel['user_id']}' from '{channel}'")
                Thread(target = remove_channel_member, args = (driver, COURSE_CHANNEL_IDS[channel], user_in_channel["user_id"])).start()
            else:
                users[user_in_channel["user_id"]] -= { channel }

    for user in users:
        if not users[user]:
            continue
        print(f"Adding '{user}' to '{users[user]}'")
        for channel in users[user]:
            Thread(target = add_channel_member, args = (driver, COURSE_CHANNEL_IDS[channel], user)).start()

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
