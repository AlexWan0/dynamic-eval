import random


class Value():
    def get_value(self):
        raise NotImplementedError()

    def get_value_units(self, units_templ: str) -> str:
        if isinstance(self, Constant):
            return units_templ.format(self.get_value())
        elif isinstance(self, Operation):
            return self.get_value()
        
        raise ValueError(f'Unknown value type: {type(self)}')


class Constant(Value):
    def __init__(self, value: str):
        self.value = value

    def get_value(self) -> str:
        return self.value


class Operation(Value):
    def get_id_utt(self) -> str:
        raise NotImplementedError()

    def get_utt(self) -> str:
        raise NotImplementedError()

    def get_value(self: str) -> str:
        return self.get_id_utt()

    def update_used_vals(self, used_vals):
        for k, v in self.id.items():
            used_vals.setdefault(k, []).append(v)

def pick_id(values, used_values, default):
    if default is not None:
        return default
    
    good_values = [v for v in values if v not in used_values]

    if len(good_values) == 0:
        raise ValueError('No more values to pick from')

    return random.choice(good_values)

class BinaryOperation(Operation):
    def __init__(
            self,
            arg0: Value,
            arg1: Value,
            
            constants: dict[str, str], # set of possible values for each id variable
            templates: dict[str, str], # templates for the utterances
            units: dict[str, str], # units for each argument
            
            defaults: dict[str, str]={},
            used_vals={}
        ):

        self.id = {}

        for id_key, possible_values in constants.items():
            self.id[id_key] = pick_id(
                possible_values,
                used_vals.get(id_key, []),
                defaults.get(id_key, None)
            )

        self.arg0 = arg0
        self.arg1 = arg1

        self.templates = templates
        self.units = units
    
    def get_id_utt(self) -> str:
        return self.templates['id_utt'].format(
            arg0=self.arg0.get_value_units(self.units['arg0']),
            arg1=self.arg1.get_value_units(self.units['arg1']),
            **self.id
        )

    def get_utt(self) -> str:
        return self.templates['utt'].format(
            arg0=self.arg0.get_value_units(self.units['arg0']),
            arg1=self.arg1.get_value_units(self.units['arg1']),
            **self.id
        )
