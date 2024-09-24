#! /bin/bash

# wrapper to start the demo

if ! python -m myutils &> /dev/null; then
  echo "Please add absolute path of directory 'ai/py_lib'"
  echo "to PATH and PYTHOPATH environmental variables"
  exit
fi

if ! (ollama list | grep -q "mistral-nemo:latest"); then
  echo "Model 'mistral-nemo' is not available."
  echo "Please download it by running 'ollama run mistral-nemo'"
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


