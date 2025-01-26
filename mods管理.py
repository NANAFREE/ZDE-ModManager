import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import json

# 定义全局变量
source_directory_entry = None
destination_directory_entry = None
listbox = None
mod_count_label = None
id_map = {}

def load_existing_mods(destination_directory):
    """
    加载目标目录中的现有Mods信息，并尝试通过源目录获取创意工坊ID
    :param destination_directory: 目标目录（包含Mods文件夹的目录）
    :return: 包含现有Mods信息的字典
    """
    existing_mods_info = {}
    for mod in os.listdir(destination_directory):
        mod_path = os.path.join(destination_directory, mod)
        if os.path.isdir(mod_path):
            # 尝试通过id_map获取创意工坊ID
            existing_mods_info[mod] = id_map.get(mod, "")
    return existing_mods_info

def copy_mods(source_directory, destination_directory, selected_mods):
    """
    复制选定的Mods文件夹内的Mods到另一个目录，并更新mods_info.json
    :param source_directory: 源目录（包含Mods文件夹的目录）
    :param destination_directory: 目标目录（将Mods复制到的地方）
    :param selected_mods: 选定的Mods列表
    """
    move_or_copy_mods(source_directory, destination_directory, selected_mods, action='copy')

def move_mods_by_id(source_directory, destination_directory):
    """
    通过创意工坊ID从源目录复制Mods到目标目录，并更新mods_info.json
    :param source_directory: 源目录（包含Mods文件夹的目录）
    :param destination_directory: 目标目录（将Mods复制到的地方）
    """
    # 选择包含创意工坊ID的txt文件
    id_file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title="选择包含创意工坊ID的文件")
    if not id_file_path:
        return

    # 读取txt文件中的ID列表
    with open(id_file_path, 'r', encoding='utf-8') as file:
        id_list = file.read().strip().split(',')

    # 检查源目录是否存在
    if not os.path.exists(source_directory):
        messagebox.showerror("错误", "源目录不存在，请检查路径是否正确。")
        return

    # 检查目标目录是否存在
    if not os.path.exists(destination_directory):
        # 目标目录不存在时创建它
        os.makedirs(destination_directory)

    # 读取或初始化JSON文档
    json_path = os.path.join(destination_directory, "mods_info.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            mods_info = json.load(file)
    else:
        mods_info = {"mods_count": 0, "mods": {}}

    # 加载目标目录中的现有Mods信息
    existing_mods_info = load_existing_mods(destination_directory)
    mods_info["mods"].update(existing_mods_info)

    missing_ids = []

    # 遍历源目录内的所有文件和子文件夹
    for item in os.listdir(source_directory):
        item_path = os.path.join(source_directory, item)
        if os.path.isdir(item_path):
            mod_folder_path = os.path.join(item_path, "mods")
            if os.path.exists(mod_folder_path):
                for mod in os.listdir(mod_folder_path):
                    mod_item_path = os.path.join(mod_folder_path, mod)
                    if os.path.isdir(mod_item_path) and item in id_list:
                        destination_mod_path = os.path.join(destination_directory, mod)
                        if os.path.exists(destination_mod_path):
                            # 如果目标目录中已经存在同名文件，直接覆盖
                            shutil.rmtree(destination_mod_path)  # 删除已存在的目录
                        shutil.copytree(mod_item_path, destination_mod_path)  # 修改为复制操作
                        print(f"已复制 {mod_item_path} 到 {destination_mod_path}")

                        # 更新mods_info
                        mods_info["mods"][mod] = item  # 使用创意工坊ID作为值

                        # 从id_list中移除已处理的ID
                        id_list.remove(item)
                    elif mod in id_list:
                        # 如果Mod名称直接匹配
                        mod_item_path = os.path.join(mod_folder_path, mod)
                        destination_mod_path = os.path.join(destination_directory, mod)
                        if os.path.exists(destination_mod_path):
                            # 如果目标目录中已经存在同名文件，直接覆盖
                            shutil.rmtree(destination_mod_path)  # 删除已存在的目录
                        shutil.copytree(mod_item_path, destination_mod_path)  # 修改为复制操作
                        print(f"已复制 {mod_item_path} 到 {destination_mod_path}")

                        # 更新mods_info
                        mods_info["mods"][mod] = item  # 使用创意工坊ID作为值

                        # 从id_list中移除已处理的ID
                        id_list.remove(item)

    # 剩余的id_list即为缺失的ID
    missing_ids = id_list

    # 更新mods_info中的mods_count
    mods_info["mods_count"] = len(mods_info["mods"])

    # 保存更新后的JSON文档
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(mods_info, file, ensure_ascii=False, indent=4)

    if missing_ids:
        messagebox.showwarning("警告", f"以下创意工坊ID在源目录中未找到：{', '.join(missing_ids)}")
        export_missing_ids_button = tk.Button(root, text="导出缺失的创意工坊ID", command=lambda: export_missing_ids(missing_ids))
        export_missing_ids_button.pack(pady=5)
    else:
        messagebox.showinfo("完成", "选定的Mods复制完成，并更新了mods_info.json。")

def export_missing_ids(mods, title="导出缺失的创意工坊ID"):
    # 获取创意工坊ID
    id_list = mods
    
    # 选择保存位置
    save_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title=title)
    if not save_file_path:
        return
    
    # 将ID列表保存为txt文件
    with open(save_file_path, 'w', encoding='utf-8') as file:
        file.write(','.join(id_list))
    
    messagebox.showinfo("完成", f"创意工坊ID已导出到 {save_file_path}")

