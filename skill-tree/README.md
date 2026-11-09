# Skill Tree

A private page that turns "I want to learn this" into a game you can play.

You tell Claude what you want to learn. It builds you a topic with short guided steps, quizzes, review cards, a practice area for code, a boss project and trophies. Your progress is saved on the page. Only you can see it.

## What you need

- Windows 10 or 11. **Mac isn't supported.**
- Claude Code, signed in with a claude.ai account.
- A claude.ai account that can make Artifacts (the private pages). Your admin may need to turn on a few page features. Setup checks this and tells you.
- Python 3. Get it from https://www.python.org/downloads/ . On the first screen of the installer, tick "Add python.exe to PATH".

## Install

The Skill Tree goes inside the folder you already use with Claude Code for work. That way it can see what your role needs.

1. **Check first:** if that folder already has a `.claude\skills\learn` folder, move yours out of `.claude\skills` before you unzip (for example to a `learn-old` folder next to `.claude`). Renaming it inside `.claude\skills` isn't enough: Claude Code would still load it as a second `learn` skill.
2. Unzip the file into the folder you already use with Claude Code for work, so `.claude` and `skill-tree` land next to your files. A path with spaces is fine. No work folder yet? Make an empty folder and use that. In Extract All, delete the last folder name so it extracts straight into your work folder. You should see `.claude` and `skill-tree` next to your own files.
3. Open Claude Code in that folder. On Windows: right-click the folder, pick Open in Terminal, then type `claude` and press Enter. Or use the desktop app's folder picker.
4. Type `/learn` and press Enter.

The kit never changes your own files. It only adds `.claude\skills\learn` and `skill-tree`, and only ever writes inside those two folders. If your folder uses git, setup adds one line, `skill-tree/`, to your `.gitignore` so your Skill Tree files stay out of git, and tells you when it does.

That's it. Claude does the rest.

Claude will ask your permission before it runs commands or saves to your page. That's expected. Say yes to carry on.

## If someone built your Skill Tree for you

Someone may have answered the setup questions for you and built your first topic already. Then:

1. Unzip what they sent into the folder you already use with Claude Code for work (the same rules as Install above). In Extract All, delete the last folder name so it extracts straight into your work folder. You should see `.claude` and `skill-tree` next to your own files.
2. Open Claude Code there and type `/learn`.
3. It takes a few minutes: Claude checks your setup, makes your private page and loads your quests. It asks once if it may read your work folder to tailor your quests. Say no if you'd rather not.
4. Open the link and make your character. Your first quest is ready.

### Building a Skill Tree for someone else

You can answer setup for someone and build their first topic on your own computer, then send it to them. Unzip the release zip into a new empty folder outside any project that has its own /learn (e.g. C:\skill-tree-builds\<learner>) and open Claude Code there. Type `/learn prebuild` and answer for them, not for yourself. At the end Claude gives you a command that zips their kit to send. Nothing is published from your side.

## What setup asks

Setup takes a while. Plan for up to an hour.

First it checks your Python and asks before installing three free add-ons (for YouTube transcripts and video notes).

Then Claude asks 10 short questions, one at a time:

- what to call you
- what your job is
- whether it's OK to read this work folder, on your computer only (say no and it skips this)
- what takes up most of your week
- what you wish you were better at
- where you want to be in a year (optional)
- what you like outside work (this picks the data for your practice projects)
- how much time you have each week
- how you like to learn: videos, reading or doing
- any training links (videos, courses, articles) you want your first session built from, or none

Then it:

- reads your work folder, if you said OK, and tells you what skills your role seems to need. It skips its own `skill-tree` and `.claude\skills\learn` folders.
- asks a couple of quick questions about each skill, so it knows where to start you
- builds your first topic and its Rank Trials, from your links if you gave some, or else from the skill your role needs most
- makes your private page and gives you the link

The first time you open the page, you make your character. If your first topic is a skill your role needs, it starts with a short placement test. Take it or skip it.

## Privacy

- Your work folder is read on your computer only, and only if you say OK. Nothing from it is copied anywhere else.
- Skills and topics are written in general terms. No company names, numbers or client names.
- Web searches never include anything from your work.
- Practice projects use public or made-up data.
- Your page is private. Don't share the link.

## What you can do

- **Quests:** short guided lessons with a quiz at each step.
- **Practice area:** try code on a small dataset right on the page.
- **Review cards:** bring back things you're about to forget.
- **Boss project:** build something real at the end of a topic.
- **Rank Trials:** timed tests on new problems. They show what you really know.
- **Placement test:** start a topic at your own level.
- **Quest Board:** skills your role needs. Accept one and Claude builds it on the next `/learn`.
- **Request training:** add a link, a skill or a file on the page. Claude turns it into a topic.
- **Trophies and levels:** you earn them as you go.
- **Gear and Master crowns:** reach Champion to unlock gear for your character, and master a skill to earn its own crown.

Type `/learn` in Claude Code any time to build what you've asked for, pick up where you left off, or add a topic. Give it a link or a skill name, like `/learn SQL basics`.

## If something goes wrong

- **"Missing capability" message:** the page needs a few Artifact features (saving progress, uploads, questions, downloads). Setup names the one that's missing. Ask your claude.ai admin to turn it on, then run `/learn` again. Nothing is lost.
- **pip install fails:** carry on. The Skill Tree works without the add-ons. Without the YouTube add-on, paste the transcript for a video. Without the video add-on, uploaded videos can't be transcribed, but PDFs, images, text and links still work. To try again, run `python -m pip install youtube_transcript_api faster-whisper av` in a terminal.
- **Python not found:** install it from the link above, tick "Add python.exe to PATH", close and reopen Claude Code, then run `/learn` again.
- **Setup stopped half way:** run `/learn` again. It picks up where it stopped and never makes a second page.
- **Mac or Linux:** not supported.

## Getting updates

- An update comes as two files: `update-N.txt` (what changed) and `update-N.zip` (only the changed files).
- Unzip `update-N.zip` into the same work folder and say yes to replacing files. It only holds Skill Tree files, so your own files aren't touched. In Extract All, delete the last folder name so it extracts straight into your work folder. You should see `.claude` and `skill-tree` next to your own files.
- Open Claude Code in the folder and type `/learn update`. Claude updates your page and tells you what changed.
- Your progress stays as it is.

## Licence

MIT. See `LICENSE`.
