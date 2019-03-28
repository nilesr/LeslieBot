#!/usr/bin/env python2
print('------')
print("Logging in now...")
import discord, asyncio
from gi.repository import GLib
from pydbus.generic import signal
import pydbus, threading, time, requests, BTEdb, json

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

@client.event
async def on_message(message):
  start = time.time()
  #print("Author: ", message.author, type(message.author))
  #print("Channel: ", message.channel, type(message.channel))
  if message.author.bot:
    print("DISCARDING BOT MESSAGE FROM ", message.author)
    return
  if not message.channel or message.channel.id != channel_id:
    print("Discarding message from " + str(message.channel));
  data = {
      "text": message.author.display_name + ": " + message.content,
      "bot_id": groupme_bot_id,
      "attachments": [
        #{"type": "image", "url": "https://i.groupme.com/512x512.jpeg.cef5c0012cb846819203fb81d9ccb4ed"}
        ]
      }
  for em in message.attachments:
    data["attachments"].append({"type": "image", "url": upload(em.url)})
  print(data)
  requests.post("https://api.groupme.com/v3/bots/post", json.dumps(data))


async def RecvMessage(string):
  channel = client.get_channel(channel_id)
  s = json.loads(string)
  if s["sender_type"] == "bot":
    print("DISCARDING RecvMessage SELF MESSAGE")
    return
  rows = db.Select("main", id = s["sender_id"])
  if len(rows) == 0:
    rows = [{"name": s["sender_id"]}]
    response = requests.get("https://api.groupme.com/v3/groups/" + s["group_id"] + "?token=" + groupme_token)
    members = json.loads(response.text)["response"]["members"]
    for m in members:
      if m["user_id"] == s["sender_id"]:
        db.Insert("main", id = s["sender_id"], name = m["nickname"])
        rows = [{"name": m["nickname"]}]
        break
  nickname = rows[0]["name"]
  e = None
  for attachment in s["attachments"]:
    if attachment["type"] == "image":
      e = discord.Embed()
      e.set_image(url = attachment["url"])
  await channel.send(nickname + ": " + s["text"], embed = e);

client_loop = asyncio.get_event_loop()

class Listener():
  """
  <node>
    <interface name='xyz.niles.LeslieBot'>
      <method name='RecvMessage'>
        <arg type='s' name='a' direction='in'/>
        <!--<arg type='s' name='response' direction='out'/>-->
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
