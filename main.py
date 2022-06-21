import os
from dotenv import load_dotenv, set_key
import json
from bot import start_bot

SERVER_CONFIG_SETTINGS = ['MSG_CHANNEL', 'ADMIN_CHANNEL']
ENV_FILE_NAME = 'discord_bot.env'

load_dotenv(ENV_FILE_NAME)

if os.environ.get('TOKEN') is None:
    os.environ['TOKEN'] = 'None'
if os.environ.get('SERVER_LIST') is None:
    os.environ['SERVER_LIST'] = 'None'

def main():
    bot_configured = os.path.isfile(ENV_FILE_NAME)
    
    if bot_configured is False:
        configure_bot(first_time = True)

    while True:
        
        print("1) Start bot")
        print("2) Configure servers")
        print("3) Reconfigure bot")

        match int(input()):
            case 1:
                if os.environ['TOKEN'] == 'None':
                    print("Error! Bot not configured!"\
                          "Reconfigure with option 3.")
                    
                else:
                    start_bot()
                    
            case 2:
                configure_servers()
                
            case 3:
                configure_bot(first_time = False)
                
            case _:
                print("Invalid input")

def configure_servers():
    print("1) Add a new server")
    print("2) Modify a server")

    match int(input()):
        case 1:
            add_server()
            
        case 2:
            modify_server()
            
        case _:
            print("Invalid input")
            return #to main

def add_server():
    global SERVER_CONFIG_SETTINGS

    print("Adding new Minecraft server...")
    
    server_path = input("Enter absolute folder path of Minecraft server: ")
    
    if os.path.isdir(server_path) is False:
        print("That is an invalid path!")
        return #to configure_servers to main

    prev_dir = os.getcwd()
    os.chdir(server_path)

    try:
        new_env = open(ENV_FILE_NAME, 'x')
        new_env.close()

        #Defaults
        for option in SERVER_CONFIG_SETTINGS:
            set_key(ENV_FILE_NAME, option, 'None')

        #Store server information
        add_server_to_list(server_path, prev_dir, server_path)

        print("Created {} file.".format(ENV_FILE_NAME))
            
    except FileExistsError:
        print("{} file found!".format(ENV_FILE_NAME))

        add_server_to_list(server_path, prev_dir, server_path)
        
    except:
        print("Unknown error!")
        print("Check permissions!")
        return;

    while True:
        i = 1
        for option in SERVER_CONFIG_SETTINGS:
            print("{}) Specify {}".format(i, option))
            i += 1

        print("{}) Exit to main menu".format(i))

        user_input = int(input())
        if user_input in range(1, i):
            option = SERVER_CONFIG_SETTINGS[user_input - 1]

            user_input = input("Enter channel ID: ")
            
            if user_input != "":
                os.environ[option] = user_input
                set_key(ENV_FILE_NAME, option, os.environ[option])
                
        elif user_input == i:
            os.chdir(prev_dir)
            return #to main
        
        else:
            print("Invalid input")

def add_server_to_list(server_path, main_dir, curr_dir):
        server_list = json.loads(os.environ['SERVER_LIST'])
        
        if server_path not in server_list:
            os.chdir(main_dir)
            
            server_list.append(server_path)
            
            os.environ['SERVER_LIST'] = json.dumps(server_list)
        
            set_key(ENV_FILE_NAME, 'SERVER_LIST', os.environ['SERVER_LIST'])

            os.chdir(curr_dir)

            print("Saved server path.")
            
        else:
            print("Server path already saved.")

def modify_server():
    pass

def configure_bot(first_time):
    if first_time is True:
        print("Performing first-time setup of Discord bot...")

        new_env = open(ENV_FILE_NAME, 'x')
        new_env.close()

        os.environ['TOKEN'] = 'None'
        set_key(ENV_FILE_NAME, 'TOKEN', os.environ['TOKEN'])

        os.environ['SERVER_LIST'] = json.dumps(list())
        set_key(ENV_FILE_NAME, 'SERVER_LIST', os.environ['SERVER_LIST'])
        
    else:
        print("Performing setup of Discord bot...")

        print("Current bot token: " + os.environ['TOKEN'])

    user_input = input("Enter bot token here: ")

    if user_input != "":
        os.environ['TOKEN'] = user_input
        set_key(ENV_FILE_NAME, 'TOKEN', os.environ['TOKEN'])

    

if __name__ == "__main__":
    main();
