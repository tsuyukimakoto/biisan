from importlib import import_module


def get_klass(pth):
    sep_index = pth.rfind('.')
    module_name = pth[:sep_index]
    class_name = pth[sep_index + 1:]
    mod = import_module(module_name)
    return getattr(mod, class_name)


get_function = get_klass
