# __init__.py
#
# Command-line interface (CLI).

import sys
from .common import find, require
from .Config import Config
from . import status
from . import sources
from . import list
from . import privacy
from . import exclude
from . import fetch
from . import anonymize
from . import shell
from .LlamaApi import LlamaApi
from .LlamaStats import LlamaStats

# The Llama command-line interface runs by executing one command with
# additional paraamters. Here are the list of commands.
#
# Each command has the following properties:
#   cmd: the actual command
#   desc: one-line textual description of the command
#   require: list of strings: what operations need to be done before the
#            command can be executed.
#   call: which function to call to execute the command.
COMMANDS = [
  {
    'cmd': 'status',
    'desc': 'Show the working tree status',
    'require': ['config'],
    'call': status.command,
  },
  {
    'cmd': 'source',
    'desc': 'Manage sources for learning data',
    'call': sources.command,
  },
  {
    'cmd': 'list',
    'desc': 'List available data tables and columns',
    'require': ['config', 'source'],
    'call': list.command,
  },
  {
    'cmd': 'privacy',
    'desc': 'Configure privacy (default: pseudoanonymous)',
    'call': privacy.command,
  },
  {
    'cmd': 'exclude',
    'desc': 'Exclude selected tables, columns, or persons at fetch',
    'require': ['config', 'source'],
    'call': exclude.command,
  },
  {
    'cmd': 'fetch',
    'desc': 'Fetch data from sources',
    'require': ['config', 'source'],
    'call': fetch.command,
  },
  {
    'cmd': 'anonymize',
    'desc': 'Export anonymized data',
    'require': ['config', 'source'],
    'call': anonymize.command,
  },
  {
    'cmd': 'shell',
    'desc': 'Open python REPL with \'llama\' instance to export data',
    'call': shell.command,
  }
]

def llama_cli(cmd, args):
  definition = find(COMMANDS, lambda c: c['cmd'] == cmd)
  require(definition, 'Unknown command')
  config = Config()

  # End program if some command requirement is not met.
  requirements = definition.get('require', [])
  if 'config' in requirements:
    require(config.exists, 'The working directory has no configuration (.llama)')
  if 'source' in requirements:
    require(config.sources, 'First, use command \'source\' to configure a data source')

  require(definition.get('call', None), 'FATAL: command missing implementation', 1)

  definition['call'](args, config)

def main():
  if len(sys.argv) < 2:
    print('Llama CLI fetches and preprocesses learning data\n')
    print('usage: llama <cmd> [<args>]\n')
    for c in COMMANDS:
      print(f'   {c["cmd"]: <12}{c["desc"]}')
    sys.exit(0)
  llama_cli(sys.argv[1], sys.argv[2:])
