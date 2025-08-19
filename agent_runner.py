from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_community.chat_models import ChatOpenAI
from langchain_modules.agent_tools import get_stock_info, generate_memo_for_client

def run_agent():
    tools = [get_stock_info, generate_memo_for_client]
    llm = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo")

    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True  # This makes the agent show each tool it uses
    )

    print("Welcome to the Deal Memo Agent.")
    print("Examples:")
    print("- Generate a memo for Tesla_Deal with TSLA")
    print("- Get stock info for AAPL")
    print("- Generate a memo for Apple_Deal")

    while True:
        query = input("\nWhat would you like to do? (type 'exit' to quit): ")
        if query.lower() in ['exit', 'quit']:
            break
        response = agent_executor.run(query)
        print("\nResponse:\n", response)




if __name__ == "__main__":
    run_agent()
