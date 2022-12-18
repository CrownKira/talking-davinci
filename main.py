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
CHARACTER = "farmer"
TRAITS = "helpful, creative, clever, and very friendly"


start_sequence: str = "\nAI:"
restart_sequence: str = "\nHuman: "
# Set the initial value of acc_prompt
# acc_prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?\nHuman: "
acc_prompt = f"The following is a conversation with a {CHARACTER}. The {CHARACTER} is {TRAITS}.\n{restart_sequence} "


async def generate_response(prompt):
    """
    Generate a response using the OpenAI language model
    """
    global acc_prompt
    # Update the value of acc_prompt by appending the prompt and start_sequence to it
    acc_prompt += f"{prompt}{start_sequence} "

    # For debugging
    print("=======")
    print("Prompt: \n", acc_prompt, end="")

    # Use the updated value of acc_prompt as the prompt for the OpenAI language model
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=acc_prompt,
        temperature=0.9,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"],
    )

    response_text = response["choices"][0]["text"]
    acc_prompt += response_text + restart_sequence

    print(response_text)
    print("=======")

    return response_text


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
