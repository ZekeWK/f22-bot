from mattermostdriver import Driver
from threading import Thread
import json

from secret import TOKEN
from configuration import *

def remove_channel_member(driver, channel_id, user_id):
    driver.channels.remove_channel_member(channel_id, user_id)

def add_channel_member(driver, channel_id, user_id):
    driver.channels.add_user(channel_id, {"user_id": user_id})

def get_channel_members(driver, channel, channel_id, users_in_channels):
    users_in_channels[channel] = [user["user_id"] for user in driver.channels.get_channel_members(channel_id)]

class CourseChannels:
    def __init__(self, driver: Driver):
        self.driver = driver

    def reactions_update(self):
        reactions = self.driver.reactions.get_reactions_of_post(post_id = COURSE_REACTIONS_POST_ID) or []

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
            thread = Thread(target = get_channel_members, args = (self.driver, channel, COURSE_CHANNEL_IDS[channel], users_in_channels))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        for channel in COURSE_CHANNEL_IDS:
            for user_in_channel in users_in_channels[channel]:
                if user_in_channel not in users or channel not in users[user_in_channel]:
                    if user_in_channel == self.driver.client.userid:
                        continue
                    print(f"Removing '{user_in_channel}' from '{channel}'")
                    Thread(target = remove_channel_member, args = (self.driver, COURSE_CHANNEL_IDS[channel], user_in_channel)).start()
                else:
                    users[user_in_channel] -= { channel }

        for user in users:
            if not users[user]:
                continue
            print(f"Adding '{user}' to '{users[user]}'")
            for channel in users[user]:
                Thread(target = add_channel_member, args = (self.driver, COURSE_CHANNEL_IDS[channel], user)).start()

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

    cc = CourseChannels(driver)
    cc.reactions_update()

#    driver.init_websocket(event)

    #driver.disconnect()

if __name__ == "__main__":
    main()
