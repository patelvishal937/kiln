# APK reverse-engineering in Kiln

Kiln does not reimplement Android reverse-engineering. For `--from-apk` runs the `recon`
phase uses the installed **`apk-reverse`** skill (newliver666/apk-reverse) as its extraction
engine, and turns what that skill reveals into a Kiln `Teardown`.

## Install (once)
```
npx skills add newliver666/apk-reverse --skill apk-reverse -y
```
Then its own doctor:
```
python skills/apk-reverse/scripts/doctor.py
```

## How Kiln uses it
1. In the `recon` phase, load the `apk-reverse` skill and follow its procedure only far
   enough to understand the app at the level a rebuild needs:
   - the screens and navigation,
   - the features the user wants rebuilt,
   - the data entities the app clearly stores,
   - the backend APIs / SDKs it talks to (its integration surface),
   - the stack (native, Flutter, React Native, WebView).
2. Write those findings into the `Teardown` schema (same as the website path).
3. Put every brand name, logo, and block of verbatim copy into `do_not_copy`.

## Boundary
The goal is a **feature map to build an original app on Greta** — not to modify, patch, or
repackage the original binary. Kiln only consumes the structural understanding; it does not
ship or alter the source app. Study only an APK the user is entitled to analyze; if it is
protected beyond read-level inspection, record that in the Teardown's `gaps` /
`confidence_notes` and rebuild from what is understood.

The Teardown then flows into `blueprint` → `app_build` exactly like a website teardown.
