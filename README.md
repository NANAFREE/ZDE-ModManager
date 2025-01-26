# ZDE ModManager

![GitHub](https://img.shields.io/github/license/nana/mods管理2.0)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/tkinter-8.6%2B-blue)
![PyInstaller](https://img.shields.io/badge/PyInstaller-3.6%2B-blue)

## 简介
ZDE ModManager 是一款用于管理《僵尸毁灭工程》(Project Zomboid) Mod的工具。它可以帮助你轻松地复制、移动和删除Mods，并生成 Mods_info.json 文件以便于版本控制和同步。

## 功能
- **选择源目录和目标目录**：指定包含Mods的源目录和需要复制到的目标目录。
- **复制选定的Mods**：从源目录复制选定的Mods到目标目录，并更新 Mods_info.json 文件。
- **移动 Mods**：通过创意工坊ID将Mods从源目录移动到目标目录。
- **生成 Mods_info.json**：自动生成或更新 Mods_info.json 文件，记录每个Mod的创意工坊ID。
- **比较Mods**：选择一个远程的 Mods_info.json 文件并与本地进行比较，找出本地和远程缺少的Mods。
- **导出创意工坊ID**：将选定的Mods的创意工坊ID导出为txt文件。
- **计算Mods总大小**：计算选定的Mods文件夹的总大小，并显示在界面上。
- **删除选定的目标Mods**：从目标目录中删除选定的Mods，并更新 Mods_info.json 文件。

## 使用方法
1. 从源目录选择包含Mods的文件夹。
2. 从目标目录选择你需要复制Mods到的文件夹。
3. 在源Mods列表框中选择需要复制的Mods。
4. 点击“开始复制已选择的mods到目标目录”按钮。
5. 你也可以选择“生成Mods_info.json”来生成或更新 Mods_info.json 文件。
6. 使用“选择文件来比较本地和远程缺少的Mods”来比较本地和远程的Mods信息。
7. 使用“导出源Mods创意工坊ID”将所选Mods的创意工坊ID导出为txt文件。
8. 使用“计算源Mods总大小”来计算选定的Mods的总大小。
9. 使用“删除选定的目标Mods”来删除目标目录中不需要的Mods。

## 技术栈
- **Python**：用于编写脚本逻辑。
- **Tkinter**：用于构建用户界面。
- **PyInstaller**：用于将Python脚本打包成独立的可执行文件。

## 开源许可
本项目基于MIT协议开源，任何人可以自由使用、修改、分发本项目的代码。

## 联系方式
如果你有任何问题或建议，欢迎通过以下方式联系作者：
- 邮箱：nana@example.com
- GitHub：[Nana](https://github.com/nana)

## 致谢
感谢所有为《僵尸毁灭工程》(Project Zomboid)贡献Mod的开发者们！
