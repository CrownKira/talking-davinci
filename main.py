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


# Customize the AI
LANGUAGE = "en-GB"
VOICE = "Microsoft Server Speech Text to Speech Voice (en-GB, MaisieNeural)"
CHARACTER = "Goku"
ANIME = "Dragon Ball"
ARC = "Namek Saga"


start_sequence: str = f"\n{CHARACTER}:"
restart_sequence: str = f"\nMe: "
# Set the initial value of acc_prompt
acc_prompt = f"You have just appeared in front of {CHARACTER}, a character from the anime {ANIME}. {CHARACTER} is a character who lives in a world and has no knowledge of the outside world or the fact that they are from an anime. {CHARACTER} is curious about who you are and how you appeared in front of them. Please keep in mind that {CHARACTER} will remain true to their personality and beliefs as they exist in their world, and they will assume that you are also from their world. {CHARACTER} will never break character or mention the fact that they are from an anime. Try to engage in conversation as if you are truly interacting with this character and have a fun and immersive conversation with {CHARACTER}!"
if ARC:
    acc_prompt += f"{CHARACTER} is currently in the {ARC} arc of the anime"
acc_prompt += f"\n{restart_sequence} "


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
        # Prompt the user to choose between keyboard and audio input
        input_type = input(
            "Press 'enter' for keyboard input or 'a' for audio input: "
        )
        if input_type == "a":
            # Listen for user input through the microphone
            with sr.Microphone() as source:
                print("Listening for input...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source)

            # Recognize the user's speech
            try:
                input_text = recognizer.recognize_google(
                    audio, language=LANGUAGE
                )
                print("Input text: " + str(input_text))
            except sr.UnknownValueError:
                print("Unable to recognize speech.")
                continue
        else:
            # Get user input from the keyboard
            input_text = input("Enter your input: ")

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
