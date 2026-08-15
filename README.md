# Flask + Express App — PM2 + Jenkins CI/CD (Local or EC2)

Same Flask backend (port **5000**) + Express frontend (port **3000**) app as
before, now set up to run with **PM2** (process manager) and get deployed
automatically through **two separate Jenkins pipelines**, triggered by a
**GitHub webhook** on every push.

This works identically on your **local machine** or on an **AWS EC2
instance** — there is exactly **ONE line** you need to change when you move
between the two (explained below).

---

## 1. Project structure

```
jenkins-project/
├── backend/
│   ├── app.py                # Flask API + simple HTML data-view page
│   └── requirements.txt
├── frontend/
│   ├── server.js              # Express server, reads API_BASE_URL
│   ├── package.json
│   └── public/index.html      # Colorful animated form
├── ecosystem.config.js        # PM2 config for BOTH apps (see below)
├── Jenkinsfile-backend         # Jenkins pipeline #1 (Flask)
├── Jenkinsfile-frontend        # Jenkins pipeline #2 (Express)
└── README.md
```

---

## 2. ⚠️ The ONE thing to change (Local vs EC2)

Open **`ecosystem.config.js`** in the project root. Inside the
`express-frontend` app block there's one line:

```js
API_BASE_URL: "http://localhost:5000",
```

| Where you're running | What to set it to |
|---|---|
| Your local machine | `"http://localhost:5000"` (already the default — no change needed) |
| AWS EC2 instance | `"http://<YOUR_EC2_PUBLIC_IP>:5000"` — e.g. `"http://13.234.56.78:5000"` |

That's it — nothing else in the code needs to change. The backend already
listens on `0.0.0.0` (all network interfaces), so it's reachable from
outside as long as the port is open (see EC2 section below).

If you ever restart the app after changing this line, just run:
```bash
pm2 restart express-frontend
```

---

## 3. Prerequisites

| Tool | Check | Install |
|---|---|---|
| Python 3 + pip | `python3 --version` | usually pre-installed |
| Node.js + npm | `node --version` | https://nodejs.org |
| PM2 | `pm2 --version` | `npm install -g pm2` |
| Git | `git --version` | https://git-scm.com |

---

## 4. Run it manually — Local machine

```bash
cd jenkins-project

# 1. Install backend dependencies
cd backend
pip3 install -r requirements.txt
cd ..

# 2. Install frontend dependencies
cd frontend
npm install
cd ..

# 3. Start both apps with PM2 (uses ecosystem.config.js)
pm2 start ecosystem.config.js

# 4. Check status
pm2 status
```

Open:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

Fill the form → data is saved by the Flask backend and shows up both on the
frontend list and on `http://localhost:5000`.

**Useful PM2 commands:**
```bash
pm2 logs                    # see logs from both apps
pm2 logs flask-backend      # logs for just the backend
pm2 restart flask-backend   # restart one app
pm2 restart express-frontend
pm2 stop all                # stop both
pm2 delete all              # remove both from PM2
```

---

## 5. Run it manually — AWS EC2

