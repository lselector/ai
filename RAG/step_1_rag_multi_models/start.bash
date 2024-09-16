#! /bin/bash

# wrapper to start the demo

rm -rf ./milvus_demo.db
rm -rf .milvus_demo.db.lock

python rag_multi_models.py

