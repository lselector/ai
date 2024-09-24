#! /bin/bash

# wrapper to start the demo

if ! python -m myutils &> /dev/null; then
  echo "Please add absolute path of directory 'ai/py_lib'"
  echo "to PATH and PYTHOPATH environmental variables"
  exit
fi

echo "removing milvus_demo.db"
rm -rf ./milvus_demo.db
echo "removing milvus_demo.db.lock"
rm -rf .milvus_demo.db.lock
echo "removing uploaded_files/"
rm -rf uploaded_files/*

echo "starting python script"
python rag_multi_models.py


