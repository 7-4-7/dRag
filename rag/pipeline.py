from pathlib import Path
from tqdm import tqdm
from uuid import uuid4
from backend.rag.utils import (
    load_prompts,
    perform_search,
    load_generating_model,
    pptx_content_handler,
    docx_content_handler,
    pdf_content_handler,
    load_embedding_model,
    load_pinecone,
)
from backend.config import PINECONE_INDEX_NAME
class RAGPipeline():
    def __init__(self, web_search : bool = True):
        self.web_search = web_search
        self.emb_model = load_embedding_model()
        self.pc, self.idx = load_pinecone()
        
    def load_documents(self, kb_dir:Path):
        """Supports pdf, docx, ppt with metadata attached for back referal"""
        all_content = []
        all_file_path = kb_dir.glob('*')
        for i in all_file_path:
            if i.suffix == '.pptx':
                pptx_content = pptx_content_handler(i)
                all_content.extend(pptx_content)
            elif i.suffix == '.pdf':
                pdf_content = pdf_content_handler(i)
                all_content.extend(pdf_content)
            elif i.suffix == '.docx':
                docx_content = docx_content_handler(i)
                all_content.extend(docx_content)
            else:
                continue
        return all_content
    
    def chunk_text(self, all_content, chunk_size, chunk_overlap):
        """Performs chunking along with the meta data, file name"""
        chunks = []

        for entry in all_content:
            text = entry['text']
            file_name = entry['file_name']
            
            words = text.split()
            start = 0
            while start < len(words):
                end = start + chunk_size
                chunk_text = " ".join(words[start:end])
                if chunk_text.strip():
                    chunks.append({
                        "file_name": file_name,
                        "text": chunk_text
                    })
                start += chunk_size - chunk_overlap
        return chunks

    def embed_chunks(self, chunks):
        """Embeds each chunk to a dense vector"""
        embeds = []
        
        for chunk in chunks:
            text = chunk['text']
            encode = self.emb_model.encode(text)
            embeds.append({
                "id" : str(uuid4()),
                'embedding' : encode,
                'text' : chunk['text'],
                'file_name' : chunk['file_name'],                
            })
        return embeds
    
    def store_embeds(self,):
        """Stores the generated embeddings in pinecone db"""
        for embed_chunk in embed_chunk:
            vectors = [
                {
                    "id" : embed_chunk['id'],
                    "values" : embed_chunk['embedding'],
                    "metadata" : {'text' : embed_chunk['text'],
                                  'file_name' : embed_chunk['file_name']}
                }
            ]
            self.idx.upsert(vectors)
        
    def query_embed(self, query):
        """Returns embeded query"""
        q_emb = self.emb_model.encode(query)
        return q_emb
    
    def lookup_and_retrieval(self, q_emb, top_k):
        """Retrieves top_k similar vector embedding's meta data to form context""" 
        response = self.idx.query(
            vector = q_emb,
            top_k = top_k,            
            includeValues = False,
            includeMetadata = True,
        )
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
            new_context = perform_search(search_phrase)
            search_context += "\n" + new_context

            attempts += 1
            if attempts >= max_attempts:
                break

        return search_context
    
    def generate_answer(self, query):
        generating_model = load_generating_model()
        prompts = load_prompts()['generate_answer']
        model_response_json = generating_model.generate(prompts)
        return model_response_json
        
        
rgp = RAGPipeline(web_search=False)

# Stage 1
kb_dir = Path("backend\\rag\\kb")
all_content = rgp.load_documents(kb_dir)
print(all_content)

# Stage 2
chunks = rgp.chunk_text(all_content=all_content, chunk_size=500, chunk_overlap=50)
print(len(chunks))

# Stage 3 
emb_chunks = rgp.embed_chunks(chunks=chunks)
print(len(emb_chunks))



    