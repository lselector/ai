#! /bin/bash

# wrapper to start the demo

rm -rf ./milvus_demo.db
rm -rf .milvus_demo.db.lock
rm -rf uploaded_files/*

python rag_multi_models.py

