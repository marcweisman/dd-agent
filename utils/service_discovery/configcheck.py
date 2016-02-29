from config import load_check_directory, SD_CONFIG_BACKENDS
from util import get_hostname
from utils.dockerutil import DockerUtil
from utils.service_discovery.config_stores import get_config_store


def sd_configcheck(agentConfig):
    hostname = get_hostname(agentConfig)
    agentConfig['trace_config'] = True
    configs = {
        # check_name: (config_source, config)
    }

    print("\nLoading check configurations...\n\n")
    configs = load_check_directory(agentConfig, hostname)
    print("\nSource of the configuration objects built by the agent:\n")
    for check_name, config in configs.iteritems():
        print('Check "%s":\n  source --> %s\n  config --> %s\n' % (check_name, config[0], config[1]))

    try:
        print_containers()
    except Exception:
        print("Failed to collect containers info.")

    try:
        print_templates(agentConfig)
    except Exception:
        print("Failed to collect configuration templates.")


def print_containers():
    containers = DockerUtil().client.containers()
    print("\nContainers info:\n")
    print("Number of containers found: %s" % len(containers))
    for co in containers:
        c_id = 'ID: %s' % co.get('Id')[:12]
        c_image = 'image: %s' % co.get('Image')
        c_name = 'name: %s' % DockerUtil.container_name_extractor(co)[0]
        print("\t- %s %s %s" % (c_id, c_image, c_name))
    print('\n')


def print_templates(agentConfig):
    if agentConfig.get('sd_config_backend') in SD_CONFIG_BACKENDS:
        print("Configuration templates:\n")
        templates = {}
        sd_template_dir = agentConfig.get('sd_template_dir')
        config_store = get_config_store(agentConfig)
        try:
            templates = config_store.dump_directory(sd_template_dir)
        except Exception as ex:
            print("Failed to extract configuration templates from the backend:\n%s" % str(ex))

        for img, tpl in templates.iteritems():
            print(
                "- Image %s:\n\tcheck name: %s\n\tinit_config: %s\n\tinstance: %s" % (
                    img,
                    tpl.get('check_name'),
                    tpl.get('init_config'),
                    tpl.get('instance'),
                )
            )
