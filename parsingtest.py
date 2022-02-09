import argparse
import enum
import typing

from dataclasses import dataclass

parser = argparse.ArgumentParser()

class ConnectionProtocolType(enum.Enum):
    HTTP = 'http',
    WS = 'ws'

@dataclass
class ConnectionType:
    http: str
    ws: str

def indent_collection_as_str(collection: typing.Sequence[typing.Any]) -> str:
    #  print(f'{collection}')
    if not collection or len(collection) == 0:
        return "None"
    return "\n    ".join(f"{item}" for item in collection)


class ParseToDict(argparse.Action):
    compound_data:typing.List[dict[ConnectionProtocolType,str]] = []
    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            if len(values) == 1:
                self.compound_data.append({ConnectionProtocolType.HTTP: values[0], ConnectionProtocolType.WS: values[0]})
            else:
                self.compound_data.append({ConnectionProtocolType.HTTP: values[0], ConnectionProtocolType.WS: values[1]})
            setattr(namespace, self.dest, self.compound_data)

class ParseToClass(argparse.Action):
    compound_data:typing.List[ConnectionType] = []
    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            if len(values) == 1:
                self.compound_data.append(ConnectionType(values[0], values[0]))
            else:
                self.compound_data.append(ConnectionType(values[0], values[1]))
            setattr(namespace, self.dest, self.compound_data)


parser.add_argument('--cluster-url', nargs='*', action=ParseToDict,
                    default = None)
parser.add_argument('--cluster-url2', nargs='*', action=ParseToClass,
                    default = None)

aargs = parser.parse_args()
print(f'>> {aargs.cluster_url}')
print(f'>> {indent_collection_as_str(aargs.cluster_url2)}')
