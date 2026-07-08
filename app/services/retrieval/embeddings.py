import time
import logfire
from langchain_openai import OpenAIEmbeddings
from app.config import settings

BATCH_SIZE=50
_EMBEDDING_DIM=1536
_FALLBACK_DIM=768

_active_model=None
_model_type:str|None=None

def _probe_Openai():
    """Try one embedded call to verify Open ai is rechargable . Returns model or none"""
    try:
        model=OpenAIEmbeddings(model="text-embedding-3-small",api_key=settings.OPENAI_API_KEY)
        model.embed_query("probe")
        logfire.info("OpenAI embeddings ready(text-embeddings-3-small,1536-dim).")
        return model
    except Exception as e:
        logfire.warning( f"OpenAI probe failed: {e}. Will use sentence-transformers fallback.")
        return None    
    
def _load_fallback():
    """Load the fallback model."""
    from sentence_transformers import SentenceTransformer
    logfire.info("Loading sentence-transformers fallback (all-mpnet-base-v2, 768-dim).")
    return SentenceTransformer("all-mpnet-base-v2")

def _init():
    """Initialise embedding model once per process. Called lazily on first use."""
    global _active_model,_model_type
    if _active_model is not None:
        return
    openai=_probe_Openai()
    if openai:
        _active_model=openai
        _model_type="openai"
    else:
        _active_model=_load_fallback()
        _model_type="fallback"


# HELPER FUNCTIONS
def get_embedding_dim()->int:
    """Return the vector dimension for the active model.Call after _init()."""
    _init()
    return _EMBEDDING_DIM if _model_type=="openai" else _FALLBACK_DIM

def _embed_batch(batch:list[str])->list[list[float]]:
    """Embed a batch of text using OpenAI."""
    for attempt in range(4): #Because sometimes the OpenAI API might temporarily fail due to:Network issues,Rate limits (too many requests),Temporary server problems
        try:
            return _active_model.embed_documents(batch)
        except Exception as e:
            err=str(e).lower()#Converts the exception message to lowercase so it's easier to search for specific error text.
            is_rate_limit=any(x in err for x in("429","rate","quota"))
            if is_rate_limit and attempt <3:
                wait=2**attempt
                logfire.warning(f"OpenAI rate limit hit - retrying in {wait}s"
                                f"(attempt{attempt+1}/4)")
                time.sleep(wait)
            else:
                logfire.error(f"OpenAi embedding failed:{e}")
                raise
    raise RuntimeError("OpenAi rate limit persisted after 4 attempts.")

def embed_query(query:str)->list[float]: # converting the user query into embedding
    """Embed a single query  using OpenAI."""
    _init()
    return _active_model.embed_query(query)

def embed_texts(texts:list[str])->list[list[float]]:
    _init()
    all_embeddings:list[list[float]]=[]
    for i in range(0,len(texts),BATCH_SIZE):
        batch=texts[i:i+BATCH_SIZE]
        with logfire.span("Embed batch",model=_model_type,start=i,size=len(batch)):
            all_embeddings.extend(_embed_batch(batch))
    return all_embeddings










"""
Why do we call logfire.error() in the else block and not in the if block?

The answer is because a rate limit is considered a temporary error, 
while the else block contains errors that we are not going to recover from.
Case 1: Rate Limit (429)

Suppose OpenAI says:

429 Too Many Requests.This doesn't mean your code is wrong.
It simply means:"You are sending requests too fast. Please wait."
Imagine you're entering a restaurant.Restaurant is full.Manager says:"Please wait 2 minutes."Would you consider this an error? No.You just wait and try again.

That's why your code does this:

logfire.warning(...)
time.sleep(wait)

Notice it uses warning, not error.

Because nothing is permanently wrong.

Case 2: Wrong API Key

Suppose OpenAI says

401 Unauthorized
Incorrect API key

Can waiting 1 second fix this?

❌ No.

Can waiting 2 seconds fix this?

❌ No.

Can waiting 10 minutes fix this?

❌ No.

The API key is wrong.

So your code immediately does

logfire.error(...)
raise

because retrying is pointless.

Another Example

Suppose you accidentally write

model="abc"

instead of

model="text-embedding-3-small"

OpenAI replies

Model not found

Will retrying help?

❌ No.

So your code logs an error immediately.

Why not log an error during retries?

Imagine this:
Attempt 1 429 Attempt 2 429 Attempt 3 429 Attempt 4 Success
If you logged an error every time, your logs would show:
ERROR
ERROR
ERROR

But in reality, nothing failed permanently. The request eventually succeeded.
That's why the code logs only a warning while retrying.
Then why log an error after retries?
Suppose
Attempt 1 → 429
Attempt 2 → 429
Attempt 3 → 429
Attempt 4 → 429

Now we've given OpenAI enough chances.
At this point, it is a real failure.
That's why the code executes

"""