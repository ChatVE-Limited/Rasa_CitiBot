import os
import time
import threading
import logging
import subprocess
from dotenv import load_dotenv
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from openai import OpenAI
import faiss
import pickle
from langchain.embeddings.openai import OpenAIEmbeddings
import schedule

logger = logging.getLogger(__name__)
load_dotenv()

# Initialize OpenRouter client
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# ==============================
#  Action 1: OpenAI Default (via OpenRouter)
# ==============================
class ActionDefaultGPTResponse(Action):
    MAX_WORDS = 150
    MAX_TOKENS = 200

    def name(self) -> str:
        return "action_default_gpt_response"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        user_message = tracker.latest_message.get("text")

        try:
            response = client.chat.completions.create(
                model="openai/gpt-4",  # OpenRouter expects provider/model format
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert on Nigerian topics. Provide concise answers focusing on Nigeria.
                        - Be extremely brief (under {self.MAX_WORDS} words)
                        - Use simple language
                        - Prioritize key facts
                        - Use bullet points if helpful
                        - Avoid long introductions"""
                    },
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.MAX_TOKENS,
                temperature=0.3
            )

            gpt_reply = response.choices[0].message.content

            if len(gpt_reply.split()) > self.MAX_WORDS:
                gpt_reply = ' '.join(gpt_reply.split()[:self.MAX_WORDS]) + "..."

            dispatcher.utter_message(text=gpt_reply)

        except Exception as e:
            logger.error(f"OpenRouter Error: {e}")
            dispatcher.utter_message(
                text="Sorry, I couldn't fetch an answer right now. Please try again later."
            )

        return []

# ==============================
#  Action 2: RAG Fallback
# ==============================
class ActionRAG(Action):
    def name(self) -> str:
        return "action_rag"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        user_message = tracker.latest_message.get("text")

        index_path = "rag_store/index.faiss"
        store_path = "rag_store/store.pkl"

        if not os.path.exists(index_path) or not os.path.exists(store_path):
            dispatcher.utter_message("Knowledge base is not ready. Please try again later.")
            return []

        try:
            index = faiss.read_index(index_path)
            with open(store_path, "rb") as f:
                doc_store = pickle.load(f)

            embeddings = OpenAIEmbeddings(
                openai_api_key=os.getenv("OPENROUTER_API_KEY"),
                openai_api_base="https://openrouter.ai/api/v1"
            )
            query_vector = embeddings.embed_query(user_message)

            # Search top 3 documents
            D, I = index.search([query_vector], k=3)
            retrieved_docs = [doc_store[i].page_content for i in I[0] if i < len(doc_store)]

            context_text = "\n".join(retrieved_docs)

            response = client.chat.completions.create(
                model="openai/gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Use the provided context to answer the question."},
                    {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {user_message}"}
                ],
                temperature=0.3,
                max_tokens=300
            )

            answer = response.choices[0].message.content.strip()
            dispatcher.utter_message(answer)

        except Exception as e:
            logger.error(f"RAG Error: {e}")
            dispatcher.utter_message("Sorry, I couldn't retrieve that information right now.")
        
        return []

# ==============================
#  Background Scheduler
# ==============================
def run_ingestion():
    """Runs ingest.py to refresh FAISS index."""
    try:
        logger.info("Running daily ingestion...")
        subprocess.run(["python", "ingest.py"], check=True)
        logger.info("Ingestion completed.")
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")

def start_scheduler():
    """Starts daily ingestion at a fixed time."""
    schedule.every().day.at("02:00").do(run_ingestion)

    def scheduler_loop():
        while True:
            schedule.run_pending()
            time.sleep(60)

    threading.Thread(target=scheduler_loop, daemon=True).start()

start_scheduler()
