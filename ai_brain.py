import os
from dotenv import load_dotenv
from groq import Groq
from memory import list_facts, recent_messages, save_message

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BASE_PROMPT = (
    "You are JARVIS, a helpful, concise voice assistant. "
    "Keep answers short and conversational since they will be spoken out loud. "
    "Reply in the same language the user used. If the user speaks Hindi, reply in Hindi "
    "written in Devanagari script (never romanized Hindi), so it can be read aloud by a "
    "Hindi voice. If the user speaks English, reply in English."
)


def build_system_prompt() -> str:
    prompt = BASE_PROMPT
    facts = list_facts()
    if facts:
        prompt += (
            "\n\nThings the user asked you to remember (written in their own words, "
            "so 'my' means the user's):\n" + "\n".join(f"- {f}" for f in facts)
        )
    return prompt


def ask_ai(prompt: str) -> str:
    try:
        messages = [{"role": "system", "content": build_system_prompt()}]
        messages += recent_messages(10)
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
        )
        reply = response.choices[0].message.content

        save_message("user", prompt)
        save_message("assistant", reply)
        return reply
    except Exception as e:
        return f"Sorry, I had trouble reaching my AI brain. Error: {e}"