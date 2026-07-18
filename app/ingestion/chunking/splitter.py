from typing import List
import logfire


def chunk_text(text: str, chunk_size: int = 1500) -> List[str]:
    """
    Simple semantic-ish chunker that splits by paragraphs.
    Ensures chunks do not exceed the specified size.
    If a single paragraph is larger than chunk_size,
    it is split into fixed-size chunks.
    """
    with logfire.span("✂️ Text Chunking", text_length=len(text)):

        if not text.strip():
            return []

        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for p in paragraphs:
            p = p.strip()

            if not p:
                continue

            # If paragraph fits into current chunk
            if len(current_chunk) + len(p) + 2 <= chunk_size:
                current_chunk += p + "\n\n"

            else:
                # Save current chunk first
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                    current_chunk = ""

                # If a single paragraph itself is too large,
                # split it into fixed-size pieces.
                if len(p) > chunk_size:
                    for i in range(0, len(p), chunk_size):
                        piece = p[i:i + chunk_size].strip()
                        if piece:
                            chunks.append(piece)
                else:
                    current_chunk = p + "\n\n"

        # Save remaining chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        valid_chunks = [c for c in chunks if c.strip()]

        logfire.info(f"✅ Generated {len(valid_chunks)} chunks")

        return valid_chunks

"""
So Logfire records something like:
Operation : ✂️ Text Chunking
Text Length : 11
Time Taken : 5 ms
Status : Success





"""