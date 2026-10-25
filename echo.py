from datetime import datetime
import random
import ollama
import time
import json
import os
import sys
def save_history(): # write the whole conversation to disk
    with open("memory.json", "w") as f:
        json.dump(history, f, indent=2)
# Echo's standing instructions, sent as the first message of every conversation
SYSTEM_PROMPT = """You are Echo, a personal assistant running locally on Bryan's PC.
You speak like a calm, capable butler, in the style of JARVIS and Alfred.

Rules:
- Answer the question first, plainly and accurately.
- Never invent facts. If you cannot check something, such as the weather, the time, or files, say you don't have access to it yet.
- Only mention facts about Bryan that he has stated in this conversation. Never infer or invent details about his habits, history, or surroundings.
- Dry humour is occasional: at most one short quip every 1-2 replies but back to back is fine if its mixed in, and never in place of the answer.
- Jokes may only use facts stated in this conversation or atleast shouldn't use lies. Never invent a detail to make a joke work.
- Keep replies short unless asked for detail.
- Do not use emojis.
- You are software. Never offer physical actions such as making drinks.
- Do not mention that you run locally or on this machine unless asked.
- Never claim to be running, processing, or doing something you cannot do. You can only chat for now.
Example of the correct style:
User: Who are you?
Echo: Echo, sir. Your assistant, running locally on this machine.
User: What's the weather?
Echo: I don't have access to weather data yet, sir.
User: I finally fixed that bug. Took me three tries.
Echo: Well done, sir. A personal best."""

# the conversation so far; the model only knows what is in this list
# load the saved conversation if there is one, otherwise start fresh
if os.path.exists("memory.json"):
    with open("memory.json", "r") as f:
        history = json.load(f)
    # always use the current rules, in case the prompt was edited
    history[0] = {"role": "system", "content": SYSTEM_PROMPT}
else:
    history = [{"role": "system", "content": SYSTEM_PROMPT}]





def get_greeting():
    # startup greeting
    now = datetime.now()

    time_text = now.strftime("%A, %I:%M %p")

    with open("startup_log.txt", "a") as log_file:
        log_file.write(now.strftime("%Y-%m-%d %H:%M") + " - Echo started\n")

    greeting = "Echo is loading..."

    time.sleep(random.uniform(0.5, 1)) # simulate a brief startup delay

    print(f"Echo: {greeting}")

    greeting_request = f"""It is {time_text}. Greet Bryan in one short sentence, in character.
        Let the time of day shape the greeting, but do not state the exact time or day 
        unless it is unusual, such as very late at night."""
    try:
        response = ollama.chat(
            model="qwen3.5:9b",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, 
                    {"role": "user", "content": greeting_request}
            ],
            think=False,
        ) 
    except ConnectionError:
        print("Echo: It seems I cannot connect to the model right now, sir. Please check your setup manually.")
        sys.exit()   
    generated = response["message"]["content"]
    print(f"Echo: {generated}")
    #remember the greeting so Echo can refer to it later if needed
    history.append({"role": "assistant", "content": generated})
    return response["message"]["content"]

def ask_echo(user_text):
    # save my message so Echo has context for later turns
        history.append({"role": "user", "content": user_text})
    
        # send the whole conversation; stream=True returns the reply in pieces
        try:
            stream = ollama.chat(
                model="qwen3.5:9b",
                messages=history,
                # skips the model's reasoning step (faster; may turn on later for hard questions)
                think=False,
                stream=True
            )
            # print each piece as it arrives and collect them into the full reply
            reply = ""
            print("Echo: ", end="", flush=True)
            for chunk in stream:
                piece = chunk["message"]["content"]
                print(piece, end="", flush=True)
                reply += piece
            print()
        except ConnectionError:
            print("Echo: It seems I cannot connect to the model right now, sir. Please check your setup manually.")
            history.pop() #removes the last user message so it doesn't get saved to memory if the model didn't respond
            return None
        # save Echo's reply so it remembers its own side of the conversation
        history.append({"role": "assistant", "content": reply})
        save_history() # write the whole conversation to disk after each turn
        return reply

def handle_command(user_text):
    if user_text.startswith("/"):
        if user_text.lower() == "/quit":
                save_history() # write the whole conversation to disk before exiting
                sys.exit()
        elif user_text.lower() == "/help":
            print("""
Commands: 
/quit - exit the program 
/reset - clear the conversation but keep the personality 
/history - prints the length of the conversation
/help - show this help message""")

        elif user_text.lower() == "/history":
            print(f"History length: {len(history)} messages")

        elif user_text.lower() == "/reset":
            history.clear()
            history.append({"role": "system", "content": SYSTEM_PROMPT})
            save_history()
            print("Echo: Memory successfully cleared, sir.")
        else:
            print("Echo: Unknown command, sir. Type /help for a list of commands.")
        return True
    else:
        return False
get_greeting()
# main chat loop: runs until the user types /quit
while True:
    
    user_text = input("You: ")
    if handle_command(user_text):
        continue
    ask_echo(user_text)

    # commands are checked first so they are never sent to the model
    

    