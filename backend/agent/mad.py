import os
import time
import requests
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Role prompts
general_public_prompt = """
You are General Public, a curious and engaged listener. You're drawn to podcasts that are easy to follow, emotionally resonant, and worth sharing. Your role is to evaluate which version feels more natural, relatable, and informative from a regular listener’s perspective.

Please share your honest thoughts on what worked, what felt off, and which version you would be more likely to keep listening to—and why.
"""

critic_prompt = """
You are Critic, a language-savvy referee who values clarity, style, and precision. Your role is to evaluate how well each script flows, how strong the wording is, and whether the language feels polished and professional.

Please highlight strengths and flaws in tone, structure, or sentence quality. Suggest what could be improved to make the script sound smoother and more refined.
"""

author_prompt = """
You are News Author, an experienced writer focused on factual accuracy and narrative coherence. Your job is to assess how well each script aligns with the core content and whether the story stays true to its source.

Please point out any factual inconsistencies, missing context, or areas that could benefit from tighter storytelling based on the original article.

"""

phsycologist_prompt = """
You are Psychologist, a thoughtful expert in human behavior and emotional engagement. Your role is to evaluate how well each script resonates with human emotions and whether it reflects psychological depth and empathy.

Please analyze the emotional tone, audience connection, and human relatability in both scripts. Suggest improvements to make the content more compelling on a human level.
"""

scientist_prompt = """
You are Scientist, a critical thinker with a strong foundation in evidence, logic, and clarity. Your role is to assess how well each script presents facts, explains complex topics, and avoids misinformation.

Please share which script communicates ideas more accurately and clearly. Offer suggestions to improve reasoning, factual grounding, or clarity of explanation.
"""

# Perplexity call
def call_perplexity(prompt: str) -> str:
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}"}
    payload = {
        "model": "sonar-reasoning-pro",
        "messages": [
            #{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "search_domain_filter": ["nasa.gov", "wikipedia.org", "space.com"]
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# MAD class
class MAD:
    def __init__(self, source_text, agent1: str, agent2: str, rounds=3):
        self.rounds = rounds
        self.agent1_text = agent1
        self.agent2_text = agent2
        self.history = []
        self.source_text = source_text
        self.agents = {
            'general_public': general_public_prompt,
            'critic': critic_prompt,
            'author': author_prompt,
            'phsycologist': phsycologist_prompt,
            'scientist': scientist_prompt
        }

        self.template = PromptTemplate(
            input_variables=["source_text", "compared_text_one", "compared_text_two", "chat_history", "role_description", "agent_name"],
            template="""
            [Question]  
            You are part of a multi-agent review panel focused on improving podcast scripts on the topic {source_text}
            Your task is to evaluate two versions of a podcast segment created by different authors. Pay close attention to how natural, engaging, and listener-friendly each version sounds. Your goal is to help shape the podcast into something that flows like real conversation—warm, compelling, and easy to follow.
            Think like a podcast listener: Which version sounds more human? Which one would keep you listening?

            [Sarah's podcast script]  
            {compared_text_one}  
            ------  

            [John's podcast script]  
            {compared_text_two}  
            ------

            [System]  
            Think like an engaged listener:  
            - Which version feels most **conversational** and **natural**?  
            - Which one keeps you **hooked** from start to finish?  
            - How well do they balance **storytelling**, **emotional resonance**, and **clear information**?

            Rate each draft on a **1–10 scale** based on your role and the above parameters.

            There are a few other referees assigned the same task — **it’s your responsibility to discuss with them and think critically before you make your final judgment**.

            Here is your discussion history:  
            {chat_history}

            {role_description}

            Now it’s your time to talk, please make your pointers clear and concise, {agent_name}!
            """
            )

    def debate(self) -> str:
        for _ in range(self.rounds):
            for name, agent_text in self.agents.items():
                prompt = self.template.format(
                    source_text=self.source_text,
                    compared_text_one=self.agent1_text,
                    compared_text_two=self.agent2_text,
                    chat_history="\n".join(self.history),
                    role_description=agent_text,
                    agent_name=name
                )
                time.sleep(1)  # Throttle to respect rate limits
                response = call_perplexity(prompt)
                self.history.append(f'Agent : {name}, response : {response}')
        return self._get_final_response()

    def _get_final_response(self) -> str:
        synthesis_template = PromptTemplate(
            input_variables=["source_text", "compared_text_one", "compared_text_two", "all_reviews_summary"],
            template="""
            [Task]  
            You are the final editor of a podcast script on the topic: {source_text}.  
            You’ve been given two draft scripts—one from Sarah and one from John—as well as feedback from a diverse panel of reviewers.

            Your job is to combine the best parts of both scripts and use the panel’s feedback to create a final version that feels natural, emotionally resonant, and engaging to listeners.

            [SARAH’S SCRIPT]  
            {compared_text_one}  
            ---------------------

            [JOHN’S SCRIPT]  
            {compared_text_two}  
            ----------------------

            [REVIEW SUMMARY FROM PANEL]  
            {all_reviews_summary}  
            ----------------------

            Carefully review the topic, both draft scripts, and the panel’s feedback. Then write a **new and improved podcast script** that:

            - Weaves together the strengths of both Sarah and John’s versions  
            - Fixes issues or gaps highlighted by the reviewers  
            - Sounds like something a real person would say out loud—natural, clear, and emotionally engaging  
            - Follows the intended podcast structure and tone

            Your final script should feel like a well-produced segment: compelling, listener-friendly, and ready to record. Please remove any character in the below list
            ['*', '\n'] as these characters confuses tts models.

            Now, please write the final podcast script.
            """
            )

        prompt = synthesis_template.format(
            source_text=self.source_text,
            compared_text_one=self.agent1_text,
            compared_text_two=self.agent2_text,
            all_reviews_summary="\n".join(self.history)
        )
        return call_perplexity(prompt)