__all__ = ("undefined",)


class UndefinedClass(str):

    def __repr__(self):
        return "undefined"

undefined = UndefinedClass()