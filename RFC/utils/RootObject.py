import os

from .functional_utils import log, parse_restriction, check_restriction, pretty_print_parser


class RootObject:
    def print(
        self,
        include='all',
        exclude='none',
        include_sub=True,
        **kwargs,
    ):
        file = kwargs.pop('file', ['stdout'])
        mode = kwargs.pop('mode', 'info')
        log('\n'+self._to_str(include=include, exclude=exclude, include_sub=include_sub)+'\n', file=file, mode=mode, **kwargs)

    def _get_self_type_name(
        self,
    ):
        return type(self).__name__
    
    def _parse_attr(
        self,
        include='all',
        exclude='none',
        include_sub=True,
        base_type=object,
    ):
        include = parse_restriction(include, 'include', __name__)
        exclude = parse_restriction(exclude, 'exclude', __name__)
        _dict = {}
        for k, v in self.__dict__.items():
            if not include_sub and isinstance(v, base_type):
                continue
            if check_restriction(k, include, exclude):
                _dict[k] = v
        return _dict

    def _to_str(
        self,
        include='all',
        exclude='none',
        include_sub=True,
        base_type=object,
        return_attr=False,
    ):
        if return_attr:
            return self._parse_attr(
                include=include,
                exclude=exclude,
                include_sub=include_sub,
                base_type=base_type,
            )
        else:
            return f"{self._get_self_type_name()}\n" + pretty_print_parser(
                self._parse_attr(
                    include=include,
                    exclude=exclude,
                    include_sub=include_sub,
                    base_type=base_type,
                )
            )

    def __str__(
        self,
    ):
        # return f"{self._get_self_type_name()}\n" + pretty_print_parser(self.__dict__)
        return self._to_str()