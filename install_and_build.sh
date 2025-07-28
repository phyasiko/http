#!/bin/bash

echo "========================================"
echo "机场订阅自动抓取器 - 一键安装和构建"
echo "========================================"
echo

# 检测Python环境
echo "[1/5] 检测Python环境..."
if command -v python3 &> /dev/null; then
    echo "✅ Python环境检测成功"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    echo "✅ Python环境检测成功"
    PYTHON_CMD="python"
else
    echo "❌ 未检测到Python环境，请先安装Python 3.8+"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

# 检测Git环境
echo
echo "[2/5] 检测Git环境..."
if command -v git &> /dev/null; then
    echo "✅ Git环境检测成功"
else
    echo "❌ 未检测到Git环境，请先安装Git"
    echo "Ubuntu/Debian: sudo apt install git"
    echo "CentOS/RHEL: sudo yum install git"
    echo "macOS: brew install git"
    exit 1
fi

# 创建虚拟环境
echo
echo "[3/5] 创建Python虚拟环境..."
if [ -d "venv" ]; then
    echo "虚拟环境已存在，跳过创建"
else
    $PYTHON_CMD -m venv venv
    echo "✅ 虚拟环境创建成功"
fi

# 激活虚拟环境并安装依赖
echo
echo "[4/5] 安装Python依赖..."
source venv/bin/activate
$PYTHON_CMD -m pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
else
    echo "✅ 依赖安装成功"
fi

# 检测项目类型并运行相应脚本
echo
echo "[5/5] 检测项目配置..."
if [ -f "subscription_config.yaml" ]; then
    echo "检测到多订阅配置文件，使用多订阅模式"
    echo "运行多订阅抓取器..."
    $PYTHON_CMD multi_subscription_fetcher.py
else
    echo "使用单订阅模式"
    echo "请确保设置了 AIRPORT_SUBSCRIPTION_URL 环境变量"
    echo "运行单订阅抓取器..."
    $PYTHON_CMD subscription_fetcher.py
fi

echo
echo "========================================"
echo "安装和构建完成！"
echo "========================================"
echo
echo "下一步操作："
echo "1. 在GitHub上创建仓库并上传代码"
echo "2. 设置仓库Secrets（订阅地址）"
echo "3. 启用GitHub Actions工作流"
echo "4. 享受自动抓取的便利！"
echo 