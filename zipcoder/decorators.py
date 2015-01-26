
def singleton(the_class):
    """Singleton decorator. Only one instance is ever created per run-time."""
    _instances = dict()

    def get_instance():
        if the_class not in _instances:
            _instances[the_class] = the_class()
        return _instances[the_class]

    return get_instance