# Learn: lessons

Rules learned from corrected runs. Read before every run. They all apply. Add new ones under "Your lessons" at the end, one line each with the date.

## Sources and data

- YouTube often blocks the transcript script (bot check). If it fails, read "Show transcript" in a new Chrome tab (when Claude in Chrome is set up) or ask the learner to paste it. Never use cookies.
- Every data project says where the data comes from (site, exact URLs, how it was loaded) in quest 1 and a README next to the data. The learner must be able to get it themselves.
- Teach collecting and loading data too (download, CSV, CREATE TABLE, INSERT, clean with CREATE TABLE AS), not only querying.
- Several links on one subject = one topic. Later links in the same category merge in (Mode 5) without touching their progress. Always add your own research from high-trust sources on top of their links.
- The learner can add files to Request training (a saved video, PDF, screenshots). Files sit in the page's private asset store (mp4/webm/PDF/images/text, 20 MB each). Videos get a local transcript + frames via `video_notes.py`; a short clip seeds the topic, good free sources fill the gaps.
- Phone videos are often over 20 MB. The page splits files over 20 MB (and .mov) into base64 text parts, up to 300 MB; join with `join_parts.py`, then delete the parts once built.

## The page

- No placeholder skills on the page. A skill card appears only when a topic that uses it starts. Role gaps are offered on the Quest Board, never pre-seeded as skills.
- The page does everything. No pasting into chat. Hands-on skills get an in-page sandbox with auto-checked answers.
- Trophies are unique RPG-style pixel art with a name and a story line, shown locked (silhouette + progress) until earned. Each new topic gets its own trophies.
- The guides (The Mentor, The Professor) offer quests on the page from `role-gaps.json`, up to 5 live. Accept queues it; every /learn builds accepted offers first, then restocks the board. Facts in pitches come only from the gaps file, never from company facts.
- The learner can request training on the page (Request training box: a YouTube link, course or skill). Every /learn builds queued requests first.
- Check every page change at phone width (390px) before publishing. Grid columns use minmax(0, 1fr) and long text wraps, so nothing pushes the page sideways.
- Several quests run at once: one main quest plus side quests in the Quest Log. New topics arrive as Quest Board offers they accept, each with its own guide NPC who then talks them through the training. Never switch their main quest for them.
- Accepting anything on the Quest Board needs an "Are you sure?" step first, and every accept can be undone until they start (Undo for role-gap offers, Give it back for topics). Role-gap offers only become playable after /learn builds them: say so at the point of accepting.
- Accepted offers show in the Quest Log straight away as "Being prepared" (with Undo), not only under the board.
- Review card flip state is tied to one card id, never a true/false flag, so the next card can never open answer-side up.
- "Again" on a card puts a Refresher row in the Quest Log: the card plus the matching step lesson, until they press "Got it now". Cards forgotten 2+ times show as struggles in evidence_report.
- Every lesson step has an "Ask Claude" box on the page for follow-ups. It doesn't give mission answers unless they ask.
- Before republishing after a change to the page script, render every step of every live topic (e.g. in Node: pull the topics, call questView per step). A do-step with no hints once crashed the quest screen, so whole topics wouldn't open.

## Teaching

