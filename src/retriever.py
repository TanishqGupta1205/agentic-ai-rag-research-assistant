def retrieve_documents(query, embeddings_model, index, documents, all_chunks, top_k=8):

    query_embedding = embeddings_model.encode([query])

    # Search all chunks
    candidate_k = len(all_chunks)

    distances, indices = index.search(
        query_embedding,
        candidate_k
    )

    candidates = []

    query_words = set(query.lower().split())

    important_words = {
        "problem",
        "problems",
        "limitation",
        "limitations",
        "challenge",
        "challenges",
        "weakness",
        "weaknesses",
        "issue",
        "issues",
        "error",
        "errors",
        "noise",
        "difficulty",
        "difficulties",
        "drawback",
        "drawbacks",
        "constraint",
        "constraints",
        "segmentation",
        "region-based",
        "region",
        "object detection",
        "conclusion",
        "conclusions",
        "finding",
        "findings",
        "future",
        "method",
        "methods",
        "application",
        "applications",
        "result",
        "results",
        "objective",
        "objectives",
    }

    for i, distance in zip(indices[0], distances[0]):

        if i < 0:
            continue

        text = all_chunks[i]["text"].lower()

        keyword_score = 0

        # Query word matches
        for word in query_words:
            if word in text:
                keyword_score += 1

        # Important research terms
        for word in important_words:
            if word in text:
                keyword_score += 2

        # Stronger priority for section-specific questions
        if "conclusion" in query.lower() and "conclusion" in text:
            keyword_score += 5

        if (
            "finding" in query.lower()
            or "findings" in query.lower()
        ) and (
            "finding" in text
            or "findings" in text
            or "conclusion" in text
        ):
            keyword_score += 4

        if "future" in query.lower() and "future" in text:
            keyword_score += 4

        if (
            "method" in query.lower()
            or "methods" in query.lower()
        ) and (
            "method" in text
            or "methods" in text
        ):
            keyword_score += 4

        if (
            "application" in query.lower()
            or "applications" in query.lower()
        ) and (
            "application" in text
            or "applications" in text
        ):
            keyword_score += 4

        candidates.append(
            (
                keyword_score,
                distance,
                all_chunks[i]
            )
        )

    # First select semantically relevant candidates
    candidates.sort(
        key=lambda x: x[1]
    )

    semantic_candidates = candidates[:50]

    # Then use keywords to rerank candidates
    semantic_candidates.sort(
        key=lambda x: (-x[0], x[1])
    )

    retrieved_docs = [
        item[2]
        for item in semantic_candidates[:top_k]
    ]

    for i, doc in enumerate(retrieved_docs):

        print(f"\n--- Retrieved Chunk {i + 1} ---")
        print(doc["text"])
        print("Source:", doc["source"])
        print("Page:", doc["page"])
        print("-" * 50)

    return retrieved_docs