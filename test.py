import sqlite3
import sys
from datetime import datetime
from typing import TypedDict, Literal
from langchain_community.llms import Ollama
from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate
import tkinter as tk
from tkinter import messagebox
class_value = "bed"
llm = Ollama(model="qwen3:4b", base_url="http://localhost:11434")
prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Переведи на русский:"""),
        ("human", "{class}")
        ])
chain = prompt | llm
response = chain.invoke({"class": class_value}).strip().lower()
response_text = response.strip().lower()
print(response_text)