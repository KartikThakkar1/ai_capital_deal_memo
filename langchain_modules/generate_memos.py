from langchain.chains import RetrievalQA, LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_modules.automation_tools import fetch_stock_data

def build_memo_chain(vector_store):
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_store.as_retriever(),
        return_source_documents=False
    )

def generate_investment_memo(qa_chain, ticker=None, all_chunks=None, llm=None):
    stock_text = ""
    if ticker:
        data = fetch_stock_data(ticker)
        if "error" not in data:
            stock_text = (
                f"\n\nHere is the latest market data to include:\n"
                f"- Company Name: {data.get('name')}\n"
                f"- Sector: {data.get('sector')}, Industry: {data.get('industry')}\n"
                f"- Current Price: {data.get('current_price')}\n"
                f"- Market Cap: {data.get('market_cap')}\n"
                f"- P/E Ratio: {data.get('pe_ratio')}\n"
                f"- Beta: {data.get('beta')}\n"
            )

    prompt = (
        "You are an investment analyst. Based on the available documents, generate a one-page investment memo.\n\n"
        "Include:\n"
        "- Company name and industry\n"
        "- Executive summary\n"
        "- Financial highlights\n"
        "- Key risks\n"
        "- Suggested financing type\n"
        "- Conclusion\n"
        f"{stock_text}"
    )
    # sometimes the llm won't generate the full memo stating it does not have enough information. This is probably happening because of using RetrievalQA chain
    # which only gives a handful of top chunks to be loaded. 
    # step 1: Try using the retriever-based QA chain
    response = qa_chain.run(prompt)

    # therefore, for times when such a case occur, using LLMChain instead. For this, i create a new prompt with ALL THE CHUNKS of the document.
    # step 2: Detect fallback trigger
    fallback_phrases = [
        "cannot generate a one-page investment memo",
        "insufficient context",
        "not enough information"
    ]
    if any(phrase in response.lower() for phrase in fallback_phrases) and all_chunks and llm:
        print("Fallback: switching to full-context 'stuff' chain...")

        # Stuff prompt over full document
        full_text = "\n\n".join([chunk.page_content for chunk in all_chunks])[:12000]

        template = PromptTemplate.from_template(
            "You are an investment analyst. Use the following document to generate a one-page investment memo.\n"
            "Document:\n{doc}\n\n"
            "Instructions:\n"
            "- Company name and industry\n"
            "- Executive summary\n"
            "- Financial highlights\n"
            "- Key risks\n"
            "- Suggested financing type\n"
            "- Conclusion\n"
            f"{stock_text}"
        )

        stuff_chain = LLMChain(llm=llm, prompt=template)
        response = stuff_chain.run(doc=full_text)

    return response



def generate_swot_analysis(qa_chain):
    prompt = (
        "Create a SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) for this company based on the available documents."
    )
    return qa_chain.run(prompt)

def generate_summary(qa_chain):
    prompt = "Summarize the company and the most important points in the documents in 5-7 bullet points."
    return qa_chain.run(prompt)


