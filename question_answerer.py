#!/usr/bin/env python3
import os
import json
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleQASystem:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        self.embedding_model = self.embedding_model.to('cuda') 
        self.llm = ChatNVIDIA(model="meta/llama-3.1-70b-instruct")
        self.master_index_path = "metadata/master_index.json"
        
    def load_documents(self):
        """Load all processed documents."""
        if not os.path.exists(self.master_index_path):
             
            return None
            
        with open(self.master_index_path, "r", encoding="utf-8") as f:
            return json.load(f) 
    
    def find_relevant_chunk(self, question, top_k=10, document_hash=None):
        """Find the most relevant chunks for the question with comprehensive search."""
        master_index = self.load_documents()
        if not master_index:
            return None
            
        all_results = []
        
        # Extract key terms from question for keyword matching
        question_lower = question.lower()
        key_terms = []
        
        # Extract question words and important terms
        import re
        
        # Extract numbers (dates, amounts, percentages)
        numbers = re.findall(r'\d+(?:\.\d+)?%?', question)
        key_terms.extend(numbers)
        
        # Extract time-related words
        time_words = ['days', 'months', 'years', 'period', 'waiting', 'grace']
        for word in time_words:
            if word in question_lower:
                key_terms.append(word)
        
        # Extract common question words
        question_words = ['what', 'when', 'where', 'how', 'why', 'who', 'which']
        for word in question_words:
            if word in question_lower:
                key_terms.append(word)
        
        # Extract general terms based on question content
        if 'period' in question_lower:
            key_terms.extend(['period', 'time', 'duration', 'waiting'])
        if 'coverage' in question_lower or 'cover' in question_lower:
            key_terms.extend(['coverage', 'cover', 'included', 'excluded', 'benefits'])
        if 'limit' in question_lower or 'maximum' in question_lower:
            key_terms.extend(['limit', 'maximum', 'cap', 'ceiling'])
        if 'condition' in question_lower or 'requirement' in question_lower:
            key_terms.extend(['condition', 'requirement', 'criteria', 'eligible'])
        if 'define' in question_lower or 'definition' in question_lower:
            key_terms.extend(['define', 'definition', 'means', 'refers'])
        
        # Extract all meaningful terms from the question (domain-agnostic)
        domain_terms = re.findall(r'\b[a-zA-Z]{3,}\b', question_lower)
        key_terms.extend([term for term in domain_terms if len(term) > 3])
        
        # Remove duplicates and common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        key_terms = [term for term in key_terms if term.lower() not in stop_words]
        
        # Limit to most relevant terms
        key_terms = key_terms[:15]  # Keep top 15 most relevant terms
        
        # Determine which documents to search
        documents_to_search = master_index["pdfs"].items()
        if document_hash:
            # If specific document hash provided, only search that document
            if document_hash in master_index["pdfs"]:
                documents_to_search = [(document_hash, master_index["pdfs"][document_hash])]
            else:
                documents_to_search = master_index["pdfs"].items() # Search all if not found
        
        for pdf_hash, pdf_info in documents_to_search:
            try:
                # Load PDF-specific data
                index_path = pdf_info["embeddings_path"]
                metadata_path = pdf_info["metadata_path"]
                
                if not (os.path.exists(index_path) and os.path.exists(metadata_path)):
                    continue
                
                # Load FAISS index
                index = faiss.read_index(index_path)
                
                # Load metadata
                with open(metadata_path, "rb") as f:
                    metadata = pickle.load(f)
                
                # Generate question embedding
                question_embedding = self.embedding_model.encode([question])
                faiss.normalize_L2(question_embedding)
                
                # Search with larger scope
                scores, indices = index.search(question_embedding.astype('float32'), top_k)
                
                # Collect all results from this PDF with enhanced scoring
                for score, idx in zip(scores[0], indices[0]):
                    if idx < len(metadata):
                        chunk_data = metadata[idx]
                        chunk_text = chunk_data.get('text', '').lower()
                        
                        # Calculate keyword bonus
                        keyword_bonus = 0
                        for term in key_terms:
                            if term in chunk_text:
                                keyword_bonus += 0.1
                        
                        # Calculate semantic similarity bonus
                        semantic_bonus = 0
                        if len(key_terms) > 0:
                            # Check for semantic matches (similar words)
                            semantic_matches = 0
                            for term in key_terms:
                                # Look for variations and synonyms
                                if any(similar in chunk_text for similar in [term, term.replace('-', ' '), term.replace(' ', '-')]):
                                    semantic_matches += 1
                            semantic_bonus = (semantic_matches / len(key_terms)) * 0.2
                        
                        # Apply bonuses to score
                        enhanced_score = float(score) + keyword_bonus + semantic_bonus
                        
                        # Much lower threshold for comprehensive coverage
                        if enhanced_score > 0.05:  # Even lower threshold for maximum coverage
                            all_results.append({
                                'pdf_hash': pdf_hash,
                                'pdf_filename': pdf_info["filename"],
                                'score': enhanced_score,
                                'metadata': metadata[idx],
                                'original_score': float(score),
                                'keyword_bonus': keyword_bonus
                            })
                        
            except Exception as e:
                continue
        
        # Sort by enhanced relevance score
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Return more results for comprehensive coverage
        if not all_results:
            return None
            
        return all_results[:15]  # Return top 15 results for maximum coverage
    
    def direct_text_search(self, question, document_hash=None):
        """Perform direct text search across all documents for specific terms."""
        master_index = self.load_documents()
        if not master_index:
            return None
            
        question_lower = question.lower()
        search_terms = []
        
        # Extract key terms for direct search (domain-agnostic)
        # Extract all meaningful words from the question for keyword matching
        import re
        question_words = re.findall(r'\b[a-zA-Z0-9%]+\b', question_lower)
        search_terms.extend([word for word in question_words if len(word) > 2])
        
        all_results = []
        
        # Determine which documents to search
        documents_to_search = master_index["pdfs"].items()
        if document_hash:
            # If specific document hash provided, only search that document
            if document_hash in master_index["pdfs"]:
                documents_to_search = [(document_hash, master_index["pdfs"][document_hash])]
            else:
                documents_to_search = master_index["pdfs"].items() # Search all if not found
        
        for pdf_hash, pdf_info in documents_to_search:
            try:
                metadata_path = pdf_info["metadata_path"]
                if not os.path.exists(metadata_path):
                    continue
                
                with open(metadata_path, "rb") as f:
                    metadata = pickle.load(f)
                
                for idx, chunk_data in enumerate(metadata):
                    chunk_text = chunk_data.get('text', '').lower()
                    
                    # Check for direct matches
                    for term in search_terms:
                        if term in chunk_text:
                            all_results.append({
                                'pdf_hash': pdf_hash,
                                'pdf_filename': pdf_info["filename"],
                                'score': 0.8,  # High score for direct matches
                                'metadata': chunk_data,
                                'original_score': 0.8,
                                'keyword_bonus': 0.0,
                                'direct_match': True
                            })
                            break  # Only add each chunk once
                    
            except Exception as e:
                continue
        
        # Sort by score and return top results
        all_results.sort(key=lambda x: x['score'], reverse=True)
        return all_results[:10] if all_results else None
    
    def extract_intent_from_question(self, question):
        """Extract intent and sub-intents from the question."""
        prompt = f"""
Analyze this question and extract the main intent and sub-intents:

Question: "{question}"

Return only valid JSON in this format:
{{
  "main_intent": "Coverage|Exclusions|Claims|Premiums|Terms",
  "sub_intents": ["specific topics or conditions mentioned"],
  "question_type": "what|how|when|where|why|who"
}}

Focus on the core intent of what the person is asking about.
"""
        
        try:
            response = self.llm.invoke(prompt)
            # Extract JSON from response
            start = response.content.find("{")
            end = response.content.rfind("}") + 1
            json_data = response.content[start:end]
            return json.loads(json_data)
        except Exception as e:
            return {
                "main_intent": "General",
                "sub_intents": ["general inquiry"],
                "question_type": "what"
            }
    
    def generate_answer(self, question, relevant_chunks, intent_info):
        """Generate a focused answer based on the question and relevant chunks."""
        if not relevant_chunks:
            return "Sorry, I couldn't find relevant information to answer your question."
        
        # Handle both single chunk and multiple chunks
        if isinstance(relevant_chunks, dict):
            relevant_chunks = [relevant_chunks]
        
        # Prepare document context from multiple chunks
        document_context = ""
        for i, chunk in enumerate(relevant_chunks):
            chunk_data = chunk['metadata']
            document_context += f"""
Chunk {i+1} (Relevance: {chunk['score']:.3f}):
- Source: {chunk['pdf_filename']}
- Main Intent: {chunk_data['main_intent']}
- Section: {chunk_data['metadata']['section']}
- Clause: {chunk_data['metadata'].get('clause_number', 'N/A')}
- Sub-intents: {', '.join(chunk_data['sub_intents'])}
- Content: {chunk_data['text']}

"""
        
        prompt = f"""
You are a document intelligence assistant. Answer the question with ONLY the essential information.

Question: "{question}"

Document Information:
{document_context}

CRITICAL INSTRUCTIONS:
- Answer in 1-2 sentences maximum
- Use exact numbers and facts from the document
- Do NOT mention "According to the document" or "Based on the provided chunks"
- Do NOT include chunk references or relevance scores
- Do NOT add explanations or context
- Do NOT list exclusions unless specifically asked
- Do NOT add notes or additional information
- Provide direct, factual answers without extra commentary

Answer:
"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return f"Error generating answer: {e}"
    
    def ask_question(self, question, document_hash=None):
        """Main function to ask a question and get an answer."""
        
        # Step 1: Extract intent
        intent_info = self.extract_intent_from_question(question)
        
        # Step 2: Find relevant document chunks
        question_lower = question.lower()
        relevant_chunks = self.find_relevant_chunk(question, document_hash=document_hash)
        
        # If no good results, try broader search
        if not relevant_chunks or (isinstance(relevant_chunks, list) and len(relevant_chunks) < 3):
            relevant_chunks = self.find_relevant_chunk(question, top_k=30, document_hash=document_hash)  # Search even more chunks
        
        # If still no good results, try searching all chunks
        if not relevant_chunks or (isinstance(relevant_chunks, list) and len(relevant_chunks) < 3):
            relevant_chunks = self.find_relevant_chunk(question, top_k=50, document_hash=document_hash)  # Search maximum chunks
        
        # Special search for specific terms that might be missed
        if not relevant_chunks or (isinstance(relevant_chunks, list) and len(relevant_chunks) < 3):
            # Create search terms based on question (domain-agnostic)
            search_terms = []
            # Extract all meaningful words from the question for keyword matching
            question_words = re.findall(r'\b[a-zA-Z0-9%]+\b', question_lower)
            search_terms.extend([word for word in question_words if len(word) > 2])
            
            # Try searching with these specific terms
            for term in search_terms:
                temp_results = self.find_relevant_chunk(term, top_k=20, document_hash=document_hash)
                if temp_results and isinstance(temp_results, list):
                    if not relevant_chunks:
                        relevant_chunks = temp_results
                    else:
                        relevant_chunks.extend(temp_results)
                    break
            
            # If still no results, try direct text search across all documents
            if not relevant_chunks or (isinstance(relevant_chunks, list) and len(relevant_chunks) < 3):
                relevant_chunks = self.direct_text_search(question, document_hash)
        
        if relevant_chunks:
            if isinstance(relevant_chunks, list):
                for i, chunk in enumerate(relevant_chunks):
                    pass # Removed print statements
            else:
                pass # Removed print statements
        else:
            pass # Removed print statements
        
        # Step 3: Generate answer
        answer = self.generate_answer(question, relevant_chunks, intent_info)
        
        # Step 4: Display answer
        return answer

def main():
    print("Document Q&A System")
    print("=" * 50)
    print("Ask questions about your documents!")
    print("Examples:")
    print("- What is covered under this policy?")
    print("- What are the main terms and conditions?")
    print("- How does the process work?")
    print("- What are the requirements?")
    print("\nType 'quit' to exit")
    print("=" * 50)
    
    qa_system = SimpleQASystem()
    
    while True:
        try:
            question = input("\nYour question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                print(" Please enter a question.")
                continue
            
            # Get answer
            qa_system.ask_question(question)
            
        except KeyboardInterrupt:
            print("\n Goodbye!")
            break
        except Exception as e:
            print(f" Error: {e}")

if __name__ == "__main__":
    main() 