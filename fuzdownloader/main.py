import sys
from .param import *
from .downloader import *


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
        elif len(sys.argv) >= argv_offset + 1 and sys.argv[argv_offset] == "debug-mode":
            param.set_debug_mode(True)
            argv_offset += 1

    fuzdl = fuz_downloader()
    fuzdl.run(skip_sele)

    fuzdl.terminal()
