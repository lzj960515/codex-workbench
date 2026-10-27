from converter import Converter


class ConverterRegistry:
    def get(self, name):
        if name == 'article':
            return Converter()
        raise ValueError(name)
