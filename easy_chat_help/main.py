from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from typing import Any, Dict, List, Union
from langchain.schema import AgentAction, AgentFinish, LLMResult

from fastapi import FastAPI, WebSocket
from starlette.middleware.cors import CORSMiddleware as CORSMiddleware
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.embeddings import OpenAIEmbeddings

import pickle
import numpy as np
import pandas as pd

from dotenv import load_dotenv

import os

from google.cloud import storage

####
from utilities import *
timer = Timer()
####


success = False
initial_try = True
current_dir = os.getcwd()
# move upwards in the directory tree
while not success:
    success = load_dotenv(".env")
    if not success:
        if initial_try:
            os.chdir("./backend")
            initial_try = False
        os.chdir("..")
        print("changed directory to",os.getcwd())
        if os.getcwd() == "/":
            print("could not find .env file")
            break
#change back to current directory
os.chdir(current_dir)


# Get environment variable
OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
ORGANIZATION_NAME = os.getenv("ORGANIZATION_NAME")
DATA_DEPTH_THRESHOLD = int(os.getenv("DATA_DEPTH_THRESHOLD"))

debug_env = False
if debug_env:
    print("ENV values", OPEN_AI_KEY,ORGANIZATION_NAME,DATA_DEPTH_THRESHOLD)

os.environ["OPENAI_API_KEY"] = OPEN_AI_KEY

########

# Set the path to the service account key in the environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "storage-key.json"

# Initialize the Storage client
storage_client = storage.Client()

all_ebbeddings_file_path = 'embeddings/all_embeddings.pkl'
all_ebbeddings_df_file_path = 'embeddings/all_embeddings_df.pkl'


def upload_blob(source_file_name, destination_blob_name, bucket_name="easychathelp"):
    """Uploads a file to the bucket."""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name} in bucket {bucket_name}.")

# test
# local_file_paths = [f"{all_ebbeddings_df_file_path}"]
# for file_path in local_file_paths:
#     destination_blob_name = f"chris/{all_ebbeddings_df_file_path}"
#     upload_blob(file_path, destination_blob_name)


def download_blob_to_memory(source_blob_name, bucket_name="easychathelp"):
    """Downloads a blob from the bucket into memory."""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob_data = blob.download_as_bytes()

    print(f"Blob {source_blob_name} downloaded into memory from bucket {bucket_name}.")

    return blob_data

import pickle

def download_and_load_pkl(source_blob_name, bucket_name="easychathelp"):
    """Downloads a pickle blob from the bucket into memory and loads it into a Python object."""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob_data = blob.download_as_bytes()

    print(f"Blob {source_blob_name} downloaded into memory from bucket {bucket_name}.")

    # Load the pickle data into a Python object
    object = pickle.loads(blob_data)

    return object


########


def simple_cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_embeddings_with_text(df, text):
    open_ai_embeddings = OpenAIEmbeddings()
    query_embedding = open_ai_embeddings.embed_query(text)
    df['similarities'] = df.embedding.apply(lambda x : simple_cosine_similarity(x, query_embedding))
    res = df.sort_values('similarities', ascending = False)
    return res

def search_embeddings_embedding(df, query_embedding):
    df['similarities'] = df.embedding.apply(lambda x : simple_cosine_similarity(x, query_embedding))
    res = df.sort_values('similarities', ascending = False)
    return res

def load_pkl(file_path,verbose=False):
    try:
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
            if verbose:
                print("Type:", type(data))
                print("Contents:", data)
            try:
                if verbose:
                    print("length:", len(data))
            except Exception as e:
                pass
            return data
    except FileNotFoundError:
        print("File not found.")
    except pickle.UnpicklingError:
        print("Unable to unpickle the file.")

def remove_duplicates_from_sorted_list(sorted_list):
    return [v for i, v in enumerate(sorted_list) if i == 0 or sorted_list[i-1] != v]


class WebsocketCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming. Only works with LLMs that support streaming."""
    def __init__(self, websocket):
        super().__init__()
        self.websocket = websocket
        self.current_response = ""

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        print("on_llm_start")
        """Run when LLM starts running."""

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        await self.websocket.send_json({"message": token})
        """Run on new LLM token. Only available when streaming is enabled."""
        self.current_response += token

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        # print("llm ending!",response)
        print("on_llm_end")
        await self.websocket.send_json({"type": "llm_end"})
        """Run when LLM ends running."""

    async def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when LLM errors."""

    async def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""

    async def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        # print("chain ending!",outputs)
        print("chain ending!")
        """Run when chain ends running."""

    async def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when chain errors."""

    async def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Run when tool starts running."""

    async def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Run when tool ends running."""

    async def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        print("tool error")
        """Run when tool errors."""

    async def on_text(self, text: str, **kwargs: Any) -> None:
        print("text! ontext")
        """Run on arbitrary text."""

    async def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        print("agent action!",action)
        """Run on agent action."""

    async def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Run on agent end."""
        print("agent ending!")
        await self.websocket.send_json({"type": "agent_end", "output": "Agent finished!"})

