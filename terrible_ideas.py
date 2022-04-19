import builtins
import ctypes
import warnings
from collections.abc import Mapping, Sequence
from numbers import Number

import fishhook

IDEAS = {}
IS_IPYTHON = hasattr(builtins, "get_ipython")

CHAR_SPLIT_MAP = {
    "w": "vv",
    "W": "VV",
    "m": "nn",
    "d": "cl",
    "L": "|_",
    "X": "><",
    "V": "\/",
    "K": "|<",
    "B": "|3",
    "D": "|)",
    # etc..
}


class Idea:
    def __init__(self):
        self.enabled = None

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


def camelize(match):
    a, b = match.groups()
    return f"{a}_{b.lower()}" if a else b.lower()


def register(cls):
    import re

    inst = cls()
    IDEAS[re.sub(r"(.?)([A-Z])", camelize, cls.__name__)] = inst
    return inst


@register
class DictSort(Idea):
    def enable(self):
        @fishhook.hook(dict)
        def sort(self, key=None):
            keys = sorted(self, key=key)
            new = {key: self[key] for key in keys}
            self.clear()
            self.update(new)

        super().enable()

    def disable(self):
        fishhook.unhook(dict, "sort")
        super().disable()


@register
class IterableInt(Idea):
    def enable(self):
        @fishhook.hook(int)
        def __iter__(self):
            return iter(range(self))

        super().enable()

    def disable(self):
        fishhook.unhook(int, "__iter__")
        super().disable()


@register
class SpellcheckClasses(Idea):
    def enable(self):
        import spelcheck

        if spelcheck.new != builtins.__build_class__:
            builtins.__build_class__ = spelcheck.new
        super().enable()

    def disable(self):
        import spelcheck

        builtins.__build_class__ = spelcheck.old
        super().disable()


@register
class FloatSlicing(Idea):
    def enable(self):
        @fishhook.hook(str)
        def __getitem__(self, something):
            if not isinstance(something, slice):
                return fishhook.orig(self, something)
            start, stop, step = something.start, something.stop, something.step
            split_start = start % 1 == 0.5 if start else False
            split_stop = stop % 1 == 0.5 if stop else False
            if split_start:
                start = int(start)
            if split_stop:
                stop = int(stop) + 1
            res = fishhook.orig(self, slice(start, stop, step))
            if split_start:
                res = CHAR_SPLIT_MAP.get(res[0], (..., res[0]))[1] + res[1:]
            if split_stop:
                res = res[:-1] + CHAR_SPLIT_MAP.get(res[-1], (res[-1], ...))[0]
            return res

        super().enable()

    def disable(self):
        fishhook.unhook(str, "__getitem__")
        super().disable()


