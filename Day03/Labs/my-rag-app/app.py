"""PDF Buddy: a small Streamlit app for chatting with an uploaded PDF."""
import hashlib
import io
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

# Add the repository root so this app can reuse the course's AWS settings.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from askit_core import bedrock, config

import streamlit as st
from botocore.exceptions import BotoCoreError, ClientError
from pypdf import PdfReader

EMBED_MODEL = "amazon.titan-embed-text-v2:0"
AVATAR = "🤖"
AWS_HELP = "Check your .env keys, AWS region, and Titan model access, then try again."

st.set_page_config(page_title="PDF Buddy", page_icon=AVATAR)

# Use saffron accents on white so the app feels warm and easy to scan.
st.markdown(
    """<style>
    .main h1 { color: #c77700; }
    [data-testid="stChatMessage"] { border: 1px solid #f2d7a6; border-radius: 16px; }
    .stButton button { background: #e69500; border-radius: 12px; color: white; }
    </style>""",
    unsafe_allow_html=True,
)

# Keep the PDF index and chat across reruns so users do not rebuild unnecessarily.
for key, value in (("pdf_hash", ""), ("chunks", []), ("vectors", None),
                   ("settings", None), ("messages", [])):
    if key not in st.session_state:
        st.session_state[key] = value


def chunk_text(text, size, overlap):
    """Split page text into overlapping word chunks."""
    words = text.split()
    step = size - overlap
    return [" ".join(words[i:i + size]) for i in range(0, len(words), step)]


def embed_text(client, text):
    """Get one normalized vector from Titan Text Embeddings."""
    result = client.invoke_model(
        modelId=EMBED_MODEL,
        body=json.dumps({"inputText": text, "dimensions": 512, "normalize": True}),
    )
    return json.loads(result["body"].read())["embedding"]


def cosine_similarity(left, right):
    """Compare two vectors by the angle between them."""
    size = np.linalg.norm(left) * np.linalg.norm(right)
    return float(np.dot(left, right) / max(size, 1e-12))


def find_sources(question_vector, chunks, vectors, count):
    """Select the closest chunks so answers can point back to PDF pages."""
    scores = [cosine_similarity(question_vector, vector) for vector in vectors]
    best = np.argsort(scores)[::-1][:count]
    return [{"page": chunks[i]["page"], "text": chunks[i]["text"], "score": scores[i]}
            for i in best]


# Accept only PDF uploads and clear the old index and chat when the file changes.
st.title(f"{AVATAR} PDF Buddy")
st.caption("Upload. Ask. Done.")
pdf_file = st.file_uploader("Upload a PDF to get started", type="pdf")
if pdf_file:
    pdf_bytes = pdf_file.getvalue()
    current_hash = hashlib.sha256(pdf_bytes).hexdigest()
    if current_hash != st.session_state.pdf_hash:
        st.session_state.pdf_hash = current_hash
        st.session_state.chunks = []
        st.session_state.vectors = None
        st.session_state.settings = None
        st.session_state.messages = []
elif st.session_state.pdf_hash:
    st.session_state.pdf_hash = ""
    st.session_state.chunks = []
    st.session_state.vectors = None
    st.session_state.settings = None
    st.session_state.messages = []

# Offer simple retrieval controls and a small creator card in the sidebar.
with st.sidebar:
    st.header("Settings")
    top_k = st.slider("Top-K chunks", 1, 6, 3)
    chunk_size = st.slider("Chunk size (words)", 60, 300, 120, step=10)
    overlap = st.slider("Chunk overlap (words)", 0, min(100, chunk_size - 1),
                        min(30, chunk_size - 1), step=5)
    if st.button("Clear chat"):
        st.session_state.messages = []
    st.markdown("---")
    st.subheader("About me")
    st.markdown(
        f"<div style='background:#fff7e8;padding:12px;border-radius:12px'>"
        f"<b>Gowthami</b><br>{date.today():%B %d, %Y}<br>"
        "Fun fact: PDFs can hold a lot of page-turners.</div>",
        unsafe_allow_html=True,
    )

# Extract page-labeled text, chunk it, then embed at most four chunks per pass.
if pdf_file and st.button("Build index", type="primary"):
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        chunks = []
        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            chunks.extend({"page": page_number, "text": piece}
                          for piece in chunk_text(page_text, chunk_size, overlap))
        if not chunks:
            st.info("This PDF has no selectable text. Scanned PDFs are not supported yet.")
            st.stop()

        progress = st.progress(0, text="Embedding PDF chunks...")
        client, vectors = bedrock.client(), []
        for start in range(0, len(chunks), 4):
            batch = chunks[start:start + 4]
            vectors.extend(embed_text(client, item["text"]) for item in batch)
            done = start + len(batch)
            progress.progress(done / len(chunks), text=f"Embedded {done} of {len(chunks)} chunks")
        st.session_state.chunks = chunks
        st.session_state.vectors = np.asarray(vectors, dtype=float)
        st.session_state.settings = (chunk_size, overlap)
        st.session_state.messages = []
        st.success(f"Indexed {len(reader.pages)} pages into {len(chunks)} chunks.")
    except (BotoCoreError, ClientError):
        st.error(f"Could not reach AWS Bedrock. {AWS_HELP}")

# Ask for a new index when chunk controls differ from the settings last built.
index_ready = bool(st.session_state.chunks) and st.session_state.settings == (chunk_size, overlap)
if st.session_state.chunks and not index_ready:
    st.info("Chunk settings changed. Select Build index to update the index.")

# Display saved messages and answer new questions only from retrieved PDF context.
if index_ready:
    for message in st.session_state.messages:
        avatar = AVATAR if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["text"])
            if message["role"] == "assistant":
                with st.expander("Sources"):
                    for source in message["sources"]:
                        st.markdown(
                            f"**[p.{source['page']}] · similarity {source['score']:.2f}**\n\n"
                            f"{source['text']}"
                        )

    question = st.chat_input("Ask a question about your PDF")
    if question:
        st.session_state.messages.append({"role": "user", "text": question})
        with st.chat_message("user"):
            st.markdown(question)
        try:
            client = bedrock.client()
            query = embed_text(client, question)
            sources = find_sources(query, st.session_state.chunks, st.session_state.vectors, top_k)
            context = "\n\n".join(f"[p.{s['page']}] {s['text']}" for s in sources)
            prompt = (
                "Answer ONLY from the context. If the answer is not in the context, say you "
                "could not find it in the PDF. Cite the page like [p.3]. Speak like a calm "
                "senior engineer, using simple language, and always end with a brief joke "
                "based only on the context. Do not add outside facts.\n\n"
                f"Context:\n{context}\n\nQuestion: {question}"
            )
            result = client.converse(
                modelId=config.SMALL_MODEL,
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"maxTokens": 500, "temperature": 0.2},
            )
            answer = result["output"]["message"]["content"][0]["text"]
            st.session_state.messages.append(
                {"role": "assistant", "text": answer, "sources": sources}
            )
            st.rerun()
        except (BotoCoreError, ClientError):
            st.error(f"Could not reach AWS Bedrock. {AWS_HELP}")
elif not pdf_file:
    st.info("Upload a PDF and build its index before asking questions.")

st.markdown("---")
st.caption("Built by Gowthami with vibe coding at DevPro Academy")
