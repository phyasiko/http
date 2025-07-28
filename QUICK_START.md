# 🚀 快速开始指南

## 5分钟快速部署

### 第一步：准备环境
1. 确保已安装 Python 3.8+ 和 Git
2. 下载项目文件到本地

### 第二步：一键部署
```bash
# Windows用户
双击运行 install_and_build.bat

# Linux/Mac用户
chmod +x install_and_build.sh
./install_and_build.sh
```

### 第三步：配置订阅地址

#### 方式一：单订阅（最简单）
在GitHub仓库的Settings > Secrets中添加：
```
AIRPORT_SUBSCRIPTION_URL = 你的机场订阅地址
```

#### 方式二：多订阅
编辑 `subscription_config.yaml` 文件：
```yaml
subscriptions:
  - name: "我的机场"
    url: "https://your-airport.com/sub"
```

### 第四步：创建GitHub仓库
1. 在GitHub上创建新仓库
2. 上传所有项目文件
3. 进入Actions页面启用工作流

### 第五步：享受自动抓取
- 每4分钟自动更新订阅
- 获得稳定的raw链接
- 自动生成provider配置

## 常用链接格式

### 订阅链接
```
https://raw.githubusercontent.com/你的用户名/仓库名/main/subscription.txt
```

### Provider配置
```
https://raw.githubusercontent.com/你的用户名/仓库名/main/provider.yaml
```

## 故障排除

### 问题1：GitHub Actions运行失败
- 检查Secrets配置是否正确
- 确认订阅地址是否有效
- 查看Actions日志获取详细错误信息

### 问题2：订阅内容为空
- 运行 `python test_config.py` 测试配置
- 检查机场订阅地址是否过期
- 确认网络连接正常

### 问题3：权限错误
- 确保GitHub Token有仓库写入权限
- 检查仓库是否为公开仓库

## 高级配置

### 自定义更新频率
编辑 `.github/workflows/fetch_subscription.yml`：
```yaml
schedule:
  - cron: '*/3 * * * *'  # 每3分钟
```

### 添加更多订阅
在 `subscription_config.yaml` 中添加：
```yaml
subscriptions:
  - name: "机场1"
    url: "https://airport1.com/sub"
  - name: "机场2"
    url: "https://airport2.com/sub"
  - name: "机场3"
    url: "https://airport3.com/sub"
```

## 支持的工具

- ✅ Clash
- ✅ Clash for Windows
- ✅ ClashX
- ✅ V2Ray
- ✅ Shadowrocket
- ✅ Quantumult X

## 获取帮助

- 📖 查看完整文档：[README.md](README.md)
- 🐛 报告问题：创建GitHub Issue
- 💡 提出建议：提交Pull Request

---

**提示**: 首次部署后，建议等待5-10分钟让GitHub Actions完成第一次运行。 