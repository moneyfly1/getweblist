# SSPanel Mining

[![GitHub Actions](https://github.com/RobAI-Lab/sspanel-mining/workflows/SSPanel%20Mining/badge.svg)](https://github.com/RobAI-Lab/sspanel-mining/actions)

> 基于 Google 搜索引擎的 SSPanel 站点采集器

## ✨ 特性

- 🔍 **智能采集**: 基于 Google 搜索引擎的智能站点发现
- 🛡️ **反检测机制**: 内置重试机制和随机延迟，减少被 Google 拦截的可能性
- 📊 **数据分类**: 自动对采集到的站点进行分类和过滤
- 🚀 **高性能**: 支持多线程并发处理
- 🔄 **自动重试**: 当遇到 Google 拦截时自动重试，提高成功率

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Chrome 浏览器
- ChromeDriver

### 安装

```bash
# 克隆仓库
git clone https://github.com/RobAI-Lab/sspanel-mining.git
cd sspanel-mining

# 安装依赖
pip install -r requirements.txt

# 安装配置
python src/main.py install
```

### 使用

```bash
# 运行采集器（推荐）
python src/main.py mining --collector --classifier

# 仅运行采集器
python src/main.py mining --collector

# 仅运行分类器
python src/main.py mining --classifier

# 生产环境运行
python src/main.py mining --env=production --collector --classifier
```

## 🔧 配置

### 环境变量

- `CHROME_DRIVER_PATH`: ChromeDriver 路径（可选）
- `MAX_RETRIES`: 最大重试次数（默认: 3）
- `RETRY_DELAY`: 重试延迟时间（默认: 30秒）

### 参数说明

- `--env`: 运行环境 (`development` | `production`)
- `--silence`: 静默模式（默认: `True`）
- `--collector`: 启用采集器
- `--classifier`: 启用分类器
- `--source`: 数据源 (`local` | `remote`)
- `--power`: 分类器功率（默认: 16）

## 🛡️ 反检测机制

### 重试机制

当遇到 `CollectorSwitchError`（Google 拦截）时，系统会自动重试：

1. **递增延迟**: 每次重试的等待时间递增（30秒、60秒、90秒）
2. **随机行为**: 添加随机滚动和延迟，模拟人类浏览行为
3. **智能检测**: 自动检测 Google 拦截页面并触发重试
4. **优雅降级**: 如果重试失败，提供详细的错误信息和解决建议

### 行为模拟

- 随机页面滚动（PAGE_DOWN、END、PAGE_UP）
- 随机延迟（0.5-3秒）
- 模拟人类点击行为
- 智能页面切换

## 📊 数据分类

采集到的站点会被自动分类为：

- **Normal**: 无验证站点
- **Google reCAPTCHA**: Google reCAPTCHA 人机验证
- **GeeTest Validation**: 极验滑块验证
- **Email Validation**: 邮箱验证
- **SMS**: 手机短信验证
- **CloudflareDefenseV2**: 高防服务器

## 🔍 故障排除

### ChromeDriver 问题

如果遇到 ChromeDriver 兼容性问题，请参考 [ChromeDriver 修复指南](CHROME_DRIVER_FIX.md)。

### Google 拦截

如果频繁遇到 Google 拦截：

1. **增加延迟**: 调整 `RETRY_DELAY` 环境变量
2. **使用代理**: 配置代理服务器
3. **减少频率**: 降低采集频率
4. **手动处理**: 在 Windows 环境下可以手动处理验证码

### 常见错误

- `CollectorSwitchError`: Google 拦截，系统会自动重试
- `CollectorNoTouchElementError`: 元素定位失败
- `ManuallyCloseTheCollectorError`: 手动关闭采集器

## 📁 项目结构

```
sspanel-mining/
├── src/
│   ├── apis/              # API 接口
│   ├── database/          # 数据存储
│   ├── services/          # 核心服务
│   └── main.py           # 主程序
├── docs/                 # 文档
├── examples/             # 示例
└── requirements.txt      # 依赖
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## ⚠️ 免责声明

本项目仅供学习和研究使用。请遵守相关法律法规和网站使用条款。


