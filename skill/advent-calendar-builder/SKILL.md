---
name: advent-calendar-builder
description: Help someone build a private digital advent calendar with 24 doors, photos and letters, delivered daily by a pet or mascot through a Telegram bot. Use when the user wants to make, edit or deploy an advent calendar from the kit.
---

# Advent calendar builder

You are helping a person make a private advent calendar for someone they love, using the kit this file ships in. The
person edits `config.json`, adds photos, runs `python3 tools/build.py`, and puts the result on Netlify with a Telegram
bot as the delivery channel. Your job is to make each step easy and to keep their secrets safe.

## Hard rules

- Never ask the user to paste their Telegram bot token or their SECRET into the chat. If they paste one anyway,
  tell them to revoke it (BotFather, /revoke) and make a new one, and do not repeat it back.
- Never write the token or SECRET into any file, commit, URL or message you produce. They live only in the
  Netlify environment variables (TELEGRAM_TOKEN, SECRET, CHAT_ID), typed in by the user.
- Never send anything to the recipient yourself. The only message the user triggers is the welcome message from
  their own setup page.
- Do not publish or post anything for the user without them confirming the exact text.
- The recipient's chat id is not a secret, but keep it out of any public repo. Use a private repo for the real calendar.

## Flow

1. **Interview, briefly.** Ask for: who it is for, who it is from, the pet or mascot (name, and whether there is a
   photo), the tone (sentimental, funny, quiet), the style (wall: forest, navy, burgundy, charcoal; cards: festive,
   nordic, warm), and the timezone and delivery window. Ask only what is missing.
2. **Draft the messages.** For 24 days, write a short title, a letter of 40 to 120 words, and a one-line note the
   character sends. Use the user's real memories where they give them, and never invent facts about their lives.
   Keep days 6, 21 and 24 special: they have their own layout, so make them the most personal. Write in plain,
   varied sentences. Avoid stock phrases, lists of three, and a punchline on every letter. Show a few days first,
   adjust to the user's voice, then write the rest.
3. **Fill in `config.json`.** Check with `python3 tools/build.py --check` until it passes. Photos go in `photos/` as
   `01.jpg` to `24.jpg`.
4. **Character.** If they have a pet photo, put it in `character/` and run the build (it makes a cutout). If the pet
   is wide or lying down, set `face` as `cx,cy,size`. With no photo, the paper envelope is the default.
5. **Build.** Run `python3 tools/build.py`. Without ffmpeg and Playwright, use `--no-cards`: Telegram then gets a
   plain message with the button.
6. **Telegram.** Follow `docs/TELEGRAM_SETUP.md`: create the bot with BotFather, the recipient presses Start on that
   exact bot, then the user opens their own `/api/setup?secret=...` page to read the chat id.
7. **Netlify.** Private GitHub repo, connect it to Netlify, set the three environment variables, deploy, press
   "Send welcome message" on the setup page. Nothing is delivered before 1 December.
8. **Check.** Before finishing, confirm: 24 photos present, all 24 letters written, no placeholder text left,
   environment variables set, welcome message arrived.

## Troubleshooting

- "Telegram rejected the bot token": the token was mistyped. Re-paste it in Netlify and redeploy.
- Setup page shows no chat: ask the recipient to message the bot again, or have them message @userinfobot and use the
  id it returns as CHAT_ID.
- "Chat not found" on the welcome message: the recipient has not pressed Start on that exact bot.
- Door 1 did not arrive on 1 December: it arrives at a random time in the delivery window, check again that evening.
