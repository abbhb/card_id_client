import time

import consul

from config import server_port, my_ip, service_id, consul_server_ip, consul_server_port


class ConsulService(object):
    def __init__(self):
        # 服务信息
        self.service_id = service_id  # 自定义的 service_id,设备id
        self.service_name = "signin"
        self.service_address = my_ip
        self.service_port = server_port
        self.service_tags = ["signin"]
        self.service_meta = {"zc": "card,"}
        # 注册服务到 Consul
        # 创建 Consul 客户端连接
        self.c = consul.Consul(host=consul_server_ip, port=consul_server_port)
        self.c.agent.service.deregister(self.service_id)
        # 构建服务定义
        service_definition = {
            "service_id": self.service_id,  # 设置 service_id
            "name": self.service_name,
            "address": self.service_address,
            "port": self.service_port,
            "tags": self.service_tags or [],
            "meta": self.service_meta or {},

        }
        check_demo = consul.Check.http(f'http://{ self.service_address}:{ self.service_port}/health',interval='15s')

    # 注册服务
        self.c.agent.service.register(**service_definition,check=check_demo)
        print("Service registered successfully.")
    def clean(self):
        self.c.agent.service.deregister(self.service_id)
        print(f"Service {self.service_id} deregistered.")
    # time.sleep(5)
    # c.agent.service.deregister(service_id)
    # print(f"Service {service_id} deregistered.")
