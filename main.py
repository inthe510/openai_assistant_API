from flask import Flask, request, render_template, session
import openai
import os
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key

openai_api = os.environ.get('OPENAI_API_KEY')
client = openai.OpenAI(api_key=openai_api)

assistant_id = "asst_s8SHsIuNr69CbAxvKXytcX8C"

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'thread_id' not in session:
        # Create a new thread for a new user session
        thread = client.beta.threads.create()
        session['thread_id'] = thread.id
        session['messages'] = []

    if request.method == 'POST':
        user_input = request.form['user_input']
        process_user_input(user_input)

    return render_template('index.html', messages=session.get('messages'))

def process_user_input(user_input):
    # Add user's message to the session
    session['messages'].append({'role': 'user', 'content': user_input})

    # Create a message in the thread
    client.beta.threads.messages.create(
        thread_id=session['thread_id'],
        role="user",
        content=user_input
    )

    # Create and run the assistant
    run = client.beta.threads.runs.create(
        thread_id=session['thread_id'],
        assistant_id=assistant_id
    )

    while True:
        # Retrieve the run status
        run_status = client.beta.threads.runs.retrieve(
            thread_id=session['thread_id'],
            run_id=run.id
        )

        if run_status.status == 'completed':
            break

        time.sleep(5)

    # Retrieve the messages
    messages = client.beta.threads.messages.list(
        thread_id=session['thread_id']
    )

    # Add assistant's messages to the session
    for message in messages.data:
        if message.role == 'assistant':
            session['messages'].append({'role': 'assistant', 'content': message.content[0].text.value})

if __name__ == '__main__':
    app.run(debug=True, port = 5001)
