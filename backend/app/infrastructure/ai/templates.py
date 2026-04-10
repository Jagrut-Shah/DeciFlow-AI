import re

class PromptTemplate:
    def __init__(self, template: str):
        self.template = template
        self.variables = set(re.findall(r"\{(\w+)\}", template))

    def format(self, **kwargs) -> str:
        missing = self.variables - kwargs.keys()
        if missing:
            raise ValueError(f"Missing prompt variables: {missing}")
        return self.template.format(**kwargs)
