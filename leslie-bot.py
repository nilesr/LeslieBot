#!/usr/bin/env python3
print('------')
print("Logging in now...")
import discord, asyncio, re
from gi.repository import GLib
from pydbus.generic import signal
import pydbus, threading, time, requests, json, BTEdb, hashlib, io, string
from PIL import Image

db = BTEdb.Database("leslie-bot-cache.json")
if not db.TableExists("main"): db.CreateTable("main")

groupme_token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
groupme_bot_id = "XXXXXXXXXXXXXXXXXXXXXXXXXX"

guild_id = 339858259617906710 # final destination
channel_id = 542156512550977545 # #vt-bois

#guild_id = 498691390683742208 # pixel
#channel_id = 498691390683742210 # #general

client = discord.Client()

@client.event
async def on_ready():
  print('Logged in as')
  print(client.user.name)
  print(client.user.id)
  print('------')

def upload(url):
  print("Downloading from: " + url)
  data = requests.get(url)
  print("Response: " + str(data))
  r = requests.post("https://image.groupme.com/pictures", files = {'file': data.content}, headers = {"X-Access-Token": groupme_token})
  print(r)
  j = json.loads(r.text)
  return j["payload"]["url"] + ".large"

def apply_format(text, alphabet):
  base = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
  result = ""
  for c in text:
    idx = base.find(c)
    if idx >= 0:
      result += alphabet[idx]
    else:
      result += c
  return result
def bold_italic(k): return apply_format(k, "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕")
def bold(k): return apply_format(k, "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭")
def italic(k): return apply_format(k, "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡")
def underline(k): return apply_format(k, list(map(lambda c: c + chr(0x332), string.ascii_letters)))
def strikethrough(k): return apply_format(k, list(map(lambda c: c + chr(0x336), string.ascii_letters)))

def format(text):
  split = re.split('(~~[^~]*~~|___[^_]*___|__[^_]*__|_[^_]*_|\\*\\*\\*[^\\*]*\\*\\*\\*|\\*\\*[^\\*]*\\*\\*|\\*[^\\*]*\\*)', text)
  result = ""
  for k in split:
    if k.startswith("***") and k.endswith("***"):
      result += bold_italic(k[3:-3])
    elif k.startswith("**") and k.endswith("**"):
      result += bold(k[2:-2])
    elif k.startswith("*") and k.endswith("*"):
      result += italic(k[1:-1])
    elif k.startswith("___") and k.endswith("___"):
      result += underline(italic(k[3:-3]))
    elif k.startswith("__") and k.endswith("__"):
      result += underline(k[2:-2])
    elif k.startswith("_") and k.endswith("_"):
      result += italic(k[1:-1])
    elif k.startswith("~~") and k.endswith("~~"):
      result += strikethrough(k[2:-2])
    else:
      result += k
  return result

# key, user_id, emoji_id
async def get_emoji(key, user_id, display_name):
  results = db.Select("main", key = key);
  if len(results) == 1:
    return results[0]["emoji_id"]
  guild = client.get_guild(guild_id)
  old_emoji = db.Select("main", user_id = user_id)
  if len(old_emoji) > 0:
    e = client.get_emoji(int(old_emoji[0]["emoji_id"].split(":")[2].replace(">", "")))
    if e:
      print("Deleting emoji " + str(e))
      await e.delete(reason = "User " + user_id + ", " + display_name + " has new profile picture")
    db.Delete("main", user_id = user_id)
  name = hashlib.md5(key.encode("utf-8")).hexdigest()[:6]
  print("Creating emoji " + name + " for user "+user_id+", "+display_name+" with image from " + key)
  data = requests.get(key)
  image = Image.open(io.BytesIO(data.content))
  image = image.resize((32, 32), Image.ANTIALIAS)
  resized = io.BytesIO()
  image.save(resized, format='PNG')
  print(len(resized.getvalue()));
  emoji = await guild.create_custom_emoji(name = name , image = resized.getvalue(), reason = "Leslie-Bot: New avatar for user ID " + user_id + ", name: " + display_name)
  emoji_id = "<:{}:{}>".format(name, emoji.id);
  db.Insert("main", key = key, user_id = user_id, emoji_id = emoji_id);
  return emoji_id

@client.event
async def on_message(message):
  if message.author.bot:
    print("DISCARDING BOT MESSAGE FROM ", message.author)
    return
  if not message.channel or message.channel.id != channel_id:
    print("Discarding message from " + str(message.channel));
    return
  while True:
    m = re.search("<@!?([0-9]*)>", message.content)
    if not m: break
    user = message.channel.guild.get_member(int(m.group(1)))
    message.content = message.content.replace(m.group(0), "@" + user.display_name)
  while True:
    m = re.search("<:([^:]*):\d+>", message.content)
    if not m: break
    message.content = message.content.replace(m.group(0), "(" + m.group(1) + " emoji)")
  data = {
      "text": message.author.display_name + ": " + format(message.content),
      "bot_id": groupme_bot_id,
      "attachments": [
        #{"type": "image", "url": "https://i.groupme.com/512x512.jpeg.cef5c0012cb846819203fb81d9ccb4ed"}
        ]
      }
  for em in message.attachments:
    data["attachments"].append({"type": "image", "url": upload(em.url)})
  data["text"] = data["text"].replace("%", chr(0x200b) + "0⁄0" + chr(0x200b));
  requests.post("https://api.groupme.com/v3/bots/post", json.dumps(data))


async def RecvMessage(string):
  channel = client.get_channel(channel_id)
  s = json.loads(string)
  if s["sender_type"] == "bot":
    print("DISCARDING RecvMessage SELF MESSAGE")
    return
  nickname = s["name"]
  e = None
  for attachment in s["attachments"]:
    if attachment["type"] == "image":
      e = discord.Embed()
      e.set_image(url = attachment["url"])
  emoji = await get_emoji(s["avatar_url"], s["sender_id"], s["name"]) if s["sender_id"] != "system" else ""
  await channel.send(emoji + "**" + nickname + "**: " + s["text"], embed = e);

client_loop = asyncio.get_event_loop()

class Listener():
  """
  <node>
    <interface name='xyz.niles.LeslieBot'>
      <method name='RecvMessage'>
        <arg type='s' name='a' direction='in'/>
      </method>
    </interface>
  </node>
  """
  def RecvMessage(self, string):
    print("Recieved message: " + string)
    coro = RecvMessage(string)
    future = asyncio.run_coroutine_threadsafe(coro, client_loop)
    future.result()


def dbus_server():
  loop = GLib.MainLoop()
  bus = pydbus.SystemBus();
  bus.publish("xyz.niles.LeslieBot", Listener())
  loop.run()

t = threading.Thread(target = dbus_server)
t.start();

# assuming that this line calls asyncio run_forever()
client.run("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
