"""Single import point for experiment-controlled FA implementations."""

from __future__ import annotations

import os
from importlib import import_module
from typing import Type


IMPL_ENV = "FA_IMPL"
MUTATION_ENV = "FA_MUTATION"
DEFAULT_IMPL = "FA_simple"


def get_fa_class() -> Type:
    impl = os.getenv(IMPL_ENV, DEFAULT_IMPL)
    mutation = os.getenv(MUTATION_ENV)
    module_name = f"src.mutations.{mutation}" if mutation else f"src.{impl}"
    module = import_module(module_name)

    try:
        fa_class = getattr(module, impl)
    except AttributeError as exc:
        raise ImportError(
            f"{module_name} does not define expected class {impl}"
        ) from exc

    setattr(fa_class, "__factory_impl__", impl)
    setattr(fa_class, "__factory_mutation__", mutation)
    setattr(fa_class, "__factory_module__", module_name)
    return fa_class


def describe_selected_fa() -> str:
    fa_class = get_fa_class()
    mutation = getattr(fa_class, "__factory_mutation__", None) or "none"
    module = getattr(fa_class, "__factory_module__", fa_class.__module__)
    impl = getattr(fa_class, "__factory_impl__", fa_class.__name__)
    return f"impl={impl}; class={fa_class.__name__}; mutation={mutation}; module={module}"


FA = get_fa_class()