@register
class WeakTyping(Idea):
    def enable(self):
        @fishhook.hook(str)
        def __add__(self, other):
            if isinstance(other, (int, float, type(None))):
                try:
                    val = int(self)
                except ValueError:
                    try:
                        val = float(self)
                    except ValueError:
                        return self + str(other)
                return val + other
            elif isinstance(other, list):
                return [self, *other]
            elif isinstance(other, tuple):
                return tuple(self, *other)
            elif isinstance(other, dict):
                return {self: None, **other}
            return fishhook.orig(self, other)

        @fishhook.hook(dict)
        def __add__(self, other):
            if isinstance(other, Mapping):
                res = {}
                for k in self.keys() | other.keys():
                    if k in self and k not in other:
                        res[k] = self[k]
                    elif k not in self and k in other:
                        res[k] = other[k]
                    elif isinstance(self[k], Number) and isinstance(other[k], Number):
                        res[k] = self[k] + other[k]
                    else:
                        res[k] = other[k]
                return res

            if isinstance(other, Sequence):
                return self + dict(other)

            if isinstance(other, Number):
                res = self.copy()
                for k, v in res.items():
                    if isinstance(v, Number):
                        res[k] = v + other
                return res
            else:
                return self
        fishhook.hook(dict, name="__radd__")(__add__)

        @fishhook.hook(dict)
        def __mul__(self, other):
            if isinstance(other, Mapping):
                res = {}
                for k in self.keys() | other.keys():
                    if k in self and k not in other:
                        res[k] = self[k]
                    elif k not in self and k in other:
                        res[k] = other[k]
                    elif isinstance(self[k], Number) and isinstance(other[k], Number):
                        res[k] = self[k] * other[k]
                    else:
                        res[k] = other[k]
                return res

            if isinstance(other, Sequence):
                return self * dict(other)

            if isinstance(other, Number):
                res = self.copy()
                for k, v in res.items():
                    if isinstance(v, Number):
                        res[k] = v * other
                return res
            else:
                return self
        fishhook.hook(dict, name="__rmul__")(__mul__)

        @fishhook.hook(dict)
        def __truediv__(self, other):
            if isinstance(other, Mapping):
                res = {}
                for k in self.keys() | other.keys():
                    if k in self and k not in other:
                        res[k] = self[k]
                    elif k not in self and k in other:
                        res[k] = other[k]
                    elif isinstance(self[k], Number) and isinstance(other[k], Number):
                        res[k] = self[k] / other[k]
                    else:
                        res[k] = other[k]
                return res

            if isinstance(other, Sequence):
                return self / dict(other)

            if isinstance(other, Number):
                res = self.copy()
                for k, v in res.items():
                    if isinstance(v, Number):
                        res[k] = v / other
                return res
            else:
                return self

        @fishhook.hook(dict)
        def __sub__(self, other):
            if isinstance(other, Mapping):
                res = {}
                for k in self.keys() | other.keys():
                    if k in self and k not in other:
                        res[k] = self[k]
                    elif k not in self and k in other:
                        res[k] = other[k]
                    elif isinstance(self[k], Number) and isinstance(other[k], Number):
                        res[k] = self[k] - other[k]
                    else:
                        res[k] = other[k]
                return res

            if isinstance(other, Sequence):
                return self - dict(other)

            if isinstance(other, Number):
                res = self.copy()
                for k, v in res.items():
                    if isinstance(v, Number):
                        res[k] = v - other
                return res
            else:
                return self

        @fishhook.hook(str)
        def __sub__(self, other):
            error = TypeError(
                f"unsupported operand type(s) for -: 'str' and {type(other).__name__!r}"
            )
            if isinstance(other, (int, float)):
                try:
                    val = int(self)
                except ValueError:
                    try:
                        val = float(self)
                    except ValueError:
                        raise error
                return val - other
            raise error

        if not IS_IPYTHON:

            @fishhook.hook(list)
            def __add__(self, other):
                if isinstance(other, (int, float, type(None))):
                    return [*self, other]
                elif other is Ellipsis:
                    new = [*self]
                    new.append(new)
                    return new
                elif isinstance(other, (dict, tuple)):
                    return [*self, *other]
                return fishhook.orig(self, other)

        super().enable()

    def disable(self):
        fishhook.unhook(dict, "__add__")
        fishhook.unhook(dict, "__radd__")
        fishhook.unhook(dict, "__sub__")
        fishhook.unhook(dict, "__mul__")
        fishhook.unhook(dict, "__rmul__")
        fishhook.unhook(dict, "__truediv__")
        fishhook.unhook(str, "__add__")
        fishhook.unhook(str, "__sub__")
        if not IS_IPYTHON:
            fishhook.unhook(list, "__add__")
        super().disable()


@register
class MutableTuples(Idea):
    def enable(self):
        @fishhook.hook(tuple)
        def __setitem__(self, idx, item):
            old_value = self[idx]
            element_ptr = ctypes.c_longlong.from_address(id(self) + (3 + idx) * 8)
            element_ptr.value = id(item)

            ref_count = ctypes.c_longlong.from_address(id(item))
            ref_count.value += 1

            ref_count = ctypes.c_longlong.from_address(id(old_value))
            ref_count.value -= 1

        @fishhook.hook(tuple)
        def resize(self, new_size):
            size = ctypes.c_longlong.from_address(id(self) + 2 * 8)
            if new_size > size.value:
                warnings.warn("New tuple size is larger than old size")
            size.value = new_size

        super().enable()

    def disable(self):
        fishhook.unhook(tuple, "__setitem__")
        fishhook.unhook(tuple, "resize")
        super().disable()


@register
class MutableStrings(Idea):
    def enable(self):
        # size is always in position 16?
        def get_size(s):
            return ctypes.c_long.from_address(id(s) + 16).value

        def set_size(s, val):
            ctypes.c_long.from_address(id(s) + 16).value = val

        fishhook.hook(str, name="size")(property(fget=get_size, fset=set_size))

        def unicode_kind(s):
            c = ord(max(s))
            if c < 256:
                return 1
            elif c < 256*256:
                return 2
            else:
                return 4

        @fishhook.hook(str)
        def __setitem__(self, item, value):
            if isinstance(item, slice):
                for i, char in zip(range(item.start or 0, item.stop or 999, item.step or 1), value):
                    self[i] = char
                return
            kind = unicode_kind(self)
            if kind == 1:
                ctypes.c_uint8.from_address(id(self) + 48 + item).value = ord(value)
            elif kind == 2:
                ctypes.c_uint16.from_address(id(self) + 48 + item).value = ord(value)
            elif kind == 4:
                ctypes.c_uint32.from_address(id(self) + 48 + item).value = ord(value)

        super().enable()

    def disable(self):
        fishhook.unhook(str, "__setitem__")
        fishhook.unhook(str, "size")
        super().disable()


def __getattr__(attr):
    if attr not in IDEAS:
        raise AttributeError
    idea = IDEAS[attr]
    if idea.enabled is None:
        idea.enable()
    return idea
