# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

class BaseForm(object):
    def __init__(self, line, column, filename="<string>"):
        self.line = line
        self.column = column
        self.filename = filename


class NumberForm(BaseForm):
    def __init__(self, value, raw, line, column, filename="<string>"):
        BaseForm.__init__(self, line, column, filename)
        self.value = value
        self.raw = raw


class StringForm(BaseForm):
    def __init__(self, value, line, column, filename="<string>"):
        BaseForm.__init__(self, line, column, filename)
        self.value = value


class SymbolForm(BaseForm):
    def __init__(self, name, line, column, filename="<string>"):
        BaseForm.__init__(self, line, column, filename)
        self.name = name


class ListForm(BaseForm):
    def __init__(self, items, line, column, filename="<string>"):
        BaseForm.__init__(self, line, column, filename)
        self.items = items

