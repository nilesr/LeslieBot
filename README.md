## LeslieBot is a GroupMe <-> Discord bridge

### Set Up

Install prerequisites: discord.py rewrite, `BTEdb`, `python-gobject`

Install and configure [mako-server](https://github.com/nilesr/mako-server) such that you can receive API posts

Install `index.pyhtml` to somewhere publicly accessible via mako-server.

Install `xyz.niles.LeslieBot.conf` to `/etc/dbus-1/system.d/xyz.niles.LeslieBot.conf` and reload or restart dbus.

Create a discord bot and GroupMe bot. For the GroupMe bot, set your callback url to the publicly accessible url of the `index.pyhtml` that you installed earlier.

Put your discord bot access token in the `client.run` call at the bottom of `leslie-bot.py`

Put your personal GroupMe access token, GroupMe bot ID, and the guild ID and channel ID to mirror in the variables at the top of `leslie-bot.py`

### Running

Just run `leslie-bot.py`. It will connect to discord, and also acquire the `xyz.niles.LeslieBot` bus name.

When a discord message is received, it will POST a message to the GroupMe bot API to send that message to the groupme channel. If the post contains an uploaded image, it will download the image and re-upload it to the GroupMe image service API.

When a GroupMe message is sent, GroupMe will send a POST request to the callback URL that you specified, the URL of `index.pyhtml`. `index.pyhtml` will then connect to dbus and invoke `RecvMessage` on `xyz.niles.LeslieBot`, passing it the json-encoded blob as an argument. The glib main loop, which is running on a background thread of `leslie-bot.py`, will then use the main thread's event loop to execute the global `RecvMessage` function in the async context that discord.py expects.

The json blob that GroupMe posts to us does not include a username. `RecvMessage` will attempt to pull usernames from a local cache kept in `leslie-bot-cache.json`, but if a user ID is not in the cache, it will attempt to get the group information (and member names) from the GroupMe API (NOT the bot API), using the personal access token at the top of the file, and then save it in the cache.

The personal access token is also used for uploading images to GroupMe
