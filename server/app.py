from flask import Flask, request
from flask_cors import CORS
from loguru import logger
import openai

# flask configuration--------------------------------------------------------------
DEBUG = True

# instantiate the app
app = Flask(__name__)
# Load configuration variables
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})
# flask configuration--------------------------------------------------------------


# openai chatGPT configuration--------------------------------------------------------------
openai.api_key = "https://platform.openai.com/playground"
# init_prompt = ""  # it can make chatGPT be some different role, for example: beautiful girl.

# By global `all_messages`, we can use it easily.
# it includes every bot&user messages.
all_messages = {}



def get_answer_from_bot(bot_name, prompt):
    """
    1.prepare the input message according the bot which you talk to
    2.input the complete messages into model, to get the answer

    during this, log something for DEBUG in the future
    """
    try:
        messages = all_messages[bot_name]
    except KeyError:
        logger.info("all_messages[%s] is none, so init it." % bot_name)
        all_messages[bot_name] = []
        messages = all_messages[bot_name]

    messages.append({
        "role": "user",
        "content": prompt
    })
    logger.info("user: " + prompt)

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    message = completion["choices"][0]["message"]
    messages.append(message)
    logger.info("%s: %s" % (bot_name, message['content']))

    return message['content']


@app.route('/get_answer', methods=['GET', 'POST'])
def get_answer():
    post_data = request.get_json()
    logger.info("post_data: " + str(post_data))
    prompt = post_data["prompt"]
    bot_name = post_data["bot"]

    return {
        'status': 'success',
        "answer": get_answer_from_bot(bot_name, prompt)
    }


if __name__ == '__main__':
    logger.add(
        "./log/run.log",
        encoding="utf-8",
        format="{level} | {time:YYYY-MM-DD HH:mm:ss} | {file} | {line} | {message}",
        retention="30 days",
        rotation="500 MB"
    )
    logger.info("System initializing.")

    # # Before officially using the model, initialize the model by giving it `init_prompt`
    # chat_init()

    # Bind to all network interfaces
    app.run(host='0.0.0.0', port=5000)