def move_or_copy_mods(source_directory, destination_directory, selected_mods, action='copy'):
    """
    复制或移动选定的Mods文件夹内的Mods到另一个目录，并更新mods_info.json
    :param source_directory: 源目录（包含Mods文件夹的目录）
    :param destination_directory: 目标目录（将Mods复制到的地方）
    :param selected_mods: 选定的Mods列表
    :param action: 动作，'copy' 或 'move'
    """
    # 检查源目录是否存在
    if not os.path.exists(source_directory):
        messagebox.showerror("错误", "源目录不存在，请检查路径是否正确。")
        return

    # 检查目标目录是否存在
    if not os.path.exists(destination_directory):
        # 目标目录不存在时创建它
        os.makedirs(destination_directory)

    # 读取或初始化JSON文档
    json_path = os.path.join(destination_directory, "mods_info.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            mods_info = json.load(file)
    else:
        mods_info = {"mods_count": 0, "mods": {}}

    # 加载目标目录中的现有Mods信息
    existing_mods_info = load_existing_mods(destination_directory)
    mods_info["mods"].update(existing_mods_info)

    # 遍历源目录内的所有文件和子文件夹
    for item in os.listdir(source_directory):
        item_path = os.path.join(source_directory, item)
        if os.path.isdir(item_path):
            mod_folder_path = os.path.join(item_path, "mods")
            if os.path.exists(mod_folder_path):
                for mod in os.listdir(mod_folder_path):
                    mod_item_path = os.path.join(mod_folder_path, mod)
                    if os.path.isdir(mod_item_path) and mod in selected_mods:
                        destination_mod_path = os.path.join(destination_directory, mod)
                        if os.path.exists(destination_mod_path):
                            # 如果目标目录中已经存在同名文件，直接覆盖
                            shutil.rmtree(destination_mod_path)  # 删除已存在的目录
                        if action == 'copy':
                            shutil.copytree(mod_item_path, destination_mod_path)
                        elif action == 'move':
                            shutil.move(mod_item_path, destination_mod_path)
                        print(f"已{action} {mod_item_path} 到 {destination_mod_path}")

                        # 更新mods_info
                        mods_info["mods"][mod] = id_map.get(mod, item)  # 使用id_map获取创意工坊ID

    # 更新mods_info中的mods_count
    mods_info["mods_count"] = len(mods_info["mods"])

    # 保存更新后的JSON文档
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(mods_info, file, ensure_ascii=False, indent=4)

    messagebox.showinfo("完成", f"选定的Mods{action}完成，并更新了mods_info.json。")

def select_source_directory():
    directory = filedialog.askdirectory()
    if source_directory_entry:
        source_directory_entry.delete(0, tk.END)
        source_directory_entry.insert(0, directory)
        listbox.delete(0, tk.END)
        mod_count_label.config(text="Mods总数：0")
        id_map.clear()  # 清除之前存储的ID映射
        if directory:
            load_mods(directory)

def load_mods(source_directory):
    mods_list = set()
    for item in os.listdir(source_directory):
        item_path = os.path.join(source_directory, item)
        if os.path.isdir(item_path):
            mod_folder_path = os.path.join(item_path, "mods")
            if os.path.exists(mod_folder_path):
                for mod in os.listdir(mod_folder_path):
                    mod_item_path = os.path.join(mod_folder_path, mod)
                    if os.path.isdir(mod_item_path):
                        mods_list.add(mod)
                        id_map[mod] = item  # 存储mod与创意工坊ID的映射
    for mod in mods_list:
        listbox.insert(tk.END, mod)
    mod_count_label.config(text=f"Mods总数：{len(mods_list)}")

def select_destination_directory():
    directory = filedialog.askdirectory()
    if destination_directory_entry:
        destination_directory_entry.delete(0, tk.END)
        destination_directory_entry.insert(0, directory)

def start_copying():
    source_directory = source_directory_entry.get()
    destination_directory = destination_directory_entry.get()
    
    # 检查目录是否为空
    if not source_directory:
        messagebox.showwarning("警告", "请选择源目录。")
        return
    if not destination_directory:
        messagebox.showwarning("警告", "请选择目标目录。")
        return
    
    selected_mods = listbox.curselection()
    if not selected_mods:
        messagebox.showwarning("警告", "请选择需要复制的Mods。")
        return
    
    selected_mods = [listbox.get(index) for index in selected_mods]
    copy_mods(source_directory, destination_directory, selected_mods)

def export_mod_ids():
    selected_mods = listbox.curselection()
    if not selected_mods:
        messagebox.showwarning("警告", "请选择需要导出ID的Mods。")
        return
    
    selected_mods = [listbox.get(index) for index in selected_mods]
    
    # 获取创意工坊ID
    id_list = [id_map[mod] for mod in selected_mods]
    
    # 选择保存位置
    save_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title="保存文件")
    if not save_file_path:
        return
    
    # 将ID列表保存为txt文件
    with open(save_file_path, 'w', encoding='utf-8') as file:
        file.write(','.join(id_list))
    
    messagebox.showinfo("完成", f"创意工坊ID已导出到 {save_file_path}")

