# Telegram setup

You need a bot, a token, and the recipient's chat number. No coding.

## 1. Create the bot

1. In Telegram search for **@BotFather** (the one with the blue tick) and open it.
2. Send `/newbot`.
3. Give it a display name, for example the name of your character. People see this name.
4. Give it a username that ends in `bot`, for example `biscuitadvent_bot`.
5. BotFather replies with a long token that looks like numbers, a colon, then letters. **That is your token.**
   Copy it somewhere safe. Never paste it into a file, a chat with other people, or a public page. If it leaks,
   send `/revoke` to BotFather to get a new one.

Optional: send `/setuserpic` to BotFather and choose your character's face as the profile picture
(`site/character/face.webp` converted to a JPG works well).

## 2. Give the token to Netlify

Netlify, your project, Project configuration, Environment variables, Add a variable:

- Key `TELEGRAM_TOKEN`, value: your token.
- Key `SECRET`, value: a long phrase only you know.

Leave both on "Same value for all deploy contexts". Then trigger a new deploy.

## 3. Let the bot find the recipient

A bot cannot message anyone first, so the recipient has to start it:

1. Send them the link `https://t.me/YOUR_BOT_USERNAME`.
2. They open it and tap **Start**. (If you are doing this on their phone, do it yourself.)
3. Open `https://YOUR-SITE.netlify.app/api/setup?secret=YOUR_SECRET` in a browser within 24 hours.
4. Copy the number next to their name.
5. Add it in Netlify as `CHAT_ID` and deploy again.

## 4. Send the welcome message

Open the setup page again and press "Send welcome message". If it arrives, everything works. You can also press
"send now" next to any day to test the format. That door will not open until its real day.

## Common problems

- **The setup page says nobody pressed Start:** they must press Start, not only open the bot. Try again, then reload.
- **404 on the setup page:** the `SECRET` in the address must match the one in Netlify exactly.
- **"Welcome failed" with a message about chat not found:** the `CHAT_ID` is wrong or Start was not pressed.
- **A message about a failed video:** the site has not finished deploying, or the cards were skipped in the build.
  Run `python3 tools/build.py`, upload the changes, and try again.
