#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置测试脚本
用于测试订阅配置是否正确
"""

import os
import yaml
import requests
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_single_subscription():
    """测试单个订阅配置"""
    url = os.getenv('AIRPORT_SUBSCRIPTION_URL')
    if not url:
        logger.warning("未设置 AIRPORT_SUBSCRIPTION_URL 环境变量")
        return False
    
    logger.info(f"测试单个订阅: {url}")
    return test_subscription_url(url)

def test_multi_subscriptions():
    """测试多个订阅配置"""
    subscriptions = {}
    
    # 从环境变量加载
    for i in range(1, 11):
        env_key = f'AIRPORT_SUBSCRIPTION_URL_{i}'
        env_name_key = f'AIRPORT_SUBSCRIPTION_NAME_{i}'
        
        url = os.getenv(env_key)
        name = os.getenv(env_name_key, f'airport_{i}')
        
        if url:
            subscriptions[name] = url
    
    # 从配置文件加载
    config_file = 'subscription_config.yaml'
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
    
    if not subscriptions:
        logger.warning("未找到任何订阅配置")
        return False
    
    logger.info(f"找到 {len(subscriptions)} 个订阅配置")
    
    success_count = 0
    for name, url in subscriptions.items():
        logger.info(f"测试订阅 [{name}]: {url}")
        if test_subscription_url(url):
            success_count += 1
    
    logger.info(f"测试完成: {success_count}/{len(subscriptions)} 个订阅可用")
    return success_count > 0

def test_subscription_url(url):
    """测试单个订阅URL"""
    try:
        logger.info(f"正在测试: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        content = response.text
        logger.info(f"✅ 订阅可用，内容长度: {len(content)} 字符")
        
        # 简单分析内容类型
        if content.startswith('vmess://'):
            logger.info("  检测到VMess订阅")
        elif content.startswith('ss://'):
            logger.info("  检测到Shadowsocks订阅")
        elif content.startswith('trojan://'):
            logger.info("  检测到Trojan订阅")
        elif 'vmess' in content.lower() or 'ss' in content.lower() or 'trojan' in content.lower():
            logger.info("  检测到混合订阅")
        else:
            logger.info("  未知订阅格式")
        
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 订阅测试失败: {e}")
        return False

def test_github_config():
    """测试GitHub配置"""
    token = os.getenv('GITHUB_TOKEN')
    repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER')
    repo_name = os.getenv('GITHUB_REPOSITORY_NAME')
    
    if not token:
        logger.warning("未设置 GITHUB_TOKEN 环境变量")
        return False
    
    if not repo_owner or not repo_name:
        logger.warning("未设置仓库信息，将使用默认值")
        return True
    
    try:
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"✅ GitHub仓库访问正常: {repo_owner}/{repo_name}")
            return True
        else:
            logger.error(f"❌ GitHub仓库访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ GitHub配置测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("开始配置测试")
    logger.info("=" * 50)
    
    # 测试GitHub配置
    logger.info("1. 测试GitHub配置")
    github_ok = test_github_config()
    
    # 测试订阅配置
    logger.info("\n2. 测试订阅配置")
    if os.path.exists('subscription_config.yaml'):
        logger.info("检测到多订阅配置文件")
        subscription_ok = test_multi_subscriptions()
    else:
        logger.info("使用单订阅模式")
        subscription_ok = test_single_subscription()
    
    # 输出测试结果
    logger.info("\n" + "=" * 50)
    logger.info("测试结果汇总:")
    logger.info(f"GitHub配置: {'✅ 正常' if github_ok else '❌ 异常'}")
    logger.info(f"订阅配置: {'✅ 正常' if subscription_ok else '❌ 异常'}")
    
    if github_ok and subscription_ok:
        logger.info("\n🎉 所有配置测试通过！可以开始使用。")
        return True
    else:
        logger.info("\n⚠️  部分配置存在问题，请检查后重试。")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 