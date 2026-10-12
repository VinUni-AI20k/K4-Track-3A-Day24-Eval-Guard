"""Shared configuration for K4 / Track 3A: Eval + Guardrail Stack."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")  # Optional: for HuggingFace models

# --- LLM provider (OpenAI-compatible) ---
# Gemini dùng qua endpoint OpenAI-compatible: đặt OPENAI_API_KEY=<Gemini key> và
# OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/ trong .env.
# OpenAI SDK tự đọc OPENAI_BASE_URL, nên setup/judge/NeMo đều trỏ cùng provider.
LLM_API_KEY = OPENAI_API_KEY
LLM_BASE_URL = os.getenv("OPENAI_BASE_URL") or None
USE_GEMINI = bool(LLM_BASE_URL and "generativelanguage.googleapis.com" in LLM_BASE_URL)
if USE_GEMINI:
    # Free tier giới hạn request/ngày theo TỪNG model → src/llm.py xoay vòng khi model hết quota.
    LLM_MODELS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash",
                  "gemini-flash-latest", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite",
                  "gemini-flash-lite-latest"]
    LLM_REASONING_EFFORT = "none"  # tắt thinking: nhanh hơn, không ăn max_tokens
    EVAL_EMBEDDING_MODEL = "gemini-embedding-001"
else:
    LLM_MODELS = ["gpt-4o-mini"]
    LLM_REASONING_EFFORT = None
    EVAL_EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = LLM_MODELS[0]


def get_llm_client():
    """OpenAI SDK client trỏ tới provider đang cấu hình (OpenAI hoặc Gemini)."""
    from openai import OpenAI
    return OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL, max_retries=6)

# --- Qdrant (same as Day 18) ---
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "lab24_production"
NAIVE_COLLECTION = "lab24_naive"

# --- Embedding (same as Day 18) ---
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

# --- Chunking (same as Day 18) ---
HIERARCHICAL_PARENT_SIZE = 2048
HIERARCHICAL_CHILD_SIZE = 256
SEMANTIC_THRESHOLD = 0.85

# --- Search (same as Day 18) ---
BM25_TOP_K = 20
DENSE_TOP_K = 20
HYBRID_TOP_K = 20
RERANK_TOP_K = 3

# --- Paths ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
FIXTURES_DIR = os.path.join(ROOT_DIR, "fixtures")
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")
TEST_SET_PATH = os.path.join(FIXTURES_DIR, "test_set_50q.json")
ANSWERS_PATH = os.path.join(ARTIFACTS_DIR, "answers_50q.json")
HUMAN_LABELS_PATH = os.path.join(FIXTURES_DIR, "human_labels_10q.json")
ADVERSARIAL_SET_PATH = os.path.join(FIXTURES_DIR, "adversarial_set_20.json")
CLEAN_SET_PATH = os.path.join(FIXTURES_DIR, "clean_set_8.json")
OUTPUT_SET_PATH = os.path.join(FIXTURES_DIR, "output_set_4.json")
GUARDRAILS_CONFIG_DIR = os.path.join(ROOT_DIR, "guardrails")
PAIR_QUESTION_IDS = (1, 5, 12, 21, 41)

# --- LLM Judge ---
GENERATION_MODEL = LLM_MODEL
JUDGE_MODEL = LLM_MODEL

# --- Guardrail latency budget ---
LATENCY_BUDGET_P95_MS = 500  # Full guard target; Task 12 currently measures input guards only.
PRESIDIO_LANGUAGE = "en"    # Presidio base language; custom VN recognizers added via PatternRecognizer
