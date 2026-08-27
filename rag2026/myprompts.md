-------------------------------------------------------

Current directory contains a design document for a RAG system for millions of documents.

Please confirm that it uses PostgreSQL for symantic search (Vector Similarity) and also full text search (keywords).

These methods can't help to understand the dependencies
between different pieces of information. The structure.

Does it make sense to also create an interconnected wiki
to help with understanding the structure and clustering ?

Please don't change anything - only propose improvements.

-------------------------------------------------------

To implement wiki, we would need to convert the documents into wiki files,
which are markdown files in Google Open Knowledge Format with links between files,
and we need to store those files in some directory structure for easy grep/find operations

-------------------------------------------------------

So we will have:

 - raw documents
 - processed files (after OCR, ...)
 - wiki versions of these documents (md files)
 - chunks and vectors in the database for keyword and vector search

 Correct?

-------------------------------------------------------

OK, please update the design document according to our conversation in this session

-------------------------------------------------------

- please remove the version number from the file names.

- please remove the Change log at the top of the document

- please add a short executive summary at the top emphasizing that
  the system is designed to work with millions of documents
  and include combination of search methods - symantic (vectors),
  keywords (full text search), and structure (wiki)

- please add an estimate of the required disk spaces and database size

-------------------------------------------------------

I am confused about wiki. Is it stored in files or in database?

-------------------------------------------------------

Can we make some improvements using techniques
from this project?

https://github.com/mempalace/mempalace

-------------------------------------------------------

Please generate a nice PDF formatted for US Letter paper with 0.7" margins

-------------------------------------------------------

Please suggest changes to the design document to describe 

- the process of updating the system when we adding/removing/updating docs (including versions, vectors, indexes, wiki, ...)

- The process of evaluation of the accuracy and completness of the RAG system and hallucination level after daily updates
