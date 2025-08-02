import json
import re

# Bảng quy đổi đơn vị → giờ
TIME_UNIT_TO_HOURS = {
    "giây": 1 / 3600,
    "phút": 1 / 60,
    "giờ": 1,
    "tiếng": 1,
    "ngày": 24,
    "tuần": 7 * 24,
    "tháng": 30 * 24,
    "năm": 365 * 24, 
    "thế kỷ": 100 * 365 * 24
}

# Hàm chuẩn hóa một lựa chọn thời gian → "X giờ"
def normalize_time_option(option):
    option = option.strip().lower()
    match = re.match(r"([\d\.]+)\s*(giây|phút|giờ|tiếng|ngày|tuần|tháng|năm)", option)
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        hours = value * TIME_UNIT_TO_HOURS[unit]
        return f"{round(hours, 3)} giờ"
    return option  # nếu không khớp định dạng → giữ nguyên

# Đường dẫn file
input_path = "/Users/chuanbico/Work/VLSP/duration_training_dataset.json"
output_path = "/Users/chuanbico/Work/VLSP/duration_training_dataset_normalize.json"

# Đọc toàn bộ file và tách từng object
with open(input_path, "r", encoding="utf-8") as f:
    content = f.read()

# Tách từng JSON object dùng regex
objects = re.findall(r'{.*?}(?=\s*{|\s*$)', content, re.DOTALL)

num_total, num_success, num_fail = 0, 0, 0

with open(output_path, "w", encoding="utf-8") as f_out:
    for i, obj_str in enumerate(objects, 1):
        num_total += 1
        try:
            obj = json.loads(obj_str)
            if not isinstance(obj, dict):
                raise ValueError("Không phải dict JSON")

            obj["options"] = [normalize_time_option(opt) for opt in obj.get("options", [])]
            f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")
            num_success += 1

        except Exception as e:
            print(f"[Lỗi dòng {i}]: {e}")
            num_fail += 1

print(f"Tổng dòng: {num_total} | Thành công: {num_success} | Lỗi: {num_fail}")
print(f"File output đã ghi tại: {output_path}")