def select_all_mods():
    if listbox:
        listbox.select_set(0, tk.END)  # 选中所有项目

def compare_mods():
    local_directory = destination_directory_entry.get()  # 使用目标目录作为本地目录
    
    # 检查本地目录是否存在
    if not os.path.exists(local_directory):
        messagebox.showerror("错误", "目标目录不存在，请检查路径是否正确。")
        return

    # 选择远程mods_info.json文件
    remote_json_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title="选择远程mods_info.json文件")
    if not remote_json_path:
        return

    local_json_path = os.path.join(local_directory, "mods_info.json")

    # 检查本地mods_info.json是否存在
    if not os.path.exists(local_json_path):
        messagebox.showerror("错误", "本地mods_info.json不存在，请检查路径是否正确。")
        return

    # 读取本地和远程的mods_info.json
    with open(local_json_path, 'r', encoding='utf-8') as file:
        local_mods_info = json.load(file)
    with open(remote_json_path, 'r', encoding='utf-8') as file:
        remote_mods_info = json.load(file)

    # 获取本地和远程的mods集合
    local_mods = set(local_mods_info["mods"].keys())
    remote_mods = set(remote_mods_info["mods"].keys())

    # 找出本地缺少的mods和远程缺少的mods
    missing_on_local = remote_mods - local_mods
    missing_on_remote = local_mods - remote_mods

    # 创建结果窗口
    result_window = tk.Toplevel()
    result_window.title("Mods比较结果")
    result_window.geometry("400x300")

    # 创建并放置结果标签
    result_label = tk.Label(result_window, text="Mods比较结果：")
    result_label.pack(pady=5)

    # 创建并放置结果文本框
    result_text = tk.Text(result_window, width=50, height=10)
    result_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

    # 显示结果
    if missing_on_local:
        result_text.insert(tk.END, "本地缺少的Mods:\n")
        for mod in missing_on_local:
            result_text.insert(tk.END, f"- {mod} (ID: {remote_mods_info['mods'][mod]})\n")
        result_text.insert(tk.END, "\n")
    if missing_on_remote:
        result_text.insert(tk.END, "远程缺少的Mods:\n")
        for mod in missing_on_remote:
            result_text.insert(tk.END, f"- {mod} (ID: {local_mods_info['mods'][mod]})\n")

    if not missing_on_local and not missing_on_remote:
        result_text.insert(tk.END, "两个设备上的Mods完全一致。")
    else:
        result_text.insert(tk.END, "请检查上述结果并进行相应的操作。")

    def export_missing_ids(mods, id_map, title="导出ID"):
        # 获取创意工坊ID
        id_list = [id_map[mod] for mod in mods]
        
        # 选择保存位置
        save_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title=title)
        if not save_file_path:
            return
        
        # 将ID列表保存为txt文件
        with open(save_file_path, 'w', encoding='utf-8') as file:
            file.write(','.join(id_list))
        
        messagebox.showinfo("完成", f"创意工坊ID已导出到 {save_file_path}")

    # 创建一个Frame来放置按钮
    button_frame = tk.Frame(result_window)
    button_frame.pack(pady=10)

    # 创建并放置导出本地缺少的ID按钮
    if missing_on_local:
        export_local_button = tk.Button(button_frame, text="导出本地缺少的ID", command=lambda: export_missing_ids(missing_on_local, remote_mods_info["mods"]))
        export_local_button.pack(side=tk.LEFT, padx=10)

    # 创建并放置导出远程缺少的ID按钮
    if missing_on_remote:
        export_remote_button = tk.Button(button_frame, text="导出远程缺少的ID", command=lambda: export_missing_ids(missing_on_remote, local_mods_info["mods"]))
        export_remote_button.pack(side=tk.LEFT, padx=10)

    # 创建并放置关闭按钮
    close_button = tk.Button(button_frame, text="关闭", command=result_window.destroy)
    close_button.pack(side=tk.LEFT, padx=10)


