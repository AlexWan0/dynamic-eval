# Overview
**Main idea:** Given a task (e.g., arithmetic in math word problems) and a model, can we figure out what types of problems models find difficult/easy?

Here, I represent math word problems with a [grammar](https://github.com/AlexWan0/dynamic-eval/blob/6ff81f813662d822ae5b2996ee0eaf7216fe6af9/mwp/problems/problem_values.py#L53), then search through this grammar using Thompson sampling. The latter was inspired by ([Sclar et al., 2023](https://arxiv.org/pdf/2310.11324)).

