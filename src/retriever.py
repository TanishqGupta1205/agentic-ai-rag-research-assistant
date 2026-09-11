def retrieve_documents(
    query,
    embeddings_model,
    index,
    documents,
    all_chunks,
    top_k=4
):

    query_embedding = embeddings_model.encode([query])

    candidate_k = len(all_chunks)

    distances, indices = index.search(
        query_embedding,
        candidate_k
    )

    query_lower = query.lower()

    # Detect list-style questions
    list_question = any(
        phrase in query_lower
        for phrase in [
            "what are",
            "what methods",
            "what techniques",
            "what categories",
            "what types",
            "what applications",
            "what architectures",
            "what future research directions",
            "list",
            "main findings"
        ]
    )

    candidates = []

    for i, distance in zip(indices[0], distances[0]):

        if i < 0:
            continue

        doc = all_chunks[i]
        text = doc["text"].lower()

        keyword_score = 0

        # Exact question-word matching
        for word in query_lower.split():

            if word in text:
                keyword_score += 1

        # Stronger score for headings / enumerated content
        if list_question:

            if any(
                marker in text
                for marker in [
                    "1.",
                    "2.",
                    "3.",
                    "4.",
                    "5.",
                    "6.",
                    "following",
                    "categories",
                    "methods",
                    "techniques",
                    "applications",
                    "future research"
                ]
            ):
                keyword_score += 3

        candidates.append(
            (
                keyword_score,
                distance,
                i
            )
        )

    # Semantic candidates first
    candidates.sort(
        key=lambda x: x[1]
    )

    semantic_candidates = candidates[:50]

    # Keyword/list reranking
    semantic_candidates.sort(
        key=lambda x: (-x[0], x[1])
    )

    # Use more primary chunks for list questions
    primary_k = 6 if list_question else top_k

    primary_candidates = semantic_candidates[:primary_k]

    retrieved_docs = []

    for _, _, i in primary_candidates:

        matched_doc = all_chunks[i]

        retrieved_docs.append(
            matched_doc
        )

        source = matched_doc["source"]
        page = matched_doc["page"]

        # Expand to nearby pages in the same document
        for doc in all_chunks:

            if doc["source"] != source:
                continue

            if abs(doc["page"] - page) <= 1:
                retrieved_docs.append(doc)

    # Remove duplicates
    unique_docs = []
    seen = set()

    for doc in retrieved_docs:

        key = (
            doc["source"],
            doc["page"],
            doc["text"]
        )

        if key not in seen:

            seen.add(key)
            unique_docs.append(doc)

    # Prevent excessive context
    max_chunks = 16 if list_question else 10

    unique_docs = unique_docs[:max_chunks]

    return unique_docs