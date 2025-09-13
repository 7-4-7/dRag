from pathlib import Path
from tqdm import tqdm
from utils import load_prompts, load_model

class RAGPipeline():
    def __init__(self, emb_model_name ,web_search : bool = True):
        self.web_search = web_search
        self.model = load_model()
        pass
    def load_documents(self, kb_dir):
        """Supports pdf, docx, slides with metadata attached for back referal"""
        combined_document = []
        return combined_document
    
    def chunk_text(self, text, chunk_size, chunk_overlap):
        """Does chunking on combined document"""
        chunks = []
        return chunks

    def embed_chunks(self, chunks, model):
        """Embeds each chunk to a dense vector"""
        embeds = []
        return embeds
    
    def store_embeds(self,):
        """Stores the generated embeddings in pinecone db"""
        pass
    
    def query_embed(self, query):
        """Returns embeded query"""
        q_emb = []
        return q_emb
    
    def lookup_and_retrieval(self, q_emb, top_k):
        """Retrieves top_k similar vector embedding's meta data to form context""" 
        context = ""
        return context
    def web_search_needed(self, query, context):
        """Performs web search and retrieves additional result if necessary"""
        prompts = load_prompts()
        search_context = context
        max_attempts = 5
        attempts = 0

        while True:
            prompt = prompts['validate_context'].format(query=query, context=search_context)
            model_response = self.model(prompt)  
            if not model_response['search_mode']:
                break

            search_phrase = model_response['search_query']
            new_context = perform_web_search(search_phrase)
            search_context += "\n" + new_context

            attempts += 1
            if attempts >= max_attempts:
                break

        return search_context
            
        

    