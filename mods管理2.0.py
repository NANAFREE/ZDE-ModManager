import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json

#作者: Nana
#版本: 2.0
#日期: 2024.1.26
# 本项目基于MIT协议开源，任何人可以自由使用、修改、分发本项目的代码。

# 定义全局变量
source_directory_entry = None
destination_directory_entry = None
source_listbox = None
destination_listbox = None
mod_count_label = None
id_map = {}
destination_mods_info = {}

#打包exe命令: pyinstaller --windowed -F --icon=icon.ppm mods管理2.0.py

def load_existing_mods(destination_directory):
    """
    加载目标目录中的现有Mods信息
    :param destination_directory: 目标目录（包含Mods文件夹的目录）
    :return: 包含现有Mods信息的字典
    """
    existing_mods_info = {}
    for mod in os.listdir(destination_directory):
        mod_path = os.path.join(destination_directory, mod)
        if os.path.isdir(mod_path):
            existing_mods_info[mod] = ""
    return existing_mods_info

def find_creative_workshop_id(mod_name, source_directory):
    """
    通过源目录查找指定Mod的创意工坊ID
    :param mod_name: Mod名称
    :param source_directory: 源目录（包含Mods文件夹的目录）
    :return: 创意工坊ID，如果找不到则返回空字符串
    """
    for item in os.listdir(source_directory):
        item_path = os.path.join(source_directory, item)
        if os.path.isdir(item_path):
            mod_folder_path = os.path.join(item_path, "mods")
            if os.path.exists(mod_folder_path) and mod_name in os.listdir(mod_folder_path):
                return item
    return ""

def generate_mods_info(source_directory, destination_directory):
    """
    生成mods_info.json文件
    :param source_directory: 源目录（包含Mods文件夹的目录）
    :param destination_directory: 目标目录（包含Mods文件夹的目录）
    """
    if not os.path.exists(source_directory):
        messagebox.showerror("错误", "源目录不存在，请检查路径是否正确。")
        return

    if not os.path.exists(destination_directory):
        messagebox.showerror("错误", "目标目录不存在，请检查路径是否正确。")
        return

    mods_info = {"mods_count": 0, "mods": {}}
    for mod in os.listdir(destination_directory):
        mod_path = os.path.join(destination_directory, mod)
        if os.path.isdir(mod_path):
            # 尝试通过源目录获取创意工坊ID
            workshop_id = find_creative_workshop_id(mod, source_directory)
            mods_info["mods"][mod] = workshop_id
    
    mods_info["mods_count"] = len(mods_info["mods"])
    json_path = os.path.join(destination_directory, "mods_info.json")
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(mods_info, file, ensure_ascii=False, indent=4)
    messagebox.showinfo("完成", "mods_info.json文件已生成。")

def copy_mods(source_directory, destination_directory, selected_mods):
    """
    复制选定的Mods文件夹内的Mods到另一个目录，并更新mods_info.json
    :param source_directory: 源目录（包含Mods文件夹的目录）
    :param destination_directory: 目标目录（将Mods复制到的地方）
    :param selected_mods: 选定的Mods列表
    """
    move_or_copy_mods(source_directory, destination_directory, selected_mods, action='copy')

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

    # 创建进度条
    progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)
    progress["maximum"] = len(selected_mods)
    progress["value"] = 0

    # 设定一个虚假的进度
    fake_max_value = 0.9 * len(selected_mods)
    for mod in selected_mods:
        mod_item_path = os.path.join(source_directory, id_map[mod], "mods", mod)
        if os.path.exists(mod_item_path):
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
            workshop_id = find_creative_workshop_id(mod, source_directory)
            mods_info["mods"][mod] = workshop_id

            # 更新进度条
            if progress["value"] < fake_max_value:
                progress["value"] += 1
            root.update()

    # 更新进度条到100%
    progress["value"] = len(selected_mods)
    root.update()

    # 更新mods_info中的mods_count
    mods_info["mods_count"] = len(mods_info["mods"])

    # 保存更新后的JSON文档
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(mods_info, file, ensure_ascii=False, indent=4)

    progress.destroy()
    messagebox.showinfo("完成", f"选定的Mods{action}完成，并更新了mods_info.json。")
    # 刷新目标目录的列表
    load_destination_mods(destination_directory)

def select_source_directory():
    directory = filedialog.askdirectory()
    if source_directory_entry:
        source_directory_entry.delete(0, tk.END)
        source_directory_entry.insert(0, directory)
        source_listbox.delete(0, tk.END)
        mod_count_label.config(text="Mods总数：0")
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
        source_listbox.insert(tk.END, mod)
    mod_count_label.config(text=f"Mods总数：{len(mods_list)}")

