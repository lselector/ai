
### RAG demo files

#### demo for website:
- step_1_rag_multi_models
- no preload
- upload one or several files
- checkbox to make response strictly based only on retrieved data
- change LLM on the fly while keeping the chat history
- test on computer and smartphone, make it look nice
  make step_1_rag_multi_models/README.md file with description and screenshots 
- record video demo fro eais.ai website

-------------------------------------<br>
#### Advanced RAG. We divide it into main steps:

   1. process documents and popualte vector database (including tags and other metadata)
   2. process user request (to match db content)
   3. similarity search (vector + metadata)
   4. rerank
   5. select top 5 to make output summary

-------------------------------------<br>
__1. process documents and popualte vector database (including tags and other metadata)__

 - make high-level description of the doc. 
   Ask LLM to extract main terms, notions, systems,
   abbreviations; make a list of tags.
 - If the doc is long - split it into meaningful pieces 
   (chapters, subchapters) and chunks, then convert chunks to vectors,
   so now we have pieces to insert into DB as following:
    - doc_name, date, author, length, ...
    - chapter #, name
    - subchapter #, name
    - chunk #
    - raw text
    - vector

Splitting into peices/chunks is very specific to the task.
<br>Here are some common use cases:
- system documentation (policy docs, instructions, ...)
- legal contracts
- resume / job description

-------------------------------------<br>
__2. process user request (to match db content)__

 - use LLM to extract the essense of user request.
   Rephrase user request - make it consize and clear.
   Understand the abbreviations and context.
   And make it match the structure of stored docs.
   For example, matching resume to job description.

<br>-------------------------------------
<br>-------------------------------------
<br>-------------------------------------

#### DONE:

```
Vitalii rag_multi_models:
        user can select local or API model (embedding or API)
        user can reset (clear) the temp DB
        user can select upload one or several files
        user can chat about their content - RAG fetches 5 top matches
        Note: files indexed into the same DB
<br>-------------------------------------<br>
Vitalii RAG_2_script to load and index files from terminal
        files need to be placed in one directory
        files may be in formats: txt, pdf, ms-word
        script will parse each file into text
        then chunk them and convert into vectors
        so you get records consisting of vectors + metadata (file name, chunk number, ...)
        the database table is cleared - and re-populated with this data
<br>-------------------------------------<br>
Vitalii RAG_2_webapp - similar for RAG_1_webapp,
        but doesn't allow t oupload files.
        Instead it uses the pre-uploaded data for chatting
<br>-------------------------------------<br>
Vitalii RAG_3_webapp - combining 1,2,3 together
        Uses 2 DB tables: one of "batch" load and one for interactive load
        Webapp has control to select the DB table (data source): one or another or both
```

#### NOTE DONE:

# -------------------------------------
Vitalii RAG_4_script - like RAG_2_script but with better data pre-processing before load
Vitalii RAG_4_webapp - like RAG_2_webapp but with better data pre-processing before load
# -------------------------------------
Vitalii RAG_5_webapp - adding better post-processing:
        fetch 20 matches, re-rank them using LLM, select top 5 for final response
# -------------------------------------
Vitalii RAG_6_evaluate - evaluate the quality of the RAG pipeline
# -------------------------------------
Vitalii: FastHTML resume matching app (fasthtml)
Vitalii: FastHTML chat+js-diagram (like Anthropic claude artifacts)
Vitalii: FastHTML building workflow of several agents (to be discussed)
