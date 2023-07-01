import requests
from discord.ext import commands
from discord import Embed
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from random import choice


def redditsearch(subreddit, sortby,posts=100):
    with open ('/home/pi/redditbot/user.txt','r') as f:
        user=f.read()
    with open ('/home/pi/redditbot/pass.txt','r') as f:
        passw=f.read()
    auth = requests.auth.HTTPBasicAuth('PDIUI8AZdt825HT5KuiO9g', 'HuIr0Jy5JmLErLqw64fFZoc3jij02A')
    data = {'grant_type': 'password',
        'username': user,
        'password': passw}
    headers = {'User-Agent': 'MyBot/0.0.1'}
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers)
    TOKEN = res.json()['access_token']
    headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}
    parameters={'limit':posts}
    urllist=[]
    requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

    for i in range(1):
        res = requests.get(f"https://oauth.reddit.com/r/{subreddit}{sortby}",
                   headers=headers,
                   params=parameters) 
        if res.status_code!= 200 or len(res.json())==0:
          return []   
        for post in res.json()['data']['children']:
            if 'https://v.redd.it/' not in post['data']['url'] and 'https://www.reddit.com/gallery/' not in post['data']['url']:
                postinfo=[]
                postinfo.append(post['data']['url'])
                postinfo.append('https://www.reddit.com'+post['data']['permalink'])
                postinfo.append(post['data']['title'])
                postinfo.append(post['data']['over_18'])
                urllist.append(postinfo)
            elif 'https://www.reddit.com/gallery/' in post['data']['url']:
                postinfo=[]
                postinfo.append(post['data']['thumbnail'])
                postinfo.append('https://www.reddit.com'+post['data']['permalink'])
                postinfo.append(post['data']['title'])
                postinfo.append(post['data']['over_18'])
                urllist.append(postinfo)
            else:
                postinfo=[]
                postinfo.append('https://www.reddit.com'+post['data']['permalink'])
                postinfo.append(post['data']['over_18'])
                urllist.append(postinfo)
    return urllist

with open ('/home/pi/redditbot/tokenid.txt','r') as f:
    tokenid=f.read()
bot_guild_ids = []

def makeids() :
  global bot_guild_ids
  for guild in client.guilds :
    bot_guild_ids.append(guild.id)
client=commands.Bot(command_prefix="!")
slash=SlashCommand(client, sync_commands=True)
@slash.slash(
    name="reddit",
    description="browse reddit!",
    guild_ids=bot_guild_ids,
    options=[
        create_option(
            name='subreddit',
            description="Choose subreddit",
            required=True,
            option_type=3
        ) ,
        create_option(
            name='sort',
            description="Choose from hot, top, and new",
            required=True,
            option_type=3,
            choices=[
                create_choice(
                    name="Top posts of all time",
                    value="/top?t=all"
                ),
                create_choice(
                    name="Top posts of today",
                    value="/top?t=today"
                ),
                create_choice(
                    name="Top of this year",
                    value="/top?t=year"
                ),
                create_choice(
                    name="Hot",
                    value="/hot"
                )
            ]
        ) ,
        create_option(
            name='posts',
            description="Number of posts expected:",
            required=False,
            option_type=4    
        )    
    ]
)
async def _reddit(ctx:SlashContext, subreddit:str,sort:str,posts:int=1):
    await ctx.send(f'Your request from r/{subreddit} is being processed...')
    postinfo=[]
    postinfo=redditsearch(subreddit,sort)
    if len(postinfo)>0:

      if posts>len(postinfo):
          posts=postinfo
      for i in range (posts):
          chosenpost=choice(postinfo)   
          if "reddit.com/r/" not in chosenpost[0] and "redgifs.com" not in chosenpost[0]:
              if (len(chosenpost[2])>256):
                  chosenpost[2]=chosenpost[2][:253]+'...'
              if ('https://' not in chosenpost[0]):
                chosenpost[0]='https://www.reddit.com'+chosenpost[0]
              embed=Embed(title=chosenpost[2], url=chosenpost[1])
              embed.set_image(url=chosenpost[0])
              await ctx.channel.send(embed=embed)
          else:
              await ctx.channel.send(chosenpost[0])       
          postinfo.remove(chosenpost)
    else:
      await ctx.send(f'Subreddit: {subreddit} does not exist')

@client.event
async def on_guild_join(guild) :
  makeids()

client.run(tokenid)
