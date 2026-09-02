def create_chunks(pages,source):
    chunk_size=500
    chunks=[]
    for page in pages:
        text=page["text"]
        page_number=page["page"]
        for i in range(0,len(text),chunk_size):
            chunk=text[i:i+chunk_size]
            chunks.append({
                "text":chunk,
                "page":page_number,
                "source":source
            })
        return chunks