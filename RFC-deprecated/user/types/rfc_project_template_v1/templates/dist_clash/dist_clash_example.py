import os
import json
import shutil

"""
proxy_pool = (
    {
        'http': 'http://127.0.0.1:10000',
        'https': 'http://127.0.0.1:10000',
        'all': 'socks5://127.0.0.1:10000',
    },
    {
        'http': 'http://127.0.0.1:10002',
        'https': 'http://127.0.0.1:10002',
        'all': 'socks5://127.0.0.1:10002',
    },
    {
        'http': 'http://127.0.0.1:10004',
        'https': 'http://127.0.0.1:10004',
        'all': 'socks5://127.0.0.1:10004',
    },
)
"""

all_lines = ["IEPL-英国1", "IEPL-英国2", "IEPL-韩国1", "IEPL-韩国2", "IEPL-台湾1", "IEPL-台湾2", "IEPL-台湾3", "IEPL-台湾4", "IEPL-台湾5", "IEPL-台湾6", "IEPL-台湾7", "IEPL-台湾8", "IEPL-台湾9", "IEPL-台湾10", "IEPL-香港1", "IEPL-香港2", "IEPL-香港3", "IEPL-香港4", "IEPL-香港5", "IEPL-香港6", "IEPL-香港7", "IEPL-香港8", "IEPL-香港9", "IEPL-香港10", "IEPL-香港11", "IEPL-香港12", "IEPL-香港13", "IEPL-香港14", "IEPL-香港15", "IEPL-香港16", "IEPL-香港17", "IEPL-香港18", "IEPL-香港19", "IEPL-香港20", "IEPL-香港21", "IEPL-香港22", "IEPL-香港23", "IEPL-香港24", "IEPL-香港25", "IEPL-香港26", "IEPL-香港27", "IEPL-香港28", "IEPL-香港29", "IEPL-香港30", "IEPL-美国1", "IEPL-美国2", "IEPL-美国3", "IEPL-美国4", "IEPL-美国5", "IEPL-美国6", "IEPL-美国7", "IEPL-美国8", "IEPL-美国9", "IEPL-美国10", "IEPL-新加坡1", "IEPL-新加坡2", "IEPL-新加坡3", "IEPL-新加坡4", "IEPL-新加坡5", "IEPL-新加坡6", "IEPL-新加坡7", "IEPL-新加坡8", "IEPL-新加坡9", "IEPL-新加坡10", "IEPL-日本1", "IEPL-日本2", "IEPL-日本3", "IEPL-日本4", "IEPL-日本5", "IEPL-日本6", "IEPL-日本7", "IEPL-日本8", "IEPL-日本9", "IEPL-日本10", "IEPL-日本11", "IEPL-日本12", "IEPL-日本13", "IEPL-日本14", "IEPL-日本15", "IEPL-日本16", "IEPL-日本17", "IEPL-日本18", "IEPL-德国", "IEPL-巴西", "IEPL-土耳其", "IEPL-阿根廷", "IEPL-印度", "IEPL-马来西亚", "IEPL-泰国", "IEPL-越南", "IEPL-菲律宾1【倍率:5】", "IEPL-菲律宾2【倍率:5】", "IEPL-俄罗斯伯力", "（SS）IEPL-英国1", "（SS）IEPL-英国2", "（SS）IEPL-马来西亚", "（SS）IEPL-台湾1", "（SS）IEPL-台湾2", "（SS）IEPL-台湾3", "（SS）IEPL-台湾4", "（SS）IEPL-台湾5", "（SS）IEPL-台湾6", "（SS）IEPL-台湾7", "（SS）IEPL-台湾8", "（SS）IEPL-台湾9", "（SS）IEPL-台湾10", "（SS）IEPL-香港1", "（SS）IEPL-香港2", "（SS）IEPL-香港3", "（SS）IEPL-香港4", "（SS）IEPL-香港5", "（SS）IEPL-香港6", "（SS）IEPL-香港7", "（SS）IEPL-香港8", "（SS）IEPL-香港9", "（SS）IEPL-香港10", "（SS）IEPL-香港11", "（SS）IEPL-香港12", "（SS）IEPL-香港13", "（SS）IEPL-香港14", "（SS）IEPL-香港15", "（SS）IEPL-香港16", "（SS）IEPL-香港17", "（SS）IEPL-香港18", "（SS）IEPL-香港19", "（SS）IEPL-香港20", "（SS）IEPL-香港21", "（SS）IEPL-香港22", "（SS）IEPL-香港23", "（SS）IEPL-香港24", "（SS）IEPL-香港25", "（SS）IEPL-香港26", "（SS）IEPL-香港27", "（SS）IEPL-香港28", "（SS）IEPL-香港29", "（SS）IEPL-香港30", "（SS）IEPL-美国1", "（SS）IEPL-美国2", "（SS）IEPL-美国3", "（SS）IEPL-美国4", "（SS）IEPL-美国5", "（SS）IEPL-美国6", "（SS）IEPL-美国7", "（SS）IEPL-美国8", "（SS）IEPL-美国9", "（SS）IEPL-美国10", "（SS）IEPL-新加坡1", "（SS）IEPL-新加坡2", "（SS）IEPL-新加坡3", "（SS）IEPL-新加坡4", "（SS）IEPL-新加坡5", "（SS）IEPL-新加坡6", "（SS）IEPL-新加坡7", "（SS）IEPL-新加坡8", "（SS）IEPL-新加坡9", "（SS）IEPL-新加坡10", "（SS）IEPL-日本1", "（SS）IEPL-日本2", "（SS）IEPL-日本3", "（SS）IEPL-日本4", "（SS）IEPL-日本5", "（SS）IEPL-日本6", "（SS）IEPL-日本7", "（SS）IEPL-日本8", "（SS）IEPL-日本9", "（SS）IEPL-日本10", "（SS）IEPL-日本11", "（SS）IEPL-日本12", "（SS）IEPL-日本13", "（SS）IEPL-日本14", "（SS）IEPL-日本15", "（SS）IEPL-日本16", "（SS）IEPL-日本17", "（SS）IEPL-日本18"]


