from mattermostdriver import Driver

from secret import TOKEN
from configuration import TEAM_ID

def event(data):
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

    print(driver.teams.get_team(team_id=TEAM_ID))

    driver.init_websocket(event)

    #driver.disconnect()

if __name__ == "__main__":
    main()
