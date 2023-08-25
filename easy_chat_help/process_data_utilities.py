from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

import re
import hashlib
import shutil
import time
from langchain.text_splitter import RecursiveCharacterTextSplitter

from starlette.middleware.cors import CORSMiddleware as CORSMiddleware
from langchain.embeddings import OpenAIEmbeddings

from dotenv import load_dotenv

import os

import pickle

import pandas as pd
import numpy as np

import library

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader

from google.cloud import storage


load_dotenv(".env")

# Get environment variable
open_ai_key = os.getenv("OPEN_AI_KEY")

# print(value)



# Set the path to the service account key in the environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "storage-key.json"

# Initialize the Storage client
storage_client = storage.Client()


# state and embedding paths

all_ebbeddings_df_file_path = 'embeddings/all_embeddings_df.pkl'
all_interviews_file_path = 'state/all_interviews.pkl'
all_files_file_path = 'state/all_files.pkl'
interview_state_filename = f'state/interviews_state.pkl'
all_embeddings_filename = f'embeddings/all_embeddings.pkl'
files_state_filename = f'state/files_state.pkl'

#backups paths
embeddings_backups_folder = 'embeddings/backups/'
state_backups_folder = 'state/backups/'


os.environ["OPENAI_API_KEY"] = open_ai_key

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
    first = res.iloc[0].content
    return res

def remove_extra_newlines(text):
    # Remove all occurrences of \xa0 from the input string
    text = text.replace('\xa0', '')

    lines = text.split('\n')

    result = []
    for i, line in enumerate(lines):
        if i == 0:
            # handle first line separately
            result.append(line.rstrip())
        else:
            if lines[i-1].strip() == '' and line.strip() == '':
                # skip extra blank lines
                continue
            else:
                result.append(line.rstrip())
                # check if there are more than two consecutive newlines
                if i < len(lines) - 1 and lines[i+1].strip() == '':
                    if len(result) == 0 or result[-1].strip() != '':
                        result.append('')

    return '\n'.join(result)

def read_file(filepath):
    with open(filepath, 'r') as file:
        content = file.read()
    return content

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

def save_as_pickle(obj, file_path):
    # Open the file in binary mode and save the object as a pickle
    with open(file_path, "wb") as file:
        pickle.dump(obj, file)

    print("Object saved as a pickle file.")

def embed_text(text):
    embeddings = OpenAIEmbeddings()
    query_result = embeddings.embed_query(text)
    return query_result

def list_of_dicts_to_dataframe(lst, pkl_filename=None):
    df = pd.DataFrame(lst)
    df['id'] = range(1, len(df) + 1)
    df.set_index('id', inplace=True)
    print(df)
    if pkl_filename is not None:
        df.to_pickle(pkl_filename)
    return df

def add_interviews_to_library(interviews,
                                all_interviews_file_path=all_interviews_file_path,
                               verbose=False,
                               overwrite=False):
    """example data ["06-20-2023", 
     {
    "Can you tell me about your current professional role and what led you to this career path?": "I am a software architect. I work primarily with Python and creating programs that use AI integrated into them.",
    "Can you share with us a non-work related hobby or interest you have, and why it appeals to you?": "I really like gardening. I have a garden with many plants like raspberries, apple trees, blueberries, grapes, and many annuals like kale, collards, corn, beans, peas, arugula to name a few.",
    }
    ],"""
    # load interview pkl
    if os.path.exists(all_interviews_file_path):
        stored_interviews = load_pkl(all_interviews_file_path, verbose=verbose)
        if stored_interviews is None:
            stored_interviews = []
    else:
        stored_interviews = []

    for interview in interviews:
        stored_interviews.append(interview)
        
    #save interview pkl
    save_as_pickle(interviews, all_interviews_file_path)

    return stored_interviews, all_interviews_file_path


def parse_questions(question_string):
    # split the string based on "QuestionX: " or "QuestionX ", case insensitive
    question_list = re.split(r'question\s*\d+\s*[:\s]', question_string, flags=re.IGNORECASE)
    # remove empty strings
    question_list = [question.strip() for question in question_list if question.strip()]
    return question_list


