#! /bin/bash

# script to update Ollama on MacOS
# uses wget, unzip, rsync (installed with brew ?)

cd ~/Downloads
rm -rf Ollama-darwin.zip  Ollama.app
wget https://ollama.com/download/Ollama-darwin.zip
unzip Ollama-darwin.zip
ollama --version
pkill -9 ollama Ollama
sudo rsync -avzh Ollama.app /Applications/
ollama --version

