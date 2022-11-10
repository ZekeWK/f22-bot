from mattermostdriver import Driver
from threading import Thread
import json

from secret import TOKEN
from configuration import *
from ws import WebSocket

def remove_channel_member(driver, channel, user_id, users_in_channels):
    driver.channels.remove_channel_member(COURSE_CHANNEL_IDS[channel], user_id)
    users_in_channels[channel].remove(user_id)

def add_channel_member(driver, channel, user_id, users_in_channels):
    driver.channels.add_user(COURSE_CHANNEL_IDS[channel], {"user_id": user_id})
    users_in_channels[channel].add(user_id)

def get_channel_members(driver, channel, channel_id, users_in_channels):
    users_in_channels[channel] = { user["user_id"] for user in driver.channels.get_channel_members(channel_id) }

class CourseChannels:
    def __init__(self, driver: Driver):
        self.driver = driver
        self.reactions = {}
        self.users_in_channels = {}
        self.users = {}

        self.setup_reactions_and_users_in_channels()
        self.build_users()
        self.fix_diff()

        print("react")
        print(self.reactions)
        print("us in ch")
        print(self.users_in_channels)
        print("users")
        print(self.users)

    def setup_reactions_and_users_in_channels(self):
        self.reactions = {}
        for reaction in (self.driver.reactions.get_reactions_of_post(post_id = COURSE_REACTIONS_POST_ID) or []):
            if reaction["user_id"] not in self.reactions:
                self.reactions[reaction["user_id"]] = set()

            self.reactions[reaction["user_id"]].add(reaction["emoji_name"])

        threads = []
        self.users_in_channels = {}
        for channel in COURSE_CHANNEL_IDS:
            thread = Thread(target = get_channel_members, args = (self.driver, channel, COURSE_CHANNEL_IDS[channel], self.users_in_channels))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def build_users(self):
        self.users = {}
        for user in self.reactions:
            if user not in self.users:
                self.users[user] = set()

            for emoji_name in self.reactions[user]:
                if emoji_name == "thermometer":
                    self.users[user] |= COURSES["physics"]
                if emoji_name == "triangular_ruler":
                    self.users[user] |= COURSES["math"]

    def fix_diff(self):
        for channel in COURSE_CHANNEL_IDS:
            for user_in_channel in self.users_in_channels[channel]:
                if user_in_channel not in self.users or channel not in self.users[user_in_channel]:
                    if user_in_channel == self.driver.client.userid:
                        continue
                    print(f"Removing '{user_in_channel}' from '{channel}'")
                    Thread(target = remove_channel_member, args = (self.driver, channel, user_in_channel, self.users_in_channels)).start()
                else:
                    self.users[user_in_channel] -= { channel }

        for user in self.users:
            if not self.users[user]:
                continue
            print(f"Adding '{user}' to '{self.users[user]}'")
            for channel in self.users[user]:
                Thread(target = add_channel_member, args = (self.driver, channel, user, self.users_in_channels)).start()

    def reaction_added(self, data):
        reaction = json.loads(data["reaction"])
        if reaction["user_id"] not in self.reactions:
            self.reactions[reaction["user_id"]] = set()

        self.reactions[reaction["user_id"]].add(reaction["emoji_name"])

        self.build_users()
        self.fix_diff()

    def reaction_removed(self, data):
        reaction = json.loads(data["reaction"])
        if reaction["user_id"] not in self.reactions:
            self.reactions[reaction["user_id"]] = set()

        if reaction["emoji_name"] in self.reactions[reaction["user_id"]]:
            self.reactions[reaction["user_id"]].remove(reaction["emoji_name"])

        self.build_users()
        self.fix_diff()

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

    ws = WebSocket()

    cc = CourseChannels(driver)

    ws.subscribe("reaction_added", cc.reaction_added)
    ws.subscribe("reaction_removed", cc.reaction_removed)

#    driver.init_websocket(event)

    #driver.disconnect()

if __name__ == "__main__":
    main()
