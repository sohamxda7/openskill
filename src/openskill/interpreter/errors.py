# Author: Soham Sen <sensoham135@gmail.com> <sohamsen2000@outlook.com>

class SkillError(Exception):
    """Base OpenSKILL error."""


class SkillSyntaxError(SkillError):
    def __init__(self, message, filename="<string>", line=None, column=None):
        self.message = message
        self.filename = filename
        self.line = line
        self.column = column
        super(SkillSyntaxError, self).__init__(self.__str__())

    def __str__(self):
        location = self.filename
        if self.line is not None and self.column is not None:
            location = "%s:%s:%s" % (location, self.line, self.column)
        return "SyntaxError at %s: %s" % (location, self.message)


class SkillEvalError(SkillError):
    def __init__(self, message, form=None):
        self.message = message
        self.form = form
        super(SkillEvalError, self).__init__(self.__str__())

    def __str__(self):
        if self.form is None:
            return "EvalError: %s" % self.message
        filename = getattr(self.form, "filename", "<string>")
        line = getattr(self.form, "line", None)
        column = getattr(self.form, "column", None)
        if line is None or column is None:
            return "EvalError at %s: %s" % (filename, self.message)
        return "EvalError at %s:%s:%s: %s" % (filename, line, column, self.message)

