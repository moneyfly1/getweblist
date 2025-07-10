#!/usr/bin/env python3
"""
文件保护脚本
监控重要数据文件的变化，防止意外删除
"""

import os
import time
import shutil
from datetime import datetime
from pathlib import Path

class FileProtector:
    def __init__(self):
        self.data_dir = "src/database/sspanel_hosts"
        self.classifier_dir = os.path.join(self.data_dir, "classifier")
        self.backup_dir = os.path.join(self.classifier_dir, "backup")
        
        # 确保备份目录存在
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def get_file_info(self, file_path):
        """获取文件信息"""
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'exists': True
            }
        return {'exists': False}
    
    def backup_files(self):
        """备份所有重要的数据文件"""
        print("开始备份数据文件...")
        
        # 备份分类器文件
        if os.path.exists(self.classifier_dir):
            csv_files = [f for f in os.listdir(self.classifier_dir) if f.endswith('.csv')]
            for csv_file in csv_files:
                source_path = os.path.join(self.classifier_dir, csv_file)
                backup_path = os.path.join(self.backup_dir, csv_file)
                
                # 如果备份文件不存在或源文件更新，则创建备份
                if not os.path.exists(backup_path) or \
                   os.path.getmtime(source_path) > os.path.getmtime(backup_path):
                    shutil.copy2(source_path, backup_path)
                    print(f"已备份: {csv_file}")
        
        # 备份数据文件
        if os.path.exists(self.data_dir):
            txt_files = [f for f in os.listdir(self.data_dir) if f.endswith('.txt')]
            for txt_file in txt_files:
                source_path = os.path.join(self.data_dir, txt_file)
                backup_path = os.path.join(self.backup_dir, txt_file)
                
                if not os.path.exists(backup_path) or \
                   os.path.getmtime(source_path) > os.path.getmtime(backup_path):
                    shutil.copy2(source_path, backup_path)
                    print(f"已备份: {txt_file}")
        
        print("备份完成！")
    
    def restore_files(self):
        """从备份恢复文件"""
        print("检查是否需要恢复文件...")
        
        if not os.path.exists(self.backup_dir):
            print("备份目录不存在，无法恢复")
            return
        
        # 恢复分类器文件
        if os.path.exists(self.classifier_dir):
            csv_files = [f for f in os.listdir(self.classifier_dir) if f.endswith('.csv')]
            for csv_file in csv_files:
                source_path = os.path.join(self.classifier_dir, csv_file)
                backup_path = os.path.join(self.backup_dir, csv_file)
                
                # 如果源文件不存在但备份存在，则恢复
                if not os.path.exists(source_path) and os.path.exists(backup_path):
                    shutil.copy2(backup_path, source_path)
                    print(f"已恢复: {csv_file}")
        
        # 恢复数据文件
        if os.path.exists(self.data_dir):
            txt_files = [f for f in os.listdir(self.data_dir) if f.endswith('.txt')]
            for txt_file in txt_files:
                source_path = os.path.join(self.data_dir, txt_file)
                backup_path = os.path.join(self.backup_dir, txt_file)
                
                if not os.path.exists(source_path) and os.path.exists(backup_path):
                    shutil.copy2(backup_path, source_path)
                    print(f"已恢复: {txt_file}")
    
    def monitor_files(self, interval=60):
        """监控文件变化"""
        print(f"开始监控文件变化，检查间隔: {interval}秒")
        print("按 Ctrl+C 停止监控")
        
        last_state = {}
        
        try:
            while True:
                current_state = {}
                
                # 检查分类器文件
                if os.path.exists(self.classifier_dir):
                    csv_files = [f for f in os.listdir(self.classifier_dir) if f.endswith('.csv')]
                    for csv_file in csv_files:
                        file_path = os.path.join(self.classifier_dir, csv_file)
                        current_state[file_path] = self.get_file_info(file_path)
                
                # 检查数据文件
                if os.path.exists(self.data_dir):
                    txt_files = [f for f in os.listdir(self.data_dir) if f.endswith('.txt')]
                    for txt_file in txt_files:
                        file_path = os.path.join(self.data_dir, txt_file)
                        current_state[file_path] = self.get_file_info(file_path)
                
                # 检查文件变化
                for file_path, current_info in current_state.items():
                    if file_path in last_state:
                        last_info = last_state[file_path]
                        
                        # 检查文件是否被删除
                        if last_info['exists'] and not current_info['exists']:
                            print(f"⚠️  警告: 文件被删除: {file_path}")
                            # 尝试从备份恢复
                            backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
                            if os.path.exists(backup_path):
                                shutil.copy2(backup_path, file_path)
                                print(f"✅ 已从备份恢复: {file_path}")
                        
                        # 检查文件大小变化
                        elif last_info['exists'] and current_info['exists']:
                            if current_info['size'] != last_info['size']:
                                print(f"📝 文件已更新: {file_path} (大小: {last_info['size']} -> {current_info['size']})")
                    else:
                        if current_info['exists']:
                            print(f"🆕 新文件: {file_path}")
                
                last_state = current_state
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n监控已停止")
    
    def list_files(self):
        """列出所有数据文件"""
        print("=" * 60)
        print("数据文件列表")
        print("=" * 60)
        
        # 分类器文件
        if os.path.exists(self.classifier_dir):
            csv_files = [f for f in os.listdir(self.classifier_dir) if f.endswith('.csv')]
            print(f"\n分类器文件 ({len(csv_files)} 个):")
            for csv_file in sorted(csv_files):
                file_path = os.path.join(self.classifier_dir, csv_file)
                size = os.path.getsize(file_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"  {csv_file} ({size} bytes, {mtime})")
        
        # 数据文件
        if os.path.exists(self.data_dir):
            txt_files = [f for f in os.listdir(self.data_dir) if f.endswith('.txt')]
            print(f"\n数据文件 ({len(txt_files)} 个):")
            for txt_file in sorted(txt_files):
                file_path = os.path.join(self.data_dir, txt_file)
                size = os.path.getsize(file_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"  {txt_file} ({size} bytes, {mtime})")
        
        # 备份文件
        if os.path.exists(self.backup_dir):
            backup_files = [f for f in os.listdir(self.backup_dir)]
            print(f"\n备份文件 ({len(backup_files)} 个):")
            for backup_file in sorted(backup_files):
                file_path = os.path.join(self.backup_dir, backup_file)
                size = os.path.getsize(file_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"  {backup_file} ({size} bytes, {mtime})")

def main():
    protector = FileProtector()
    
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "backup":
            protector.backup_files()
        elif command == "restore":
            protector.restore_files()
        elif command == "monitor":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            protector.monitor_files(interval)
        elif command == "list":
            protector.list_files()
        else:
            print("用法:")
            print("  python file_protection.py backup   # 备份文件")
            print("  python file_protection.py restore  # 恢复文件")
            print("  python file_protection.py monitor  # 监控文件")
            print("  python file_protection.py list     # 列出文件")
    else:
        print("文件保护工具")
        print("=" * 30)
        print("1. 备份文件")
        print("2. 恢复文件")
        print("3. 监控文件")
        print("4. 列出文件")
        
        choice = input("请选择操作 (1-4): ")
        
        if choice == "1":
            protector.backup_files()
        elif choice == "2":
            protector.restore_files()
        elif choice == "3":
            interval = input("监控间隔(秒): ") or "60"
            protector.monitor_files(int(interval))
        elif choice == "4":
            protector.list_files()
        else:
            print("无效选择")

if __name__ == "__main__":
    main() 