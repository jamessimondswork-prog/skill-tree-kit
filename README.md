# Skill Tree kit

A learning game you run with Claude Code. You ask to learn something, and Claude builds it into short quests on your own private Skill Tree page: guided steps, quizzes, review cards, a boss project, trophies, and Rank Trials that test real skill.

## What you need

- Windows
- Claude Code, signed in
- A claude.ai account
- Python 3

## Install

1. On this page, click **Code**, then **Download ZIP**.
2. Open the zip. Inside the `skill-tree-kit-main` folder are two folders: `.claude` and `skill-tree`.
3. Copy both into the folder you already use with Claude Code for work. They should sit next to your own files. Nothing of yours gets changed.
4. Open Claude Code in that folder and type `/learn`.

Setup asks you a few questions, builds your first topic and gives you a link to your page. It can take up to an hour.

The full guide is in [skill-tree/README.md](skill-tree/README.md).

## Updates

The current version is in [skill-tree/VERSION](skill-tree/VERSION). What changed in each version is in [skill-tree/UPDATE-NOTES.md](skill-tree/UPDATE-NOTES.md).

From 1.2.0, type `/learn update` in Claude Code. Claude checks this repo for a newer version, shows you what changed and installs it only if you say yes. Your page keeps its link and your progress.

On 1.1.0 or older, download the zip again, copy the two folders over your old ones (choose Replace), then type `/learn update`.

## Licence

MIT. See [LICENSE](LICENSE).
