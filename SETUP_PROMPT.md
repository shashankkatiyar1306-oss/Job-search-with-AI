# Setup prompt

Open a new chat in the **Claude desktop app** on the computer that will run the agent, attach your resume (PDF or Word), and paste everything in the box below. Claude will do the setup with you step by step.

```
Set up the Naukri Job Agent for me from this GitHub repo: https://github.com/shashankkatiyar1306-oss/Job-search-with-AI

My resume is attached. Please do the following, one step at a time, and ask me whenever you need something:

1. Clone the repo into your workspace and read README.md and AGENT.md.
2. Read my resume and turn it into cv_master.json, using templates/cv_master.example.json as the exact shape. Copy facts from my resume only: never add a skill, tool, number, title, employer or date that isn't in it. Render it with scripts/render_cv.py and show me the PDF so I can check it.
3. Ask me the questions needed to fill templates/config.example.md (target roles, experience range, locations, notice period, relocation, max applications per run, companies to avoid) and templates/answers.example.md. Build the Naukri search URLs for my target roles in the same format as the examples (jobAge=1, no experience filter).
4. Using the Google Drive connector, create a folder called "Naukri Job Agent" in my Drive and upload: AGENT.md, config.md, answers.md, cv_master.json, scripts/tg.py, scripts/render_cv.py. Upload them by file reference, not by retyping, and check each file's size matches.
5. Walk me through creating a Telegram bot with @BotFather. I will save the bot token myself as a file called telegram.txt in that Drive folder (just the token on one line). Remind me to press Start on my bot and send it "hi", and to add api.telegram.org to my allowed domains (claude.ai, Settings, Capabilities). Then test that you can reach Telegram and send me a test message.
6. Open https://www.naukri.com in the Claude desktop app's built-in browser and check that I'm signed in. If not, ask me to sign in myself. Never type my password.
7. Create a daily scheduled task called "Naukri Job Agent" that requires this computer, at the time I choose, using the scheduled task prompt in README.md with my Drive folder id filled in.
8. Fire one test run of the scheduled task capped at 1 application, then read the log it writes to Drive and tell me what worked.
```

Notes
- Claude may ask you to approve connector calls, folder access or site access along the way. That's expected.
- Your bot token is a password for your bot. Don't paste it into a public place. If it ever leaks, send `/revoke` to @BotFather and put the new token in telegram.txt.
