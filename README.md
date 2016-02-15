# PinchyBot-3 [![Build Status](https://travis-ci.org/ZetaRift/PinchyBot-3.svg?branch=master)](https://travis-ci.org/ZetaRift/PinchyBot-3)
PinchyBot for use on chatango group chat rooms, ported to Python 3

Uses a modified version of the chatango python library https://github.com/Nullspeaker/ch.py

## License
You are free to use and change the bot's code however you want, please note that you must provide credit for the original creator of the bot.

The details for the 'pinchybot' account on chatango will not be shared whatsoever, you will have to have the bot use another account.

## Depends
You can use 'pip install' to install the required python libraries.

lxml
(lxml needs `libxml2-dev`, `libxslt-dev`, and `python-dev` for a post-installation build if using pip, use your distro's package manager to install the required packages, otherwise installing `python3-lxml` with the distro's package manager will do)

requests (For fetching URL contents and metadata)

pytz (For grabbing timezone)

goslate (For the goslate command)

PIL (or `Pillow`, for fetching info on image URLs)

dataset (Used for the seen and wz module for database storage)

## Config file
PinchyBot uses a JSON file as a config file, look at settings-example.json for an example

You must create settings.json for the bot to run.

### Required elements

"Name" String: Username for the bot to use

"Pass" String: Password for the username

"Rooms" String array: A list of rooms for the bot to join, it can be as many as you want

"ExplicitRooms" String array: A list of rooms where the bot can send explicit content, applies for the gimg and the pony command.

"Admins" String array: List of users for the bot to consider as "botadmins", gives access to some commands such as 'eval'

"FontColor" String: 3 digit hexadecimal color code for the bot's text color, #000 is black, #FFF is white

"NameColor" String: Same as above for the username color that shows up in group chat rooms.

"FontSize" Integer: Font size for the bot's text

"Greet" Bool: For the bot to greet a joining user, true will greet users, false will omit greets

"WZ-APIKey" String: Required by the wz module.

"YT-APIKey" String: Required by the yt module.

"IgnoredURLs" String list: Required, but can be empty if you don't want the bot ignoring any URLs it sees

### Optional elements

"CommandPrefix" String: This should be a single character prefix for the bot's commands. If the element is not present, the bot will use its default prefix

"derpi_APIKey" String: This is optional, but needed if you want to apply your own filtering when the bot searches for images

## Modules
The modules are maintained as well

To use the 'wz' command, an API key is required (Look at mod/wz.py)

For youtube URL parsing, that requires an API key as well.
