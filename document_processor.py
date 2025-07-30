import json
import os
import numpy as np
import hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import time

# Load NVIDIA API key from .env
load_dotenv()
os.environ['NVIDIA_API_KEY'] = os.getenv("NVIDIA_API_KEY")

# Initialize NVIDIA LLM
llm = ChatNVIDIA(model="meta/llama-3.1-70b-instruct")

# Initialize Sentence Transformer for embeddings
embedding_model = SentenceTransformer('all-mpnet-base-v2')
embedding_model = embedding_model.to('cuda')

# Create storage directories
os.makedirs("embeddings", exist_ok=True)
os.makedirs("metadata", exist_ok=True)
os.makedirs("chunks", exist_ok=True)

def get_pdf_hash(pdf_path):
    """Generate a unique hash for the PDF file."""
    with open(pdf_path, 'rb') as f:
        content = f.read()
    return hashlib.md5(content).hexdigest()

def get_pdf_info(pdf_path):
    """Extract basic information about the PDF."""
    reader = pdfplumber.open(pdf_path)
    return {
        'filename': os.path.basename(pdf_path),
        'pages': len(reader.pages),
        'size_bytes': os.path.getsize(pdf_path),
        'processed_date': datetime.now().isoformat()
    }

def extract_from_pdf(pdf_path):
    """Extract text and tables from a PDF file using pdfplumber."""
    text = ""
    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                # Extract tables
                page_tables = page.extract_tables()
                for table in page_tables:
                    # Convert table to string (CSV-like)
                    table_str = '\n'.join([', '.join([str(cell) if cell is not None else '' for cell in row]) for row in table])
                    tables.append({
                        'page': page_num + 1,
                        'table': table_str
                    })
        return text, tables
    except Exception as e:
        return "", []

def chunk_text(text, chunk_size=1000, chunk_overlap=300):
    """Split text into overlapping chunks for LLM processing with better section preservation."""
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_text(text)

        # Post-process chunks to ensure important sections are captured
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            # If chunk is too short, try to expand it
            if len(chunk.strip()) < 200:
                # Look for the next chunk to combine
                if i + 1 < len(chunks):
                    combined = chunk + "\n\n" + chunks[i + 1]
                    if len(combined) <= chunk_size * 1.5:  # Don't make it too long
                        processed_chunks.append(combined)
                        continue  # Skip the next chunk since we combined it

            processed_chunks.append(chunk)

        return processed_chunks
    except Exception as e:
        return []

