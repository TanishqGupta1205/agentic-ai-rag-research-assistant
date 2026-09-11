def create_chunks(pages, source):

    chunk_size = 500
    chunk_overlap = 100

    chunks = []

    for page in pages:

        text = page["text"]
        page_number = page["page"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk = text[start:end]

            chunks.append({
                "text": chunk,
                "page": page_number,
                "source": source
            })

            start += chunk_size - chunk_overlap

    return chunks