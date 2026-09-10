from src.retriever import retrieve_documents
from src.llm import generate_answer
from src.embeddings import embeddings_model
from groq import Groq
from src.evaluator import evaluate_context, evaluate_answer, evaluate_faithfulness
MODEL = "openai/gpt-oss-120b"

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

The retrieved information does not need to contain a
complete answer.

Reply YES if the retrieved information contains one or more
specific facts, problems, limitations, challenges, methods,
results, or other evidence that can be combined to answer
the user's question.

For broad questions, partial but relevant evidence is enough
to reply YES.

Reply NO only if the retrieved information is mostly unrelated
to the user's question and does not provide useful evidence
for answering it.

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

    process_steps = []

    def update(message):

        process_steps.append(message)

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

        for i, doc in enumerate(retrieve_docs):

            print(f"\n--- Retrieved Chunk {i+1} ---")
            print(doc["text"])
            print("Source:", doc["source"])
            print("Page:", doc["page"])

        if not retrieve_docs:

            update("❌ No relevant information found")

            return {
                "answer": "I could not find relevant information in the research papers.",
                "sources": [],
                "context_score": 0,
                "answer_score": 0,
                "faithfulness_score": 0,
                "process": process_steps
            }

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

        context_score = evaluate_context(
            current_query,
            context
        )

        update(
            f"📊 Context Relevance Score: {context_score}"
        )

        decision = check_context(
            current_query,
            context
        )

        update(
            f"🤖 Context evaluation: {decision}"
        )

        if decision == "YES":

            update("✅ Information is sufficient")

            update("✍️ Generating grounded answer")

            answer = generate_answer(
                context,
                query,
                MODEL
            )

            answer_score = evaluate_answer(
                query,
                answer
            )

            update(
                f"📊 Answer Relevance Score: {answer_score}"
            )

            faithfulness_score = evaluate_faithfulness(
                context,
                answer
            )

            update(
                f"📊 Faithfulness Score: {faithfulness_score}"
            )

            unique_sources = set()

            for doc in retrieve_docs:

                unique_sources.add(
                    (doc["source"], doc["page"])
                )

            sorted_sources = sorted(
                unique_sources,
                key=lambda x: (x[0], x[1])
            )

            sources = "\n".join(
                f"{source} — Page {page}"
                for source, page in sorted_sources
            )

            update("✅ Answer generated successfully")

            return {
                "answer": answer,
                "sources": sources,
                "context_score": context_score,
                "answer_score": answer_score,
                "faithfulness_score": faithfulness_score,
                "process": process_steps
            }

        update("⚠️ Information is not sufficient")

        if attempt < 2:

            update("🔄 Agent is refining the search query")

            current_query = refine_query(
                current_query,
                context
            )

            update(
                f"🎯 Refined query: {current_query}"
            )

        else:

            update("🛑 Maximum search attempts reached")

            return {
                "answer": (
                    "I could not find enough information "
                    "in the research papers to answer this question."
                ),
                "sources": "",
                "context_score": context_score,
                "answer_score": 0,
                "faithfulness_score": 0,
                "process": process_steps
            }
        
def refine_query(query, context):
    """
    Agent creates a focused search query when
    the retrieved information is not sufficient.
    """

    prompt = f"""
You are a research retrieval agent.

User question:
{query}

Previous retrieved context:
{context}

The previous context was not sufficient to answer the question.

Create a NEW, focused search query that should retrieve
the specific evidence needed from the research paper.

First identify what information the user is asking for.

If the question asks about problems, limitations, challenges,
or weaknesses, search for specific evidence such as:
limitations, challenges, weaknesses, drawbacks, errors,
accuracy problems, noise, segmentation problems,
object detection errors, performance issues, constraints.

If the question asks about objectives, search for:
objectives, goals, aims, purpose.

If the question asks about methodology, search for:
methodology, method, approach, algorithm, technique,
architecture, implementation.

If the question asks about results, search for:
results, findings, performance, accuracy, evaluation.

IMPORTANT:
- Focus on the information requested by the user.
- Use concepts likely to appear in the paper.
- Do NOT search for the paper title.
- Do NOT search for author names.
- Do NOT search for PDF, year, or paper review.
- Do NOT simply repeat the original question.
- Keep the query specific and concise.
- Return ONLY the search query.

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