def extract_json_from_response(response_text):
    """Extract valid JSON from LLM response text."""
    try:
        # Remove any markdown formatting
        response_text = response_text.replace("```json", "").replace("```", "").strip()

        # Find the first complete JSON object
        start = response_text.find("{")
        if start == -1:
            raise ValueError("No JSON object found in response")

        # Find the matching closing brace
        brace_count = 0
        end = start
        for i, char in enumerate(response_text[start:], start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break

        json_data = response_text[start:end]
        return json.loads(json_data)
    except Exception as e:
        # Try to extract just the first JSON object if multiple are present
        try:
            # Split by newlines and find JSON objects
            lines = response_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    return json.loads(line)
        except:
            pass

        # Try to fix common JSON issues
        try:
            # Remove any text before the first {
            start = response_text.find("{")
            if start != -1:
                response_text = response_text[start:]

            # Remove any text after the last }
            end = response_text.rfind("}")
            if end != -1:
                response_text = response_text[:end+1]

            # Try to fix common issues
            response_text = response_text.replace("'", '"')  # Replace single quotes with double quotes
            response_text = response_text.replace("None", "null")  # Replace Python None with JSON null
            response_text = response_text.replace("True", "true")  # Replace Python True with JSON true
            response_text = response_text.replace("False", "false")  # Replace Python False with JSON false

            return json.loads(response_text)
        except:
            pass

        # If all else fails, create a minimal valid JSON
        try:
            # Extract the text content and create a basic structure
            text_content = response_text.replace('"', '\\"').replace('\n', ' ').strip()
            if len(text_content) > 500:
                text_content = text_content[:500] + "..."

            fallback_json = {
                "chunk_id": "chunk_fallback",
                "text": text_content,
                "main_intent": "General",
                "sub_intents": ["general information"],
                "metadata": {
                    "section": "Unknown",
                    "clause_number": "none"
                }
            }
            return fallback_json
        except:
            pass

        raise ValueError(f"Could not parse LLM JSON output: {e}\nRaw Output:\n{response_text}")

def process_chunk(idx, chunk, prompt_template):
    """Process a single chunk and return structured JSON."""
    chunk_id = f"chunk_{idx+1}"
    prompt = prompt_template.format(chunk_id=chunk_id, chunk_content=chunk.strip())
    try:
        response = llm.invoke(prompt)
        json_result = extract_json_from_response(response.content)
        json_result["chunk_id"] = chunk_id
        json_result["chunk_index"] = idx + 1
        return json_result
    except Exception as e:
        return None

def send_chunks_concurrently(chunks, n=10, max_workers=5):
    """Send chunks to LLM concurrently and extract structured metadata."""

    prompt_template = """
You are a Document Intelligence Engine. Your task is to extract structured metadata from insurance policy text.

Analyze the provided text chunk and extract the following information:

Return ONLY valid JSON in this format:
{
  "chunk_id": "chunk_X",
  "text": "exact text content",
  "main_intent": "Coverage|Exclusions|Claims|Premiums|Terms|Definitions|Benefits|Limits|Conditions|Processes|Maternity|Hospital|AYUSH|PlanA|GracePeriod|WaitingPeriod|OrganDonor|NCD|HealthCheck",
  "sub_intents": ["specific topics or conditions mentioned"],
  "metadata": {
    "section": "section name or type",
    "clause_number": "clause number if available"
  }
}

IMPORTANT: Pay special attention to:
- Key terms and concepts mentioned in the text
- Specific numbers, dates, and amounts
- Important definitions and conditions
- Coverage details and limitations
- Process descriptions and requirements

Text to analyze:
{chunk_content}
"""

    def process_chunk(chunk_data):
        try:
            chunk_text, chunk_index = chunk_data
            prompt = prompt_template.format(chunk_content=chunk_text)

            response = llm.invoke(prompt)
            response_text = response.content

            # Extract JSON from response
            json_data = extract_json_from_response(response_text)

            # Add chunk index and hash
            json_data['chunk_index'] = chunk_index
            json_data['pdf_hash'] = get_pdf_hash("data/policy.pdf")  # This will be updated later

            return json_data

        except Exception as e:
            # Return a fallback structure for failed chunks
            return {
                "chunk_id": f"chunk_{chunk_index}",
                "text": chunk_text[:500] + "..." if len(chunk_text) > 500 else chunk_text,
                "main_intent": "General",
                "sub_intents": ["general information"],
                "metadata": {
                    "section": "Unknown",
                    "clause_number": "none"
                },
                "chunk_index": chunk_index,
                "pdf_hash": get_pdf_hash("data/policy.pdf"),
                "processing_error": str(e)
            }

    # Prepare chunks for processing
    chunk_data = [(chunk, i) for i, chunk in enumerate(chunks)]

    # Process chunks in batches
    processed_chunks = []
    for i in range(0, len(chunk_data), n):
        batch = chunk_data[i:i+n]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            batch_results = list(executor.map(process_chunk, batch))
            processed_chunks.extend(batch_results)

    return processed_chunks

def process_chunks_simple(chunks):
    """Process chunks without LLM metadata extraction - create basic metadata for all chunks."""

    processed_chunks = []

    for i, chunk_text in enumerate(chunks):
        try:
            # Create basic metadata without LLM processing
            chunk_data = {
                "chunk_id": f"chunk_{i}",
                "text": chunk_text,
                "main_intent": "General",
                "sub_intents": ["general information"],
                "metadata": {
                    "section": "General",
                    "clause_number": "none"
                },
                "chunk_index": i,
                "pdf_hash": get_pdf_hash("data/policy.pdf")
            }

            # Try to extract some basic information from the text
            chunk_lower = chunk_text.lower()

            # Detect intent based on keywords
            if any(word in chunk_lower for word in ['grace', 'premium', 'payment']):
                chunk_data["main_intent"] = "Premiums"
                chunk_data["sub_intents"] = ["grace period", "premium payment"]
            elif any(word in chunk_lower for word in ['waiting', 'period', '36 months', '24 months']):
                chunk_data["main_intent"] = "Terms"
                chunk_data["sub_intents"] = ["waiting period"]
            elif any(word in chunk_lower for word in ['maternity', 'pregnancy', 'childbirth']):
                chunk_data["main_intent"] = "Maternity"
                chunk_data["sub_intents"] = ["maternity coverage"]
            elif any(word in chunk_lower for word in ['cataract', 'surgery']):
                chunk_data["main_intent"] = "Coverage"
                chunk_data["sub_intents"] = ["cataract surgery"]
            elif any(word in chunk_lower for word in ['organ donor', 'transplantation']):
                chunk_data["main_intent"] = "Coverage"
                chunk_data["sub_intents"] = ["organ donor"]
            elif any(word in chunk_lower for word in ['no claim discount', 'ncd']):
                chunk_data["main_intent"] = "Premiums"
                chunk_data["sub_intents"] = ["no claim discount"]
            elif any(word in chunk_lower for word in ['health check', 'preventive']):
                chunk_data["main_intent"] = "Coverage"
                chunk_data["sub_intents"] = ["health check"]
            elif any(word in chunk_lower for word in ['hospital', 'institution', 'beds']):
                chunk_data["main_intent"] = "Definitions"
                chunk_data["sub_intents"] = ["hospital definition"]
            elif any(word in chunk_lower for word in ['ayush', 'ayurveda', 'homeopathy']):
                chunk_data["main_intent"] = "AYUSH"
                chunk_data["sub_intents"] = ["ayush treatment"]
            elif any(word in chunk_lower for word in ['plan a', 'room rent', 'icu']):
                chunk_data["main_intent"] = "Coverage"
                chunk_data["sub_intents"] = ["plan a limits"]

            # Try to extract section information
            if 'preamble' in chunk_lower:
                chunk_data["metadata"]["section"] = "Preamble"
            elif 'definitions' in chunk_lower:
                chunk_data["metadata"]["section"] = "Definitions"
            elif 'benefits' in chunk_lower:
                chunk_data["metadata"]["section"] = "Benefits"
            elif 'exclusions' in chunk_lower:
                chunk_data["metadata"]["section"] = "Exclusions"
            elif 'conditions' in chunk_lower:
                chunk_data["metadata"]["section"] = "Conditions"

            processed_chunks.append(chunk_data)

        except Exception as e:
            # Create fallback chunk
            fallback_chunk = {
                "chunk_id": f"chunk_{i}",
                "text": chunk_text[:500] + "..." if len(chunk_text) > 500 else chunk_text,
                "main_intent": "General",
                "sub_intents": ["general information"],
                "metadata": {
                    "section": "Unknown",
                    "clause_number": "none"
                },
                "chunk_index": i,
                "pdf_hash": get_pdf_hash("data/policy.pdf"),
                "processing_error": str(e)
            }
            processed_chunks.append(fallback_chunk)

    return processed_chunks

def create_embeddings_for_pdf(data, pdf_hash):
    """Create embeddings for a specific PDF."""

    # Prepare texts for embedding
    texts = []
    enhanced_metadata = []

    for i, item in enumerate(data):
        try:
            text_for_embedding = f"""
            Intent: {item.get('main_intent', '')}
            Section: {item.get('metadata', {}).get('section', '')}
            Clause: {item.get('metadata', {}).get('clause_number', '')}
            Sub-intents: {', '.join(item.get('sub_intents', []))}
            Content: {item.get('text', '')}
            """
            texts.append(text_for_embedding)
            enhanced_item = item.copy()
            enhanced_item['pdf_hash'] = pdf_hash
            enhanced_metadata.append(enhanced_item)
        except Exception as e:
            continue

    texts = list(texts)  # Ensure it's a list

    # Generate embeddings
    embeddings = embedding_model.encode(texts, show_progress_bar=True, batch_size=16)

    if embeddings.shape[0] != len(texts):
        raise RuntimeError(f"Embedding count mismatch: {embeddings.shape[0]} vs {len(texts)}")

    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    faiss.normalize_L2(embeddings)
    index.add(embeddings.astype('float32'))

    return index, embeddings, enhanced_metadata

def save_pdf_data(pdf_hash, index, embeddings, metadata, pdf_info, raw_text, chunks):
    """Save all data for a specific PDF."""

    # Save FAISS index
    faiss_path = f"embeddings/{pdf_hash}_index.faiss"
    faiss.write_index(index, faiss_path)

    # Save embeddings
    embeddings_path = f"embeddings/{pdf_hash}_vectors.npy"
    np.save(embeddings_path, embeddings)

    # Save enhanced metadata
    metadata_path = f"metadata/{pdf_hash}_metadata.pkl"
    with open(metadata_path, "wb") as f:
        pickle.dump(metadata, f)

    # Save metadata as JSON for human readability
    json_metadata_path = f"metadata/{pdf_hash}_metadata.json"
    with open(json_metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Save PDF info
    pdf_info_path = f"metadata/{pdf_hash}_info.json"
    with open(pdf_info_path, "w", encoding="utf-8") as f:
        json.dump(pdf_info, f, indent=2, ensure_ascii=False)

    # Save raw text
    text_path = f"chunks/{pdf_hash}_raw_text.txt"
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(raw_text)

    # Save original chunks
    chunks_path = f"chunks/{pdf_hash}_chunks.json"
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    # Update master index
    update_master_index(pdf_hash, pdf_info, len(metadata))

def update_master_index(pdf_hash, pdf_info, num_chunks):
    """Update the master index of all processed PDFs."""
    master_index_path = "metadata/master_index.json"

    # Load existing master index or create new one
    if os.path.exists(master_index_path):
        with open(master_index_path, "r", encoding="utf-8") as f:
            master_index = json.load(f)
    else:
        master_index = {"pdfs": {}, "total_pdfs": 0, "total_chunks": 0}

    # Add/update PDF entry
    master_index["pdfs"][pdf_hash] = {
        "filename": pdf_info["filename"],
        "pages": pdf_info["pages"],
        "size_bytes": pdf_info["size_bytes"],
        "processed_date": pdf_info["processed_date"],
        "num_chunks": num_chunks,
        "embeddings_path": f"embeddings/{pdf_hash}_index.faiss",
        "metadata_path": f"metadata/{pdf_hash}_metadata.pkl"
    }

    # Update totals
    master_index["total_pdfs"] = len(master_index["pdfs"])
    master_index["total_chunks"] = sum(pdf["num_chunks"] for pdf in master_index["pdfs"].values())

    # Save updated master index
    with open(master_index_path, "w", encoding="utf-8") as f:
        json.dump(master_index, f, indent=2, ensure_ascii=False)

def search_across_all_pdfs(query, top_k=5):
    """Search across all processed PDFs."""
    master_index_path = "metadata/master_index.json"

    if not os.path.exists(master_index_path):
        return []

    with open(master_index_path, "r", encoding="utf-8") as f:
        master_index = json.load(f)

    all_results = []

    for pdf_hash, pdf_info in master_index["pdfs"].items():
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

            # Generate query embedding
            query_embedding = embedding_model.encode([query])
            faiss.normalize_L2(query_embedding)

            # Search
            scores, indices = index.search(query_embedding.astype('float32'), top_k)

            # Add results with PDF info
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(metadata):
                    result = {
                        'pdf_hash': pdf_hash,
                        'pdf_filename': pdf_info["filename"],
                        'score': float(score),
                        'metadata': metadata[idx]
                    }
                    all_results.append(result)

        except Exception as e:
            continue

    # Sort by score and return top results
    all_results.sort(key=lambda x: x['score'], reverse=True)
    return all_results[:top_k]

def save_extracted_text(text, filename="extracted_text.txt"):
    """Save extracted text from PDF to a text file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def save_output_json(data, filename="output.json"):
    """Save extracted metadata to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    pdf_path = "data/doc1.pdf"  # Process doc1.pdf

    # Check if doc1.pdf exists
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found!")
        print("Please place doc1.pdf in the data/ directory")
        return

    # Generate PDF hash and info
    pdf_hash = get_pdf_hash(pdf_path)
    pdf_info = get_pdf_info(pdf_path)

    print(f"Processing PDF: {pdf_info['filename']}")
    print(f"PDF Hash: {pdf_hash}")
    print(f" Pages: {pdf_info['pages']}")

    # Check if already processed
    if os.path.exists(f"embeddings/{pdf_hash}_index.faiss"):
        print(f"PDF {pdf_hash} already processed. Skipping processing...")
    else:
        # Extract text and tables
        t0 = time.time()
        text, tables = extract_from_pdf(pdf_path)
        if not text:
            return

        # Save the extracted text first
        save_extracted_text(text)

        # Create chunks
        t0 = time.time()
        chunks = chunk_text(text)
        if not chunks:
            return

        # Process tables
        t0 = time.time()
        processed_tables = process_chunks_simple(tables)

        # Combine text and table chunks
        combined_chunks = []
        for i, chunk_text in enumerate(chunks):
            chunk_data = {
                "chunk_id": f"chunk_{i}",
                "text": chunk_text,
                "main_intent": "General",
                "sub_intents": ["general information"],
                "metadata": {
                    "section": "General",
                    "clause_number": "none"
                },
                "chunk_index": i,
                "pdf_hash": pdf_hash
            }
            combined_chunks.append(chunk_data)
        combined_chunks.extend(processed_tables)

        # Process combined chunks with simple metadata extraction
        t0 = time.time()
        results = process_chunks_simple(combined_chunks)
        save_output_json(results)

        # Create embeddings for this specific PDF
        t0 = time.time()
        index, embeddings, enhanced_metadata = create_embeddings_for_pdf(results, pdf_hash)

        # Save all data for this PDF
        save_pdf_data(pdf_hash, index, embeddings, enhanced_metadata, pdf_info, text, combined_chunks)

        print(f"Complete! Processed PDF {pdf_hash}")

    # Automatically start the Q&A system
    print("\n" + "="*60)
    print("Starting Q&A System...")
    print("="*60)

    # Import and start the simple Q&A system
    from question_answerer import SimpleQASystem

    qa_system = SimpleQASystem()

    print("Simple Q&A System")
    print("=" * 50)
    print("Ask questions about your document!")
    print("Examples:")
    print("- What is covered under hospitalization?")
    print("- What are the exclusion clauses?")
    print("- How much is the premium?")
    print("- What is the claim settlement process?")
    print("\nType 'quit' to exit")
    print("=" * 50)

    while True:
        try:
            question = input("\n Your question: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not question:
                print("Please enter a question.")
                continue

            # Get answer
            qa_system.ask_question(question)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f" Error: {e}")

if __name__ == "__main__":
    main()
