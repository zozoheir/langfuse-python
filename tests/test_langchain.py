import os
from langchain.llms import OpenAI
from langchain.chains import LLMChain, SimpleSequentialChain, RetrievalQA
from langchain.prompts import PromptTemplate
from langfuse.callback import CallbackHandler
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.agents import AgentType, initialize_agent, load_tools


# @pytest.mark.asyncio
def test_callback_simple_chain():
    handler = CallbackHandler("pk-lf-1234567890", "sk-lf-1234567890", "http://localhost:3000")

    llm = OpenAI(openai_api_key=os.environ.get("OPENAPI_KEY"))
    template = """You are a playwright. Given the title of play, it is your job to write a synopsis for that title.
        Title: {title}
        Playwright: This is a synopsis for the above play:"""

    prompt_template = PromptTemplate(input_variables=["title"], template=template)
    synopsis_chain = LLMChain(llm=llm, prompt=prompt_template)

    review = synopsis_chain.run("Tragedy at sunset on the beach", callbacks=[handler])
    handler.langfuse.flush()

    print("output variable: ", review)


# @pytest.mark.asyncio
def test_callback_sequential_chain():
    handler = CallbackHandler("pk-lf-1234567890", "sk-lf-1234567890", "http://localhost:3000")

    llm = OpenAI(openai_api_key=os.environ.get("OPENAPI_KEY"))
    template = """You are a playwright. Given the title of play, it is your job to write a synopsis for that title.
        Title: {title}
        Playwright: This is a synopsis for the above play:"""

    prompt_template = PromptTemplate(input_variables=["title"], template=template)
    synopsis_chain = LLMChain(llm=llm, prompt=prompt_template)

    template = """You are a play critic from the New York Times. Given the synopsis of play, it is your job to write a review for that play.

        Play Synopsis:
        {synopsis}
        Review from a New York Times play critic of the above play:"""
    prompt_template = PromptTemplate(input_variables=["synopsis"], template=template)
    review_chain = LLMChain(llm=llm, prompt=prompt_template)

    overall_chain = SimpleSequentialChain(
        chains=[synopsis_chain, review_chain],
    )
    review = overall_chain.run("Tragedy at sunset on the beach", callbacks=[handler])

    print(review)
    print(handler.langfuse.future_store.futures)
    handler.langfuse.flush()
    print("output variable: ", review)


def test_callback_retriever():
    handler = CallbackHandler("pk-lf-1234567890", "sk-lf-1234567890", "http://localhost:3000")

    loader = TextLoader("./static/state_of_the_union.txt", encoding="utf8")
    llm = OpenAI(openai_api_key=os.environ.get("OPENAPI_KEY"))

    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get("OPENAPI_KEY"))
    docsearch = Chroma.from_documents(texts, embeddings)

    query = "What did the president say about Ketanji Brown Jackson"

    chain = RetrievalQA.from_chain_type(
        llm,
        retriever=docsearch.as_retriever(),
    )

    result = chain.run(query, callbacks=[handler])

    handler.langfuse.flush()

    print("output variable: ", result)


def test_callback_simple_llm():
    handler = CallbackHandler("pk-lf-1234567890", "sk-lf-1234567890", "http://localhost:3000")

    llm = OpenAI(openai_api_key=os.environ.get("OPENAPI_KEY"))

    text = "What would be a good company name for a company that makes colorful socks?"

    result = llm.predict(text, callbacks=[handler])

    handler.langfuse.flush()

    print("output variable: ", result)


def test_callback_simple_llm_chat():
    handler = CallbackHandler("pk-lf-1234567890", "sk-lf-1234567890", "http://localhost:3000")

    llm = OpenAI(openai_api_key=os.environ.get("OPENAPI_KEY"))

    tools = load_tools(["serpapi", "llm-math"], llm=llm)

    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

    result = agent.run("Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?", callbacks=[handler])

    handler.langfuse.flush()

    print("output variable: ", result)