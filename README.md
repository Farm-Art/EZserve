# EZserve
Simple (and hopefully secure enough) way to share files over HTTP. Inspired by [simple-http-server](https://github.com/TheWaWaR/simple-http-server).

## Usage

Running the package will serve the current working directory publicly on `0.0.0.0:53443`. Alternatively, you can pass one or more file/folder as a console argument to serve them as if they were in the same directory.

`py -m ezserve "Videos/Shared" "Videos/private/or_not.mp4"` will let your clients access any video in `$cwd/Videos/Shared` and its subfolders, as well as a single video from `$cwd/Videos/private`, but not other videos next to it.

## Security Concerns

Although I've attempted to prevent abuse by completely banning `..` from the paths, I can't guarantee that there's no way to access files you  

## Roadmap (in no particular order)

- [x] **Core:** Proof-of-concept: serve listed files and dirs
- [ ] **Core:** Figure out HTTPS
- [x] **Core:** Add global password protection
- [ ] **Core:** Add per-file password protection
- [ ] **QoL:** improve the web UI
- [ ] **QoL:** allow selecting multiple files and folders to download all of them in one ZIP file
- [ ] **QoL:** add CF tunnel support to make it easier for people without a public IP.
- [ ] **Maybe?** Run the server as a daemon, with a context-menu option to share a file. 

## Known Issues

* I use symlinks to simplify sharing multiple distinct folders as if they were next to each other. Windows, for some reason, is being really stingy about that. Enabling developer mode in settings seems to alleviate the issue; I'm not actively planning on fixing that, although it would be a nice thing to have.

* Large file downloads can sometimes hang the server, rendering it unresponsive to other clients. I'm looking into that one, but it seems mostly harmless in the general use case.

* I'm aware that inserting the password into the URL is insecure, but so is plain HTTP. Get over it.

## CLI Options

* `-H` `--host` - hostname to listen on. `0.0.0.0` by default, meaning your files are exposed to the internet. It can be a fully qualified domain name (FQDN) or the public IP address of the interface you intend to listen on.
* `-p` `--port` - port number to listen on. `53443` by default. Any unoccupied port works; your browser will automatically try port `80` for `http://` and port `443` for `https://`.
* `-e` `--expand-root` - when serving a single directory, the web UI will show its contents on the frontpage, instead of a list with only the root folder's name. Ignored if you serve a single file/anything more than just a single directory. At the time of writing this, it also prevents the creation of a temp folder with a symlink; this is an implementation detail and should not be relied on (although I doubt anyone will rely on it anyway).
* `-P` `--password` - sets a global password or generates a random one if `*` is passed as the value. Users must pass `password` as a query parameter to every request, otherwise they will face a 404 error. It's inserted into every hyperlink.