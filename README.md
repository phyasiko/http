# 机场订阅自动抓取器

这是一个通过GitHub Actions自动抓取机场订阅地址的工具，解决订阅链接5分钟失效的问题。

## 功能特点

- 🕐 **定时抓取**: 每4分钟自动抓取一次订阅，避免5分钟失效
- 🔄 **自动更新**: 自动更新GitHub仓库中的订阅文件
- 📝 **Provider配置**: 自动生成Clash等代理工具的provider.yaml配置
- 🔗 **Raw链接**: 提供稳定的raw.githubusercontent.com链接
- 🤖 **GitHub Actions**: 完全自动化，无需手动操作
- 📊 **多订阅支持**: 支持同时管理多个机场订阅
- 🧪 **配置测试**: 提供测试脚本验证配置正确性
- 🚀 **一键部署**: 提供一键安装和构建脚本

## 工作原理

1. GitHub Actions每4分钟运行一次
2. 抓取机场订阅地址的内容
3. 更新仓库中的`subscription.txt`文件
4. 生成`provider.yaml`配置文件
5. 提供稳定的raw链接供其他工具使用

## 使用方法

### 方法一：一键部署（推荐）

1. 下载项目文件到本地
2. 双击运行 `install_and_build.bat`
3. 按照提示完成配置

### 方法二：手动部署

#### 1. 创建GitHub仓库

1. 在GitHub上创建一个新的仓库
2. 将本项目的所有文件上传到仓库

#### 2. 配置订阅地址

**单订阅模式**：
在仓库的Settings > Secrets and variables > Actions中添加：
- `AIRPORT_SUBSCRIPTION_URL`: 您的机场订阅地址

**多订阅模式**：
方式一：使用环境变量（最多5个）
- `AIRPORT_SUBSCRIPTION_URL_1`: 第一个订阅地址
- `AIRPORT_SUBSCRIPTION_NAME_1`: 第一个订阅名称
- `AIRPORT_SUBSCRIPTION_URL_2`: 第二个订阅地址
- `AIRPORT_SUBSCRIPTION_NAME_2`: 第二个订阅名称
- ...（最多到5）

方式二：使用配置文件
编辑 `subscription_config.yaml` 文件：
```yaml
subscriptions:
  - name: "机场1"
    url: "https://your-airport1.com/sub"
  - name: "机场2"
    url: "https://your-airport2.com/sub"
```

#### 3. 启用GitHub Actions

1. 进入仓库的Actions页面
2. 选择对应的工作流：
   - 单订阅：启用"自动抓取机场订阅"
   - 多订阅：启用"自动抓取多机场订阅"
3. 可以手动触发第一次运行

#### 4. 测试配置

运行测试脚本验证配置：
```bash
python test_config.py
```

#### 5. 使用Raw链接

订阅文件将通过以下链接提供：
- 单订阅：`https://raw.githubusercontent.com/你的用户名/仓库名/main/subscription.txt`
- 多订阅：`https://raw.githubusercontent.com/你的用户名/仓库名/main/机场名称.txt`

#### 6. 使用Provider配置

生成的`provider.yaml`文件可以直接用于Clash等代理工具。

## 文件说明

### 核心文件
- `subscription_fetcher.py`: 单订阅抓取脚本
- `multi_subscription_fetcher.py`: 多订阅抓取脚本
- `test_config.py`: 配置测试脚本
- `install_and_build.bat`: 一键安装和构建脚本

### 配置文件
- `subscription_config.yaml`: 多订阅配置文件
- `requirements.txt`: Python依赖

### GitHub Actions
- `.github/workflows/fetch_subscription.yml`: 单订阅工作流
- `.github/workflows/multi_fetch_subscription.yml`: 多订阅工作流

### 生成文件
- `subscription.txt`: 单订阅内容（自动生成）
- `机场名称.txt`: 多订阅内容（自动生成）
- `provider.yaml`: Provider配置文件（自动生成）
- `subscription_list.md`: 订阅列表（自动生成）

## 配置说明

### 环境变量

- `AIRPORT_SUBSCRIPTION_URL`: 机场订阅地址（必需）
- `GITHUB_TOKEN`: GitHub访问令牌（自动提供）
- `GITHUB_REPOSITORY_OWNER`: 仓库所有者（自动设置）
- `GITHUB_REPOSITORY_NAME`: 仓库名称（自动设置）

### 定时设置

默认每4分钟运行一次，可以在`.github/workflows/fetch_subscription.yml`中修改cron表达式：

```yaml
schedule:
  - cron: '*/4 * * * *'  # 每4分钟
```

## 故障排除

### 常见问题

1. **抓取失败**: 检查机场订阅地址是否正确
2. **权限错误**: 确保GitHub Token有仓库写入权限
3. **网络超时**: 脚本设置了30秒超时，如果机场响应慢可能需要调整

### 日志查看

在GitHub Actions页面可以查看详细的运行日志。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！ 