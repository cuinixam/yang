from typing import Any, Callable


def validates(req_ids: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def _doc(func: Callable[..., Any]) -> Callable[..., Any]:
        user_doc = func.__doc__ or ""
        func.__doc__ = (
            user_doc
            + "\n"
            + f"""
         .. item:: UTEST-{func.__module__}.{func.__qualname__}
            :validates: {req_ids}
         """
        )
        return func

    return _doc


def fulfills(req_ids: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def _doc(func: Callable[..., Any]) -> Callable[..., Any]:
        user_doc = func.__doc__ or ""
        func.__doc__ = (
            user_doc
            + "\n"
            + f"""
         .. item:: IMPL-{func.__module__}.{func.__qualname__}
            :fulfills: {req_ids}
         """
        )
        return func

    return _doc
