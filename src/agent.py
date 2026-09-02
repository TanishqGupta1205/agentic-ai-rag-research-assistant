from src.retriever import retrieve_documents
from src.llm import generate_answer
from src.embeddings import embeddings_model
from groq import Groq

MODEL = "openai/gpt-oss-20b"

client = Groq()


def check_context(query, context):
    """
    Agent decides whether the retrieved information
    is sufficient to answer the question.
    """

    prompt = f"""
You are a research agent evaluating retrieved information from a research paper.

User question:
{query}

Retrieved information:
{context}

Determine whether the retrieved information contains relevant information
that can be used to answer the user's question.

The retrieved information must contain specific evidence
that directly helps answer the user's question.

Reply YES only if the retrieved information contains
information that directly answers the question.

Reply NO if the information is only generally related
to the topic but does not actually contain an answer.

For example, if the question asks for "limitations",
the context must contain actual limitations, challenges,
constraints, drawbacks, or similar evidence.

Reply with ONLY one word:
YES
or
NO
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    decision = response.choices[0].message.content.strip().upper()

    return decision

def run_agent(query, index, documents, all_chunks, progress_callback=None):

    def update(message):
        if progress_callback:
            progress_callback(message)

        print(message)

    update("🔍 Agent received your question")

    current_query = query

    for attempt in range(3):

        update(f"🔎 Search attempt {attempt + 1}")

        retrieve_docs = retrieve_documents(
            current_query,
            embeddings_model,
            index,
            documents,
            all_chunks,
            top_k=8
        )

        if not retrieve_docs:
            update("❌ No relevant information found")

            return "I could not find relevant information in the research papers."

        update(
            f"📚 Retrieved {len(retrieve_docs)} relevant sections"
        )

        context = "\n\n".join(
            f"Source: {doc['source']}\n"
            f"Page: {doc['page']}\n"
            f"Content: {doc['text']}"
            for doc in retrieve_docs
        )

        update("🧠 Agent is evaluating the retrieved context")

        decision = check_context(
            current_query,
            context
        )

        update(f"🤖 Context evaluation: {decision}")

        if decision == "YES":

            update("✅ Information is sufficient")

            update("✍️ Generating grounded answer")

            answer = generate_answer(
                context,
                query,
                MODEL
            )

            unique_sources = set()

            for doc in retrieve_docs:

                unique_sources.add(
                    f"- {doc['source']} — Page {doc['page']}"
                )

            sources = "\n".join(unique_sources)

            update("✅ Answer generated successfully")

            return answer + "\n\nSources:\n" + sources

        update("⚠️ Information is not sufficient")

        if attempt < 2:

            update("🔄 Agent is refining the search query")

            current_query = refine_query(
                query,
                context
            )

            update(
                f"🎯 Refined query: {current_query}"
            )

        else:

            update("🛑 Maximum search attempts reached")

            return (
                "I could not find enough information "
                "in the research papers to answer this question."
            )
def refine_query(query, context):
    """
    Agent creates a better search query when
    retrieved information is not sufficient.
    """

    prompt = f"""
You are a research retrieval agent.

User question:
{query}

The previous retrieved context was not sufficient.

Previous retrieved context:
{context}

Create a better search query to find the specific information
needed to answer the user's question.

IMPORTANT RULES:

1. Do NOT search for the paper title.
2. Do NOT search for author names.
3. Do NOT search for words like "PDF", "2018", or "paper review".
4. Identify the main information the user is asking for.
5. Use specific concepts, keywords, and related terms that are
likely to appear in the relevant section of the document.
6. If the question asks about problems, use terms such as:
   limitations, challenges, weaknesses, errors, performance,
   accuracy, difficulties, constraints, noise.
7. Keep the query concise and focused.

Return ONLY the improved search query.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    refined_query = response.choices[0].message.content.strip()

    return refined_query