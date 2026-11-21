"""Write generated/<version>/layout.json and layout.h without the game, for building the release in CI.

tools/make_release.py builds the runtime library (build_game.py --make-runtime-lib), which reads only the module layout
of generated/<version>: MOD_COUNT, the module bases and sizes. recomp/layout.py computes that layout from the ExeFS
module sizes; this script writes the same files from the sizes listed here, so a machine without the game can build the
setup. The sizes are those of the 1.2.1 ExeFS modules as the runtime's loader logs them ("loaded main at ... size ...").
The setup itself lifts the player's own game, so these values reach no totk.exe.

  python tools/ci_layout_stub.py [--version v121]
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'recomp'))

SIZES = {
    'v121': [('main', 0x472b000), ('subsdk0', 0x6a9000), ('sdk', 0xdd9000)],
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--version', default='v121', choices=sorted(SIZES))
    args = ap.parse_args()
    # recomp/layout.py imports nso.py, which needs no game file to import; reuse its placement and writer
    import layout
    mods, base = [], layout.FIRST_BASE
    for name, size in SIZES[args.version]:
        mods.append((name, base, size))
        base = layout.align_up(base + size)
    out = ROOT / 'generated' / args.version
    layout.write(mods, out)
    for n, b, s in mods:
        print(f'{n:8} base {b:#x} size {s:#x}')
    print(f'wrote {out / "layout.json"} and layout.h')


if __name__ == '__main__':
    main()
