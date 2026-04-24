from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate

class Agent:
    def __init__(self):
        self.llm = Ollama(model="qwen3:4b", base_url="http://localhost:11434")

    def category_detect(self, cls):
        prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Определите категорию объекта на аэродроме («разрешенный» или «посторонний»). В качестве результата выведи только название категории без обоснования, укажи "разрешённый" или "посторонний".
        Объект относится к разрешенной категории, если это одно из следующего:
        - Воздушное судно
        - Обслуживающий персонал
        - Специальная техника"""),
        ("human", "{class}")
        ])
        chain = prompt | self.llm
        response = chain.invoke({"class": cls}).strip().lower()
        response_text = response.strip().lower()
        return response_text
    
    def class_name_translated(self, cls):
        prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Переведи на русский:"""),
        ("human", "{class}")
        ])
        chain = prompt | self.llm
        response = chain.invoke({"class": cls}).strip().lower()
        translated_class = response.strip().lower()
        return translated_class