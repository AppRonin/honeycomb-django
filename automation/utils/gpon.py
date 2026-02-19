import re

def get_total_onu(file):
    onu_pattern = r"interface\sgpon-onu_\d{1,2}/\d{1,2}/\d{1,2}:\d{1,2}"
    total_onu = len(re.findall(onu_pattern, file))
    return total_onu

def get_onu_list(total_onu, port):
    onu_list = [f"{port}:{onu}" for onu in range(1, total_onu) ]
    return onu_list

def format_onu_conf(conf):
    name_pattern =  r"(name[^\n]*)\n\s+description"
    desc_pattern = r"name[^\n]*\n\s+(description .*)"
    tcount_pattern = r"tcont \d+ name [^\n]*"
    tcount_gap_pattern = r"tcont \d+ gap mode\d+"
    gem_pattern = r"gemport \d+ name [^\n]*"

    name = re.findall(name_pattern, conf)
    desc = re.findall(desc_pattern, conf)
    tcounts = re.findall(tcount_pattern, conf)
    tcounts = [re.sub(r"allocid\s\d+\s", "", tcount) for tcount in tcounts]
    tcount_gaps = re.findall(tcount_gap_pattern, conf)
    gem_ports = re.findall(gem_pattern, conf)
    gem_ports = [gem.replace("unicast ", "").replace("dir both ", "") for gem in gem_ports]
    gem_ports = [re.sub(r"portid\s\d+\s", "", gem) for gem in gem_ports]

    new_conf = name + desc + tcounts + tcount_gaps + gem_ports

    return new_conf

def format_vport_conf(conf, vport):
    vport_id = re.search(r":(\d+)", vport).group(1)
    service_pattern = rf"(service-port {vport_id} vport .*?)\s\n"
    bld_pattern = rf"gemport {vport_id} traffic-limit upstream (.*?)\s"
    service_desc_pattern = rf"(service-port {vport_id} description .*)"

    service = "".join(re.findall(service_pattern, conf))
    bld = "".join(re.findall(bld_pattern, conf))
    service_port = [f"{service} ingress {bld} egress {bld}"]
    service_desc = re.findall(service_desc_pattern, conf)
    qos = ["qos trust dscp", "qos cos dscp-remark DSCP-TO-COS", "qos egress-cos dscp-remark DSCP-TO-COS"]
    
    return service_port + service_desc + qos

def format_pon_conf(conf, onu_id):
    pon_pattern = rf"pon-onu-mng\sgpon-onu_\d+/\d+/\d+:{onu_id}\n([\s\S]*?)!"
    pon = "".join(re.findall(pon_pattern, conf)).replace('type internet', '').split('\n')
    pon = [i.strip().replace('  ', ' ') for i in pon if i != '']

    return pon

def get_onu_conf(file, onu_list):
    onu_conf = {}
    for onu in onu_list:
        onu_conf[onu] = {}
        
        # ONU CONF
        onu_id = re.search(r":(\d+)", onu).group(1)
        conf_pattern = rf"interface\sgpon-onu_\d+/\d+/\d+:{onu_id}\n[^!]*!"
        pon_conf_pattern =  rf"\npon-onu-mng\sgpon-onu_\d+/\d+/\d+:{onu_id}\n[\s\S]*?!"
        
        conf = re.findall(conf_pattern, file) + re.findall(pon_conf_pattern, file)
        conf = "".join(conf).replace(').', ')')

        formatted_conf = format_onu_conf(conf)

        onu_conf[onu]["conf"] = formatted_conf
        
        # VPORT CONF
        vport_pattern = r"service-port\s(\d+)"
        vports = re.findall(vport_pattern, conf)
        vports = [f"interface vport-{onu.replace(':','.')}:{vport}" for vport in vports]
        vports = sorted(list(set(vports)))

        if len(vports) != 0:
            for vport in vports:
                onu_conf[onu][vport] = format_vport_conf(conf, vport)
        
        # PON CONF
        pon = f"pon-onu-mng gpon_onu-{onu}"
        onu_conf[onu][pon] = format_pon_conf(conf, onu_id)

    return onu_conf

def build_template(onu_conf):
    templates = []
    for key, values in onu_conf.items():
        template = f"inteface gpon_onu-{key}\n"
        for value in values['conf']:
            template += f" {value}\n"
        
        template += "!\n"
        
        for value in values:
            if 'vport' in value or 'pon-onu' in value:
                template += f" {value}\n"
                for i in values[value]:
                    template += f" {i}\n"
                template += "!\n"

        templates.append(template)

    result = "".join(templates)
    return result