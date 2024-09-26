#! /bin/bash

# wrapper to start the demo using faiss

if [ -z "${OLLAMA_MODEL}" ] ; then 
    echo "please set env variable to preferred model";
    echo "for example: ";
    echo "export OLLAMA_MODEL=llama3.1"; 
    exit
fi

if ! (ollama list | grep -q "$OLLAMA_MODEL"); then
  echo "Model '$OLLAMA_MODEL' is not available."
  echo "Please download it by running 'ollama run $OLLAMA_MODEL'"
  exit 
fi

echo "removing uploaded_files/"
rm -rf uploaded_files/*

echo "starting python script"
python rag_faiss.py


