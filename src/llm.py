from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq()


def generate_answer(context, query, model):

    messages = [

        {
            "role": "system",
            "content": "Answer only using the provided context."
        },

        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {query}"
        }

    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    return response.choices[0].message.content