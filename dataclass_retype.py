import dataclasses
from dataclasses import dataclass
from typing import Dict, Optional
from logging import log
import typing
import inspect

## ------------ DATA -------------
@dataclass
class MyDataClass:
    optional_num: Optional[int] = None

my_dict: Dict = {'optional_num': '13'}


## ------------ FUNCTION -------------
def to_dataclass_1(cls, data: Dict):
        return cls(
            **{
                key: (data[key] if val.default == val.empty else data.get(key, val.default))
                for key, val in inspect.signature(cls).parameters.items()
            }
        )

def to_dataclass_2(cls, data: Dict):
    fields = cls.__dataclass_fields__
    return cls(
        **{
            key: fields[key].type(val)
            for key,val in data.items() if key in fields
        }
    )

def to_dataclass_3(cls, data: Dict):
    if not dataclasses.is_dataclass(cls):
        raise ValueError(f'Class "{cls}" is not a type of dataclass')

    fields = cls.__dataclass_fields__
    dict_for_loading = {}

    try:
        for key, val in data.items():
            if key in fields:

                field = fields[key]
                if field.type is typing.Optional[int]:
                    print(f'> in if: {type(field)} {field}')
                    dict_for_loading[key] = int(val)
                else:
                    dict_for_loading[key] = field.type(val)

        return cls(**dict_for_loading)
    except Exception:
        log.error(f'Config data did not provide the attribute of the dataclass "{cls}"')
        raise



## ------------ TEST -------------
dataclass_1: MyDataClass = to_dataclass_1(MyDataClass, my_dict)
# we want this to be int!
assert dataclass_1.optional_num == '13'


# this just fails with: TypeError: Cannot instantiate typing.Union
# dataclass_2: MyDataClass = to_dataclass_2(MyDataClass, my_dict)
# assert dataclass_2.optional_num == 13  

# this works but hardly to have if/else with all Optional Union subtypes - like Optional[int], Optional[float], Optional[str]...
dataclass_3: MyDataClass = to_dataclass_3(MyDataClass, my_dict)
assert dataclass_3.optional_num == 13