######### helper functions #########
def sanitize_string(s):
    return ''.join(c if c.isalnum() else '_' for c in s)

#########

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# main call
@app.websocket("/chat")
async def chat_with_bot(websocket: WebSocket):

    await websocket.accept()
    
    chat = ChatOpenAI(streaming=True, callbacks=[WebsocketCallbackHandler(websocket)], verbose=True, temperature=0.7)
    
    while True:
        incoming = await websocket.receive_json()
        # print(incoming)
        messages = incoming["messages"]
        chat_id = incoming["chat_id"]
        chat_id = "chris"
        # print("messages: ", messages)
        services_messages = []
        most_recent_message = messages[-1]["content"]


        for message in messages:
            if message["type"] == "human":
                services_messages.append(HumanMessage(content=message["content"]))
            else:
                services_messages.append(AIMessage(content=message["content"]))

        relevant_questions = ""
    
        # df = load_pkl(all_ebbeddings_df_file_path, verbose=True)
        timer.start()
        df = download_and_load_pkl(f"{chat_id}/{all_ebbeddings_df_file_path}", bucket_name="easychathelp")
        timer.stop()
        # TODO add way to create synthetic questions that are similar to the most recent message
        sorted_by_similarity_df = search_embeddings_with_text(df, most_recent_message)

        sorted_by_similarity_texts = sorted_by_similarity_df['content'].tolist()
        
        sorted_by_similarity_texts = sorted_by_similarity_texts[0:DATA_DEPTH_THRESHOLD]

        # print("sorted_by_similarity_texts: ", sorted_by_similarity_texts)
        sorted_by_similarity_texts_duplicates_removed = remove_duplicates_from_sorted_list(sorted_by_similarity_texts)
        
        # print("sorted_by_similarity_texts_duplicates_removed: ", sorted_by_similarity_texts_duplicates_removed)

        len_of_list = len(sorted_by_similarity_texts_duplicates_removed)
        for i in range(len(sorted_by_similarity_texts_duplicates_removed)):
            # check if last message is in the texts
            if i == len_of_list - 1:
                relevant_questions += f"{sorted_by_similarity_texts_duplicates_removed[i]}"
            else:
                relevant_questions += f"{sorted_by_similarity_texts_duplicates_removed[i]}\n\n"
        
        # print("relevant_questions: ", relevant_questions)

        system_string = f"""You are the official chatbot of {ORGANIZATION_NAME}
Recently {ORGANIZATION_NAME} and other people were interviewed about {ORGANIZATION_NAME} here is some of the questions they were asked and how they responded:
---- relevant questions ----
{relevant_questions}
---- end relevant questions ----

Use this to guide your conversation with the user. Answer the user questions very directly and professionally. If you don't know the answer, tell the user you don't know the answer and suggest they email chris at chriswywy@gmail.com
"""
        # we now have a list of messages, we can use this to build a conversation

        print(system_string)

        final_messages = []

        final_messages.append(SystemMessage(content=system_string))

        log_messages = [system_string]
        for message in messages:
            if message["type"] == "human":
                final_messages.append(HumanMessage(content=message["content"]))
                log_messages.append(message["content"])
            else:
                final_messages.append(AIMessage(content=message["content"]))
                log_messages.append(message["content"])

        # print("final_messages: ", final_messages[1:])

        # print("final_messages: ", final_messages)

        response = await chat.agenerate([final_messages])
        
        mod_most_recent_message = sanitize_string(most_recent_message)
        # logging can go here

        await websocket.send_json({"type": "llm_end"})
        await websocket.send_json({"done": True})



# main call
@app.websocket("/interview_training")
async def interview_training(websocket: WebSocket):

    await websocket.accept()
    
    chat = ChatOpenAI(streaming=True, callbacks=[WebsocketCallbackHandler(websocket)], verbose=True, temperature=0.7)
    
    await websocket.send_json({"type": "message", "message": "What would you like to be interviewed about?"})
    
    print("sent question")
    while True:
        incoming = await websocket.receive_json()
        print(incoming)
        messages = incoming["messages"]
        final_messages = []
        system_string = f"You are interviewing a person as them their name and what kind of questions they want to be asked. Then you interview them. Never repeat yourself and don't go down any rabbit holes."
        
        final_messages.append(SystemMessage(content=system_string))

        log_messages = [system_string]
        for message in messages:
            if message["type"] == "human":
                final_messages.append(HumanMessage(content=message["content"]))
                log_messages.append(message["content"])
            else:
                final_messages.append(AIMessage(content=message["content"]))
                log_messages.append(message["content"])

        response = await chat.agenerate([final_messages])

        # await websocket.send_json({"type": "question", "message": f"What is your name? {len(messages)}"})
        
