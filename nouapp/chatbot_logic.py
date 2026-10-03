# nouapp/chatbot_logic.py

import json
import os
import random
import re
from django.conf import settings


class NalandaChatbot:

    def __init__(self):

        # Path to FAQ data file
        data_path = os.path.join(
            settings.BASE_DIR,
            'nouapp',
            'static',
            'data',
            'faq_data.json'
        )

        try:
            with open(data_path, 'r', encoding='utf-8') as file:
                self.data = json.load(file)

        except FileNotFoundError:

            # Default Kuniya chatbot data
            self.data = [
                {
                    "tag": "greeting",
                    "patterns": [
                        "hi",
                        "hello",
                        "hey",
                        "is anyone there",
                        "good day"
                    ],
                    "responses": [
                        "Hello! Welcome to Kuniya Learning Management System. How can I help you today?",
                        "Hi there! Welcome to Kuniya LMS! How can I assist you?"
                    ]
                },
                {
                    "tag": "fallback",
                    "patterns": [],
                    "responses": [
                        "I'm sorry, I don't have the answer to that yet. Please ask me about Kuniya courses, login, registration, assignments, quizzes, or learning resources."
                    ]
                }
            ]


    def get_response(self, user_input):

        user_input = user_input.lower().strip()

        # Remove special characters
        user_input = re.sub(r'[^\w\s]', '', user_input)

        # Remove extra spaces
        user_input = re.sub(r'\s+', ' ', user_input)


        # Check exact matches
        for intent in self.data:

            for pattern in intent['patterns']:

                if pattern.lower() == user_input:

                    return (
                        random.choice(intent['responses']),
                        intent['tag']
                    )


        # Check keyword matches
        for intent in self.data:

            for pattern in intent['patterns']:

                if pattern.lower() in user_input:

                    return (
                        random.choice(intent['responses']),
                        intent['tag']
                    )


        # Check partial word matches
        user_words = user_input.split()

        for intent in self.data:

            for pattern in intent['patterns']:

                pattern_words = pattern.lower().split()

                if any(
                    p_word in user_words
                    for p_word in pattern_words
                ):

                    return (
                        random.choice(intent['responses']),
                        intent['tag']
                    )


        # Fallback response
        fallback_responses = [
            i for i in self.data
            if i['tag'] == 'fallback'
        ]

        if fallback_responses:

            return (
                random.choice(
                    fallback_responses[0]['responses']
                ),
                'fallback'
            )

        else:

            return (
                "I'm sorry, I don't have the answer to that yet.",
                'fallback'
            )


# Create chatbot
chatbot = NalandaChatbot()