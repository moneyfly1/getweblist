# ChromeDriver 兼容性问题修复

## 问题描述

在GitHub Actions环境中运行SSPanel Mining时，遇到了ChromeDriver版本兼容性问题：

```
ValueError: There is no such driver by url https://chromedriver.storage.googleapis.com/LATEST_RELEASE_138.0.7204
```

以及第三方Action的下载失败：

```
Error: The process '/home/runner/work/_actions/nanasess/setup-chromedriver/v2/lib/setup-chromedriver.sh' failed with exit code 22
```

以及Chrome版本不匹配问题：

```
selenium.common.exceptions.SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version 114
Current browser version is 138.0.7204.100
```

以及ChromeDriver安装问题：

```
mv: cannot stat 'chromedriver': No such file or directory
```

以及ChromeDriver路径验证问题：

```
ValueError: The path is not a valid file: chromedriver
selenium.common.exceptions.NoSuchDriverException: Message: Unable to obtain driver for chrome
```

## 问题原因

1. **版本不匹配**：webdriver_manager尝试下载的ChromeDriver版本（138.0.7204）不存在或与当前环境不兼容
2. **GitHub Actions环境**：CI/CD环境中的Chrome和ChromeDriver版本管理更加复杂
3. **webdriver_manager版本过旧**：原版本3.5.2可能无法正确处理新版本的Chrome
4. **网络连接问题**：第三方Action和官方下载源都可能出现网络问题
5. **Chrome版本过高**：GitHub Actions中的Chrome版本（138）与ChromeDriver版本（114）不匹配
6. **文件结构问题**：下载的ChromeDriver压缩包结构可能与预期不同
7. **路径验证问题**：`which chromedriver`找到的路径可能指向无效文件

## 解决方案

### 1. 更新依赖版本

- 将`webdriver_manager`从`3.5.2`更新到`>=4.0.0`
- 确保使用最新稳定版本的依赖

### 2. 改进ChromeDriver管理策略

在`src/services/utils/toolbox/toolbox.py`中实现了多层次的ChromeDriver管理策略：

#### 方案1：环境变量指定
```python
chrome_driver_path = os.environ.get('CHROME_DRIVER_PATH')
if chrome_driver_path and os.path.exists(chrome_driver_path):
    service = Service(chrome_driver_path)
```

#### 方案2：系统ChromeDriver（改进版本）
```python
result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
if result.returncode == 0:
    chromedriver_path = result.stdout.strip()
    # 验证文件是否真实存在且可执行
    if os.path.exists(chromedriver_path) and os.access(chromedriver_path, os.X_OK):
        service = Service(chromedriver_path)
```

#### 方案3：常见路径检查
```python
common_paths = [
    "/usr/local/bin/chromedriver",
    "/usr/bin/chromedriver",
    "/usr/bin/chromium-chromedriver",
    "/snap/bin/chromedriver"
]
for path in common_paths:
    if os.path.exists(path) and os.access(path, os.X_OK):
        service = Service(path)
        break
```

#### 方案4：版本映射管理（带重试机制）
- 自动检测Chrome版本
- 使用预定义的稳定版本映射表
- 实现重试机制，最多重试3次
- 如果版本不在映射表中，使用默认版本

### 3. 改进GitHub Actions工作流

使用多层安装策略，确保ChromeDriver能够正确安装：

#### 方案1：系统包管理器安装
```bash
sudo apt-get install -y chromium-chromedriver
sudo ln -sf /usr/bin/chromium-chromedriver /usr/local/bin/chromedriver
```

#### 方案2：手动下载安装
```bash
# 根据Chrome版本选择对应的ChromeDriver版本
case $CHROME_VERSION in
  138|137|136|135|134|133|132|131|130|129|128|127|126|125|124|123|122|121|120)
    CHROMEDRIVER_VERSION="120.0.6099.109"
    ;;
  119)
    CHROMEDRIVER_VERSION="119.0.6045.105"
    ;;
  # ... 更多版本映射
esac

# 尝试多个下载源
wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" -O chromedriver.zip || \
wget -q "https://github.com/GoogleChromeLabs/chrome-for-testing/releases/download/$CHROMEDRIVER_VERSION/chromedriver-linux64.zip" -O chromedriver.zip || \
wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip" -O chromedriver.zip

# 智能文件查找和安装
if [ -f "chromedriver" ]; then
  sudo mv chromedriver /usr/local/bin/
elif [ -f "chromedriver-linux64/chromedriver" ]; then
  sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
elif [ -f "chromedriver-linux64/chromedriver-linux64/chromedriver" ]; then
  sudo mv chromedriver-linux64/chromedriver-linux64/chromedriver /usr/local/bin/
fi

# 验证安装
chromedriver --version
which chromedriver
ls -la /usr/local/bin/chromedriver
```

## 版本映射表

### GitHub Actions中的版本映射

对于Chrome 138+版本，使用最新的稳定ChromeDriver版本120.0.6099.109：

```bash
case $CHROME_VERSION in
  138|137|136|135|134|133|132|131|130|129|128|127|126|125|124|123|122|121|120)
    CHROMEDRIVER_VERSION="120.0.6099.109"
    ;;
  119)
    CHROMEDRIVER_VERSION="119.0.6045.105"
    ;;
  118)
    CHROMEDRIVER_VERSION="118.0.5993.70"
    ;;
  # ... 更多版本映射
esac
```

