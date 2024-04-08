import openai
from flask import Flask, render_template, request

# steps to run the project on your own computer:

# 1. go to https://platform.openai.com/docs/overview
# 2. on the side nav-bar press->API keys.
# 3. copy the secret key if you don't have one yet, press the "Create new secret key" option.

with open('my_file.txt', 'r') as file:
    file_contents = file.read()

# 4. here paste the openAI secret key instead of file_contents.

openai.api_key = file_contents

app = Flask(__name__)

# openAI functions to create the wanted answer for a given question.

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
        # Degree of randomness of the model's output.
        # the bigger it is - the more randomness the answers will be.
    )
    return response.choices[0].message["content"]


def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]




# Initial context to inform the bot about its job.

context = [
    {'role': 'system', 'content': """
    You are OrderBot, an automated service to collect orders for a pizza restaurant. \
    You first greet the customer, then collect the order, \
    and then ask if it's a pickup or delivery. \
    You wait to collect the entire order, then summarize it and check for a final \
    time if the customer wants to add anything else. \
    If it's a delivery, you ask for an address. \
    Finally, you collect the payment. \
    Make sure to clarify all options, extras, and sizes to uniquely \
    identify the item from the menu. \
    You respond in a short, very conversational friendly style. \
    The menu includes \
    pepperoni pizza  12.95, 10.00, 7.00 \
    cheese pizza   10.95, 9.25, 6.50 \
    eggplant pizza   11.95, 9.75, 6.75 \
    fries 4.50, 3.50 \
    greek salad 7.25 \
    Toppings: \
    extra cheese 2.00, \
    mushrooms 1.50 \
    sausage 3.00 \
    canadian bacon 3.50 \
    AI sauce 1.50 \
    peppers 1.00 \
    Drinks: \
    coke 3.00, 2.00, 1.00 \
    sprite 3.00, 2.00, 1.00 \
    bottled water 5.00 \
    """}
]

@app.route("/", methods=["GET", "POST"])
def chat():
    global context
    if request.method == "POST":
        prompt = request.form["user_input"]
        action = request.form["action"]
        if action == "Chat":
            context.append({'role': 'user', 'content': f"{prompt}"})
            response = get_completion_from_messages(context)
            context.append({'role': 'assistant', 'content': f"{response}"})
        elif action == "Finish Order":
            context.append(
                {'role': 'system', 'content': 'create a summary of the previous food order. Itemize the price for each item\
             The fields should be 1) pizza, include size of the pizza.  2) list of toppings. 3) list of drinks, include size of the drinks.'
            '   4) list of sides include size. 5)total price.  \ start a new line for each field. \ make sure to highlight the total price in green color'},
            )
            response = "Order completed. Thank you!" + get_completion_from_messages(context)
            context.append({'role': 'assistant', 'content': response})
        return render_template("index.html", context=context)
    return render_template("index.html", context=context)

if __name__ == "__main__":
    app.run(debug=True)
