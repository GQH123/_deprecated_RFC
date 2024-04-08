import os


def launch(n_proxy, config_path, clash_st_port=10000):
    with open(config_path, 'r') as f:
        config = f.read()
    config_name = os.path.basename(config_path)
    launch_script = ''
    for i in range(n_proxy):
        port = clash_st_port + i * 2
        ui_port = port + 1
        dist_config = config.replace('mixed-port: 7890', f'mixed-port: {port}').replace('external-controller: 127.0.0.1:9090', f'external-controller: 127.0.0.1:{ui_port}')
        dist_config_name = f'clash_dist_{i}.yaml'
        clash_log_name = f'clash_dist_{i}.log'
        with open(dist_config_name, 'w') as f:
            f.write(dist_config)
        launch_script += f'nohup ./clash-linux-amd64-v1.10.0 -d . -f {dist_config_name} 2>&1 > {clash_log_name} &\n'
    with open('launch.sh', 'w') as f:
        f.write(launch_script)
        
        
launch(3, 'config.yaml')