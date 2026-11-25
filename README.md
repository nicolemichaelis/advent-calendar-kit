# A Telegram advent calendar for someone you love

Twenty-four doors, one photo and one letter behind each. From 1 December a small character (your pet, or a paper
envelope) sends a Telegram message at a random time every day. Tapping the message opens that day's door on a private
gallery wall, where the framed photos fill up one by one.

You edit one file, drop in 24 photos, run one command, and put it online for free.

## What you need

- A Telegram account for you, and one for the person you are surprising (the free app is fine)
- Free accounts on GitHub and Netlify
- A computer with Python 3.10 or newer
- For the animated cards: ffmpeg and a one-time browser download (step 2). Skip this and Telegram gets a plain
  text message with the button instead. Everything else still works.

Time needed: about an hour, most of it writing your messages.

## Step 1. Write your calendar

1. Open `config.json` in any text editor. Change the recipient, who it is from, the headline, and the character's name.
2. For each of the 24 days, write a `title`, a `letter` (what they read when the frame opens) and a `note` (the short
   line the character sends in Telegram). A blank line inside a letter is written `\n\n`.
3. Put your photos in the `photos` folder, named `01.jpg` to `24.jpg`. Landscape or portrait both work. Phone photos
   are fine, the build shrinks them.
4. Optional: put a photo of your pet in `character/pet.jpg` (the whole animal on a plain background works best). Without
   one you get a paper envelope with a wax seal. If the face stamp is cropped in the wrong place, set `"face"` in
   `config.json` to `"cx,cy,size"` as fractions, for example `"0.75,0.3,0.5"` for a head on the right.
5. Pick a look: `style.wall` is `forest`, `navy`, `burgundy` or `charcoal`. `style.cards` is `festive`, `nordic` or `warm`.

Three doors are bigger and fancier: 6 (St Nicholas Day), 21 (the longest night) and 24 (Christmas Eve). That layout is fixed,
so keep your best photos for those.

## Step 2. Build it

```
pip install -r requirements.txt
python3 -m playwright install chromium     # only for the animated cards
python3 tools/build.py
```

Ffmpeg must be installed too (`brew install ffmpeg` on a Mac). The build checks your content first and tells you
what is missing. `python3 tools/build.py --check` only checks. `--no-cards` skips the animations.

To look at the result before going online:

```
cd site
python3 -m http.server 8000
```

Open http://localhost:8000/?preview. The bar at the bottom lets you pretend it is any day in December.

## Step 3. Make the Telegram bot

Follow [docs/TELEGRAM_SETUP.md](docs/TELEGRAM_SETUP.md). It takes five minutes and ends with a bot token. Treat the
token like a password.

## Step 4. Put it online

1. On GitHub, create a new repository. Make it **Private**. Upload everything in this folder: the `site`, `netlify`,
   `tools` and `docs` folders and the loose files. Your bot token never goes into any file, only into Netlify (step 5).
2. On Netlify, choose "Add new project", "Import an existing project", pick GitHub and your repository. Leave the
   settings as they are: the included `netlify.toml` already says what to publish.
3. Choose a hard-to-guess project name, for example `advent-7k2q9x`. The address is the only thing keeping strangers out.
4. Deploy.

## Step 5. Connect Telegram

In Netlify go to Project configuration, Environment variables, and add two variables:

- `TELEGRAM_TOKEN`: the token from BotFather
- `SECRET`: a long phrase only you know (four unrelated words and a number). It protects your control page and
  decides the random delivery times. Keep a copy.

Then deploy again (Deploys, Trigger deploy). Next:

1. The recipient opens your bot link and taps **Start**.
2. You open `https://YOUR-SITE.netlify.app/api/setup?secret=YOUR_SECRET`. It shows their chat number.
3. Add that number as a third variable, `CHAT_ID`, and deploy once more.
4. Open the control page again and press "Send welcome message". They get the first card.

The control page also lists the random time chosen for every day (only you can see it) and has a "send now" link
per door for testing. A tested door only opens on its real day.

## How delivery works

- Nothing is sent before 1 December, and nothing after 24 December.
- Every day gets its own random 15-minute slot inside the window in `config.json` (default 08:00 to 20:00) in your
  `timezone`. Change those two settings in `config.json` and run the build again.
- A door only appears on the wall once it has been delivered, and only opens from the Telegram button. Tapping a
  frame on the wall without the message does nothing.
- If Netlify is slow, the message goes out at the next 15-minute check. It never goes out twice.

## Changing things later

Edit `config.json`, run `python3 tools/build.py`, upload the changed files to GitHub. Netlify rebuilds by itself.

## Troubleshooting

- **Nothing in Telegram:** check both variables exist and that you deployed after adding them. Open the control page
  and look for an error message.
- **"Nobody has pressed Start yet":** the recipient has to open the bot and press Start first. Reload the page afterwards.
- **A door says it is not ready:** the link only works on or after the delivery time of that day.
- **Cards are skipped:** install ffmpeg and run `python3 -m playwright install chromium`, then build again.
- **Pet cutout looks wrong:** use a photo with the whole animal against a plain background, or use the paper envelope.

## Using it with Claude

`skill/advent-calendar-builder/SKILL.md` is a Claude skill that walks you through all of the above: it interviews you,
drafts the 24 letters in your voice, fills in `config.json`, and guides the Telegram and Netlify steps without ever
handling your token. In Claude, add it under Settings, Capabilities, Skills (upload the `advent-calendar-builder`
folder), then ask Claude to help you build an advent calendar.

## Know before you share it

- The site address is private only because nobody knows it. Anyone who has the address and guesses the file names
  can see photos and letters in advance. Do not post the link anywhere. For strong protection, use Netlify password
  protection (a paid feature).
- Photos are published on Netlify, so only use pictures you are happy to host there.
- This was built for 24 December gift-giving in the Northern Hemisphere calendar. Doors are fixed to 1 to 24 December.
