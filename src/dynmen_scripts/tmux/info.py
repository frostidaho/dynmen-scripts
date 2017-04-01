from collections import namedtuple as _namedtuple
import subprocess as _sp
from subprocess import run as _run, PIPE as _PIPE, DEVNULL as _DEVNULL


PaneInfo = _namedtuple(
    'PaneInfo',
    (
        'session_id',
        'window_index',
        'pane_index',
        'pane_current_path',
        'pane_current_command',
        'session_name',
        'pane_title',
        'window_name',
    ),
)

NO_PANE = PaneInfo._make((None for i in range(len(PaneInfo._fields))))

def _make_get_panes():
    sep = " !@^@! "
    pane_format = sep.join(('#{{{}}}'.format(x) for x in PaneInfo._fields))
    cmd = ['tmux', 'list-panes', '-a', '-F', pane_format]
    run, PIPE, DEVNULL = _sp.run, _sp.PIPE, _sp.DEVNULL
    make = PaneInfo._make
    def get_tmux_panes():
        lines = run(cmd, stdout=PIPE, stderr=DEVNULL, stdin=DEVNULL) \
                                 .stdout.decode().splitlines()
        return [make(x.split(sep)) for x in lines]
    return get_tmux_panes
get_tmux_panes = _make_get_panes()


