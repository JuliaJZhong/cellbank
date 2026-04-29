\*made with Claude Pro. shoutout to my sister Roseann for that <3

#  welcome 2 my bank 🧬

A local web app for tracking clonal B cell lines, LN₂ tank inventory, and passage history. All data is stored as JSON files, version-controlled with git.

## Setup (one time)

```bash
# 1. Clone or copy this folder somewhere permanent
cd ~/celltracker   # or wherever you put it

# 2. Initialize git repo
git init
git add .
git commit -m "Initial CellTracker setup"

# Optionally push to GitHub:
# gh repo create celltracker --private
# git remote add origin git@github.com:YOURUSER/celltracker.git
# git push -u origin main
```

## Running

```bash
cd ~/celltracker
python3 server.py
# Then open http://localhost:8787 in your browser
```

That's it. No npm, no dependencies, no internet required.

## Workflow

1. **First time:** Go to the **Import** tab and add all your current vials. Each freeze-down event (same clone, same date) is one entry.
2. **Every freeze:** Use **Freeze Down** to log new vials going into the tank.
3. **Every thaw:** Use **Thaw** to log vials being removed.
4. **Every passage:** Use **Passage** to increment the passage counter for a clone line.
5. **After any session:** Click **↑ git commit** to save a snapshot. Or run `git commit -am "your message"` yourself.

## Data files

- `data/vials.json` — current LN₂ tank state
- `data/events.json` — append-only event log (never deleted from)

Passage number is **derived** from the event log, so it's always consistent. If you know the passage number from a notebook, you can set it manually when importing or logging a freeze.

## Git history = your version control

Every time you commit, git stores a complete snapshot of the tank state and event log. You can always:

```bash
git log --oneline           # see all snapshots
git show HEAD:data/vials.json   # see tank state at any commit
git diff HEAD~1 data/events.json  # what changed since last commit
```

## Bulk import via JSON

If you want to import many vials at once, prepare a JSON array like:

```json
[
  {"donor": "F5", "clone": "17", "freeze_date": "2025-04-23", "count": 3, "passage": 4, "notes": "from old lab member"},
  {"donor": "F2", "clone": "3",  "freeze_date": "2025-03-10", "count": 2}
]
```

And paste it into the **Import → Bulk JSON Import** section.

## Inferring passage number from notebooks

For each clone, look at your lab notebook entries and count how many times it was passaged after the first thaw. The earliest known passage number (from a freeze label or notebook entry) is your anchor — add passage events from there.
