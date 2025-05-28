import os
import re
import requests
from typing import Dict
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from .mad import MAD

load_dotenv()
from flask_sse import sse

sarah = """
You are Sarah, an experienced and thoughtful individual. You focus on the quality of the content and prefer concise, well-structured information. You have a strong appreciation for traditional topics such as sports, history, and established cultural themes.
"""
john = """
You are John, a young and energetic voice who brings fresh perspectives to the conversation. You enjoy presenting content in a lively, engaging way and aren’t afraid to explore controversial or provocative topics like crime, relationships, and social issues.
"""

def load_prompt_template() -> PromptTemplate:
    news_recitation_prompt = PromptTemplate(
    input_variables=["persona", "content", "duration", "n_speakers"],
    template="""
    {persona} 
    Please come up with a clear, consice and an engaging, well-structured script for a podcast episode on the topic `{content}` approximately {duration} minuites long. Ensure the script includes {n_speakers} speakers to create a dynamic and immersive listening experience.

    To indicate who is speaking, use [S1], [S2], [S3], etc., before each line, where S stands for Speaker and N is the speaker number. 

    Please use the following expressions to enhance realism and tone. 
    <laugh>, <chuckle>, <sigh>, <cough>, <sniffle>, <groan>, <yawn>, <gasp>. 

    Do not use any other special characters or symbols.

    Tone: Speak naturally and informally, like a close friend explaining something fascinating. Make it warm, conversational, and emotionally engaging, but still clear and informative.

    Style: Use a mix of storytelling and accessible facts. Include rhetorical questions, contractions, and emotional moments. Feel free to add brief pauses, small asides, or reflective thoughts that sound like how real people talk in podcasts. 
    
    Structure:
    1. Opening Hook: Start with a striking or emotionally resonant moment to immediately capture attention.
    2. Background & Context: Explain the key people, events, or issues involved in a way that’s clear and accessible.
    3. Main Developments: Discuss what happened, unfolding the story in a compelling sequence with important quotes or soundbites.
    4. Personal Voices / Testimonies: Include voices of those directly involved, expert opinions, or moving accounts.
    5. Closing Thoughts / What’s Next: Wrap up with the current state of things and what listeners should watch out for.

    Voice & Delivery:
    - Use contractions and informal phrasing to reflect natural human speech.
    - Ask rhetorical questions occasionally to keep listeners engaged.
    - Refer directly to the listener with phrases like “you might be wondering” or “let’s unpack that.”
    - Avoid overly formal or robotic expressions.
    - Use emotional cues, sensory descriptions, and conversational transitions like “anyway,” “but here’s the twist,” or “let’s back up for a second.”
    - Imagine this will be read aloud by podcast hosts with distinct personalities—inject personality, warmth, and realism.
    """
    )

    return news_recitation_prompt

def call_perplexity(prompt: str) -> str:
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}"}
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "search_domain_filter": [
            "nasa.gov",
            "wikipedia.org",
            "space.com"
        ],
        "temperature" : 0.7
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Summarization logic
def summarize_contents(content: Dict[str, str], sse=None) -> Dict[str, str]:
    prompt_template = load_prompt_template()
    initial_responses = []
    for persona in [sarah, john]:
        prompt = prompt_template.format(
            persona=persona,
            content=content,  # Trim if needed
            duration=5,
            n_speakers=2
        )
        
        reply = call_perplexity(prompt)
        initial_responses.append(reply)

    # print(f"Total initial response: {initial_respones}")
    # print(f"initial response 0: {initial_respones[0]}")
    
    # print(f"\n initial response 1: {initial_respones[1]}")

    if sse:
        sse.publish({"persona": "Sarah", "response": initial_responses[0]}, type='persona')
        sse.publish({"persona": "John", "response": initial_responses[1]}, type='persona')

    # Create a debate between the two personas
    mad_agents = MAD(content, initial_responses[0], initial_responses[1])
    
    if sse:
        sse.publish({"status": "mad_started"}, type='status')

    conversation = mad_agents.debate()
    return initial_responses, parse_transcript(conversation)

# Transcript parsing
def parse_transcript(transcript: str):
    # Match speaker tags like [S1] or [S2]: followed by content
    pattern = r'\[(S\d+)\]:?\s*(.*?)((?=\[S\d+\])|$)'
    matches = re.findall(pattern, transcript, re.DOTALL)
    
    cleaned = []
    for speaker, content, _ in matches:
        # Remove asterisks and any [0-9] tags inside content
        content = content.strip()
        content = content.replace("*", "")
        content = re.sub(r'\[\d+\]', '', content)  # remove tags like [1], [23], etc.
        cleaned.append((speaker, content.strip()))
    
    return cleaned


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
    


        

