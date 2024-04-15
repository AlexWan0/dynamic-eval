from .problem_values import *
from mwp.problems.base import BinaryOperation


def init_binops(problem):
    op_map = {}

    ops = problem['operations'].keys()

    for op in ops:
        def _binop(constants, templates, units):
            return lambda *args, **kwargs: BinaryOperation(
                *args,
                constants=constants,
                templates=templates,
                units=units,
                **kwargs
            )
        
        op_map[op] = _binop(
            constants=problem['constants'],
            templates=problem['operations'][op]['templates'],
            units=problem['operations'][op]['units']
        )
    
    return op_map


PROBLEMS = {
    'jobs': lambda: (init_binops(jobs), jobs),
    'jobs_nodiv': lambda: (init_binops(jobs_nodiv), jobs_nodiv),
}
