import os, sys, yaml, argparse

import jinja2
import jinja2.loaders

def _parse_ini(data_string):
    """ INI data input format.

    data.ini:

    ```
    [nginx]
    hostname=localhost
    webroot=/var/www/project
    logs=/var/log/nginx/
    ```

    Usage:

        $ j2 config.j2 data.ini
        $ cat data.ini | j2 --format=ini config.j2
    """
    from io import BytesIO

    # Override
    class MyConfigParser(ConfigParser.ConfigParser):
        def as_dict(self):
            """ Export as dict
            :rtype: dict
            """
            d = dict(self._sections)
            for k in d:
                d[k] = dict(self._defaults, **d[k])
                d[k].pop('__name__', None)
            return d

    # Parse
    ini = MyConfigParser()
    ini.readfp(BytesIO(data_string))

    # Export
    return ini.as_dict()

def _parse_json(data_string):
    """ JSON data input format

    data.json:

    ```
    {
        "nginx":{
            "hostname": "localhost",
            "webroot": "/var/www/project",
            "logs": "/var/log/nginx/"
        }
    }
    ```

    Usage:

        $ j2 config.j2 data.json
        $ cat data.json | j2 --format=ini config.j2
    """
    return json.loads(data_string)

def _parse_yaml(data_string):
    """ YAML data input format.

    data.yaml:

    ```
    nginx:
      hostname: localhost
      webroot: /var/www/project
      logs: /var/log/nginx
    ```

    Usage:

        $ j2 config.j2 data.yml
        $ cat data.yml | j2 --format=yaml config.j2
    """
    return yaml.load(data_string)

FORMATS = {
    'ini':  _parse_ini,
    'json': _parse_json,
    'yaml': _parse_yaml,
}

#endregion

#region Imports

# JSON: simplejson | json
try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
         del FORMATS['json']

# INI: Python 2 | Python 3
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

# YAML
try:
    import yaml
except ImportError:
    del FORMATS['yaml']

#endregion



def read_context_data(format, f):
    """ Read context data into a dictionary
    :param format: Data format
    :type format: str
    :param f: Data file stream, or None
    :type f: file|None
    :return: Dictionary with the context data
    :rtype: dict
    """
    # Read data string stream
    data_string = f.read()

    # Parse it
    if format not in FORMATS:
        raise ValueError('{} format unavailable'.format(format))

    return FORMATS[format](data_string)

class SingleTemplateLoader(jinja2.BaseLoader):
    """ Custom Jinja2 template loader which just loads a single template """

    def __init__(self, contents):
        self.contents = contents

    def get_source(self, environment, template):
        uptodate = lambda: False
        return self.contents, template, uptodate

def render_template(template_f, context):
    """ Render a template
    :param template_path: Path to the template file
    :type template_path: basestring
    :param context: Template data
    :type context: dict
    :return: Rendered template
    :rtype: basestring
    """
    env = jinja2.Environment(
        loader=SingleTemplateLoader(template_f.read().decode('utf-8')),
        undefined=jinja2.StrictUndefined # raises errors for undefined variables
    )

    def pillar_get(key, default=None):
      return (key in context and context[key]) or default

    env.globals['salt'] = { 'pillar.get': pillar_get }

    return env \
        .get_template('template') \
        .render() \
        .encode('utf-8')

def render_command(stdin, argv):
    """ Pure render command
    :param stdin: Stdin stream
    :type stdin: file
    :param argv: Command-line arguments
    :type argv: list
    :return: Rendered template
    :rtype: basestring
    """
    parser = argparse.ArgumentParser(
        prog='low-sodium',
        description='Command-line interface to emulate Salt for templating in shell scripts.',
        epilog=''
    )
    parser.add_argument('-f', '--format', default='?', help='Input data format', choices=['?'] + list(FORMATS.keys()))
    parser.add_argument('template', nargs='?', default='-', help='Template file to process')
    parser.add_argument('data', nargs='?', default='pillar.yaml', help='Input data path')
    args = parser.parse_args(argv)

    # Input: guess format
    if args.format == '?':
        args.format = {
            '.ini': 'ini',
            '.json': 'json',
            '.yml': 'yaml',
            '.yaml': 'yaml',
        }[os.path.splitext(args.data)[1]]

    # Input: data
    input_template_f = stdin if args.template == '-' else open(args.template)
    input_data_f = open(args.data)

    # Read data
    context = read_context_data(
        args.format,
        input_data_f
    )

    # Render
    return render_template(
        input_template_f,
        context
    )

def main():
    """ CLI Entry point """
    output = render_command(
        sys.stdin,
        sys.argv[1:]
    )
    sys.stdout.write(output)

if __name__ == "__main__":
    main()
