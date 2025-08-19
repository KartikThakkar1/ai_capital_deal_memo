import streamlit as st
from langchain_modules.assistant_qa import load_vector_store, build_qa_chain
from langchain_modules.generate_memos import (
    build_memo_chain,
    generate_investment_memo,
    generate_swot_analysis,
    generate_summary,
)
from langchain_community.chat_models import ChatOpenAI
import os

st.set_page_config(page_title="Deal Memo Assistant", layout="wide")

st.title("💼 Capital Deal Memo Assistant")

VECTOR_STORE_DIR = "vector_store/"
clients = [f for f in os.listdir(VECTOR_STORE_DIR) if os.path.isdir(os.path.join(VECTOR_STORE_DIR, f))]

client = st.selectbox("Select a client deal to work with:", clients)

# Load vector store and chains
vector_store = load_vector_store(os.path.join(VECTOR_STORE_DIR, client))
qa_chain = build_qa_chain(vector_store)
memo_chain = build_memo_chain(vector_store)
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

st.divider()

tab1, tab2, tab3 = st.tabs(["📤 Q&A Chat", "📝 Generate Memo", "🧠 Agent Prompt (coming soon)"])

with tab1:
    st.subheader("Ask a question about this client")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    chat_input = st.chat_input("Ask something...")

    if chat_input:
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": chat_input})

        # Build retriever-based context
        context_docs = vector_store.similarity_search(chat_input, k=4)
        context_text = "\n\n".join([doc.page_content for doc in context_docs])

        # Build prompt: instructions + context + conversation
        messages = [{"role": "system", "content": (
            "You are a financial analyst assistant. Answer the user's questions using the following context from documents.\n\n"
            f"{context_text}\n\nRespond clearly and concisely."
        )}]

        # Add chat history
        messages += st.session_state.chat_history

        # Get reply
        from langchain.chat_models import ChatOpenAI
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        response = llm.invoke(messages)

        # Append assistant reply
        st.session_state.chat_history.append({"role": "assistant", "content": response.content})

    # Display full conversation
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])


with tab2:
    st.subheader("Generate Insights")
    ticker = st.text_input("Stock ticker (optional)", value="")

    col1, col2, col3 = st.columns(3)

    if col1.button("Generate Investment Memo"):
        chunks = vector_store.similarity_search("all", k=1000)
        memo = generate_investment_memo(memo_chain, ticker=ticker or None, all_chunks=chunks, llm=llm)
        st.text_area("Investment Memo", memo, height=400)

    if col2.button("Generate SWOT Analysis"):
        swot = generate_swot_analysis(memo_chain)
        st.text_area("SWOT", swot, height=400)

    if col3.button("Generate Bullet Summary"):
        summary = generate_summary(memo_chain)
        st.text_area("Summary", summary, height=400)