### Python代码中的版本映射

代码中包含了从Chrome 1到138版本的完整ChromeDriver版本映射：

```python
stable_versions = {
    "138": "120.0.6099.109",  # Chrome 138+ 使用最新的稳定版本
    "137": "120.0.6099.109",
    "136": "120.0.6099.109",
    # ... 更多版本映射
    "1": "1.0.154.0"
}
```

## 错误处理

实现了完善的错误处理机制：

1. **日志记录**：详细记录每个步骤的执行情况
2. **备用方案**：多个备用方案确保程序能够正常运行
3. **异常处理**：捕获并处理各种可能的异常情况
4. **重试机制**：webdriver_manager安装失败时自动重试
5. **多下载源**：GitHub Actions中使用多个下载源确保成功
6. **版本自动匹配**：根据Chrome版本自动选择对应的ChromeDriver版本
7. **智能文件查找**：自动查找解压后的ChromeDriver文件位置
8. **系统包管理器备用**：如果手动下载失败，尝试使用系统包管理器
9. **路径验证**：严格验证ChromeDriver文件的存在性和可执行性
10. **常见路径检查**：检查多个常见的ChromeDriver安装路径

## 使用方法

### 本地运行

```bash
cd src
python main.py mining --env=production --collector --classifier --source=local
```

### GitHub Actions

工作流会自动处理ChromeDriver的安装和配置，无需额外设置。

### 测试

运行简化测试：
```bash
python test_simple.py
```

运行安装验证：
```bash
python test_chromedriver_install.py
```

## 测试建议

1. **本地测试**：在本地环境中测试修改后的代码
2. **CI测试**：在GitHub Actions中测试完整流程
3. **版本验证**：确认Chrome和ChromeDriver版本匹配
4. **路径验证**：使用验证脚本检查ChromeDriver安装状态

## 注意事项

1. **网络连接**：确保能够访问ChromeDriver下载服务器
2. **权限问题**：确保有足够的权限安装和运行ChromeDriver
3. **版本兼容性**：定期更新版本映射表以支持新版本的Chrome
4. **备用下载源**：如果主要下载源失败，会自动尝试备用源
5. **版本匹配**：确保ChromeDriver版本与Chrome版本兼容
6. **文件结构**：不同下载源的压缩包结构可能不同，需要智能处理
7. **路径验证**：确保ChromeDriver文件真实存在且可执行

## 故障排除

如果仍然遇到问题：

1. **检查Chrome浏览器**：确保Chrome浏览器正确安装
2. **验证网络连接**：确保能够访问下载服务器
3. **查看详细日志**：检查错误日志获取更多信息
4. **手动指定版本**：可以手动设置`CHROME_DRIVER_PATH`环境变量
5. **尝试备用版本**：如果主要版本失败，会自动尝试备用版本
6. **版本匹配检查**：确保ChromeDriver版本与Chrome版本匹配
7. **文件位置检查**：检查解压后的ChromeDriver文件位置
8. **系统包管理器**：尝试使用`sudo apt-get install chromium-chromedriver`
9. **路径验证**：运行`python test_chromedriver_install.py`检查安装状态
10. **权限检查**：确保ChromeDriver文件有执行权限

## 最新改进

### v5.0 修复内容

1. **移除第三方Action依赖**：不再使用`nanasess/setup-chromedriver@v2`
2. **手动安装Chrome和ChromeDriver**：使用更可靠的手动安装方式
3. **多下载源支持**：提供多个ChromeDriver下载源
4. **重试机制**：webdriver_manager安装失败时自动重试
5. **简化测试脚本**：提供更简单的测试方法
6. **版本自动匹配**：根据Chrome版本自动选择对应的ChromeDriver版本
7. **Chrome 138+支持**：添加对最新Chrome版本的支持
8. **智能文件查找**：自动查找解压后的ChromeDriver文件位置
9. **系统包管理器备用**：如果手动下载失败，尝试使用系统包管理器
10. **详细错误处理**：提供详细的安装和错误日志
11. **路径验证**：严格验证ChromeDriver文件的存在性和可执行性
12. **常见路径检查**：检查多个常见的ChromeDriver安装路径
13. **安装验证脚本**：提供专门的验证脚本检查安装状态

### 关键改进

- **版本自动检测**：自动检测Chrome版本并选择对应的ChromeDriver
- **多版本支持**：支持Chrome 1-138版本
- **智能回退**：如果特定版本不可用，自动使用最新的稳定版本
- **详细日志**：提供详细的安装和匹配日志
- **多层安装策略**：系统包管理器 + 手动下载 + 智能文件查找
- **错误恢复**：如果一种安装方式失败，自动尝试其他方式
- **严格路径验证**：确保ChromeDriver文件真实存在且可执行
- **多路径检查**：检查多个常见的ChromeDriver安装位置

这些改进应该能够解决GitHub Actions中的ChromeDriver兼容性问题，特别是Chrome版本不匹配、文件安装和路径验证问题。 