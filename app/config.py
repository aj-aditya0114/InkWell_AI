"""Application configuration and shared LLM setup."""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Shared LLM used by router, planner, workers, and image planner.
llm = ChatOpenAI(model="gpt-4.1-mini")
