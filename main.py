# Import necessary modules
import asyncio
import os
import tempfile
from playsound import playsound

import edge_tts
import openai
import speech_recognition as sr


# Set up OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]
LANGUAGE = "zh-TW"
VOICE = "Microsoft Server Speech Text to Speech Voice (zh-TW, HsiaoChenNeural)"


async def generate_response(prompt):
    """
    Generate a response using the OpenAI language model
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
    )
    return response["choices"][0]["text"]


async def main():
    """
    Main function
    """
    # Create a new speech recognition object
    recognizer = sr.Recognizer()

    # Continuously listen for and handle user input
    while True:
        # Listen for user input
        with sr.Microphone() as source:
            print("Listening for input...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)

        # Recognize the user's speech
        try:
            input_text = recognizer.recognize_google(audio, language=LANGUAGE)
            print("Input text: " + str(input_text))
        except sr.UnknownValueError:
            print("Unable to recognize speech.")
            continue

        # Generate and play a response
        response_text = await generate_response(input_text)
        communicate = edge_tts.Communicate()
        with tempfile.NamedTemporaryFile() as temporary_file:
            async for i in communicate.run(
                response_text,
                voice=VOICE,
            ):
                if i[2] is not None:
                    temporary_file.write(i[2])
            playsound(temporary_file.name)


if __name__ == "__main__":
    asyncio.run(main())
