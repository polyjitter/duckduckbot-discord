
import discord
import asyncio
import duckduckgo as ddg
import json

blocked = {}
html_tags = {"b" : "**",
             "i" : "_",
             "br/" : "\n",
             "u" : "__"}
commands = {}
safesearch_values = {}


broken = '''Sorry, but it seems your query was somehow broken. I may have been ratelimited on **DuckDuckGo\'s** end.

_**NOTE:** This bot and `duckduckgo-python3` are still in development. Results may be unexpected._'''

about_msg = '''```tex
$$ ddg!bot $$

# OWNER: {eye-sigil}
# LIB: {discord.py 0.10.0} {Rapptz, Python}
# VERSION: {0.1 Indev}

% ddg!bot is a frontend for the DuckDuckGo Instant Answers API.
% It is made for quick searches and info grabbing on Discord.
% It supports perserver safesearch, result scraping, and all DDG search syntax.
% Ready to !bang?

Powered by DuckDuckGo: {https://duckduckgo.com/about}
```'''

git_msg='''`duckduckgo-python3` <http://github.com/eye-sigil/duckduckgo-python3>

_All components under development. Results may be unexpected._'''

server_msg = '''_For more help on this bot, please visit: <https://discord.gg/011iDaqaFcbzbEsMz>_'''

addbot_msg = '''_To add this bot to your server, please use this link: <https://goo.gl/IEEHtI>_'''

client = discord.Client(max_messages=100)
print('Created discord.Client.')

def add_command(name=None):
    def inner(func):
        commands[func.__name__] = func
        return func
    return inner

def detect_call(message):
    if message.author.bot or message.author.id in blocked.values():
        return False
    if (message.content.startswith('<@183615935955861504>') or message.content.startswith('ddg!')) and len(message.content) > 1:
        return True
    else:
        return False

@add_command()
def about():
    return about_msg

@add_command()
def git():
    return git_msg

@add_command()
def connected():
    servers = [s.name for s in client.servers]
    return '```{}```'.format(str(servers))

@add_command()
def server():
    return server_msg

@add_command()
def addbot():
    return addbot_msg

@add_command()
def safesearch(s_id):
    if s_id in safesearch_values:
        safesearch_values[s_id] = not safesearch_values[s_id]
    else:
        safesearch_values[s_id] = True

    return 'Server safesearch now set to **{}.**\n\n_**Note:** This does nothing right now._'.format(str(safesearch_values[s_id]))

@add_command()
def help():

    help_msg = '''**All commands are called with `ddg!command` or `@ddgcommand`, no spaces.**

**`@ddg search here` and `ddg! search here` will also return a search to _DuckDuckGo_.**

```tex\n'''

    for command in commands:
        help_msg += '# {}\n'.format(command)

    help_msg += '```'

    return help_msg

def get_query(command):

    '''
    Gets a result from DuckDuckGo's API.
    Also a prototype for the new duckduckgo-python3 get_zci() logic.
    '''

    try:
        result = ddg.get_zci(command)
    except Exception as e:
        result = "```{}: {}```\n{}".format(e.__class__.__name__, str(e), broken)

    #result = ddg.query(search, html=True)
    #if result == ' ' or result == '':
    #    result = ddg.get_zci(search)
    #if len(result):

    return result

#def format_result(result):
#    formatted = ''
#    formatted = result.replace()

@client.event
async def on_ready():

    '''
    Executed when the bot successfully connects to Discord.
    '''

    print('\nLogged in as:')
    print(client.user.name)
    print(client.user.id)
    print('------')
    print('Ready to !bang.')
    print('')

    await client.change_status(game=discord.Game(name="ddg!help"))

@client.event
async def on_message(message):

    '''
    Executed when the bot recieves a message.
    [message] is a discord.Message object, representing the sent message.
    '''

    if detect_call(message):

        if message.channel.is_private:
            server = 'N/A'
            channel = 'Direct Message'
        else:
            server = message.server.name
            channel = message.channel.name

        print('Input: {}, {}\nServer: {}\nChannel: {}'.format(message.author.name,
                                                 message.content,
                                                 server,
                                                 channel))

        if client.user.mentioned_in(message):
            command = message.content.replace('<@183615935955861504>','')
        else:
            command = message.content.replace('ddg!','')
        print('Stripped: {}'.format(command))

        #command = message.clean_content

        if command == '':
            output = about()
        elif command == 'safesearch':
            output = safesearch(message.server.id)
        elif command in commands:
            output = commands[command]()
        else:
            output = get_query(command)

        print('Output:\n{}'.format(output))

        await client.send_message(message.channel, output)
        print('\n')

client.run('**token**')