- Write for a complete beginner: guided steps, every term defined, starter code, 2 hints, show answer after 2 tries.
- Teaching method adapted from mattpocock/skills `teach`: mission per topic, high-trust sources per quest, learner records from page evidence, balanced quizzes (checked), mixed practice before the boss, Field Guide, placement, communities shown.
- Re-running a correct answer must never look like a failure. In keepDb quests, a CREATE that already exists is checked with the step's verify and counts as correct; raw SQL errors always get a plain-English fix.
- Steps that build on earlier steps must survive a reload: the page replays the SQL they passed with (q.solved) and restores their CSV (or the sample) before checking. Starters show the full pattern (placeholders in place), and checks reject unchanged placeholders.
- Every value in an example or starter must be labelled: say which column each number is (e.g. "(name, category, qty)") and put a comment line in the starter. Never leave a bare number unexplained.
- Never require outside knowledge to clear a step. Give the data, or say plainly that any value works (e.g. "any number works for qty").
- Don't default every project to the same interest. Pick a project the learner would actually use, often from their own field or their `interests` in setup. Ask once when the choice shapes the whole topic.
- Teach the skill, not the project. The project is just what they practise on. One new keyword or concept per session, then every later session reuses all earlier ones so the last sessions use the whole toolkit.
- Never hand over the code. No half-written starters, no full formulas in teach text. Each concept: what it does + why, look at the data, tiny example on different data, then they write it from a blank editor. 3 tries per new concept (guided, own, twist), hints on all 3 (keyword, then shape with blanks, then answer), then an explain-it-back question.
- Never assume they can see the data. First step of anything new: they look at the table themselves (SELECT * LIMIT 5) with a plain-English meaning for every column code.
- Every concept in every topic gets a real-world work example from the learner's own field (their job from setup) and the logic of why it's used. Made-up numbers, never company data.
- Benchmark is a good full online course: teach it, then by the end they do it alone and apply it to their own ideas. Not too easy. Hints are a safety net, not the path.
- When a skill is best practised in a real desktop tool (PostgreSQL + pgAdmin, Power BI Desktop), the page is the guide and checks by asking for the value their work returns (`input` steps).
- Lessons were too thin and questions too easy (recall with silly wrong options). Every step has a Go deeper layer from the source, and most questions set a scene with believable wrong options. `build_pack.py` enforces both.

## Building and checking

- No plan approval gate. A request goes straight to a ready-to-play topic; the learner changes it after if they want. Every pack must pass build_pack.py first.
- Every project topic ends with a "ship it" quest: download a repo-ready zip from the page, run it in a real desktop tool, publish to GitHub (taught from zero). The learner creates accounts and pushes themselves. Data stays out of the repo; a fetch script and credit go in.
- Honesty: the project is the learner's work. The Skill Tree was built by Claude, so never present it as their own build.
- A quest can feed its own skill (`stat` on the quest). Git & GitHub is a separate skill, not part of SQL. Tools learned along the way get their own skill card.
- Quality audit: every Rank Trial problem must be taught AND practised in a quest before it (except placement-only levels on role topics: levels 1-3 trials the topic doesn't teach exist only for placement, so they're exempt from "taught first"); trial answers never appear in lesson text or worked examples; `placement` maps each level to the quests that teach that trial; quest minutes are honest for a beginner (most real quests take 25-45 min, bosses 60-90+); every concept gets 2+ hands-on reps; quests never tell them to create something that already exists in their own setup (check first, "open and improve" on replays); trials use the same tool and table they practised on.
- No quest text, answer or card may name a trial's exact scenario or its answer. Check by reading the pack against the trials file before loading. Boss rounds never repeat a practice step's answer.

## Mastery

- Skill level = proven mastery on a fixed 1-7 ladder with real benchmarks (Master = top-level knowledge), raised only by unaided, timed Rank Trials. Quests and XP are practice only. Be honest about each topic's ceiling.
- Rank Trials must be hard to pass by luck: 6 problems from a pool of 9+, 5 to pass, mostly hands-on in the real tool (type the result), 3-day lock after a fail. `build_pack.py --trials` enforces it.
- Ladder levels are knowledge-based with proof. Level 3+ trials are at least half unseen data or scenarios. Levels 5-7 need outside evidence. The page can't prove 5-7 on its own.
- At the top level the page can test, the skill card offers a level-up quest ("Become the lead engineer"). /learn builds it with research first (Mode 6).
- Suggest a Rank Trial when they've cleared the quests its placement covers and have no open struggles in them (the page shows a Quest Log row; /learn says it in one line).
- Role topics ship with Rank Trials for levels 1-3 (1-4 when they self-rate at 4) so the placement test can run. The self-rating only sets where placement starts; mastery comes from the trials.

## Your lessons

<!-- - DD.MM.YY: <rule> -->