def select_destination_directory():
    directory = filedialog.askdirectory()
    if destination_directory_entry:
        destination_directory_entry.delete(0, tk.END)
        destination_directory_entry.insert(0, directory)
        # 加载目标目录中的mods信息
        destination_directory = destination_directory_entry.get()
        if os.path.exists(destination_directory):
            load_destination_mods(destination_directory)

def load_destination_mods(destination_directory):
    global destination_mods_info
    destination_mods_info = {}
    destination_listbox.delete(0, tk.END)
    if os.path.exists(os.path.join(destination_directory, "mods_info.json")):
        with open(os.path.join(destination_directory, "mods_info.json"), 'r', encoding='utf-8') as file:
            destination_mods_info = json.load(file)
        for mod in destination_mods_info["mods"].keys():
            destination_listbox.insert(tk.END, mod)

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
    
    selected_mods = source_listbox.curselection()
    if not selected_mods:
        messagebox.showwarning("警告", "请选择需要复制的Mods。")
        return
    
    selected_mods = [source_listbox.get(index) for index in selected_mods]
    copy_mods(source_directory, destination_directory, selected_mods)

def export_mod_ids():
    selected_mods = source_listbox.curselection()
    if not selected_mods:
        messagebox.showwarning("警告", "请选择需要导出ID的Mods。")
        return
    
    selected_mods = [source_listbox.get(index) for index in selected_mods]
    
    # 获取创意工坊ID
    id_list = [id_map[mod] for mod in selected_mods]
    
    # 选择保存位置
    save_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title="保存文件")
    if not save_file_path:
        return
    
    # 将ID列表保存为txt文件
    with open(save_file_path, 'w', encoding='utf-8') as file:
        file.write(','.join(id_list))
    
    messagebox.showinfo("完成", f"创意工坊ID已导出到 {save_file_path}。")

def select_all_mods():
    if source_listbox:
        source_listbox.select_set(0, tk.END)  # 选中所有项目

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

    # 找出本地和远程的mods差异
    missing_on_local = remote_mods - local_mods
    missing_on_remote = local_mods - remote_mods

    # 创建结果窗口
    result_window = tk.Toplevel()
    result_window.title("Mods比较结果")
    result_window.geometry("600x400")

    # 创建并放置结果标签
    result_label = tk.Label(result_window, text="Mods比较结果：")
    result_label.pack(pady=5)

    # 创建并放置结果文本框
    result_text = tk.Text(result_window, width=70, height=15)
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
        
        messagebox.showinfo("完成", f"创意工坊ID已导出到 {save_file_path}。")

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

def delete_mods():
    selected_mods = destination_listbox.curselection()
    if not selected_mods:
        messagebox.showwarning("警告", "请选择需要删除的Mods。")
        return
    
    selected_mods = [destination_listbox.get(index) for index in selected_mods]
    destination_directory = destination_directory_entry.get()

    for mod in selected_mods:
        mod_path = os.path.join(destination_directory, mod)
        if os.path.exists(mod_path):
            shutil.rmtree(mod_path)  # 删除mods
            destination_listbox.delete(destination_listbox.get(0, tk.END).index(mod))  # 从列表框中删除

    # 更新mods_info.json
    json_path = os.path.join(destination_directory, "mods_info.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            mods_info = json.load(file)
        for mod in selected_mods:
            if mod in mods_info["mods"]:
                del mods_info["mods"][mod]
        mods_info["mods_count"] = len(mods_info["mods"])
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(mods_info, file, ensure_ascii=False, indent=4)
    messagebox.showinfo("完成", "选定的Mods已删除，并更新了mods_info.json。")
    # 刷新目标目录的列表
    load_destination_mods(destination_directory)

def move_mods_by_id(source_directory, destination_directory):
    """
    通过创意工坊ID将Mods从源目录复制到目标目录
    :param source_directory: 源目录（包含Mods文件夹的目录）
    :param destination_directory: 目标目录（将Mods复制到的地方）
    """
    if not os.path.exists(source_directory):
        messagebox.showerror("错误", "源目录不存在，请检查路径是否正确。")
        return

    if not os.path.exists(destination_directory):
        messagebox.showerror("错误", "目标目录不存在，请检查路径是否正确。")
        return

    # 创建进度条
    progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)
    progress["maximum"] = len(id_map)
    progress["value"] = 0

    # 设定一个虚假的进度
    fake_max_value = 0.9 * len(id_map)
    for mod, workshop_id in id_map.items():
        mod_item_path = os.path.join(source_directory, workshop_id, "mods", mod)
        if os.path.exists(mod_item_path):
            destination_mod_path = os.path.join(destination_directory, mod)
            if os.path.exists(destination_mod_path):
                # 如果目标目录中已经存在同名文件，直接覆盖
                shutil.rmtree(destination_mod_path)  # 删除已存在的目录
            shutil.move(mod_item_path, destination_mod_path)
            print(f"已移动 {mod_item_path} 到 {destination_mod_path}")

            # 更新进度条
            if progress["value"] < fake_max_value:
                progress["value"] += 1
            root.update()

    # 更新进度条到100%
    progress["value"] = len(id_map)
    root.update()

    progress.destroy()
    messagebox.showinfo("完成", "Mods已通过创意工坊ID移动完成。")
    # 刷新目标目录的列表
    load_destination_mods(destination_directory)

