
RAG demo files

Advanced RAG. We divide it on three main steps:
   - rephrazing user request. User often does not provide good responce
        that we can use it as a query for vectorDB. We need to understand 
        what user wants and rephraze his query in more semantic way.

        Maybe we should do some extra postprocessing, like if user just wants summary 
        but doc is too long to do it we need to retrieve most valuable chunks
        and summarize them

        It's a good way to create some patterns we will use to rephraze query
        depending on situation

   - better chunking. This step is very specific to the task.
        We will look at different examples of tasks 
        at 'examples of tasks for chunking' section

   - better retrieving/reranking.

   examples of tasks for chunking:
      - long docs:
           First of all we need to slice our docs on small chunks. 
           We should do it in a way when one chunk is a symantic node of text.
           It can be one paragraph

           Then we need to union chunks in different chunk-chains
           Chunk-chain - is a sequence of chunks that have similar symantic
           by some parameter, like hashtag. Chunk can be at many chunk-chains

           Small example:
           ...

           In this way we can retrieve vector length and by hashtag
           That will increase our chances to retrieve valuable chunks

implemented:

# -------------------------------------
Vitalii rag_multi_models:
        user can select local or API model (embedding or API)
        user can reset (clear) the temp DB
        user can select upload one or several files
        user can chat about their content - RAG fetches 5 top matches
        Note: files indexed into the same DB
# -------------------------------------
Vitalii RAG_2_script to load and index files from terminal
        files need to be placed in one directory
        files may be in formats: txt, pdf, ms-word
        script will parse each file into text
        then chunk them and convert into vectors
        so you get records consisting of vectors + metadata (file name, chunk number, ...)
        the database table is cleared - and re-populated with this data
# -------------------------------------
Vitalii RAG_2_webapp - similar for RAG_1_webapp,
        but doesn't allow t oupload files.
        Instead it uses the pre-uploaded data for chatting
# -------------------------------------
Vitalii RAG_3_webapp - combining 1,2,3 together
        Uses 2 DB tables: one of "batch" load and one for interactive load
        Webapp has control to select the DB table (data source): one or another or both

