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
    "năm": 365 * 24
}

# Hàm chuẩn hóa một lựa chọn thời gian → "X giờ"
def normalize_time_option(option):
    option = option.strip().lower()
    match = re.match(r"([\d\.]+)\s*(giây|phút|giờ|tiếng|ngày|tuần|tháng|năm)", option)
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        hours = value * TIME_UNIT_TO_HOURS.get(unit, 0)
        return f"{round(hours, 3)} giờ"
    return option  # nếu không khớp định dạng → giữ nguyên

# Đường dẫn file
input_path = "/SSD/team_voice/vmnghia/workdir/VLSP/duration_training_dataset.txt"
output_path = "/SSD/team_voice/vmnghia/workdir/VLSP/duration_training_dataset_normalized.txt"

# Ghi log lỗi và tiến trình
num_total, num_success, num_fail = 0, 0, 0

# Xử lý từng dòng
with open(input_path, "r", encoding="utf-8") as f_in, \
     open(output_path, "w", encoding="utf-8") as f_out:

    for i, line in enumerate(f_in):
        line = line.strip()
        if not line:
            continue

        num_total += 1
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"[Lỗi JSON dòng {i+1}]: {e}")
            num_fail += 1
            continue

        try:
            obj["options"] = [normalize_time_option(opt) for opt in obj.get("options", [])]
            f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")
            num_success += 1
        except Exception as e:
            print(f"[Lỗi xử lý dòng {i+1}]: {e}")
            num_fail += 1

print(f"Tổng dòng: {num_total} | Thành công: {num_success} | Lỗi: {num_fail}")
print(f"File output đã ghi tại: {output_path}")
