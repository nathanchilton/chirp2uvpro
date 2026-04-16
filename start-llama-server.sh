#!/bin/bash
#
# Start llama-server for OpenCode
#
# Usage:
#   ./start-llama-server.sh [model] [context_size]
#
# Models (32GB RAM recommendations):
#   gemma4        - Gemma 4 26B Q4_K_M        ~17-25GB RAM (default)
#   qwen3-coder   - Qwen3-Coder-Next Q2_K     ~26-30GB RAM, 15-25 tok/s
#   qwen2.5-coder - Qwen2.5-Coder 32B Q4_K_M  ~20-24GB RAM
#   qwen3.5-9b    - Qwen 3.5 9B Q8_0          ~10-12GB RAM
#
# Examples:
#   ./start-llama-server.sh                    # gemma4, 65k context
#   ./start-llama-server.sh qwen3-coder        # qwen3-coder-next, 65k context
#   ./start-llama-server.sh qwen2.5-coder 32768  # qwen2.5-coder, 32k context
#   ./start-llama-server.sh gemma4 49152       # gemma4, 48k context

set -e

LLAMA_SERVER="$HOME/.local/bin/llama-cpp/llama-server"
PORT=8089
MODEL_NAME="${1:-gemma4}"

case "$MODEL_NAME" in
    gemma4)
        MODEL="ggml-org/gemma-4-26B-A4B-it-GGUF:Q4_K_M"
        DEFAULT_CONTEXT=65536
        RAM_EST="~17-25GB"
        EXTRA_ARGS=()
        ;;
    qwen3-coder)
        MODEL="Qwen/Qwen3-Coder-Next-GGUF:Q2_K"
        DEFAULT_CONTEXT=65536
        RAM_EST="~26-30GB"
        EXTRA_ARGS=(--temp 1.0 --top-p 0.95 --top-k 40 --min-p 0.01)
        ;;
    qwen2.5-coder)
        MODEL="Qwen/Qwen2.5-Coder-32B-Instruct-GGUF:Q4_K_M"
        DEFAULT_CONTEXT=32768
        RAM_EST="~20-24GB"
        EXTRA_ARGS=()
        ;;
    qwen3.5-9b)
        MODEL="Qwen/Qwen3.5-9B-GGUF:Q8_0"
        DEFAULT_CONTEXT=32768
        RAM_EST="~10-12GB"
        EXTRA_ARGS=()
        ;;
    *)
        echo "Error: Unknown model '$MODEL_NAME'"
        echo "Available models: gemma4, qwen3-coder, qwen2.5-coder, qwen3.5-9b"
        exit 1
        ;;
esac

CONTEXT_SIZE="${2:-$DEFAULT_CONTEXT}"

if [ ! -f "$LLAMA_SERVER" ]; then
    echo "Error: llama-server not found at $LLAMA_SERVER"
    echo "See README.md for build instructions."
    exit 1
fi

# Check if already running
if curl -s http://127.0.0.1:$PORT/health >/dev/null 2>&1; then
    echo "llama-server is already running on port $PORT"
    curl -s http://127.0.0.1:$PORT/health
    exit 0
fi

echo "Starting llama-server on port $PORT with context size $CONTEXT_SIZE..."
echo "Model: $MODEL"
echo "Estimated RAM usage: $RAM_EST (depending on context size)"
echo ""

exec "$LLAMA_SERVER" \
    -hf "$MODEL" \
    --host 0.0.0.0 \
    --port "$PORT" \
    -ngl 99 \
    -fa on \
    -c "$CONTEXT_SIZE" \
    --jinja \
    "${EXTRA_ARGS[@]}"
