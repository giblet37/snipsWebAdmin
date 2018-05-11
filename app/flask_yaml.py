import yaml
from collections import OrderedDict

__version__ = "1.0.0"


class OrderedDictYAMLLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map',
                             type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap',
                             type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                                                    'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                                                        node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

class Yaml():
    """Main Mqtt class."""

    def __init__(self, app=None):
        # type: (Flask) -> None
        self.app = app
        #self._connect_handler = None
        self.data = {}  # type: Dict[str]

        if app is not None:
            self.init_app(app)

    def init_app(self, app, filename=None):
        if filename:
            self.file = filename
        else:
            self.file = app.config.get("YAMLFILE", None)
 
        if self.file:
            self._load_yaml()
            

    def _load_yaml(self):
        with open(self.file, 'r') as stream:
            try:
                self.data = yaml.load(stream, Loader=OrderedDictYAMLLoader)
                #self.data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def get_yaml_data(self, heading):
        #my_dictionary = OrderedDict()
        #for k, v in self.data[heading].items():
        #    print("1111 key: {} | val: {}".format(k, v))
        return self.data.get(heading, self.data)
