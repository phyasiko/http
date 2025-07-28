#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机场订阅地址自动抓取器
通过GitHub Actions定时抓取机场订阅，避免5分钟失效问题
"""

import requests
import base64
import json
import os
import sys
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SubscriptionFetcher:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER', 'your-username')
        self.repo_name = os.getenv('GITHUB_REPOSITORY_NAME', 'subscription-cache')
        self.airport_url = os.getenv('AIRPORT_SUBSCRIPTION_URL')
        
        if not self.airport_url:
            logger.error("请设置 AIRPORT_SUBSCRIPTION_URL 环境变量")
            sys.exit(1)
            
        if not self.github_token:
            logger.error("请设置 GITHUB_TOKEN 环境变量")
            sys.exit(1)
    
    def fetch_subscription(self):
        """抓取机场订阅内容"""
        try:
            logger.info(f"开始抓取订阅地址: {self.airport_url}")
            response = requests.get(self.airport_url, timeout=30)
            response.raise_for_status()
            
            content = response.text
            logger.info(f"成功抓取订阅内容，长度: {len(content)} 字符")
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"抓取订阅失败: {e}")
            return None
    
    def update_github_file(self, content):
        """更新GitHub仓库中的订阅文件"""
        try:
            # 编码内容为base64
            content_bytes = content.encode('utf-8')
            content_base64 = base64.b64encode(content_bytes).decode('utf-8')
            
            # GitHub API URL
            api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/subscription.txt"
            
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # 获取当前文件信息
            response = requests.get(api_url, headers=headers)
            current_sha = None
            if response.status_code == 200:
                current_sha = response.json()['sha']
                logger.info("获取到当前文件SHA")
            
            # 准备更新数据
            data = {
                'message': f'自动更新订阅 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'content': content_base64,
                'branch': 'main'
            }
            
            if current_sha:
                data['sha'] = current_sha
            
            # 更新文件
            response = requests.put(api_url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                logger.info("成功更新GitHub文件")
                return True
            else:
                logger.error(f"更新GitHub文件失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"更新GitHub文件时出错: {e}")
            return False
    
    def create_provider_yaml(self, content):
        """创建provider.yaml文件"""
        try:
            # 生成raw链接
            raw_url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/main/subscription.txt"
            
            yaml_content = f"""# 自动生成的Provider配置
# 更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# 原始订阅地址: {self.airport_url}

providers:
  - name: "机场订阅"
    type: "http"
    path: "./subscription.txt"
    url: "{raw_url}"
    interval: 3600  # 1小时更新一次
    health-check:
      enable: true
      url: "http://www.gstatic.com/generate_204"
      interval: 300
    filter: "!((SELECTED))"
    hysteria2:
      enable: true
    shadowsocks:
      enable: true
    vmess:
      enable: true
    trojan:
      enable: true
    wireguard:
      enable: true
"""
            
            # 保存provider.yaml文件
            with open('provider.yaml', 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            logger.info("成功创建provider.yaml文件")
            return True
            
        except Exception as e:
            logger.error(f"创建provider.yaml文件时出错: {e}")
            return False
    
    def run(self):
        """主运行函数"""
        logger.info("开始执行订阅抓取任务")
        
        # 抓取订阅内容
        content = self.fetch_subscription()
        if not content:
            logger.error("抓取订阅内容失败")
            return False
        
        # 更新GitHub文件
        if not self.update_github_file(content):
            logger.error("更新GitHub文件失败")
            return False
        
        # 创建provider.yaml
        if not self.create_provider_yaml(content):
            logger.error("创建provider.yaml失败")
            return False
        
        logger.info("订阅抓取任务完成")
        return True

def main():
    """主函数"""
    fetcher = SubscriptionFetcher()
    success = fetcher.run()
    
    if success:
        logger.info("任务执行成功")
        sys.exit(0)
    else:
        logger.error("任务执行失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 