from langchain.agents import Tool
from langchain.tools import tool
from langchain_modules.automation_tools import fetch_stock_data
from langchain_modules.assistant_qa import load_vector_store, build_qa_chain
from langchain_modules.generate_memos import generate_investment_memo
from langchain_community.chat_models import ChatOpenAI

@tool
def get_stock_info(ticker: str) -> str:
    """
    Fetches stock data (price, PE ratio, market cap, etc) for the given ticker symbol.
    Example: 'AAPL', 'TSLA'
    """
    data = fetch_stock_data(ticker)
    if "error" in data:
        return data["error"]
    
    summary = (
        f"Company: {data.get('name')}\n"
        f"Sector: {data.get('sector')}, Industry: {data.get('industry')}\n"
        f"Price: {data.get('current_price')}\n"
        f"Market Cap: {data.get('market_cap')}\n"
        f"P/E Ratio: {data.get('pe_ratio')}, Beta: {data.get('beta')}\n"
    )
    return summary

@tool
def generate_memo_for_client(input_str: str) -> str:
    """
    Generates an investment memo for a given client folder name (e.g., 'Apple_Deal') and optionally a stock ticker.
    Format: 'Apple_Deal, AAPL' or just 'Apple_Deal'
    """
    parts = input_str.split(",")
    client = parts[0].strip()
    ticker = parts[1].strip().upper() if len(parts) > 1 else None

    vector_path = f"vector_store/{client}"
    vector_store = load_vector_store(vector_path)
    qa_chain = build_qa_chain(vector_store)
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

    all_chunks = vector_store.similarity_search("all", k=1000)

    return generate_investment_memo(qa_chain, ticker=ticker, all_chunks=all_chunks, llm=llm)
