def get_klass(pth):
    sep_index = pth.rfind('.')
    module_name = pth[:sep_index]
    class_name = pth[sep_index + 1:]
    _tmp = __import__(
        module_name,
        globals(),
        locals(),
        [
            class_name,
        ],
        0,
    )
    return getattr(_tmp, class_name)


get_function = get_klass