def main():
    global source_directory_entry, destination_directory_entry, listbox, mod_count_label, root

    # 创建主窗口
    root = tk.Tk()
    root.title("Mods复制工具")
    root.geometry("800x600")

    # 创建左侧框架
    left_frame = tk.Frame(root, width=350)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

    # 创建右侧框架
    right_frame = tk.Frame(root, width=450)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

    # 左侧框架：源目录选择
    source_directory_label = tk.Label(left_frame, text="源目录（包含Mods文件夹的目录）：")
    source_directory_label.pack(pady=5)
    source_directory_entry = tk.Entry(left_frame, width=50)
    source_directory_entry.pack(pady=5)
    source_directory_button = tk.Button(left_frame, text="选择目录", command=select_source_directory)
    source_directory_button.pack(pady=5)

    # 左侧框架：目标目录选择
    destination_directory_label = tk.Label(left_frame, text="目标目录（将Mods复制到的地方）：")
    destination_directory_label.pack(pady=5)
    destination_directory_entry = tk.Entry(left_frame, width=50)
    destination_directory_entry.pack(pady=5)
    destination_directory_button = tk.Button(left_frame, text="选择目录", command=select_destination_directory)
    destination_directory_button.pack(pady=5)

    # 左侧框架：操作按钮
    button_frame_left = tk.Frame(left_frame)
    button_frame_left.pack(pady=20)

    start_button = tk.Button(button_frame_left, text="开始复制", command=start_copying)
    start_button.pack(side=tk.TOP, padx=10, pady=5)

    compare_button = tk.Button(button_frame_left, text="比较Mods", command=compare_mods)
    compare_button.pack(side=tk.TOP, padx=10, pady=5)
    move_by_id_button = tk.Button(button_frame_left, text="通过创意工坊ID从源目录复制目标目录Mods", command=lambda: move_mods_by_id(source_directory_entry.get(), destination_directory_entry.get()))
    move_by_id_button.pack(side=tk.TOP, padx=10, pady=5)

    # 右侧框架：Mods列表框
    listbox_label = tk.Label(right_frame, text="请选择需要复制或导出ID的Mods：")
    listbox_label.pack(pady=5)
    listbox = tk.Listbox(right_frame, selectmode=tk.MULTIPLE, width=50, height=20)
    listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

    # 右侧框架：Mods总数标签
    mod_count_label = tk.Label(right_frame, text="Mods总数：0")
    mod_count_label.pack(pady=5)

    # 右侧框架：操作按钮
    button_frame_right = tk.Frame(right_frame)
    button_frame_right.pack(pady=20)

    select_all_button = tk.Button(button_frame_right, text="全选", command=select_all_mods)
    select_all_button.pack(side=tk.LEFT, padx=10)

    export_button = tk.Button(button_frame_right, text="导出创意工坊ID", command=export_mod_ids)
    export_button.pack(side=tk.LEFT, padx=10)

    # 进入主循环
    root.mainloop()

if __name__ == "__main__":
    main()
