from importlib import import_module
from jinja2 import Environment, FileSystemLoader


def get_klass(pth):
    sep_index = pth.rfind('.')
    module_name = pth[:sep_index]
    class_name = pth[sep_index + 1:]
    mod = import_module(module_name)
    return getattr(mod, class_name)

def get_environment(config):
    env = Environment(loader=FileSystemLoader(config.settings.template_dirs))
    for filter_name, filter_func in config.settings.custom_filters.items():
        env.filters[filter_name] = filter_func
    return env


get_function = get_klass
