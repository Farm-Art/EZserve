import argparse
import pathlib as p
import secrets
import tempfile

import bottle as b


def abs_path(path: str) -> p.Path:
    return p.Path(path).absolute()


def password_input(string: str | None) -> str | None:
    if string is None:
        return None

    if string == '*':
        return secrets.token_hex(32)

    return string


@b.get('<path:path>')
def serve_files(path):
    if args.password:
        if b.request.query.password != args.password:
            b.abort(404)

    path = p.Path(path[1:])

    # Preliminary abuse protection (are there even other hazards?)
    if '..' in path.parts:
        b.abort(404)

    file = (root / path)

    if not file.exists():
        b.abort(404)

    if file.is_dir():
        return render_dir(file, args.password)
    return b.static_file(file.name, file.parent)


def list_item(f: p.Path, password: str | None) -> str:
    return f'<a href="/{f.relative_to(root)}{get_password_string(password)}">{f.name}</a>'


def back_button(f: p.Path, password: str | None) -> str:
    return f'<a href="/{f.relative_to(root).parent}{get_password_string(password)}">Back</a>'


def render_dir(filepath: p.Path, password: str | None):
    out = ''
    if filepath != root:
        out += f'{back_button(filepath, password)}<br>'

    return out + '<br>'.join(
        list_item(f, password) for f in filepath.iterdir())


def serve(host='0.0.0.0', port=53443, password: str | None = None, quiet: bool = False):
    if not quiet:
        print(f'Serving on http://{host}:{port}/.\nCtrl-C to quit.')
        if password:
            print(f'Append `{get_password_string(password)}` at the end of your URL to access files.')
    b.run(host=args.host, port=args.port, quiet=True)


def get_password_string(password: str | None) -> str:
    return f'?password={password}' if password else ''


if __name__ == '__main__':
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
    parser.add_argument(
        '-P', '--password',
        type=password_input,
        help='password to protect files; set to * to generate a random one'
    )

    args = parser.parse_args()


    if all((len(args.files) == 1, args.files[0].is_dir(), args.expand_root)):
        root = args.files[0]
        serve(args.host, args.port, args.password)
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = p.Path(tmpdir).absolute()
            for content_root in args.files:
                (root / content_root.name).symlink_to(
                    content_root,
                    target_is_directory=content_root.is_dir()
                )
            serve(args.host, args.port, args.password)
