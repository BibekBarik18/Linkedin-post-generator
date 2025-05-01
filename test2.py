import os
from openai import OpenAI
from duckduckgo_search import DDGS
import arxiv
import streamlit as st

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=st.secrets["openrouter"]["api_key"],
)

def sizeof(length):
    if length == "Short":
        return "1 to 5 lines"
    if length == "Medium":
        return "6 to 10 lines"
    if length == "Long":
        return "11 to 15 lines"

def search_ddg(query: str, max_results: int = 3) -> str:
    """Fetch DuckDuckGo search results."""
    with DDGS() as ddgs:
        results = []
        for result in ddgs.text(query, max_results=max_results):
            results.append(f"- {result['title']}: {result['body']} (Source: {result['href']})")
        return "\n".join(results) if results else "No results found."
    
def search_arxiv(query: str, max_results: int = 3) -> str:
    """Search arXiv for recent papers using the arxiv.py library."""
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    formatted_results = []
    for paper in client.results(search):
        formatted_results.append(
            f"- **{paper.title}** ({paper.published.year})\n"
            f"  Authors: {', '.join(author.name for author in paper.authors)}\n"
            f"  Abstract: {paper.summary}\n"
            f"  URL: {paper.entry_id}"
        )
    return "\n\n".join(formatted_results) if formatted_results else "No papers found."

def generate_posts(tag, topic, length, tone, news, research, messages, modify_index=None):
    len_str = sizeof(length)
    
    # If we're modifying an existing post, include it in the prompt
    if modify_index is not None and 0 <= modify_index < len(messages):
        original_post = messages[modify_index]['content']
        modification_prompt = f"\n\nOriginal Post to Modify:\n{original_post}\n\nPlease update this post with the following changes:"
    else:
        modification_prompt = ""
    
    if news and research:
        search_results = search_ddg(f"{topic} site:news.google.com 2024", max_results=3)
        papers = search_arxiv(topic)
        prompt = (
            f'''Analyze the following information and generate an engaging description for a LinkedIn post.{modification_prompt}
            
            1) Topic={topic}
            2) Length={len_str}
            3) Tone={tone}
            4) Tag={tag}
            **Latest News (2024):**
            {search_results}

            **Relevant Research Papers:**
            {papers}

            Task:
            1. Summarize key developments from the news.
            2. Highlight research insights.
            3. Compare trends between academia and industry.
            4. Cite sources where applicable.
            Add emojis and hashtags where applicable.
            Start at a new line where ever necessary make it look more authentic.
            '''
        )
    elif news:
        search_results = search_ddg(f"{topic} site:news.google.com 2024", max_results=3)
        prompt = (
            f"""Use the latest DuckDuckGo search results below to generate an engaging LinkedIn post description.{modification_prompt}
            Search Query: {topic}
            Length={len_str}
            Tone={tone}
            Tag={tag}
            Latest Web Results:
            {search_results}
            Provide sources wherever necessary.
            Add emojis and hashtags where applicable.
            Start at a new line where ever necessary make it look more authentic.
            """
        )
    elif research:
        papers = search_arxiv(topic)
        prompt = (
            f'''Use the following research papers to generate an engaging LinkedIn post description.{modification_prompt}

            1) Topic={topic}
            2) Length={len_str}
            3) Tone={tone}
            4) Tag={tag}
            Relevant Papers:
            {papers}  
            Cite paper titles and authors where applicable.
            Add emojis and hashtags where applicable.
            Start at a new line where ever necessary make it look more authentic.
            '''
        )
    else:
        prompt = (
            f'''Generate an engaging description for a LinkedIn post using the below information.{modification_prompt}

            1) Topic={topic}
            2) Length={len_str}
            3) Tone={tone}
            4) Tag={tag}
            Add emojis and hashtags where applicable.
            Start at a new line where ever necessary make it look more authentic.
            '''
        )
    
    messages = [
        {
            "role": "system",
            "content": "You are an intelligent LinkedIn post generator that creates engaging posts. When asked to modify existing posts, preserve the core message while incorporating requested changes."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    completion = client.chat.completions.create(
        model="meta-llama/llama-3.3-70b-instruct:free",
        messages=messages
    )
    return completion.choices[0].message.content