from importlib import import_module
from jinja2 import Environment, FileSystemLoader


def get_klass(pth):
    sep_index = pth.rfind('.')
    module_name = pth[:sep_index]
    class_name = pth[sep_index + 1:]
    mod = import_module(module_name)
    return getattr(mod, class_name)


get_function = get_klass


def get_jinja_environment(
    template_dir,
    template_filters,
    template_functions
):
    env = Environment(loader=FileSystemLoader(template_dir))
    for filter in template_filters:
        env.filters[filter.__name__] = filter
    for func in template_functions:
        env.globals[func.__name__] = func
    return env
