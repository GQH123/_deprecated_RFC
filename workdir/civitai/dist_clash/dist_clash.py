import os


def launch(n_proxy, config_path, clash_st_port=20000):
    with open(config_path, 'r') as f:
        config = f.read()
    config_name = os.path.basename(config_path)
    launch_script = ''
    for i in range(n_proxy):
        port = clash_st_port + i * 4
        socks_port = port + 1
        redir_port = port + 2
        ui_port = port + 3
        dist_config = config.replace('port: 7890', f'port: {port}').replace('socks-port: 7891', f'socks-port: {socks_port}').replace('redir-port: 7892', f'redir-port: {redir_port}').replace("external-controller: '0.0.0.0:9090'", f"external-controller: '0.0.0.0:{ui_port}'")
        dist_config_name = f'clash_dist_{i}.yaml'
        clash_log_name = f'clash_dist_{i}.log'
        with open(dist_config_name, 'w') as f:
            f.write(dist_config)
        launch_script += f'nohup ./clash-linux-amd64-v1.10.0 -d . -f {dist_config_name} 2>&1 > {clash_log_name} &\n'
    with open('launch.sh', 'w') as f:
        f.write(launch_script)
        
        
launch(1, 'config.yaml')