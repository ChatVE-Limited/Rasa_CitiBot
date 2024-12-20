# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import openai
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import os
from dotenv import load_dotenv


class ActionDefaultGPTResponse(Action):
    load_dotenv()

    OPENAI_KEY = os.getenv("OPENAI_API_KEY")

    def name(self) -> str:
        return "action_default_gpt_response"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        user_message = tracker.latest_message.get("text")

        openai.api_key = os.getenv("OPENAI_API_KEY")
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert on Nigerian topics and should focus on Nigeria in all your answers."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300
            )
            response_dict = response.model_dump()

            gpt_reply = response_dict["choices"][0]["message"]["content"]

            dispatcher.utter_message(text=gpt_reply)

        except Exception as e:
            dispatcher.utter_message(
                text="I'm sorry, I couldn't fetch an answer at the moment. Please try again later."
            )
            print(f"Error: {e}")

        return []
