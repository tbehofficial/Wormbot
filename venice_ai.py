import requests

import json

import logging

import uuid

from typing import List, Dict

from config import VENICE_AI_HEADERS, VENICE_AI_COOKIES

class VeniceAI:

    def __init__(self):

        self.base_url = "https://outerface.venice.ai/api/inference/chat"

        self.headers = VENICE_AI_HEADERS

        self.cookies = VENICE_AI_COOKIES

        

    def generate_ids(self):

        return {

            'requestId': f'req_{str(uuid.uuid4()).replace("-", "")}',

            'messageId': f'msg_{str(uuid.uuid4()).replace("-", "")}',

            'userId': f'user_anon_{str(uuid.uuid4()).replace("-", "")}'

        }

    

    def prepare_payload(self, prompt: List[Dict], user_message: str):

        ids = self.generate_ids()

        current_prompt = prompt + [{'role': 'user', 'content': user_message}]

        

        payload = {

            'requestId': ids['requestId'],

            'conversationType': 'text',

            'type': 'text',

            'modelId': 'dolphin-3.0-mistral-24b',

            'modelName': 'Venice Uncensored',

            'modelType': 'text',

            'prompt': current_prompt,

            'systemPrompt': '',

            'messageId': ids['messageId'],

            'includeVeniceSystemPrompt': True,

            'isCharacter': False,

            'userId': ids['userId'],

            'simpleMode': False,

            'characterId': '',

            'id': '',

            'textToSpeech': {

                'voiceId': 'af_sky',

                'speed': 1,

            },

            'webEnabled': True,

            'reasoning': True,

            'temperature': 0.3,

            'topP': 1,

            'clientProcessingTime': 11,

        }

        

        return payload

    

    def get_ai_response(self, conversation_history: List[Dict], user_message: str) -> str:

        try:

            payload = self.prepare_payload(conversation_history, user_message)

            

            response = requests.post(

                self.base_url,

                headers=self.headers,

                cookies=self.cookies,

                json=payload,

                timeout=30

            )

            

            if response.status_code != 200:

                logging.error(f"Venice AI API error: {response.status_code}")

                return "Sorry, I'm having trouble connecting. Please try again."

            

            full_text = ''

            for line in response.text.strip().splitlines():

                if line.strip():

                    try:

                        data = json.loads(line.strip())

                        if isinstance(data, dict) and "content" in data:

                            content = data.get("content", "")

                            full_text += content

                    except json.JSONDecodeError:

                        try:

                            data = eval(line.strip())

                            if isinstance(data, dict) and "content" in data:

                                content = data.get("content", "")

                                full_text += content

                        except:

                            continue

            

            if not full_text.strip():

                return "I received your message but couldn't generate a response. Please try again."

            

            return full_text.strip()

            

        except requests.exceptions.Timeout:

            logging.error("Venice AI API timeout")

            return "The AI is taking too long to respond. Please try again."

        except requests.exceptions.ConnectionError:

            logging.error("Venice AI API connection error")

            return "Connection error. Please check your internet connection."

        except Exception as e:

            logging.error(f"Venice AI error: {e}")

            return "An unexpected error occurred. Please try again later."