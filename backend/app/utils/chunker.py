def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if end < len(text):
            space_pos = chunk.rfind(' ')
            if space_pos > chunk_size * 0.5:
                end = start + space_pos
                chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
    return chunks