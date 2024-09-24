#! /bin/bash

# update_ollama_linux.bash
# -----------------------------------------------------
time_start=$(date +%s.%N)
# -----------------------------------------------------
print_time () {
    time_end=$(date +%s.%N);
    elapsed=$(echo "$time_end - $time_start" | bc);
    hours=$(echo "$elapsed / 3600" | bc);
    minutes=$(echo "($elapsed % 3600) / 60" | bc);
    seconds=$(echo "$elapsed % 60" | bc);
    echo "FINISHED   $(date) - finished $model";
    printf "ELAPSED TIME for %s (hh:mm:ss) : %02d:%02d:%02.0f\n" $model $hours $minutes $seconds;
    time_start=$(date +%s.%N);
};
# -----------------------------------------------------
ollama --version
sudo systemctl stop ollama
ps auxww | grep -i ollama | grep -v grep
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl start ollama
ollama list
ollama --version
# -----------------------------------------------------
echo "updating models"

ollama list | tail -n +2 | awk '{print $1}' | while read -r model
do
    echo "---------------------------------------";
    echo "START $model";
    ollama pull "$model";
    print_time;
done

ollama --version
ollama list

