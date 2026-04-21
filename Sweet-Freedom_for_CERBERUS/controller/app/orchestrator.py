from .visible_runtime import VisibleRuntime

runtime = VisibleRuntime()


def handle_text(text: str):
    return runtime.process(text)
