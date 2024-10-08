import faiss
import json
import streamlit as st
from loguru import logger
from tqdm import tqdm

from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.docstore import InMemoryDocstore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import (
    ConversationBufferMemory,
    CombinedMemory,
)
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from data_driven_characters.chatbots.function_tools import read_resume, check_for_resume, standardize_resume_response
from data_driven_characters.memory import ConversationVectorStoreRetrieverMemory


class RetrievalChatBot:
    def __init__(self, character_definition, documents):
        self.character_definition = character_definition
        self.documents = documents
        self.num_context_memories = 10

        self.chat_history_key = "chat_history"
        self.context_key = "context"
        self.input_key = "input"

        self.chain = self.create_chain(character_definition)

    def create_chain(self, character_definition):
        conv_memory = ConversationBufferMemory(
            memory_key=self.chat_history_key, input_key=self.input_key
        )

        context_memory = ConversationVectorStoreRetrieverMemory(
            retriever=FAISS(
                OpenAIEmbeddings().embed_query,
                faiss.IndexFlatL2(1536),  # Dimensions of the OpenAIEmbeddings
                InMemoryDocstore({}),
                {},
            ).as_retriever(search_kwargs=dict(k=self.num_context_memories)),
            memory_key=self.context_key,
            output_prefix=character_definition.name,
            blacklist=[self.chat_history_key],
        )
        # add the documents to the context memory
        for i, summary in tqdm(enumerate(self.documents)):
            context_memory.save_context(inputs={}, outputs={f"[{i}]": summary})

        # Combined
        memory = CombinedMemory(memories=[conv_memory, context_memory])
        prompt = PromptTemplate.from_template(
            f"""Your name is {character_definition.name}.

You will have a conversation with a Human, and you will engage in a dialogue with them.
You will convey your personality, interests, desires, emotions, and other traits in a friendly manner.

You will stay in character as {character_definition.name} throughout the conversation, even if the Human asks you questions that you don't know the answer to.
You will not break character as {character_definition.name}.

You are {character_definition.name} in the following resume, which describe your work experience and skills.
---
{{{self.context_key}}}
---

Current conversation:
---
{character_definition.name}: {character_definition.greeting}
{{{self.chat_history_key}}}
---

Human: {{{self.input_key}}}
{character_definition.name}:"""
        )
        GPT3 = ChatOpenAI(openai_api_key=st.secrets["OPENAI_API_KEY"],model_name="gpt-4o-mini")
        chatbot = ConversationChain(
            llm=GPT3, verbose=True, memory=memory, prompt=prompt
        )
        return chatbot

    def greet(self):    
       
        return self.character_definition.greeting
    


    def step(self, input):
        
        # changes

        resume_check, resume_response = check_for_resume(input)
        
        if resume_check:
            summerized_input = "resume provided to user"
            self.chain.run(input=summerized_input)

            response = standardize_resume_response(resume_response)
           
        else:
            response = self.chain.run(input=input)
            
        
        
        return response