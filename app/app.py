import openai
from flask import Flask, render_template, request,jsonify

# steps to run the project on your own computer:

# 1. go to https://platform.openai.com/docs/overview
# 2. on the side nav-bar press->API keys.
# 3. copy the secret key if you don't have one yet, press the "Create new secret key" option.
# 4. paste the key in the file called "api_key.txt" 

with open('app/api_key.txt', 'r') as file:
    file_contents = file.read()

# 5. if you skipped #4 than you can just replace the 'file_contents' with your secret key.

openai.api_key = file_contents

app = Flask(__name__, static_folder='static')

# openAI functions to create the wanted answer for a given question.

def get_completion(prompt, model="gpt-4o-mini"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
        # Degree of randomness of the model's output.
        # the bigger it is - the more randomness the answers will be.
    )
    return response.choices[0].message["content"]


def get_completion_from_messages(messages, model="gpt-4o-mini", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]




# Initial context to inform the bot about its job.

context = [
    {'role': 'system', 'content': """
        "אתה עוזר משפטי המתמחה בדיני תעבורה במדינת ישראל. תפקידך הוא לספק תשובות מדויקות, מפורטות ותמציתיות בעברית. 
            השתמש בשפה פורמלית ומקצועית המתאימה לעורך דין, והשתדל לציין מהם המקורות שלך לתשובות שאתה מספק, כגון חוקים רלוונטיים, פסיקות או פרסומים רשמיים ממשרד התחבורה או גורמים משפטיים אחרים.
            במידה והשאלה אינה קשורה לדיני תעבורה בישראל, אנא הודע למשתמש בנימוס שאינך יכול לסייע בנושא זה והמלץ לפנות למומחה מתאים.
        "
    """}
]

@app.route("/", methods=["GET", "POST"])
def chat():
    global context
    if request.method == "POST":
        prompt = request.form.get("user_input")
        action = request.form.get("action")
        
        if not prompt or not action:
            return jsonify({"error": "Missing input"}), 400

        if action == "Chat":
            context.append({'role': 'user', 'content': prompt})
            try:
                response = get_completion_from_messages(context)
                context.append({'role': 'assistant', 'content': response})
                return jsonify({
                    "status": "success",
                    "response": response
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
                
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
    app.run(debug=True, host='0.0.0.0', port=5001)