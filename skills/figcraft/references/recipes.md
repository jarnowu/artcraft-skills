# FigCraft recipes

Tested on FigCraft 0.10.0. On Windows the CLI is `C:/Program Files/FigCraft/figcraft-cli.exe`.

## Contents
- Social post built with one script
- Template to an exact-size thumbnail
- Live edit of the open file

## Social post built with one script

Save as `post.json` and run `figcraft-cli run post.json --out post.figcraft`. The frame uses vertical auto layout, so its children stay centred when the text changes.

```json
[
 {"command":"frame.create","params":{"x":0,"y":0,"width":1080,"height":1080,"name":"Post","props":{"fill":"#0B0B14","layout":"vertical","mainAlign":"center","crossAlign":"center","gap":72,"clip":true}}},
 {"command":"frame.create","params":{"parent":{"$step":0},"name":"Copy","props":{"fills":[],"layout":"vertical","crossAlign":"center","gap":20,"sizingH":"hug","sizingV":"hug"}}},
 {"command":"text.create","params":{"parent":{"$step":1},"text":"NIGHT DRIVE","x":0,"y":0,"props":{"fontFamily":"Inter","fontStyle":"Bold","fontSize":136,"textAlign":"center","fill":"#FFFFFF"}}},
 {"command":"text.create","params":{"parent":{"$step":1},"text":"New single out Friday","x":0,"y":0,"props":{"fontFamily":"Inter","fontStyle":"Regular","fontSize":44,"textAlign":"center","fill":"#B9B6D3"}}},
 {"command":"frame.create","params":{"parent":{"$step":0},"name":"Button","props":{"fill":"#FF3D7F","cornerRadius":999,"layout":"horizontal","mainAlign":"center","crossAlign":"center","padding":[26,64],"sizingH":"hug","sizingV":"hug"}}},
 {"command":"text.create","params":{"parent":{"$step":4},"text":"Listen now","x":0,"y":0,"props":{"fontFamily":"Inter","fontStyle":"Semi Bold","fontSize":36,"fill":"#FFFFFF"}}}
]
```

Export at 2x: `figcraft-cli export post.figcraft -o post.png --node Post --scale 2` (2160x2160).

## Template to an exact-size thumbnail

List templates with a one-step script `[{"command":"template.list","params":{}}]`. Then:

```json
[
 {"command":"file.newFromTemplate","params":{"template":"slides","name":"Thumbnail"}},
 {"command":"text.set","params":{"id":13,"characters":"NIGHT DRIVE"}},
 {"command":"node.set","params":{"id":9,"strokes":[]}},
 {"command":"file.export","params":{"ids":[9],"format":"png","size":{"by":"width","value":1280},"path":"thumbnail.png"}}
]
```

Ids 9 (the title slide frame) and 13 (its headline) are what the `slides` template produced in testing; find yours with `node.get` before editing. Removing the slide's stroke keeps the export at exactly 1280x720.

## Live edit of the open file

The user launched `figcraft --control 7981` with the file open. With this skill's helper:

```bash
python scripts/mcp_call.py --out-dir shots -- "C:/Program Files/FigCraft/figcraft-cli.exe" mcp --attach 7981 \
  :: get_node '{"id":3}' \
  :: batch '{"label":"Bigger, centred headline","commands":[{"command":"node.set","params":{"ids":[3],"props":{"fontSize":124.8}}},{"command":"align.hcenter","params":{"ids":[3]}},{"command":"align.vcenter","params":{"ids":[3]}}]}' \
  :: screenshot '{}'
```

The batch is one undo step. Do not save; the user decides.
