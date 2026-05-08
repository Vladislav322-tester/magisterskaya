import os

MUTATION = os.getenv("FA_MUTATION")
IMPL = os.getenv("FA_IMPL", "FA_simple")

if MUTATION:
    module = __import__(f"src.mutations.{MUTATION}", fromlist=[IMPL])
    FA = getattr(module, IMPL)
else:
    module = __import__(f"src.{IMPL}", fromlist=[IMPL])
    FA = getattr(module, IMPL)