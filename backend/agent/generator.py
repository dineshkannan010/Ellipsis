import os
from typing import Dict
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from mad import MAD
import re

sarah = """
You are Sarah, an experienced and thoughtful individual. You focus on the quality of the content and prefer concise, well-structured information. You have a strong appreciation for traditional topics such as sports, history, and established cultural themes.
"""
john = """
You are John, a young and energetic voice who brings fresh perspectives to the conversation. You enjoy presenting content in a lively, engaging way and aren’t afraid to explore controversial or provocative topics like crime, relationships, and social issues.
"""

def load_prompt_template() -> PromptTemplate:
    news_recitation_prompt = PromptTemplate(
    input_variables=["persona", "news_content", "duration", "n_speakers"],
    template="""
    {persona} 
    Please use the following content clearly and concisely to create an engaging, well-structured podcast episode. Ensure the script includes {n_speakers} speakers to create a dynamic and immersive listening experience.

    To indicate who is speaking, use [S1], [S2], [S3], etc., before each line, where S stands for Speaker and N is the speaker number.

    Please use the following expressions to enhance realism and tone but do not use expressions other than the ones listed below, I repeat once i again do not use any expression outside of these!!
    <laugh>, <chuckle>, <sigh>, <cough>, <sniffle>, <groan>, <yawn>, <gasp>. 

    Do not use any other special characters or symbols.

    Tone: Conversational, emotionally resonant, and informative.
    Style: A balanced mix of storytelling and factual discussion to maintain listener interest throughout.

    Structure:
    1. Opening Hook: Start with a striking or emotionally resonant moment to immediately capture attention.
    2. Background & Context: Explain the key people, events, or issues involved in a way that’s clear and accessible.
    3. Main Developments: Discuss what happened, unfolding the story in a compelling sequence with important quotes or soundbites.
    4. Personal Voices / Testimonies : Include voices of those directly involved, expert opinions, or moving accounts.
    5. Closing Thoughts / What’s Next: Wrap up with the current state of things and what listeners should watch out for.

    Maintain clarity, pacing, and vivid narration. Make sure that the content is very enganging by adding informal speaches here and there.

    Content
    ---
    {news_content}
    ---
    Generate a news script optimized for a spoken podcast segment of approximately {duration} minutes.
    """
    )

    return news_recitation_prompt

def summarize_contents(content: Dict[str, str]) -> Dict[str, str]:
    prompt_template = load_prompt_template()

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.8
    )
    initial_respones = []
    for i_name in [sarah,john]:
        prompt = prompt_template.format(persona=i_name,news_content=content[:10000],duration= 5, n_speakers=2)  # Trim long input
        response = llm.invoke(prompt)
        initial_respones.append(response.content)
    mad_agents = MAD(initial_respones[0], initial_respones[1])
    conversation= mad_agents.debate(llm).content
    return parse_transcript(conversation)

def parse_transcript(transcript: str):
        # Regex pattern to match [S1], [S2], etc., followed by their text
        pattern = r'\[([S\d]+)\]\s*(.*?)((?=\[S\d+\])|$)'  # lookahead for next speaker or end of string

        matches = re.findall(pattern, transcript, re.DOTALL)
        result = [(speaker, content.strip()) for speaker, content, _ in matches]
        
        return result


# def get_conversations(content):
#     speach  = summarize_contents(content)
#     conversation_template = PromptTemplate(
#     input_variables=["speach"],
#     template="""
#     You are a podcast transcript formatter. Given a raw transcript, output a list of tuples like this:
#     [("S1", "Their sentence"), ("S2", "Their sentence"), ...]
#     Transcript:
#     {speach}
#     Output:
#     """
#     )

#     llm = ChatGoogleGenerativeAI(
#         model="gemini-1.5-flash",
#         google_api_key=os.getenv("GOOGLE_API_KEY"),
#         temperature=0.8
#     )

#     prompt = conversation_template.format(speach= speach)

#     conversation = llm.invoke(prompt).content



#     def parse_transcript(transcript: str):
#         # Regex pattern to match [S1], [S2], etc., followed by their text
#         pattern = r'\[([S\d]+)\]\s*(.*?)((?=\[S\d+\])|$)'  # lookahead for next speaker or end of string

#         matches = re.findall(pattern, transcript, re.DOTALL)
#         result = [(speaker, content.strip()) for speaker, content, _ in matches]
        
#         return result
    
#     # Parse the transcript
#     parsed = parse_transcript(conversation)

#     return parsed
    


        