def launch(n_proxy, config_path, clash_st_port=21000):
    shutil.rmtree('configs', ignore_errors=True)
    os.makedirs('configs', exist_ok=True)
    if n_proxy > len(all_lines):
        raise ValueError(f'n_proxy should be less than or equal to {len(all_lines)}')
    with open(config_path, 'r') as f:
        config = f.read()
    config_name = os.path.basename(config_path)
    launch_script = ''
    proxy_pool = []
    for i in range(n_proxy):
        port = clash_st_port + i * 2
        ui_port = port + 1
        dist_config = config.replace('mixed-port: 7890', f'mixed-port: {port}').replace('external-controller: 127.0.0.1:9090', f'external-controller: 127.0.0.1:{ui_port}').split('\n')
        assert dist_config[246] == '      - ♻️ 自动选择'
        dist_config[246] = dist_config[246].replace('♻️ 自动选择', all_lines[i])
        dist_config = '\n'.join(dist_config)
        dist_config_name = f'configs/{i}/clash_dist_{i}.yaml'
        clash_log_name = f'configs/{i}/clash_dist_{i}.log'
        os.makedirs(f'configs/{i}', exist_ok=True)
        with open(dist_config_name, 'w') as f:
            f.write(dist_config)
        launch_script += f'cp cache.db configs/{i}/cache.db\n'
        launch_script += f'cp Country.mmdb configs/{i}/Country.mmdb\n'
        launch_script += f'nohup ./clash-my -d configs/{i}/ -f {dist_config_name} 2>&1 > {clash_log_name} &\n'
        proxy_pool.append({
            'http': f'http://127.0.0.1:{port}',
            'https': f'http://127.0.0.1:{port}',
            'all': f'socks5://127.0.0.1:{port}',
        })
    with open('launch.sh', 'w') as f:
        f.write(launch_script)
    return proxy_pool


proxy_pool = launch(174, 'config.yaml')
print(f"proxy_pool = {json.dumps(proxy_pool, indent=4, ensure_ascii=False).replace('[', '(').replace(']', ')')}", file=open('proxy_pool.py', 'w'))