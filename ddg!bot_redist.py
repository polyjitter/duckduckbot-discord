import discord
import asyncio
import duckduckgo as ddg
import json

# Bot Info
__author__ = 'eye-sigil'
__version__ = '0.2.3'

# Settings
blocked = {}
commands = {}
safesearch_values = {}

# Message Templates
html_tags = {"b": "**",
             "i": "_",
             "br/": "\n",
             "u": "__"}

ready_msg = '''
Logged in as...
USER: {}
ID: {}
------
Ready to !bang.
'''

broken_msg = '''```{}: {}```
Sorry, but it seems your query was somehow broken. I may have been ratelimited on **DuckDuckGo\'s** end.

_**NOTE:** This bot and `duckduckgo-python3` are still in development. Results may be unexpected._'''

about_msg = '''```tex
$$ ddg!bot $$

# OWNER: {{{}}}
# LIB: {{discord.py {}}} {{Rapptz, Python}}
# VERSION: {{{}}}

% ddg!bot is a frontend for the DuckDuckGo Instant Answers API.
% It is made for quick searches and info grabbing on Discord.
% It supports perserver safesearch, result scraping, and all DDG search syntax.
% Ready to !bang?

Powered by DuckDuckGo: {{https://duckduckgo.com/about}}
```'''.format(__author__, discord.__version__, __version__)

git_msg = '''`duckduckgo-python3` <http://github.com/eye-sigil/duckduckgo-python3>
`duckduckbot-discord` <https://github.com/eye-sigil/duckduckbot-discord>

_All components under development. Results may be unexpected._'''

server_msg = '''_For more help on this bot, please visit: <https://discord.gg/011iDaqaFcbzbEsMz>_'''

addbot_msg = '''_To add this bot to your server, please use this link: <https://goo.gl/IEEHtI>_'''

safesearch_msg = '''Server safesearch now set to **{}.**

_**Note:** This does nothing right now._'''

help_msg = '''**All commands are called with `ddg!command` or `@ddgcommand`.**

**`ddg! search here` and `@ddg search here` will also return a search to _DuckDuckGo_.**

```tex
{}
```'''

client = discord.Client(max_messages=100)
print('\nCreated discord.Client...')


def add_command(name=None):
    '''
    Adds a command to the commands list. Allows Discord users to call it.
    '''

    def inner(func):
        commands[func.__name__] = func
        return func
    return inner


def detect_call(message):
    '''
    Detects a bot call. Ran on every message received.
    '''

    if message.author.bot or message.author.id in blocked.values():
        return False
    elif message.clean_content.startswith('@{}'.format(message.server.me.display_name)) or message.clean_content.startswith('ddg!'):
        return True
    else:
        return False


@add_command()
def about(message):
    '''
    Returns info on the bot.
    '''

    return about_msg


@add_command()
def git(message):
    '''
    Returns info about the github repos.
    '''

    return git_msg


@add_command()
def connected(message):
    '''
    Returns a list of servers bot is in.
    '''

    servers = [s.name for s in client.servers]
    return '```{}```'.format(str(servers))


@add_command()
def server(message):
    '''
    Returns help server link.
    '''

    return server_msg


@add_command()
def addbot(message):
    '''
    Returns bot OAuth link.
    '''

    return addbot_msg


@add_command()
def safesearch(message):
    '''
    Toggles safesearch on and off for a particular server.
    '''

    s_id = message.server.id

    if s_id in safesearch_values:
        safesearch_values[s_id] = not safesearch_values[s_id]
    else:
        safesearch_values[s_id] = True

    return safesearch_msg.format(str(safesearch_values[s_id]))


@add_command()
def help(message):
    '''
    Returns a list of commands and help on bot usage.
    '''

    help_list = ''
    for command in commands:
        help_list += '# {}\n'.format(command)

    return help_msg.format(help_list)


@add_command()
def search(command):
    '''
    Gets a result from DuckDuckGo's API.
    Also a prototype for the new duckduckgo-python3 get_zci() logic.
    '''

    try:
        result = ddg.get_zci(command)
    except Exception as e:
        result = broken_msg.format(e.__class__.__name__, str(e))
    if result.startswith('https://api.duckduckgo.com'):
        result = '**Sorry, no results were found.**'

    # result = ddg.query(search, html=True)
    # if result == ' ' or result == '':
    #    result = ddg.get_zci(search)
    # if len(result):

    return result

# def format_result(result):
#    formatted = ''
#    formatted = result.replace()


@client.event
async def on_ready():
    '''
    Executed when the bot successfully connects to Discord.
    '''

    # Current Account
    print(ready_msg.format(client.user.name, client.user.id))

    # Help Hint
    await client.change_status(game=discord.Game(name="ddg!help"))


@client.event
async def on_message(message):
    '''
    Executed when the bot receives a message.
    [message] is a discord.Message object, representing the sent message.
    # '''

    if detect_call(message):

        # Info
        if message.channel.is_private:
            server = 'N/A'
            channel = 'Direct Message'
        else:
            server = message.server.name
            channel = message.channel.name

        print('Input: {}, {}\nServer: {}\nChannel: {}'.format(message.author.name,
                                                              message.clean_content,
                                                              server,
                                                              channel))

        # Stripping
        command = message.clean_content
        command = command.replace('@{}'.format(message.server.me.display_name), '')
        command = command.replace('ddg!', '')
        command = command.strip()

        print('Stripped: {}'.format(command))

        # Parsing
        if command == '':
            output = about(message)
        elif command in commands:
            output = commands[command](message)
        else:
            output = search(command)

        print('Output:\n{}'.format(output))

        # Outputting
        await client.send_message(message.channel, output)
        print('\n')

client.run('**token**')
