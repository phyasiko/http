#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多机场订阅地址自动抓取器
支持多个机场订阅，通过GitHub Actions定时抓取，避免5分钟失效问题
"""

import requests
import base64
import json
import os
import sys
import yaml
from datetime import datetime
import logging
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MultiSubscriptionFetcher:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER', 'your-username')
        self.repo_name = os.getenv('GITHUB_REPOSITORY_NAME', 'subscription-cache')
        
        # 支持多个机场订阅
        self.subscriptions = self._load_subscriptions()
        
        if not self.subscriptions:
            logger.error("没有配置任何订阅地址")
            sys.exit(1)
            
        if not self.github_token:
            logger.error("请设置 GITHUB_TOKEN 环境变量")
            sys.exit(1)
    
    def _load_subscriptions(self) -> Dict[str, str]:
        """加载订阅配置"""
        subscriptions = {}
        
        # 从环境变量加载单个订阅
        single_url = os.getenv('AIRPORT_SUBSCRIPTION_URL')
        if single_url:
            subscriptions['airport'] = single_url
        
        # 从环境变量加载多个订阅
        for i in range(1, 11):  # 支持最多10个订阅
            env_key = f'AIRPORT_SUBSCRIPTION_URL_{i}'
            env_name_key = f'AIRPORT_SUBSCRIPTION_NAME_{i}'
            
            url = os.getenv(env_key)
            name = os.getenv(env_name_key, f'airport_{i}')
            
            if url:
                subscriptions[name] = url
        
        # 从配置文件加载
        config_file = os.getenv('SUBSCRIPTION_CONFIG_FILE', 'subscription_config.yaml')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if config and 'subscriptions' in config:
                        for sub in config['subscriptions']:
                            name = sub.get('name', f'airport_{len(subscriptions)}')
                            url = sub.get('url')
                            if url:
                                subscriptions[name] = url
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")
        
        return subscriptions
    
    def fetch_subscription(self, name: str, url: str) -> Optional[str]:
        """抓取单个订阅内容"""
        try:
            logger.info(f"开始抓取订阅 [{name}]: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            content = response.text
            logger.info(f"成功抓取订阅 [{name}]，长度: {len(content)} 字符")
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"抓取订阅 [{name}] 失败: {e}")
            return None
    
    def update_github_file(self, filename: str, content: str) -> bool:
        """更新GitHub仓库中的文件"""
        try:
            # 编码内容为base64
            content_bytes = content.encode('utf-8')
            content_base64 = base64.b64encode(content_bytes).decode('utf-8')
            
            # GitHub API URL
            api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{filename}"
            
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # 获取当前文件信息
            response = requests.get(api_url, headers=headers)
            current_sha = None
            if response.status_code == 200:
                current_sha = response.json()['sha']
                logger.info(f"获取到文件 {filename} 的SHA")
            
            # 准备更新数据
            data = {
                'message': f'自动更新订阅 {filename} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'content': content_base64,
                'branch': 'main'
            }
            
            if current_sha:
                data['sha'] = current_sha
            
            # 更新文件
            response = requests.put(api_url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                logger.info(f"成功更新GitHub文件: {filename}")
                return True
            else:
                logger.error(f"更新GitHub文件 {filename} 失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"更新GitHub文件 {filename} 时出错: {e}")
            return False
    
    def create_provider_yaml(self) -> bool:
        """创建provider.yaml文件"""
        try:
            providers = []
            
            for name, url in self.subscriptions.items():
                # 生成raw链接
                raw_url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/main/{name}.txt"
                
                provider = {
                    'name': f"机场订阅 - {name}",
                    'type': "http",
                    'path': f"./{name}.txt",
                    'url': raw_url,
                    'interval': 3600,  # 1小时更新一次
                    'health-check': {
                        'enable': True,
                        'url': "http://www.gstatic.com/generate_204",
                        'interval': 300
                    },
                    'filter': "!((SELECTED))",
                    'hysteria2': {'enable': True},
                    'shadowsocks': {'enable': True},
                    'vmess': {'enable': True},
                    'trojan': {'enable': True},
                    'wireguard': {'enable': True}
                }
                providers.append(provider)
            
            yaml_content = f"""# 自动生成的多机场Provider配置
# 更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# 原始订阅地址数量: {len(self.subscriptions)}

providers:
"""
            
            # 添加所有provider
            for provider in providers:
                yaml_content += yaml.dump([provider], default_flow_style=False, allow_unicode=True, indent=2)
                yaml_content = yaml_content.replace('- ', '  - ')
            
            # 保存provider.yaml文件
            with open('provider.yaml', 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            logger.info("成功创建provider.yaml文件")
            return True
            
        except Exception as e:
            logger.error(f"创建provider.yaml文件时出错: {e}")
            return False
    
    def create_subscription_list(self) -> bool:
        """创建订阅列表文件"""
        try:
            list_content = f"""# 机场订阅列表
# 更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# 订阅数量: {len(self.subscriptions)}

"""
            
            for name, url in self.subscriptions.items():
                raw_url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/main/{name}.txt"
                list_content += f"## {name}\n"
                list_content += f"- 原始地址: {url}\n"
                list_content += f"- Raw地址: {raw_url}\n\n"
            
            # 保存订阅列表文件
            with open('subscription_list.md', 'w', encoding='utf-8') as f:
                f.write(list_content)
            
            logger.info("成功创建订阅列表文件")
            return True
            
        except Exception as e:
            logger.error(f"创建订阅列表文件时出错: {e}")
            return False
    
    def run(self) -> bool:
        """主运行函数"""
        logger.info(f"开始执行多订阅抓取任务，共 {len(self.subscriptions)} 个订阅")
        
        success_count = 0
        
        # 抓取每个订阅
        for name, url in self.subscriptions.items():
            content = self.fetch_subscription(name, url)
            if content:
                # 更新GitHub文件
                filename = f"{name}.txt"
                if self.update_github_file(filename, content):
                    success_count += 1
                    logger.info(f"订阅 [{name}] 处理成功")
                else:
                    logger.error(f"订阅 [{name}] 更新失败")
            else:
                logger.error(f"订阅 [{name}] 抓取失败")
        
        # 创建provider.yaml
        if not self.create_provider_yaml():
            logger.error("创建provider.yaml失败")
        
        # 创建订阅列表
        if not self.create_subscription_list():
            logger.error("创建订阅列表失败")
        
        logger.info(f"订阅抓取任务完成，成功处理 {success_count}/{len(self.subscriptions)} 个订阅")
        return success_count > 0

def main():
    """主函数"""
    fetcher = MultiSubscriptionFetcher()
    success = fetcher.run()
    
    if success:
        logger.info("任务执行成功")
        sys.exit(0)
    else:
        logger.error("任务执行失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 