### 5.1 Launch the EC2 instance
- AMI: Amazon Linux 2023 or Ubuntu 22.04
- Instance type: t2.micro is enough for this demo
- **Security Group** — add inbound rules for:
  - `22` (SSH) — your IP
  - `3000` (frontend) — `0.0.0.0/0` (or your IP for safety)
  - `5000` (backend) — `0.0.0.0/0` (or your IP for safety)
  - `8080` (Jenkins UI, if you're hosting Jenkins on this same instance) — your IP

### 5.2 Connect and install prerequisites
```bash
ssh -i your-key.pem ec2-user@<YOUR_EC2_PUBLIC_IP>

# Amazon Linux
sudo yum update -y
sudo yum install -y python3 python3-pip git
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs
sudo npm install -g pm2

# Ubuntu (alternative)
# sudo apt update && sudo apt install -y python3 python3-pip git
# curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
# sudo apt install -y nodejs
# sudo npm install -g pm2
```

### 5.3 Get the code onto the instance
```bash
git clone <your-git-repo-url> jenkins-project
cd jenkins-project
```
(Or upload the project folder with `scp` if you're not using Git yet.)

### 5.4 Set the ONE config line (see Section 2)
```bash
nano ecosystem.config.js
# change API_BASE_URL to http://<YOUR_EC2_PUBLIC_IP>:5000
# save: Ctrl+O, Enter, Ctrl+X
```

### 5.5 Install dependencies and start
```bash
cd backend && pip3 install -r requirements.txt && cd ..
cd frontend && npm install && cd ..
pm2 start ecosystem.config.js
pm2 save
pm2 startup     # follow the printed command to make PM2 survive reboots
```

### 5.6 Open it
- Frontend: `http://<YOUR_EC2_PUBLIC_IP>:3000`
- Backend: `http://<YOUR_EC2_PUBLIC_IP>:5000`

---

## 6. Jenkins Setup — Two Pipelines

### 6.1 Install Jenkins (skip if you already have a Jenkins server)
```bash
# Amazon Linux / EC2 example
sudo yum install -y java-17-amazon-corretto
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
sudo yum install -y jenkins
sudo systemctl enable jenkins
sudo systemctl start jenkins
```
Open `http://<SERVER_IP>:8080`, unlock Jenkins using:
```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```
Install the **suggested plugins**, then also install from
**Manage Jenkins → Plugins**:
- `Git plugin` (usually already installed)
- `GitHub plugin`
- `Pipeline` (usually already installed)

Make sure the **jenkins** system user can run `pm2`, `pip3`, and `npm`
(install Node/Python/PM2 on the Jenkins machine too, same as Section 5.2).

### 6.2 Create Pipeline #1 — Flask backend
1. Jenkins Dashboard → **New Item**
2. Name: `flask-backend-pipeline` → select **Pipeline** → OK
3. Under **Build Triggers**, check ✅ **GitHub hook trigger for GITScm polling**
4. Under **Pipeline**:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: your Flask backend repo URL
   - Branch: `*/main`
   - Script Path: `Jenkinsfile-backend`
5. Save

> Before this works, edit `Jenkinsfile-backend` in your repo and replace
> `https://github.com/<your-username>/<flask-backend-repo>.git` with your
> actual repository URL.

### 6.3 Create Pipeline #2 — Express frontend
Repeat the same steps:
1. **New Item** → Name: `express-frontend-pipeline` → **Pipeline** → OK
2. ✅ **GitHub hook trigger for GITScm polling**
3. Pipeline script from SCM → Git → your Express frontend repo URL → branch `*/main` → Script Path: `Jenkinsfile-frontend`
4. Save

> Same here — edit `Jenkinsfile-frontend` and replace the placeholder repo
> URL with your actual one.

### 6.4 What each pipeline does
```
Checkout  →  Install Dependencies  →  Restart with PM2
```
- **Flask pipeline:** `git pull` → `pip3 install -r requirements.txt` → `pm2 restart flask-backend`
- **Express pipeline:** `git pull` → `npm install` → `pm2 restart express-frontend`

---

## 7. GitHub Webhook — auto-trigger on every push

For **each** GitHub repository (Flask repo and Express repo):

1. Open the repo on GitHub → **Settings** → **Webhooks** → **Add webhook**
2. **Payload URL:**
   ```
   http://<YOUR_JENKINS_SERVER_IP>:8080/github-webhook/
   ```
   (Note the trailing slash — it's required.)
3. **Content type:** `application/json`
4. **Which events:** "Just the push event"
5. Click **Add webhook**

Now every `git push` to that repo will automatically trigger the matching
Jenkins pipeline, which pulls the code, installs dependencies, and restarts
the app with PM2 — no manual steps needed.

> If Jenkins is running on an EC2 instance, make sure port `8080` is open in
> the Security Group (at least to GitHub's IP ranges, or `0.0.0.0/0` for
> simplicity in a test setup).

### Test it
```bash
git commit --allow-empty -m "test webhook"
git push
```
Then check **Jenkins Dashboard → flask-backend-pipeline (or express-frontend-pipeline) → Build History** — a new build should start within a few seconds.

---

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| Frontend loads but shows "Could not reach backend API" | `API_BASE_URL` in `ecosystem.config.js` is wrong — check Section 2. Run `pm2 restart express-frontend` after fixing it |
| Can't open the app from browser on EC2 | Security Group isn't allowing inbound traffic on port 3000/5000 — check Section 5.1 |
| `pm2: command not found` | Run `sudo npm install -g pm2` |
| `pip3: command not found` | Install Python 3: `sudo yum install -y python3 python3-pip` (or `apt` on Ubuntu) |
| App doesn't restart after PM2 config change | `pm2 delete all` then `pm2 start ecosystem.config.js` |
| PM2 processes gone after reboot | Run `pm2 save` and `pm2 startup` once (Section 5.5) |
| Jenkins build fails at "Restart Application" | The `jenkins` user can't find `pm2`/`pip3`/`npm` — install them for that user, or add their install path to Jenkins' `PATH` (Manage Jenkins → Configure System → Global properties → Environment variables) |
| Webhook doesn't trigger the pipeline | Check GitHub repo → Settings → Webhooks → click the webhook → "Recent Deliveries" tab for the error; make sure the Payload URL is reachable from the internet and ends with `/github-webhook/` |
| `git` checkout fails in Jenkins | Make sure the repo URL in the `Jenkinsfile` is correct and, for private repos, that Jenkins has valid Git credentials configured (Manage Jenkins → Credentials) |
| Data resets after every deploy | This is expected if you delete `backend/data/items.db`. Normally it persists across `pm2 restart` since restart doesn't wipe files, only recreates the process |

---

## 9. How data flows

```
Browser (any IP/hostname)
   │
   │ opens :3000
   ▼
Express frontend (PM2: express-frontend)
   │
   │ form submit → fetch(API_BASE_URL + "/api/items")
   ▼
Flask backend (PM2: flask-backend, port 5000)
   │
   ▼
SQLite file: backend/data/items.db
```

Because `API_BASE_URL` is the single configurable value, the exact same code
works whether the browser, frontend, and backend are all on `localhost`, or
spread across an EC2 instance reachable by its public IP.
