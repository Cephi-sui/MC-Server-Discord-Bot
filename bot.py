import os
import subprocess
import asyncio
import re
import discord
from discord.ext import commands

TOKEN = ''

#An arbitrary change

bot = commands.Bot(command_prefix = '/')
server_proc = None
server_running = False
log_search = -1
command_ctx = None

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord.')

@bot.command(name = 'test')
async def test(ctx, *args):
    await ctx.send("Test!")
    for i in ctx.args:
        print(i)

@bot.command(name = 'servertest')
async def server_test(ctx):
    global server_proc

##    await server_proc.communicate(b"say hi")

    server_proc.stdin.write(b"say hi\r\n")
    await server_proc.stdin.drain()

@bot.command(name = 'start')
async def server_start(ctx):
    global server_proc
    global server_running

    if server_running is True:
        print("Command received to start server, but server is running or starting!")
        await ctx.send("The server is currently running/starting.")
    else:
        server_running = True
        
        print("Command received to start server.")
        print("Starting server now...")
        await ctx.send("Starting server now...")

        try:
            server_proc = await asyncio.create_subprocess_exec('run.bat',
                stdin = asyncio.subprocess.PIPE, stdout = asyncio.subprocess.PIPE)
        except BaseException:
            server_running = False
            print("Error in starting server!")
            await ctx.send("Error in starting server! Contact Cephi!")

        server_started = False
        while server_started is False:
            data = await server_proc.stdout.readline()

            if b'Done' in data:
                server_started = True
                print("Server is now running.")
                await ctx.send("Server is now running.")

                data = await server_proc.stdout.readline()
                while b'diseases' not in data:
                    data = await server_proc.stdout.readline()
                    
        await log_reader(ctx)

async def log_reader(ctx):
    global server_running
    global log_search
    global command_ctx
    channel = bot.get_channel()
    admin_channel = bot.get_channel()
    
    while server_running is True:
        try:
            data = await server_proc.stdout.readline()
            data_decoded = data.decode('utf-8')

            message = None
            if log_search == -1:
                message = re.search(r'[<].*[>].*', data_decoded)
                if message is not None:
                    await channel.send(message.group())
                else:
                    await admin_channel.send(data_decoded)
            elif log_search == 0:
                message = re.search(
                    r'There are .* of a max of .* players online: .*',
                                    data_decoded)
                if message is not None:
                    message_str = message.group()
                    print(message_str)
                    await command_ctx.send(message_str)

                    log_search = -1
        except BaseException:
            admin_channel.send("Log reader error! Recovering...")

@bot.command(name = 'list')
async def server_list(ctx):
    global server_proc
    global server_running
    global log_search
    global command_ctx

    if server_running is False:
        print("Command received to list players, but server is not running!")
        await ctx.send("The server is currently not running.")
    else:
        print("Command received to list players.")

        log_search = 0 #This must go before the command is input, or the list will be caught by the admin read.
        command_ctx = ctx

        server_proc.stdin.write(b"list\r\n")
        await server_proc.stdin.drain()

@bot.command(name = 'admin')
async def server_admin(ctx):
    global server_proc
    global server_running
    admin_channel = bot.get_channel()

    if ctx.channel.id == admin_channel.id:
        if server_running is False:
            print("Wildcard command received from admin, but server is not running!")
            await ctx.send("The server is currently not running.")
        else:
            print("Wildcard command received from admin.")

            server_proc.stdin.write(ctx.message.content[7:].encode('utf-8') + b"\r\n")
            await server_proc.stdin.drain()

@bot.command(name = 'stop')
async def server_stop(ctx):
    global server_proc
    global server_running

    if server_running is False:
        print("Command received to stop server, but server is not running!")
        await ctx.send("The server is currently not running.")
    else:
        print("Command received to stop server.")
        print("Stopping server now...")
        await ctx.send("Stopping server now...")

    ##    await server_proc.communicate(b"stop")

        server_proc.stdin.write(b"stop\r\n")
        await server_proc.stdin.drain()

        server_proc.wait()

        print("Server stopped.")
        await ctx.send("Server stopped.")

        server_running = False

bot.run(TOKEN)
