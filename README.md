# reMarkable capture experiment

Test cloud access and original-notebook downloads from a reMarkable 2 using
the community-maintained [rmapi fork](https://github.com/ddvk/rmapi).
Requires Git, Docker, and just. No Obsidian required.

## Run

From this directory, build the upstream Docker image. This downloads source,
container images, and build dependencies; it does not install rmapi globally.

```bash
just setup
just pair
```

If Docker is unavailable, run `just setup-local` instead of `just setup`.
This downloads Go 1.23.12 and build dependencies under `.local/`, and the
commands below automatically use that local binary when present.

Follow rmapi's prompt to obtain a one-time code from reMarkable and enter it
in your terminal. Keep pairing codes and `.local/state/auth` private.

```bash
just list
just download DOCUMENT_UUID
```

Replace `DOCUMENT_UUID` with a notebook's `id` from the JSON listing. Prefer a
small test notebook containing a distinctive sentence, such as "Capture test
one". Downloads are stored under `.local/downloads/`. They are native archives,
not transcribed text or necessarily viewable PDFs.

## Check updates

1. Run `just list > .local/before.json` and download the test notebook.
2. Copy its downloaded archive to a separate filename to preserve this version.
3. Add "Capture test two" on the tablet and wait for official cloud sync.
4. Run `just list > .local/after.json` and download the same ID again.
5. Compare the metadata and archives. We still need to inspect/render the page
   data to confirm the second sentence was captured; a changed archive alone
   does not prove that.

The wrapper only exposes listing and downloading; pairing registers an API
client. It does not schedule jobs or modify notebooks. Authentication tokens
and notes stay in the ignored `.local/` directory. The cloud integration is
unofficial and may need updates if reMarkable changes its service.

## Validation status

The local binary builds successfully. Account pairing and JSON listing work;
the live account returned 58 documents and 12 folders. A document download
succeeded. Shell syntax and ShellCheck checks pass. Update detection and
handwriting recognition still require live tests. Network downloads work with
the session's updated permissions, but the configured Docker socket is absent;
use `just setup-local` on this machine until Docker is available.

## Render a captured page

Requires `uv` and the system Cairo library. Install project-local dependencies:

```bash
just setup-render
just render .local/downloads/Leadership.rmdoc 2
```

The preview, source page ID, and renderer warnings are saved under
`.local/render-test/`. This prototype supports the modern `cPages` notebook
format and sorts by page position; it has only been exercised on this notebook.
The upstream renderer warns about some unparsed data, so compare previews
against the tablet before relying on fidelity. The renderer's byte-alpha SVG
colours are normalised to preserve translucent highlights.

The downloaded Leadership notebook contains 10 pages plus an internal table
of contents. Pages 1 and 2 render successfully. A sample visual transcription
of page 2 is saved as `page-02-transcription.txt` with provenance in the adjacent
JSON file. This transcription was made by the assistant from the preview in
chat, with punctuation lightly normalised; it is not an unattended local OCR
test. Recognition accuracy, edited-page capture, and RDF extraction remain
to be evaluated.
