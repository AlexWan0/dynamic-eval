from abc import ABC, abstractmethod
import anthropic
import os

from .prompts import get_prompt


class Model(ABC):
    @abstractmethod
    def predict(self, input: str) -> str:
        pass

    @abstractmethod
    def is_correct(self, raw_output: str, answer: int) -> bool:
        pass


class ClaudeModel(Model):
    def __init__(self, model_name: str, prompt: str=get_prompt('basic_cot')):
        self.model_name = model_name
        self.prompt = prompt

        self.key = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

    def predict(self, input_problem: str, max_tokens: int = 128, verbose: bool=False) -> str:
        fs_example = self.prompt.fs
        input_template = self.prompt.input_template

        fs_prefix = f"{anthropic.HUMAN_PROMPT} {input_template.format(problem=fs_example[0])}{anthropic.AI_PROMPT} {fs_example[1]}"

        model_input_str = f"{fs_prefix}"
        model_input_str += f"{anthropic.HUMAN_PROMPT} {input_template.format(problem=input_problem)}{anthropic.AI_PROMPT}"

        if verbose:
            print('>' * 80)
            print(model_input_str)

        model_output = self.key.completions.create(
            prompt=model_input_str,
            stop_sequences=[anthropic.HUMAN_PROMPT],
            model=self.model_name,
            max_tokens_to_sample=max_tokens,
            temperature=0.0
        )

        model_output_str = model_output.completion.strip()

        if verbose:
            print('<' * 80)
            print(model_output_str)

        return model_output_str

    def is_correct(self, raw_output: str, answer: int) -> bool:
        return self.prompt.parser(raw_output) == answer
