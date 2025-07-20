from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import json
from tqdm import tqdm
import os

# ====== Config ======
HF_TOKEN = "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"
MODEL_ID = "Viet-Mistral/Vistral-7B-Chat"
INPUT_PATH = "/SSD/team_voice/vmnghia/workdir/VLSP/resource/duration_training_dataset_normalized.txt"
OUTPUT_PATH = "/SSD/team_voice/vmnghia/workdir/VLSP/vistral_predictions.txt"
MAX_NEW_TOKENS = 64

# ====== Auth + Load Model ======
print("Đăng nhập Hugging Face...")
login(token=HF_TOKEN)

print(f"Tải model: {MODEL_ID}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=False)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto"
)

chat_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=MAX_NEW_TOKENS
)

# ====== Load Input Data ======
print(f"📄 Đọc dữ liệu từ: {INPUT_PATH}")
with open(INPUT_PATH, 'r', encoding='utf-8') as f:
    data = [json.loads(line.strip()) for line in f if line.strip()]

# ====== Inference Function ======
def classify_option(context, question, option):
    prompt = f"""Bạn hãy trả lời "yes" hoặc "no" cho lựa chọn thời gian dưới đây có phù hợp với ngữ cảnh hay không.

Ngữ cảnh: {context}
Câu hỏi: {question}
Lựa chọn: {option}

Trả lời chỉ bằng "yes" hoặc "no":
"""
    try:
        output = chat_pipeline(prompt)[0]["generated_text"]
        for line in output.split('\n')[::-1]:
            if "yes" in line.lower():
                return "yes"
            if "no" in line.lower():
                return "no"
    except Exception as e:
        print(f"[Lỗi mô hình] {e}")
    return "no"

print("🤖 Đang suy luận...")
output_data = []

for ex in tqdm(data):
    preds = []
    for opt in ex["options"]:
        pred = classify_option(ex["context"], ex["question"], opt)
        preds.append(pred)

    output_data.append({
        "context": ex["context"],
        "question": ex["question"],
        "options": ex["options"],
        "qid": ex["qid"],
        "labels": ex["labels"],
        "predictions": preds
    })

# ====== Save Output ======
print(f"Ghi kết quả ra: {OUTPUT_PATH}")
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for item in output_data:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print("Hoàn tất!")