def main():
    global source_directory_entry, destination_directory_entry, source_listbox, destination_listbox, mod_count_label, root

    # 创建主窗口
    root = tk.Tk()
    root.title("ZDE ModManager")
    root.geometry("800x600")
    # 更改窗口图标
    root.iconphoto(True, tk.PhotoImage(file=r"d:\github\僵尸毁灭工程脚本\icon.ppm"))


    # 创建左侧框架
    left_frame = tk.Frame(root, width=350)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

    # 创建右侧框架
    right_frame = tk.Frame(root, width=450)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

    # 左侧框架：源目录选择
    source_directory_label = tk.Label(left_frame, text="源目录（steamapps/common/创意工坊）：")
    source_directory_label.pack(pady=5)
    source_directory_entry = tk.Entry(left_frame, width=50)
    source_directory_entry.pack(pady=5)
    source_directory_button = tk.Button(left_frame, text="选择目录", command=select_source_directory)
    source_directory_button.pack(pady=5)

    # 左侧框架：目标目录选择
    destination_directory_label = tk.Label(left_frame, text="目标目录（PZsave/mods）：")
    destination_directory_label.pack(pady=5)
    destination_directory_entry = tk.Entry(left_frame, width=50)
    destination_directory_entry.pack(pady=5)
    destination_directory_button = tk.Button(left_frame, text="选择目录", command=select_destination_directory)
    destination_directory_button.pack(pady=5)

    # 左侧框架：操作按钮
    button_frame_left = tk.Frame(left_frame)
    button_frame_left.pack(pady=20)

    start_button = tk.Button(button_frame_left, text="开始复制已选择的mods到目标目录", command=start_copying)
    start_button.pack(side=tk.TOP, pady=5)

    compare_button = tk.Button(button_frame_left, text="选择文件来比较本地和远程缺少的Mods", command=compare_mods)
    compare_button.pack(side=tk.TOP, pady=5)

    move_by_id_button = tk.Button(button_frame_left, text="通过创意工坊ID将Mods从源目录复制到目标目录", command=lambda: move_mods_by_id(source_directory_entry.get(), destination_directory_entry.get()))
    move_by_id_button.pack(side=tk.TOP, pady=5)

    generate_info_button = tk.Button(button_frame_left, text="生成Mods_info.json", command=lambda: generate_mods_info(source_directory_entry.get(), destination_directory_entry.get()))
    generate_info_button.pack(side=tk.TOP, pady=5)
    
    #增加注释标签
    # 左侧框架：注释标签
    comment_label = tk.Label(left_frame, text="注：外部删除Mods会引发更新及显示问题，建议在软件内操作")
    comment_label.pack(pady=5)
    comment_label = tk.Label(left_frame, text="第一次打开软件建议选择完目录后点击生成Mods_info.json进行同步")
    comment_label.pack(pady=5)
    

    # 右侧框架：源Mods列表框
    source_listbox_label = tk.Label(right_frame, text="请选择需要复制或导出ID的源Mods：")
    source_listbox_label.pack(pady=5)
    source_listbox = tk.Listbox(right_frame, selectmode=tk.MULTIPLE, width=50, height=10)
    source_listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

    # 右侧框架：目标Mods列表框
    destination_listbox_label = tk.Label(right_frame, text="目标目录中的Mods：")
    destination_listbox_label.pack(pady=5)
    destination_listbox = tk.Listbox(right_frame, selectmode=tk.MULTIPLE, width=50, height=10)
    destination_listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

    # 右侧框架：Mods总数标签
    mod_count_label = tk.Label(right_frame, text="Mods总数：0")
    mod_count_label.pack(pady=5)

    # 右侧框架：操作按钮
    button_frame_right = tk.Frame(right_frame)
    button_frame_right.pack(pady=10)

    select_all_button = tk.Button(button_frame_right, text="全选源Mods", command=select_all_mods)
    select_all_button.pack(side=tk.LEFT, padx=10)

    export_button = tk.Button(button_frame_right, text="导出源Mods创意工坊ID", command=export_mod_ids)
    export_button.pack(side=tk.LEFT, padx=10)

    delete_button = tk.Button(button_frame_right, text="删除选定的目标Mods", command=delete_mods)
    delete_button.pack(side=tk.LEFT, padx=10)

    # display_mods_button = tk.Button(button_frame_right, text="显示目标目录中的Mods列表", command=select_destination_directory)
    # display_mods_button.pack(side=tk.LEFT, padx=10)

    # 进入主循环
    root.mainloop()

if __name__ == "__main__":
    main()
