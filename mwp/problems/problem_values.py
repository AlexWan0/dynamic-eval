_constants = {
    'name': ['Alice',  'Bob',  'Charlie',  'David',  'Eve',  'Fiona',  'George',  'Hannah',  'Ian',  'Julia',  'Kevin',  'Linda',  'Mike',  'Nora',  'Oscar',  'Patty',  'Quinn',  'Rachel',  'Steve',  'Tina'],
    'job': ['cashier',  'cook',  'cleaner',  'manager',  'waiter',  'driver',  'nurse',  'engineer',  'teacher',  'clerk',  'barista',  'chef',  'therapist',  'pharmacist',  'carpenter',  'plumber',  'electrician',  'scientist',  'artist',  'lawyer'],
    'color': ['red',  'blue',  'green',  'yellow',  'purple',  'orange',  'pink',  'black',  'white',  'gray',  'teal',  'maroon',  'violet',  'silver',  'gold',  'beige',  'navy',  'lime',  'olive',  'cyan'],
    'item': ['toy',  'book',  'game',  'piece of candy',  'puzzle',  'ball',  'sticker',  'notebook',  'pen',  'keychain',  'map',  'flashlight',  'hat',  'scarf',  'glove',  'sock',  'dollar',  'watch',  'tape',  'bag']
}

jobs = {
    'constants': _constants,
    'operations': {
        '*': {
            'templates': {
                'id_utt': 'the amount {name} made working as a {job}',
                'utt': 'Being a {job} pays {arg0} an hour. {name} worked {arg1} as a {job}.'
            },
            'units':{
                'arg0': '${}',
                'arg1': '{} hours'
            }
        },
        '+': {
            'templates': {
                'id_utt': 'the amount of money in the {color} piggy bank',
                'utt': 'The group pooled {arg0} and {arg1} and put it in a {color} piggy bank.'
            },
            'units':{
                'arg0': '${}',
                'arg1': '${}'
            }
        },
        '-': {
            'templates': {
                'id_utt': 'the amount of money left after buying a {item}',
                'utt': 'A {item} costs {arg1}. The group bought a {item} using {arg0}.'
            },
            'units':{
                'arg0': '${}',
                'arg1': '${}'
            }
        },
        '/': {
            'templates': {
                'id_utt': 'the amount of money in the {color} piggy bank',
                'utt': 'The group split {arg0} among {arg1} piggy banks. One of these piggy banks is {color}.'
            },
            'units':{
                'arg0': '${}',
                'arg1': '{}'
            }
        }
    },
    'question': 'What is the value of {query}?',
    'grammar': """
        S -> E
        E -> '(' ADD ')' | '(' SUB ')' | '(' MUL ')' | '(' DIV ')'
        ADD -> E '+' E
        SUB -> E '-' N
        MUL -> N '*' N
        DIV -> E '/' N
        N -> '{x}'
    """,
    'val_range': (10, 1000),
}