def process_interviews(interviews, overwrite=False, 
                       ll_embeddings_filename=all_embeddings_filename, 
                       interview_state_filename=interview_state_filename):
    if os.path.exists(all_embeddings_filename):
        all_embeddings = pickle.load(open(all_embeddings_filename, 'rb'))
    else:
        # create it
        all_embeddings = []

    if os.path.exists(interview_state_filename):
        interview_state = pickle.load(open(interview_state_filename, 'rb'))
    else:
        # create it
        print("Creating new state for interviews")
        interview_state = {}

    # print(interview_state)
    for interview in interviews:
        print("processing interview: ", interview[0])
        data = interview[0].encode()  # .encode() converts str to bytes
        hash_object = hashlib.sha256(data)
        hex_dig = hash_object.hexdigest()      
        if hex_dig not in interview_state or overwrite:
            for key, value in interview[1].items():
                print(key, value)
                key_embedding = embed_text(key)
                value_embedding = embed_text(value)
                all_embeddings.append({"embedding": key_embedding, "content" : key + " " + value})
                all_embeddings.append({"embedding": value_embedding, "content" : key + " " + value})
            
            # save hash to not rerun again
            # interview_state[hex_dig] = interview

            interview_state[hex_dig] = True
            pickle.dump(interview_state, open(interview_state_filename, 'wb'))
            pickle.dump(all_embeddings, open(all_embeddings_filename, 'wb'))
        else:
            print("Already processed " + interview[0])
    return all_embeddings, interview_state


def process_files(files, overwrite=False,
                  all_embeddings_filename=all_embeddings_filename, 
                  files_state_filename=files_state_filename,
                  verbose=False,
                  chunk_size=512,
                  chunk_overlap=0):
    
    if os.path.exists(all_embeddings_filename):
        all_embeddings = pickle.load(open(all_embeddings_filename, 'rb'))
    else:
        # create it
        all_embeddings = []

    if os.path.exists(files_state_filename):
        files_state = pickle.load(open(files_state_filename, 'rb'))
    else:
        # create it
        print("Creating new state for files")
        files_state = {}

    # print(files_state)
    for file in files:
        print("processing file: ", file[0])
        if os.path.exists(file[1]):
            with open(file[1], 'rb') as f:
                bytes_of_file = f.read()
                if verbose:
                    print(type(bytes_of_file), bytes_of_file)
        elif os.path.exists("files/"+file[1]):
            with open("files/"+file[1], 'rb') as f:
                bytes_of_file = f.read()
                if verbose:
                    print(type(bytes_of_file), bytes_of_file)
        else:
            text_of_file = file[1]
            bytes_of_file = text_of_file.encode()  # .encode() converts str to bytes
            if verbose:
                print(type(bytes_of_file), bytes_of_file)
        hash_object = hashlib.sha256(bytes_of_file)
        hex_dig = hash_object.hexdigest()    
        text_of_file = bytes_of_file.decode('utf-8')  
        if hex_dig not in files_state or overwrite:
            chat = ChatOpenAI(temperature=1, max_tokens=256)
            # textsplit
            text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap  = chunk_overlap,
            length_function = len,
            )
            texts = text_splitter.split_text(text_of_file)
            print("texts",texts)
            for i in range(len(texts)):
                print()
                print()
                print(f"{i} :", texts[i])
                print()
                print()

                system_prompt = f"""You create questions with no preamble or debriefing statements. 
You never say something like oh yes I can do that or or any explanation you simply create the questions.
You always respond with the format:
Question 1: <question>
Question 2: <question>
Question 3: <question>
Rest of questions..."""

                topic_prompt = "The questions are likely about"
                if len(library.topics) == 0:
                    topic_prompt = ""
                else:
                    if len(library.topics) == 1:
                        topic_prompt = f" {library.topics[0]}."
                    else:
                        for i in range(len(library.topics)):
                            if i == len(library.topics) - 1:
                                topic_prompt += f"or {library.topics[i]}"
                            elif i == len(library.topics) - 2:
                                topic_prompt += f"or {library.topics[i]}. "
                            else:
                                topic_prompt += f"{library.topics[i]}, "
                print("topic_prompt", topic_prompt)

                prompt = f"""I am about to show you a piece of text. The piced of text is something that was just looked up to help answer a question. {topic_prompt}. Do not be overly specific to the context. One of the questions needs to be be super vague.

--- Text that is being used to answer a question ---
{texts[i]}
--- End of text that is being used to answer a question ---

Now come up with 5 questions that hypothetically could have been asked that may have prompted this text to be looked up.

Questions:"""
                messages = []
                messages.append(SystemMessage(content=system_prompt))
                messages.append(HumanMessage(content=prompt))
                llm_result = chat.generate([messages])
                result_text = llm_result.generations[-1][-1].text
                print()
                print()
                print("result_text\n\n", result_text)
                print()
                print()
                
                questions_parsed = parse_questions(result_text)

                answer_embedding = embed_text(texts[i])
                premable = "Some information about the topic: "
                all_embeddings.append({"embedding": answer_embedding, "content" : premable + texts[i]})
                for question in questions_parsed:
                    print("question", question)
                    question_embedding = embed_text(question)
                    all_embeddings.append({"embedding": question_embedding, "content" : premable + texts[i]})

            #back up the previous state and embeddings by copying them to a new file
            all_embeddings_backup_filename = "all_embeddings_" + str(time.time())
            files_state_backup_name = "file_state_backup_" + str(time.time())
            try:
                shutil.copyfile(all_embeddings_filename, embeddings_backups_folder + all_embeddings_backup_filename + ".bak")
                shutil.copyfile(files_state_filename, state_backups_folder + files_state_backup_name + ".bak")
            except Exception as e:
                print("Error backing up files", e)
            # save hash to not rerun again
            files_state[hex_dig] = True
            pickle.dump(files_state, open(files_state_filename, 'wb'))
            pickle.dump(all_embeddings, open(all_embeddings_filename, 'wb'))
        else:
            print("Already processed: ", file[0])
    return all_embeddings, files_state


