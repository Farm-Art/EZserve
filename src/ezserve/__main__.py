import bottle as b
import pathlib as p
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', default='0.0.0.0', help='host to listen on')
parser.add_argument('-p', '--port', default=8080, type=int, help='port to listen on')

args = parser.parse_args()

root = p.Path.cwd()


@b.get('<path:path>')
def serve(path):
    path = p.Path(path[1:])

    # Preliminary abuse protection (are there even other hazards?)
    if '..' in path.parts:
        b.abort(404)

    file = (root/path).resolve()

    if not file.exists():
        b.abort(404)

    if file.is_dir():
        return render_dir(file)
    return b.static_file(file.name, file.parent)


def render_dir(filepath):
    out = ''
    if filepath != root:
        out += f'<a href="/{filepath.relative_to(root).parent}">Back</a><br>'

    return out + '<br>'.join(f'<a href="/{f}">{f.name}</a>' for f in filepath.iterdir())



b.run(host=args.host, port=args.port)
