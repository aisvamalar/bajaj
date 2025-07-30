# PDF Document Q&A System

A simple and powerful system for processing PDF documents and asking questions about them.

## Features

- 📄 **PDF Text Extraction**: Extract text from PDF files with page numbering
- 🧩 **Smart Chunking**: Split documents into optimal chunks for processing
- 🤖 **AI Analysis**: Use NVIDIA LLM to extract structured metadata
- 🔍 **Semantic Search**: Fast similarity search using FAISS and embeddings
- ❓ **Simple Q&A**: Ask questions and get direct answers

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Fix Keras Compatibility (if needed)

If you encounter Keras compatibility issues:

```bash
pip install tf-keras
```

### 3. Upload PDF

Place your PDF file in the `data/` directory and rename it to `doc1.pdf`:

```bash
# Create data directory if it doesn't exist
mkdir -p data

# Copy your PDF file to data/ and rename it
cp /path/to/your/document.pdf data/doc1.pdf
```

### 4. Run the System

```bash
python main.py
```

This will:
- Process doc1.pdf automatically
- Extract text, create chunks and embeddings
- Start the Q&A system immediately
- Allow you to ask questions about your document

## Usage

### Running the System

```bash
python main.py
```

### Asking Questions

Once the system starts, you can ask questions like:
- "What is covered under hospitalization?"
- "What are the exclusion clauses?"
- "How much is the premium?"
- "What is the claim settlement process?"
- "Is angioplasty covered?"

## File Structure

```
doc_load/
├── data/                    # Place doc1.pdf here
│   └── doc1.pdf
├── embeddings/              # FAISS indexes and vectors
├── metadata/               # PDF metadata and info
├── chunks/                 # Raw text and chunks
├── main.py                 # Main launcher script
├── api.py                  # FastAPI REST API
├── document_processor.py   # Processing and Q&A system
├── question_answerer.py    # Q&A system module
└── requirements.txt        # Dependencies
```

## Processing Pipeline

1. **Manual Upload**: Place doc1.pdf in `data/` directory
2. **Text Extraction**: Extract text with page numbering
3. **Chunking**: Split into 1500-character chunks with 200-character overlap
4. **AI Analysis**: Process chunks with NVIDIA LLM to extract metadata
5. **Embedding Generation**: Create semantic embeddings using Sentence Transformers
6. **FAISS Index**: Build fast similarity search index
7. **Q&A System**: Start interactive question-answering

## Configuration

### Environment Variables
Create a `.env` file with your NVIDIA API key:
```
NVIDIA_API_KEY=your_nvidia_api_key_here
```

### Processing Parameters
- **Chunk Size**: 1500 characters (configurable in `document_processor.py`)
- **Chunk Overlap**: 200 characters (configurable in `document_processor.py`)
- **Embedding Model**: `all-mpnet-base-v2` (fast and accurate)
- **LLM Model**: `meta/llama-3.1-70b-instruct`

## Troubleshooting

### Keras Compatibility Error
```bash
pip install tf-keras
```

### NVIDIA API Key Missing
Create `.env` file with your API key:
```
NVIDIA_API_KEY=your_key_here
```

### File Not Found
Make sure `doc1.pdf` is in the `data/` directory:
```bash
ls data/
# Should show: doc1.pdf
```

### Memory Issues
- Reduce chunk size in `document_processor.py`
- Process smaller PDFs first
- Close other applications

### Processing Time
- Large PDFs may take 10-30 minutes
- Progress is shown during processing
- Can be interrupted and resumed

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure NVIDIA API key is set correctly
4. Check file permissions and disk space

## License

This project is for educational and research purposes. 