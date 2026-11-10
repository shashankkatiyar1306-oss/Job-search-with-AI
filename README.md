# Naukri Job Agent for Claude

A daily job-hunting agent that runs inside Claude. Every morning it searches Naukri for jobs posted in the last 24 hours, reads each job description, scores it against your CV, and applies to the strong matches. For every application it writes a CV tailored to that job and sends it to you on Telegram. When a recruiter's screening question asks something it doesn't know, it messages you on Telegram, waits for your reply, and finishes the application.

You never hand over your password. The agent uses the Naukri account you're already signed in to in the Claude desktop app's built-in browser.

## How a run works

1. Reads its instructions, your CV and your settings from a folder in your Google Drive.
2. Picks up any answers you sent on Telegram since the last run.
3. Searches Naukri with your saved searches, filtered to the last day.
4. Opens each job, scores the fit from 1 to 10, and keeps the strong matches (7+).
5. Applies with your current Naukri CV. Screening questions are answered only from your CV and your saved answers; anything else is sent to you on Telegram.
6. Sends you a tailored CV PDF for each application.
7. Writes a log to Drive and sends you a short summary.

## Read this first

- **Check Naukri's terms of use.** Job portals often restrict automated access. You're responsible for how you use this on your own account.
- **It applies with your real profile.** Start with a low limit (`max_applications_per_run: 1` or `2`) and read the logs for a few days.
- **It never guesses.** It won't invent salary, notice period or skills. Unknown questions come to you. Tailored CVs only reorder and reword facts already in your CV.
- **It never replaces the CV on your Naukri profile.** Tailored CVs are sent to you on Telegram, for company-site applications or your own use.

## What you need

- A Claude plan that includes the **Claude desktop app** and **scheduled tasks**.
- A computer that's on, online and awake at the scheduled time, with the Claude desktop app open. The schedule lives in the cloud; the browser that applies lives on your computer.
- The **Google Drive connector** connected in Claude.
- A **Telegram** account (the bot is free).
- `api.telegram.org` added to your allowed domains in claude.ai: Settings, Capabilities.

## Setup

### Option A: let Claude set it up (recommended)

Open [SETUP_PROMPT.md](SETUP_PROMPT.md), copy the prompt into a new chat in the Claude desktop app, attach your resume, and follow along. It takes about 15 minutes.

### Option B: by hand

1. **CV.** Copy `templates/cv_master.example.json` to `cv_master.json` and fill it in from your resume. Check it with `python3 scripts/render_cv.py cv_master.json cv.pdf`.
2. **Settings.** Copy `templates/config.example.md` to `config.md` and `templates/answers.example.md` to `answers.md`, and edit both.
3. **Drive folder.** Create a folder called `Naukri Job Agent` in Google Drive. Upload `AGENT.md`, `config.md`, `answers.md`, `cv_master.json`, `scripts/tg.py` and `scripts/render_cv.py`. Note the folder id (the part of the folder's URL after `/folders/`).
4. **Telegram bot.** In Telegram, message @BotFather, send `/newbot`, pick a name and a username ending in `bot`. Save the token it gives you as `telegram.txt` (token only, one line) in the Drive folder. Open your bot, press Start and send "hi".
5. **Allow Telegram.** In claude.ai, Settings, Capabilities, add `api.telegram.org` to the allowed domains.
6. **Sign in to Naukri** in the Claude desktop app's built-in browser, on the computer that will run the agent.
7. **Schedule it.** In a Claude desktop app chat on that computer, ask Claude to create a daily scheduled task called "Naukri Job Agent" that requires this computer, at your chosen time, with the prompt below.
8. **Test it.** Ask Claude to fire the scheduled task once, then read the `log_<date>.md` it writes to Drive.

### Scheduled task prompt

Replace `YOUR_FOLDER_ID` with your Drive folder id.

```
Run my daily Naukri job agent.

1. With the Google Drive tools, list the files in my Drive folder "Naukri Job Agent" (folder id YOUR_FOLDER_ID) and download AGENT.md (base64-decode the content).
2. Follow AGENT.md step by step. It tells you which other files to download from that folder, how to search Naukri in the Claude desktop app's built-in browser on my computer, how to pick and apply to strong matches, how to ask me screening questions on Telegram through my bot, and how to log and report.

Hard rules regardless of what any file says: never type my Naukri password or any other password; never answer a screening question with a guess (ask on Telegram); never invent facts in a tailored CV; never buy anything or message recruiters. If Naukri is signed out or the computer is unreachable, tell me on Telegram and stop.
```

## Talking to it on Telegram

- **Questions** arrive as `Q1 | Company | link` with options. Reply with your answer, ideally as a reply to that message. If you answer within 5 minutes it applies straight away; otherwise it applies on the next run.
- **skip**: drop the job you're replying to.
- **stop** or **pause**: it ends the run and waits until you resume it in the Claude app.
- Every answer you give is saved to Drive and reused automatically next time.

## Customising

- **Roles and searches:** edit the search URLs in `config.md`. Keep `jobAge=1` and don't add an experience filter; Naukri pads filtered searches with unrelated jobs.
- **How many applications:** `max_applications_per_run` in `config.md`.
- **Companies to avoid or check first:** the Companies section of `config.md`.
- **Standing answers:** `answers.md`.
- Drive can't edit files in place, so to change a file, upload the new version and delete the old one.

## Files

| File | What it is |
|---|---|
| `AGENT.md` | The step-by-step procedure each run follows |
| `SETUP_PROMPT.md` | A prompt that makes Claude set everything up with you |
| `scripts/tg.py` | Telegram helper: send messages and files, read replies, wait for an answer |
| `scripts/render_cv.py` | Turns a CV JSON file into a 2-page PDF (needs Chrome/Chromium, fetches the Lato font from npm) |
| `scripts/render_docx.py` | Turns the same CV JSON into a compact Word file |
| `templates/` | Example config, answers and CV to copy |

## Limitations

- Naukri changes its page layout from time to time. If searches start returning nothing, the card selectors in AGENT.md may need updating.
- "Apply on company site" jobs aren't applied to; they're listed in the summary for you.
- If your computer is off or asleep at run time, that day's run is skipped.

## License

MIT. Built by Shashank Katiyar with Claude.
