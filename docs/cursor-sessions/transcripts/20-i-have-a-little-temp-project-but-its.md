---
cursor_session: 7d684de9-64c3-456a-be24-d9c2e4eb8dbd
source: cursor-composer
cursor_hint: ?
user_entries: 6
---

# transcript — i-have-a-little-temp-project-but-its

### you

i have a little temp project, but its' 10+ years old, so isn't building well... minimal changes, what does this need so it can work in my local browser?@waveform.prototyping.bbc.co.uk-master fix it up

### assistant

Checking for JavaScript errors and inspecting the waveform area:

### assistant

Checking for install/build issues and applying minimal fixes:

### assistant

Checking buildUi and whether the waveform data format is compatible:

### assistant

Applying minimal fixes: removing the dead html5shim and fixing script loading.

### assistant

Checking whether `dataUri` format causes the issue and ensuring the `static` start script works:

### assistant

Trying JSON-only for waveform data to avoid ArrayBuffer compatibility issues:

### assistant

Adding explicit dimensions so the container has a width before Peaks initializes:

### assistant

Reverting to a simpler setup and keeping only essential fixes:

### assistant

Fixing the container reference in the closure:

### you

I don't care about the build process, I just want to be able to see the Example Demo section animate correctly on play. Remove everything except that.

### assistant

Simplified the project to only the Example Demo:

- **index.html** – Only the demo section (waveform container, audio player, zoom/segment/point buttons)
- **index.js** – Peaks init and button handlers; removed drag-drop, file upload, and DOMContentLoaded
- **vendor/peaks.css** – Only styles needed for the waveform demo

Run `npm run build:dev` (or `npm run build`) after changes, then open `index.html` in a browser or use `npm start` to serve it.

### you

run it for me

### assistant

Server is up. Open **http://127.0.0.1:3000** in your browser.

### you

bundle.js:2 Uncaught TypeError: Peaks.init is not a function
    at Object.<anonymous> (bundle.js:2:979)
    at o (bundle.js:1:265)
    at r (bundle.js:1:431)
    at bundle.js:1:460
(anonymous) @ bundle.js:2
o @ bundle.js:1
r @ bundle.js:1
(anonymous) @ bundle.js:1
favicon.ico:1  GET http://127.0.0.1:3000/favicon.ico 404 (Not Found)
favicon.ico:1  GET http://127.0.0.1:3000/favicon.ico 404 (Not Found)

### assistant

Using the standalone `peaks.js` build because the package's CommonJS export is a factory, not the Peaks constructor.

### assistant

Using the standalone `peaks.js` build that exposes `window.peaks` instead of the CommonJS export. Reload the page; no build step is required.

### you

I quite like this peaks approach, but not quite right for this project (streaming media), might be useful in later stages though, so put all the relevant code into a single html with included js+css, keeping it simple, so I can just archive that one file somewhere in the repo.

### assistant

Created `waveform.prototyping.bbc.co.uk-master/archive/peaks-demo.html` (~35KB) with:

- Inline CSS and JS
- Waveform data embedded in the HTML
- Peaks.js loaded from unpkg
- Audio sources pointing to `../data/sample.mp3` and `../data/sample.ogg`

Serve it from the waveform project root (e.g. `npm start`) so the `../data/` paths resolve correctly.

### you

note it's apache2.0

### assistant

Inserted an Apache-2.0 license note into the archive file comment.
