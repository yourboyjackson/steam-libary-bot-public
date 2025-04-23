# Steam Library Bot Setup Guide
Setup this bot to monitor the steam libraries of given users and make posts in discord when new games are added to any of the users libraries.
note: The steam library of each user needs to be set to public.

## 🛠 Step 1: Get a GitHub account (if you don’t already)

GitHub is used to store your project code, steam library data, and execute code on a specified schedule. Render (Cloud service) pulls the code from your GitHub project and uploads the library data back to GitHub.

## Step 2: Create new GitHub projects

1. Create a new project (`steam-library-bot`)
2. Create 2 files in project: `main.py` and `requirements.txt`
3. Add attached code below into each file and commit (save)
4. Create 2nd new project (`steam-games-tracker`)
5. Create `README.md` file in new folder by entering the name `games-data/README.md` and commit

## Step 3: Create a GitHub Personal Access Token (PAT)

1. Go to **GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens**:  
   [GitHub Tokens](https://github.com/settings/tokens)
2. Click **"Generate new token"**:
   - **Token name**: e.g. render web server
   - **Expiration**: No expiration
   - **Repository access**:
     - Only select repositories → `<yourgithub>/steam-games-tracker`
   - **Permissions**:
     - Repositories → Contents → Read & Write ✅
3. Generate the token and copy/save it for later

## Step 4: Setup Discord webhook

1. Go to **server settings → Integrations → Webhooks**
2. Create new webhook
3. Click the webhook and update the name and text channel then copy the webhook URL and save it for later

## Step 5: Get your Steam API Key & SteamID64

1. Go to: [https://steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey)
2. Sign in and register for a key and put `localhost` as the domain
3. Copy your API key

To find your SteamID64:

1. Go to [https://steamid.io/](https://steamid.io/)
2. Paste your profile link, it will show your 64-bit SteamID
3. Get the SteamID64 of each users library you wish to track

✅ Save both values somewhere handy.

## Step 6: Deploy on Render

1. Go to [https://dashboard.render.com/](https://dashboard.render.com/) and sign up
2. Click **Add new → Web Service**
3. Connect your GitHub and find your `steam-library-bot` repo
4. Fill settings (leave others as default):
   - **Name**: whatever you want
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
   - **Auto-Deploy (under Advanced)**: No
   - **Instance Type**: Free
5. Set Environment variables:
   - `STEAM_API_KEY` → e.g. `E0FDE3D8279FA948DDDDDDDD03FD897E`
   - `DISCORD_WEBHOOK_URL` → e.g. `https://discord.com/api/webhooks/138778GH…`
   - `STEAM_ACCOUNTS` → `[{"steamid":"<STEAM64ID>","name":"<Display Name>"}]`  
     Example:  
     ```json
     [{"steamid":"76561198777777690","name":"John"},{"steamid":"76561198888888690","name":"Jane"}]
     ```
   - `GITHUB_TOKEN` → e.g. `github_pat_11A7N5NMQ_......sRRH6ISL3PCtkjVJVcy`
   - `GITHUB_REPO` → e.g. `yourgithubusername/steam-games-tracker`
6. Deploy the web service and copy your web service's unique URL, e.g. `https://YOUR-RENDER-URL.onrender.com`

## Step 7: Create GitHub Action/Workflow

1. In your project `steam-library-bot` create a new workflow by creating a new file with the name `.github/workflows/steam_check.yml`
2. In the attached code update the URL to your unique render web service URL and add `/run` to the end
3. Copy the code into your `steam_check.yml` file in GitHub and commit
4. The workflow will now be executed every 2 hours (or however often you like) by GitHub Actions

---

# Optional - How to run task on demand (Manually)

1. From your project `steam-library-bot` click the **Actions** tab at the top
2. On the left-hand side under **Actions** click your workflow **Steam Library Checker**
3. Click **Run workflow** and wait for the results below

---

# Additional Information

If you ever update the environment variables on Render, before the new values will take effect you need to clear the build cache by clicking **Manual Deploy → Clear build cache & deploy**.
