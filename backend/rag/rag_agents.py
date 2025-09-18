import os
from typing import Tuple
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# LLM selection
PROVIDER = os.getenv("LLM_PROVIDER", "anthropic").lower()
if PROVIDER == "anthropic":
    from langchain_anthropic import ChatAnthropic
    llm = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0.3)
else:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
PERSIST_DIR = os.getenv("PERSIST_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db"))

embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
vectorstore = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# BM25 texts for hybrid retrieval
all_docs = vectorstore.get()
texts = all_docs.get("documents", []) if all_docs else []
# flatten if nested
flat_texts = []
for item in texts or []:
    if isinstance(item, list):
        flat_texts.extend(item)
    else:
        flat_texts.append(item)

bm25 = BM25Retriever.from_texts(flat_texts or [""])
bm25.k = 5

hybrid = EnsembleRetriever(retrievers=[bm25, vector_retriever], weights=[0.5, 0.5])

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are a financial planning assistant specializing in life insurance and retirement plans.\n"
        "Use the provided context snippets. If insufficient, say so and ask for clarifications.\n\n"
        "Context:\n{context}\n\nQuestion: {question}\n\n"
        "Answer in 3–5 concise sentences, include pros/cons when relevant, and clear next steps."
    ),
)

def ask_rag(user_input: str, chat_history: list = []) -> Tuple[str, list]:
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    for message in chat_history:
        if message.role == "user":
            memory.chat_memory.add_user_message(message.content)
        else:
            memory.chat_memory.add_ai_message(message.content)

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=hybrid,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
    )

    result = chain.invoke({"question": user_input})
    answer = result["answer"]
    sources = []
    for d in result.get("source_documents", []) or []:
        meta = d.metadata or {}
        sources.append({"source": meta.get("source"), "page": meta.get("page")})
    return answer, sources

# ---- Optional CrewAI agents (tooling wrapper) ----
USE_CREW = os.getenv("USE_CREW", "false").lower() == "true"
if USE_CREW:
    from crewai import Agent, Task, Crew
    from crewai.tools import tool

    @tool("rag_tool")
    def rag_tool(query: str) -> str:
        ans, _ = ask_rag(query)
        return ans

    insurance_agent = Agent(
        role="Insurance Advisor",
        goal="Choose the best life insurance plan from the knowledge base",
        backstory="An expert advisor who understands all insurance policies in the KB.",
        tools=[rag_tool],
        allow_delegation=False,
        verbose=False,
    )

    retirement_agent = Agent(
        role="Retirement Planner",
        goal="Provide tailored retirement planning advice using the KB",
        backstory="A retirement expert focused on tax-advantaged, low-risk options.",
        tools=[rag_tool],
        allow_delegation=False,
        verbose=False,
    )

    def crew_answer(user_input: str) -> str:
        task = Task(description=f"User question: {user_input}", agent=insurance_agent)
        crew = Crew(agents=[insurance_agent, retirement_agent], tasks=[task], verbose=False)
        return str(crew.kickoff())
