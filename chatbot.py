# chatbot.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# .env file se API key load karo
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Client initialize karo
client = OpenAI(api_key=api_key)

# ChatGPT se baat karo
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

# ChatGPT ka jawab print karo
print(response.choices[0].message.content)