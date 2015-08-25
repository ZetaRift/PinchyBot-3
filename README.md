# PinchyBot-3
PinchyBot for use on chatango group chat rooms, ported to Python 3

# License
You are free to use and change the bot's code however you want, please note that you must provide credit for the original creator of the bot.

The details for the 'pinchybot' account on chatango will not be shared whatsoever, you will have to have the bot use another account.

# Depends
You can use 'pip install' to install the required python libraries.

lxml

requests

pytz (For grabbing timezone)

goslate (For the goslate command)

PIL (or 'pillow', for fetching info on image URLs)

# Config file
PinchyBot uses a JSON file as a config file, look at settings-example.json for an example

You must create settings.json for the bot to run, the required JSON elements are listed here:

"Name" String: Username for the bot to use

"Pass" String: Password for the username

"Rooms" String array: A list of rooms for the bot to join, it can be as many as you want

"Admins" String array: List of users for the bot to consider as "botadmins", gives access to some commands such as 'eval'

"FontColor" String: 3 digit hexadecimal color code for the bot's text color, #000 is black, #FFF is white

"NameColor" String: Same as above for the username color that shows up in group chat rooms.

"FontSize" Integer: Font size for the bot's text

"Greet" Bool: For the bot to greet a joining user, true will greet users, false will omit greets
