from utils.config import Config
from utils.document_processor import DocumentProcessor

config = Config()
print(f"Config chunk size: {config.chunk_size}")

processor = DocumentProcessor(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
print(f"Processor chunk size: {processor.chunk_size}")

text = "This is a sentence. " * 500
tokens = processor.count_tokens(text)
print(f"Test text tokens: {tokens}")

chunks = processor.create_chunks(text)
print(f"Number of chunks: {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"Chunk {i} tokens: {chunk['tokens']}")
