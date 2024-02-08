import sys
from .param import *
from .downloader import *
from .demo import *


def main() -> None:
    skip_sele = False
    argv_offset = 1
    while len(sys.argv) > argv_offset:
        if len(sys.argv) >= argv_offset + 1 and sys.argv[argv_offset] == "new":
            skip_sele = True
            argv_offset += 1
        elif len(sys.argv) >= argv_offset + 2 and sys.argv[argv_offset] == "set-lang":
            param.set_languague(sys.argv[argv_offset + 1])
            argv_offset += 2
        elif len(sys.argv) >= argv_offset + 2 and sys.argv[argv_offset] == "set-dir":
            param.set_output_directory(sys.argv[argv_offset + 1])
            argv_offset += 2

    run_qt5_gui()

    fuzdl = fuz_downloader()
    fuzdl.run(skip_sele)

    fuzdl.terminal()
