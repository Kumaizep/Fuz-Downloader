import sys
from .context import *
from .downloader import *

def main() -> None:
    skip_sele = False
    if len(sys.argv) >= 2 and sys.argv[1] == "new":
        skip_sele = True
    if len(sys.argv) >= 3 and sys.argv[1] == "set-lang":
        context.set_languague(sys.argv[2])

    fuzdl = fuz_downloader()
    fuzdl.run(skip_sele)
   
