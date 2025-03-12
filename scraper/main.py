import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# Base URL for player index pages (A-Z)
BASE_URL = "https://www.pro-football-reference.com/players/{}/"

# Function to get player links from a given letter page
def get_player_links(letter):
    all_links = []
    page_num = 1
    
    while True:
        url = BASE_URL.format(letter) + f"/index.htm?letter={letter}&page={page_num}"  # Adjust URL for pagination
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        links = []

        # Find all player links
        for link in soup.select("th.left a"):
            href = link.get("href")
            if href.startswith("/players/"):
                player_link = "https://www.pro-football-reference.com" + href
                links.append(player_link)
                print(f"Found player link: {player_link}")  # Debug print

        if not links:
            break  # Stop scraping if no links are found (end of pages)

        all_links.extend(links)
        page_num += 1

    return all_links

def get_player_stats(player_url):
    response = requests.get(player_url)
    if response.status_code != 200:
        print(f"Failed to fetch {player_url}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find player name
    name = soup.find("h1", {"itemprop": "name"}).text.strip()

    # Find player position
    position_elem = soup.find("strong", text="Position:")
    position = position_elem.find_next_sibling(text=True).strip() if position_elem else "N/A"

    # Extract player career stats from the first stats table (Basic Stats)
    table = soup.find("table", {"id": "stats"})
    stats = {}
    
    if table:
        headers = [th.text.strip() for th in table.find_all("th")][1:]  # Skip first header (index column)
        rows = table.find_all("tr")[-1]  # Get last row (career stats)
        
        for i, td in enumerate(rows.find_all("td")):
            stats[headers[i]] = td.text.strip()

    return {"Name": name, "Position": position, **stats}


def scrape_all_players():
    all_players = []
    total_requests = 0 # Keep track of the total number of requests made

    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        print(f"Scraping players from letter: {letter}")
        player_links = get_player_links(letter)

        for player_url in player_links:
            print(f"Scraping stats for {player_url}")
            player_stats = get_player_stats(player_url)
            if player_stats:
                all_players.append(player_stats)
            
            total_requests += 1
            
            # Ensure not to exceed rate limit (10 requests per minute)
            if total_requests % 10 == 0:
                print(f"Sleeping for 60 seconds...")
                time.sleep(60)  # Sleep for 1 minute to stay within rate limits

            # Add random delay between requests to further reduce the risk of being blocked
            time.sleep(random.uniform(1, 3))  # Sleep for a random interval (1 to 3 seconds)

    df = pd.DataFrame(all_players)
    df.to_csv("nfl_players_stats.csv", index=False)
    print("All player stats saved to nfl_players_stats.csv")

scrape_all_players()