# common workflow
def main(use_manual_library=True, verbose=False):
    if use_manual_library:
        interviews = library.interviews
        files = library.files
    else:
        interviews = load_pkl(all_interviews_file_path, verbose=verbose)
        files = load_pkl(all_files_file_path, verbose=verbose)

    # process interviews
    process_interviews(interviews)

    # process files
    process_files(files)

    # save all embeddings
    embeddings_loaded = load_pkl(all_embeddings_filename, verbose=verbose)
    list_of_dicts_to_dataframe(embeddings_loaded, pkl_filename=all_ebbeddings_df_file_path)


if __name__ == "__main__":
    # main(verbose=True)

    # test the embeddings
    embeddings_loaded = load_pkl(all_ebbeddings_df_file_path)

    for index, row in embeddings_loaded.iterrows():
        print(f"Index: {index}")
        print(f"Row data: \n{row}")
        print("-------------------")
    
    # res = search_embeddings_with_text(embeddings_loaded, "tell me about chris' programming skills")
    
    # print(res["content"].head(10).tolist())


    # ideas_from_parsed = [text[0] for text in parsed_texts]
    # parsed_texts_metadatas = [{"request":text[0], "answer":text[1]} for text in parsed_texts]
    # print("ideas_from_parsed: ", ideas_from_parsed)
    
    # embeddings = OpenAIEmbeddings()
    # faiss_db = FAISS.from_texts(ideas_from_parsed, embeddings, metadatas=parsed_texts_metadatas)

    # faiss_db.save_local("faiss_index")

    # faiss_db = FAISS.load_local("faiss_index", embeddings)

    # faiss_db.similarity_search
    # docs = faiss_db.similarity_search("a viral video for a beer company", k=10)
    # print("similarity search")

    # parsed_texts = load_pkl(f"run-{RUN_ID}/parsed_texts-{RUN_ID}.pkl")

    # embeddings = OpenAIEmbeddings()
    # faiss_db = FAISS.load_local("faiss_index", embeddings)

    # faiss_db.similarity_search
    # docs = faiss_db.similarity_search("a viral video for a beer company", k=5)
    # for doc in docs:
    #     print("---------------------\n\n")
    #     print(doc)
    #     print("---------------------\n\n")