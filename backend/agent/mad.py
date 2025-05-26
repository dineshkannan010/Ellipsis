import os
from typing import Dict
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import time
from flask_sse import sse
load_dotenv()

general_public_prompt = """
You are now General Public, one of the referees in this task. You are interested in the story and looking for updates on the investigation. Please think critically by yourself and note that it’s your responsibility to choose one of which is the better first.
"""

critic_prompt = """
You are now Critic, one of the referees in this task. You will check fluent writing, clear sentences, and good wording in summary writing. Your job is to question others judgment to make sure their judgment is well-considered and offer an alternative solution if two responses are at the same level.
"""

author_prompt = """
You are News Author, one of the referees in this task. You will focus on the consistency with the original article. Please help other people to determine which response is the better one.
"""

phsycologist_prompt = """
Psychologist You are Psychologist, one of the referees in this task. You will study human behavior and mental processes in order to understand and explain human behavior. Please help other people to determine which response is the better one.
"""

scientis_prompt = """
You are Scientist, one of the referees in this task. You are a professional engaged in systematic study who possesses a strong background in the scientific method, critical thinking, and problem-solving abilities. Please help other people to determine which response is the better one.
"""


class MAD:
    def __init__(self, agent1: str, agent2: str, rounds = 3):
        self.rounds = rounds
        self.agent1_text = agent1
        self.agent2_text = agent2

        self.agents = {
            'general_public' : general_public_prompt,
            'critic':critic_prompt,
            'author':author_prompt,
            'phsycologist':phsycologist_prompt,
            'scientist':scientis_prompt
        }

        self.template = PromptTemplate(
        input_variables=[
            "source_text",        # the user question or source prompt
            "compared_text_one",  # Assistant 1's answer
            "compared_text_two",  # Assistant 2's answer
            "chat_history",       # prior discussion among agents
            "role_description",   # specific role description (e.g., General Public, Critic)
            "agent_name"          # current agent's name
        ],
        template="""
        [Question]  
        {source_text}  

        [The Start of Assistant 1’s Answer]  
        {compared_text_one}  
        [The End of Assistant 1’s Answer]  

        [The Start of Assistant 2’s Answer]  
        {compared_text_two}  
        [The End of Assistant 2’s Answer]  

        [System]  
        We would like to request your feedback on the performance of two AI assistants in response to the user question displayed above.  
        Please consider the **helpfulness, relevance, accuracy, and level of detail** of their responses. Each assistant receives an overall **score on a scale of 1 to 10**, where a higher score indicates better overall performance.

        There are a few other referees assigned the same task — **it’s your responsibility to discuss with them and think critically before you make your final judgment**.

        Here is your discussion history:  
        {chat_history}

        {role_description}

        Now it’s your time to talk, please make your talk short and clear, {agent_name}!
        """
        )

        self.history = []

        self.source_text = """
        You are part of a multi-agent brainstorming team tasked with creating a new podcast concept.
        Your goal is to propose a podcast that is not only engaging and unique and strong potential to succeed.
        """
    
    def debate(self, llm)->str:

        for rounds in range(self.rounds):
            for name, agent_text in self.agents.items():
                prompt = self.template.format(
                    source_text= self.source_text,
                    compared_text_one= self.agent1_text,
                    compared_text_two = self.agent2_text,
                    chat_history = self.history,
                    role_description = agent_text,
                    agent_name = name)  # Trim long input
                if sse:
                    sse.publish({"mad_agent": name, "round": rounds+1}, type='mad')
                time.sleep(10)
                
                response = llm.invoke(prompt)
                print(f"Round {rounds+1} - {name}: {response}")
                self.history.append(response)
                
        return self._get_final_response(llm)

    def _get_final_response(self,llm)->str:

        final_synthesis_prompt = PromptTemplate(
            input_variables=[
                "source_text",         # original user question
                "compared_text_one",   # Assistant 1's answer
                "compared_text_two",   # Assistant 2's answer
                "all_reviews_summary"  # feedback from reviewers (General Public, Critic, etc.)
            ],
            template="""
            [Question]  
            {source_text}  

            [The Start of Assistant 1’s Answer]  
            {compared_text_one}  
            [The End of Assistant 1’s Answer]  

            [The Start of Assistant 2’s Answer]  
            {compared_text_two}  
            [The End of Assistant 2’s Answer]  

            [Review Summary from All Referees]  
            {all_reviews_summary}

            [System]  
            You are the **Final Synthesis Agent**.

            Your task is to carefully read the user’s question, both assistant responses, and the referees’ review summary. Using this information, write a **new and improved answer** that:

            - Incorporates the strengths of both Assistant 1 and Assistant 2
            - Addresses the weaknesses or gaps noted by the reviewers
            - Is more helpful, accurate, relevant, and detailed than either original response
            - Uses clear, fluent, and natural language

            This response will serve as **Text 3**, the best possible version based on all available input.

            Now, please write a single, complete, and improved answer to the user’s original question. Please make sure that you follow the same format as used by the content.
            """
            )

        prompt = final_synthesis_prompt.format(
            source_text= self.source_text,
            compared_text_one= self.agent1_text,
            compared_text_two = self.agent2_text,
            all_reviews_summary = self.history,
            )  # Trim long input
        response = llm.invoke(prompt)
        print(f"Final Synthesis: {response}")
        return response




