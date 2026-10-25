# EffectCraft recipes

Tested on EffectCraft 0.16.0. Paths use forward slashes; on Windows the CLI is `C:/Program Files/EffectCraft/effectcraft-cli.exe`.

## Contents
- Title built with one script
- Lower third with alpha
- Live edit through the bridge

## Title built with one script

A normal After Effects script. Save it as `title.jsx` and run `effectcraft-cli script title.jsx --empty --save-as title.ecproj`.

```javascript
app.beginUndoGroup("Build title");
var comp = app.project.items.addComp("Title", 1280, 720, 1, 5, 24);
comp.bgColor = [0.05, 0.05, 0.08];
var t = comp.layers.addText("NIGHT DRIVE");
var doc = t.property("Source Text").value;
doc.fontSize = 120; doc.fillColor = [1, 1, 1]; doc.justification = ParagraphJustification.CENTER_JUSTIFY;
t.property("Source Text").setValue(doc);
var pos = t.property("Transform").property("Position");
pos.setValueAtTime(0, [-400, 360]);
pos.setValueAtTime(1, [640, 360]);
pos.setTemporalEaseAtKey(2, [new KeyframeEase(0, 75)], [new KeyframeEase(0, 75)]);
var op = t.property("ADBE Transform Group").property("ADBE Opacity");
op.setValueAtTime(4.5, 100);
op.setValueAtTime(comp.duration - comp.frameDuration, 0);
app.endUndoGroup();
```

Then render and look: `effectcraft-cli render-frame --project title.ecproj --comp Title --time 0.5 --out f.png` and `effectcraft-cli render --project title.ecproj --comp Title --format h264 --out title.mp4`.

Script times (`setValueAtTime`) are comp seconds. `writeLn()` output and the last expression's value are printed; an error exits 1 with `file:line:col`.

## Lower third with alpha

1. Build the bar, the text and an animated null as usual (script or `exec`), on a comp with no background layer.
2. Preview with `render-frame ... --transparent`, or the semi-transparent bar disappears against the comp background.
3. Render: `effectcraft-cli render --project lt.ecproj --comp "Lower Third" --format prores --prores 4444 --channels rgba --audio off --out lowerthird.mov`
4. Check alpha with ffprobe if installed: `ffprobe -v error -show_entries stream=codec_name,profile,pix_fmt -of compact lowerthird.mov` should show `prores`, `4444`, `yuva444p12le`.

To use it in FilmCraft, import the .mov as footage. After re-rendering to the same path, run FilmCraft's `media.refreshChanged`.

## Live edit through the bridge

The user launched `effectcraft --control 9881` with their project open.

```bash
effectcraft-cli info --bridge 9881 --json
effectcraft-cli exec layer.setText --params '{"layer":"Headline","fill":"#FF8C1A"}' --bridge 9881
effectcraft-cli exec effect.apply --params '{"effect":"ec.stylize.glow","layers":[2]}' --bridge 9881
effectcraft-cli render-frame --bridge 9881 --time 1 --out after.png
```

Find the glow's parameter paths with `props COMP LAYER --flat --bridge 9881` and set them with `set`. Do not save; the user decides.
