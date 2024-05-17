import pandas as pd
from typing import Callable, Any

from ..model import Model


def make_model_reward(model: Model, **kwargs) -> Callable[[pd.DataFrame], int]:
    def reward_func(samples: pd.DataFrame) -> tuple[int, list[Any]]:
        correct = 0

        raw_outputs = []

        for _, row in samples.iterrows():
            input_str = f'{row["problem"]} {row["question"]}'
            target_val = row['target_val']

            raw_output = model.predict(input_str, **kwargs)

            if model.is_correct(raw_output, target_val):
                correct += 1
            
            raw_outputs.append({
                'index': row.name,
                'input_str': input_str,
                'raw_output': raw_output
            })

        return correct, raw_outputs

    return reward_func
