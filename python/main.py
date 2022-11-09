from mattermostdriver import Driver

from secret import TOKEN, TEAM_ID

def main():
    driver = Driver({
        'url': 'mattermost.fysiksektionen.se',
        'scheme': 'https',
        'port': 443,
        'token': TOKEN,
        'keepalive': True,
        'keepalive_delay': 5
        })

    driver.login()

    print(driver.teams.get_team(team_id=TEAM_ID))

if __name__ == "__main__":
    main()
