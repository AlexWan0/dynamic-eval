from dataclasses import dataclass
import re


basic_cot_prompt = """The following is a math word problem:
{problem}

Explain your reasoning step by step. Write your final answer at the end. Prefix your answer with "The answer is"."""

basic_cot_prompt_fs = ("There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?", "There are 15 trees originally. Then there were 21 trees after some more were planted. So there must have been 21 - 15 = 6. The answer is 6")

def basic_cot_prompt_parse(raw_output: str) -> int:
    # get everything after prefix
    match = re.search(r'answer is(.*)', raw_output)
    if not match:
        return None
    
    match_str = match.group(1)
    print('parser str:', match_str)

    # find an integer in the string
    match = re.findall(r'\d+', match_str)
    if not match:
        return None
    
    val = int(match[-1])
    print('parser int:', val)
    
    return val


@dataclass
class Prompt:
    input_template: str
    fs: tuple[str]
    parser: callable = basic_cot_prompt_parse


PROMPTS = {
    'basic_cot': Prompt(basic_cot_prompt, basic_cot_prompt_fs, basic_cot_prompt_parse),
}

def get_prompt(prompt_name: str) -> Prompt:
    return PROMPTS[prompt_name]
