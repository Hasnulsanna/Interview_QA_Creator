from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.text_splitter import TokenTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFaceEndpoint
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_text_splitters import TokenTextSplitter
from transformers import AutoTokenizer

import os
from dotenv import load_dotenv
from src.prompt import *


# Huggingface  authentication
load_dotenv()
HUGGINFACE_API_KEY = os.getenv("HUGGINFACE_API_KEY")
os.environ["HUGGINFACE_API_KEY"] = HUGGINFACE_API_KEY


def file_processing(file_path):

    # Load data from PDF
    loader = PyPDFLoader(file_path)
    data = loader.load()

    question_gen = ''

    for page in data:
        question_gen += page.page_content
        

    #use llm for the context remember instead of chunk_overlap
    hf_model = "mistralai/Mistral-7B-Instruct-v0.1"
    tokenizer = AutoTokenizer.from_pretrained(hf_model)

    splitter_ques_gen = TokenTextSplitter.from_huggingface_tokenizer(
        tokenizer,
        chunk_size = 10000,
        chunk_overlap = 200
    )
 

    chunks_ques_gen = splitter_ques_gen.split_text(question_gen)

    document_ques_gen = [Document(page_content=t) for t in chunks_ques_gen]

    # do the chunking prev was a demo 
    splitter_ans_gen = TokenTextSplitter.from_huggingface_tokenizer(
        tokenizer,
        chunk_size = 1000,
        chunk_overlap = 100
    )

    document_answer_gen = splitter_ans_gen.split_documents(
        document_ques_gen
    )

    return document_ques_gen, document_answer_gen



def llm_pipeline(file_path):

    document_ques_gen, document_answer_gen = file_processing(file_path)


    hf_model = "mistralai/Mistral-7B-Instruct-v0.1"

    llm_ques_gen_pipeline = HuggingFaceEndpoint(
        endpoint_url=f"https://api-inference.huggingface.co/models/{hf_model}",
        huggingfacehub_api_token=HUGGINFACE_API_KEY,
        temperature=0.3,  # Controls randomness
        model_kwargs={"max_length": 512}
    )

   

    PROMPT_QUESTIONS = PromptTemplate(template=prompt_template, input_variables=["text"])

    

    REFINE_PROMPT_QUESTIONS = PromptTemplate(
        input_variables=["existing_answer", "text"],
        template=refine_template,
    )

    ques_gen_chain = load_summarize_chain(llm = llm_ques_gen_pipeline, 
                                            chain_type = "refine", 
                                            verbose = True, 
                                            question_prompt=PROMPT_QUESTIONS, 
                                            refine_prompt=REFINE_PROMPT_QUESTIONS)

    ques = ques_gen_chain.run(document_ques_gen)

    embeddings = HuggingFaceInferenceAPIEmbeddings(
        api_key=HUGGINFACE_API_KEY, model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


    vector_store = FAISS.from_documents(document_answer_gen, embeddings)

    ques_list = ques.split("\n")
    filtered_ques_list = [element for element in ques_list if element.endswith('?') or element.endswith('.')]

    answer_generation_chain = RetrievalQA.from_chain_type(llm=llm_ques_gen_pipeline, 
                                                chain_type="stuff", 
                                                retriever=vector_store.as_retriever())

    return answer_generation_chain, filtered_ques_list


