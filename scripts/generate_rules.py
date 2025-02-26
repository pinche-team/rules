#!/usr/bin/env python3
import requests
import yaml
from datetime import datetime
import re

def fetch_acl4ssr_list():
    url = 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/Binance.list'
    response = requests.get(url)
    rules = []
    if response.status_code == 200:
        for line in response.text.splitlines():
            if line.startswith('DOMAIN-SUFFIX,'):
                domain = line.split(',')[1]
                rules.append(domain)
    return rules

def fetch_acl4ssr_yaml():
    url = 'https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Providers/Ruleset/Binance.yaml'
    response = requests.get(url)
    rules = []
    if response.status_code == 200:
        try:
            data = yaml.safe_load(response.text)
            if 'payload' in data:
                for rule in data['payload']:
                    if rule.startswith('DOMAIN-SUFFIX,'):
                        domain = rule.split(',')[1]
                        rules.append(domain)
        except yaml.YAMLError:
            print('Error parsing YAML file')
    return rules

def fetch_strickland_list():
    url = 'https://raw.githubusercontent.com/StricklandF/Filter/main/Binance.list'
    response = requests.get(url)
    rules = []
    if response.status_code == 200:
        for line in response.text.splitlines():
            if line.startswith('DOMAIN-SUFFIX,'):
                domain = line.split(',')[1]
                rules.append(domain)
    return rules

def parse_quantumult_x_rules():
    url = 'https://raw.githubusercontent.com/StricklandF/Filter/main/Binance.list'
    response = requests.get(url)
    rules = set()
    
    if response.status_code == 200:
        for line in response.text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if line.startswith('host-suffix,'):
                parts = line.split(',')
                if len(parts) >= 2:
                    domain = parts[1].strip()
                    rules.add(domain)
            elif line.startswith('host,'):
                parts = line.split(',')
                if len(parts) >= 2:
                    domain = parts[1].strip()
                    base_domain = re.sub(r'^[^.]+\.', '', domain)
                    if base_domain not in rules:
                        rules.add(domain)
    
    return rules

def remove_subdomain_rules(rules):
    # 将规则转换为集合以提高查找效率
    rules_set = set(rules)
    rules_to_remove = set()

    # 遍历每个规则，检查是否存在父域名规则
    for rule in rules:
        parts = rule.split('.')
        for i in range(1, len(parts)):
            parent_domain = '.'.join(parts[i:])
            if parent_domain in rules_set:
                rules_to_remove.add(rule)
                break

    # 从原始规则集中移除被父域名覆盖的规则
    return sorted(list(rules_set - rules_to_remove))

def generate_binance_list():
    # 获取所有规则
    all_rules = set()
    all_rules.update(fetch_acl4ssr_list())
    all_rules.update(fetch_acl4ssr_yaml())
    all_rules.update(fetch_strickland_list())
    all_rules.update(parse_quantumult_x_rules())
    
    # 移除被父域名规则覆盖的子域名规则
    sorted_rules = remove_subdomain_rules(all_rules)
    
    # 生成文件内容
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_rules = len(sorted_rules)
    
    content = [
        '# NAME: Binance',
        '# AUTHOR: pinche-team',
        '# REPO: https://github.com/pinche-team/rules'
        f'# UPDATED: {current_time}',
        f'# DOMAIN-SUFFIX: {total_rules}',
        f'# TOTAL: {total_rules}'
    ]
    
    # 添加规则
    for domain in sorted_rules:
        content.append(f'DOMAIN-SUFFIX,{domain}')
    
    return '\n'.join(content) + '\n'

def main():
    try:
        rules_content = generate_binance_list()
        with open('surge/Binance/Binance.list', 'w') as f:
            f.write(rules_content)
        print('Successfully generated Binance.list')
    except Exception as e:
        print(f'Error generating rules: {str(e)}')

if __name__ == '__main__':
    main()