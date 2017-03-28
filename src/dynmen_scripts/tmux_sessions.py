from dynmen.rofi import Rofi
from subprocess import run, PIPE, Popen
from collections import namedtuple
from tabulate import tabulate
from os import path

HOME_DIR = path.expanduser('~')
PaneInfo = namedtuple(
    'PaneInfo',
    (
        'session_id',
        'window_index',
        'pane_index',
        'pane_current_path',
        'pane_current_command',
        'session_name',
    ),
)

def get_panes():
    sep = " !@^@! "
    cmd = ['tmux', 'list-panes', '-a', '-F']
    info = PaneInfo._fields
    args = ['#{{{}}}'.format(x) for x in info]
    args = sep.join(args)
    cmd.append(args)
    res = run(cmd, stdout=PIPE)
    lines = res.stdout.decode().splitlines()
    lines = [x.split(sep) for x in lines]
    make = PaneInfo._make
    return [make(x) for x in lines]

tty_script_template = """
#!/usr/bin/sh
tmux source '{tmux_commands_path}'
#{shell}
"""

tmux_commands_template = '''
attach -t "{session_id}"
select-window -t "{window_index}"
'''

def attach(pane_info):
    from tempfile import TemporaryDirectory
    from stat import S_IEXEC
    from os import getenv, chmod, stat

    with TemporaryDirectory() as td:
        fpath = path.join(td, 'torun.tmux')
        fpath_torun = path.join(td, 'torun')

        with open(fpath, mode='w') as fscript:
            tmux_commands = tmux_commands_template.format(**pane_info._asdict())
            fscript.write(tmux_commands)

        with open(fpath_torun, mode='w') as fscript:
            ttyscript = tty_script_template.format(
                tmux_commands_path=fpath,
                shell=getenv('SHELL', 'bash'),
            )
            fscript.write(ttyscript)
        st = stat(fpath_torun)
        chmod(fpath_torun, st.st_mode | S_IEXEC)
        return run(['xfce4-terminal', '--command={}'.format(fpath_torun)])

def get_display_dict():
    d = {}
    panes = get_panes()
    display = []
    for pane in panes:
        session = '{} ({})'.format(pane.session_name, pane.session_id)
        path = pane.pane_current_path.replace(HOME_DIR, '~')
        cmd = pane.pane_current_command
        idx = '{}/{}'.format(pane.pane_index, pane.window_index)
        total = [session, path, cmd, idx]
        display.append(total)
    display = tabulate(display, tablefmt='plain').strip().splitlines()
    return dict(zip(display, panes))

def main():
    menu = Rofi()
    menu.font = 'Dejavu Sans Mono 14'
    menu.color_window = "argb:dc222222, #fac863, #fac863"
    menu.color_normal = "argb:0000000, #ffffff, argb:0000000, #fac863, #1b2b34"
    menu.color_active = "argb:0000000, #6699cc, argb:0000000, #6699cc, #1b2b34"
    menu.color_urgent = "argb:0000000, #f99157, argb:0000000, #f99157, #1b2b34"
    menu.monitor = -1
    res = menu(get_display_dict())
    res2 = attach(res.value)
    return 0

