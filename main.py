from fastapi import FastAPI, BackgroundTasks
import requests
import json
import os
import base64

app = FastAPI()

STEAM_API_KEY = os.getenv("STEAM_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
STEAM_ACCOUNTS = json.loads(os.getenv("STEAM_ACCOUNTS", "[]"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")  # Format: "username/reponame"
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")  # Defaults to main if not set

def github_get_file(account_name):
    path = f"games-data/{account_name}_games.json"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}?ref={GITHUB_BRANCH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()["content"]
        decoded = base64.b64decode(content).decode()
        return json.loads(decoded)
    else:
        print(f"[INFO] No previous games list found for {account_name}. Assuming first run.")
        return None

def github_put_file(account_name, games):
    path = f"games-data/{account_name}_games.json"
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Check if file already exists to get its SHA
    get_resp = requests.get(api_url, headers=headers)
    sha = get_resp.json().get("sha") if get_resp.status_code == 200 else None

    content = base64.b64encode(json.dumps(games, indent=2).encode()).decode()

    payload = {
        "message": f"Update games list for {account_name}",
        "content": content,
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    put_resp = requests.put(api_url, headers=headers, json=payload)
    if put_resp.status_code not in (200, 201):
        print(f"[ERROR] Failed to upload {account_name}_games.json: {put_resp.text}")

def get_owned_games(steam_id):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": STEAM_API_KEY,
        "steamid": steam_id,
        "include_appinfo": True
    }
    response = requests.get(url, params=params)
    return response.json().get('response', {}).get('games', [])

def send_discord_embed(new_games_by_account):
    if not new_games_by_account:
        return

    embeds = []

    for account_name, new_games in new_games_by_account.items():
        for game in new_games:
            appid = game['appid']
            game_name = game['name']
            store_url = f"https://store.steampowered.com/app/{appid}"
            header_image_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"

            embed = {
                "title": f"{account_name}: {game_name}",
                "url": store_url,
                "image": {"url": header_image_url},
                "color": 0x1b2838
            }
            embeds.append(embed)

    for i in range(0, len(embeds), 10):
        chunk = embeds[i:i+10]
        payload = {"content": "🎮 New games added to Steam libraries!", "embeds": chunk}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code != 204:
            print(f"[ERROR] Failed to send Discord message: {response.text}")

def check_for_new_games():
    new_games_by_account = {}

    for account in STEAM_ACCOUNTS:
        steam_id = account['steamid']
        account_name = account.get('name', steam_id)

        previous_games = github_get_file(account_name)
        current_games = get_owned_games(steam_id)

        if previous_games is None:
            print(f"[INFO] First run for {account_name}. Saving games without sending notification.")
            github_put_file(account_name, current_games)
            continue

        previous_game_ids = {game['appid'] for game in previous_games}
        new_games = [game for game in current_games if game['appid'] not in previous_game_ids]

        if new_games:
            new_games_by_account[account_name] = new_games

        github_put_file(account_name, current_games)

    if new_games_by_account:
        send_discord_embed(new_games_by_account)

@app.get("/run")
def run_checker(background_tasks: BackgroundTasks):
    background_tasks.add_task(check_for_new_games)
    return {"status": "OK"}
