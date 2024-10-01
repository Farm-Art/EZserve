import argparse
import pathlib as p
import tempfile

import bottle as b


def abs_path(path: str) -> p.Path:
    return p.Path(path).absolute()


parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', default='0.0.0.0', help='host to listen on')
parser.add_argument('-p', '--port', default=53443, type=int, help='port to listen on')
parser.add_argument(
    'files', nargs='*',
    default=[p.Path.cwd()], type=abs_path,
    help='files and dirs to serve'
)
parser.add_argument(
    '-e', '--expand-root',
    action='store_true',
    help='when serving a single dir, immediately show contents instead; ignored otherwise'
)

args = parser.parse_args()


@b.get('<path:path>')
def serve(path):
    path = p.Path(path[1:])

    # Preliminary abuse protection (are there even other hazards?)
    if '..' in path.parts:
        b.abort(404)

    file = (root / path)

    if not file.exists():
        b.abort(404)

    if file.is_dir():
        return render_dir(file)
    return b.static_file(file.name, file.parent)


def render_dir(filepath):
    out = ''
    if filepath != root:
        out += f'<a href="/{filepath.relative_to(root).parent}">Back</a><br>'

    return out + '<br>'.join(f'<a href="/{f.relative_to(root)}">{f.name}</a>' for f in filepath.iterdir())


if all((len(args.files) == 1, args.files[0].is_dir(), args.expand_root)):
    root = args.files[0]
    b.run(host=args.host, port=args.port)
else:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = p.Path(tmpdir).absolute()
        for content_root in args.files:
            (root / content_root.name).symlink_to(
                content_root,
                target_is_directory=content_root.is_dir()
            )

        b.run(host=args.host, port=args.port)
