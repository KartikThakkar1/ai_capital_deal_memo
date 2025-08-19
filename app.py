# runner file

import os
from s3_uploader import upload_all_pdfs_from_folder
from langchain_modules.assistant_qa import (load_and_split_pdf, embed_chunks_and_store, load_vector_store, build_qa_chain)
from langchain_modules.generate_memos import (build_memo_chain, generate_investment_memo, generate_swot_analysis, generate_summary)

DATA_FOLDER = "data/"
VECTOR_STORE_DIR = "vector_store/"

def process_all_clients(data_folder):
    for client_folder in os.listdir(data_folder):
        client_path = os.path.join(data_folder, client_folder)
        vector_path = os.path.join("vector_store", client_folder)

        if not os.path.isdir(client_path):
            continue

        if os.path.exists(os.path.join(vector_path, "index.faiss")):
            print(f"Skipping {client_folder} — already processed.")
            continue

        print(f"\nProcessing this client deal: {client_folder}")
        all_chunks = []

        for filename in os.listdir(client_path):
            if filename.endswith(".pdf"):
                file_path = os.path.join(client_path, filename)
                chunks = load_and_split_pdf(file_path)
                for chunk in chunks:
                    chunk.metadata["source_doc"] = filename
                all_chunks.extend(chunks)

        embed_chunks_and_store(all_chunks, save_path=vector_path)

def list_available_documents(vector_folder):
    return [
        f for f in os.listdir(vector_folder)
        if os.path.isdir(os.path.join(vector_folder, f))
        and os.path.exists(os.path.join(vector_folder, f, "index.faiss"))
    ]

def client_session_menu(doc_name):
    vector_path = os.path.join("vector_store", doc_name)
    vector_store = load_vector_store(vector_path)
    qa_chain = build_qa_chain(vector_store)
    memo_chain = build_memo_chain(vector_store)

    print(f"\nSession started for: {doc_name}")

    while True:
        print("\nWhat do you want to do?")
        print("1. Chat/QA with and about documents related to this client")
        print("2. Generate a memo or summary")
        print("3. Exit this client session")
        choice = input("Enter choice (1/2/3): ").strip()

        if choice == "1":
            print("Entering chat mode. Type 'exit' to return.")
            while True:
                question = input("Question: ")
                if question.lower() in ['exit', 'quit']:
                    break
                response = qa_chain.run(question)
                print("Answer:", response)


        elif choice == "2":
            ticker = input("Enter stock ticker (e.g., AAPL, TSLA) or press Enter to skip: ").strip().upper()

            while True:
                print("\nMemo Options:")
                print("1. Full Investment Memo")
                print("2. SWOT Analysis")
                print("3. Bullet Summary")
                memo_choice = input("Enter choice (1/2/3) or type 'back': ").strip()

                if memo_choice == "1":
                    from langchain.chat_models import ChatOpenAI  # placed here to avoid circular import
                    all_chunks = vector_store.similarity_search("all", k=1000)  # rough proxy for all docs
                    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
                    print(generate_investment_memo(memo_chain, ticker=ticker if ticker else None, all_chunks=all_chunks, llm=llm))
                elif memo_choice == "2":
                    print(generate_swot_analysis(memo_chain))
                elif memo_choice == "3":
                    print(generate_summary(memo_chain))
                elif memo_choice.lower() == "back":
                    break
                else:
                    print("Invalid choice.")


        

        elif choice == "3":
            print("Ending session for", doc_name)
            break

        else:
            print("Invalid selection.")

def client_entry_point():
    docs = list_available_documents("vector_store/")
    if not docs:
        print("No clients found.")
        return

    print("\nAvailable clients:")
    for i, doc in enumerate(docs):
        print(f"{i + 1}. {doc}")

    try:
        index = int(input("Select a client: ").strip())
        doc_name = docs[index - 1]
        client_session_menu(doc_name)
    except Exception as e:
        print("Invalid selection.")

if __name__ == "__main__":
    print("\nSTATUS: Uploading all PDFs to S3..")
    upload_all_pdfs_from_folder(DATA_FOLDER)
    print("\nSTATUS: Embedding, chunking, and storing all PDFs locally")
    process_all_clients(DATA_FOLDER)
    print("\nSTATUS: Starting session")
    client_entry_point()
