import ast
import os

def extract_docstrings(file_path):
    """Trích xuất docstring từ module, class và function."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    docs = []
    
    # 1. Lấy docstring của Module (đầu file)
    module_doc = ast.get_docstring(tree)
    if module_doc:
        docs.append(f"--- MODULE: {os.path.basename(file_path)} ---\n{module_doc}\n")

    for node in tree.body:
        # 2. Lấy docstring của Class
        if isinstance(node, ast.ClassDef):
            class_doc = ast.get_docstring(node)
            if class_doc:
                docs.append(f"  [CLASS] {node.name}:\n    {class_doc}\n")
            
            # Lấy docstring của các hàm bên trong Class
            for sub_node in node.body:
                if isinstance(sub_node, ast.FunctionDef):
                    func_doc = ast.get_docstring(sub_node)
                    if func_doc:
                        docs.append(f"    (Method) {sub_node.name}:\n      {func_doc}")

        # 3. Lấy docstring của các hàm tự do (không nằm trong class)
        elif isinstance(node, ast.FunctionDef):
            func_doc = ast.get_docstring(node)
            if func_doc:
                docs.append(f"  [FUNCTION] {node.name}:\n    {func_doc}\n")

    return "\n".join(docs)

# Danh sách các file cần trích xuất trong đồ án của bạn
target_files = ["algorithms.py", "game_logic.py", "ui.py", "main.py", "settings.py", "sound_manager.py"]

print("Đang trích xuất tài liệu cho báo cáo IT003...\n")

with open("PHU_LUC_DOCSTRING.txt", "w", encoding="utf-8") as output_file:
    for filename in target_files:
        if os.path.exists(filename):
            print(f"Đang xử lý: {filename}")
            file_docs = extract_docstrings(filename)
            output_file.write(f"{'='*60}\n")
            output_file.write(file_docs + "\n\n")
        else:
            print(f"Cảnh báo: Không tìm thấy file {filename}")

print("\nHoàn tất! Bạn có thể mở file 'PHU_LUC_DOCSTRING.txt' để lấy nội dung cho báo cáo.")