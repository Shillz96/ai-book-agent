# 🚀 Platform Setup – 1-Page Quick-Start

This guide shows how to:
1. Add your social & Google credentials.
2. Verify each platform connection.
3. Watch scheduler logs to track autonomous jobs.

---

## 1. Add Credentials

Copy the sample file and fill in real keys:
```bash
cp .env.sample .env
```

| Service | Required variables | Where to obtain |
|---------|--------------------|-----------------|
| Google Analytics 4 | `GOOGLE_ANALYTICS_PROPERTY_ID`  <br>`GOOGLE_ANALYTICS_CREDENTIALS_PATH` | GA4 Admin → Property Settings.<br>Create Service-Account JSON in Google Cloud → download file & point the path. |
| Google Ads | `GOOGLE_ADS_CUSTOMER_ID` <br>`GOOGLE_ADS_DEVELOPER_TOKEN` <br>`GOOGLE_ADS_CREDENTIALS_PATH` | Google Ads UI → Tools → API Centre.<br>Create OAuth2 / Service-Account JSON. |
| Twitter / X | `TWITTER_API_KEY` <br>`TWITTER_API_SECRET` <br>`TWITTER_ACCESS_TOKEN` <br>`TWITTER_ACCESS_TOKEN_SECRET` | https://developer.twitter.com → Project → Keys & Tokens. |
| Facebook & Instagram | `FACEBOOK_ACCESS_TOKEN` <br>`FACEBOOK_PAGE_ID` <br>`INSTAGRAM_ACCESS_TOKEN` <br>`INSTAGRAM_BUSINESS_ACCOUNT_ID` | Meta App Dashboard → Graph API Explorer & Pages tab. |
| Pinterest | `PINTEREST_ACCESS_TOKEN` <br>`PINTEREST_BOARD_ID` | Pinterest Dev Portal → Apps → OAuth Token. |

After editing `.env`, restart the backend so changes load.

```bash
# local run
python backend/main.py
```

---

## 2. Verify Platform Connections

The backend exposes a quick health check for each platform.
Replace `<platform>` with **twitter**, **facebook**, **instagram**, or **pinterest**.

```bash
curl http://localhost:5000/api/test-platform/<platform> | jq
```
Expected output example:
```json
{
  "platform": "twitter",
  "test_result": { "success": true, "message": "Connected as @YourHandle" },
  "timestamp": "..."
}
```
If `success` is `false`, re-check the matching credentials in `.env`.

---

## 3. Watch Scheduler Logs

Autonomous jobs (daily posts, weekly reports) run inside APScheduler.
To tail live logs:

### Local dev
```bash
# Standard terminal
python backend/main.py
# Logs stream to stdout. Look for lines like:
#   INFO  SchedulerService  - Executing daily autonomous operation
```

### Docker / cloud
```bash
# Docker
docker logs -f ai-book-agent-backend

# Render / Heroku / Railway
#   Use provider's "Logs" tab or CLI (e.g. heroku logs --tail).
```

Key log tags to watch:
* `SchedulerService` – job start/finish & next run time.
* `AsyncSocialMediaManager` – per-platform post status.
* `AutonomousMarketingManager` – performance analysis & decisions.

---

🎉  That's it!  Your system is ready to post, track, and optimise automatically. 