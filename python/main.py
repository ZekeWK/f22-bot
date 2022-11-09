from mattermostdriver import Driver

from secret import TOKEN

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

    print(driver.teams.get_teams())

if __name__ == "__main__":
    main()
