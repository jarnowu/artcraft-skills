# SoundCraft recipes

Tested on SoundCraft 0.12.1. On Windows the CLI is `C:/Program Files/SoundCraft/soundcraft-cli.exe`. Clip and track ids below are what testing produced; read yours with `--inspect`.

## Contents
- Master a song to a loudness target
- Bring a whole mix to a loudness target
- EQ and compression on tracks
- Mute and a marker in the open session

## Master a song to a loudness target

Example: `song.wav` (48 kHz) starts with 2 s of silence; trim it, fade out the last 3 s, reach -14 LUFS.

1. Import and inspect: `run --cmd 'file.import_audio={"path":"C:/media/song.wav"}' --inspect`. The clip id is in `tracks[].clips[].id` (3 in testing).
2. Trim, move, fade, and bounce a probe in one run (positions in samples: 2 s = 96000, 3 s = 144000 at 48 kHz):

```bash
soundcraft-cli run --cmd 'file.import_audio={"path":"C:/media/song.wav"}' \
  --cmd 'edit.trim_clip={"clip":3,"start":96000}' \
  --cmd 'edit.move_clips={"clips":[3],"to":0}' \
  --cmd 'edit.fades_create={"clip":3,"side":"out","length":144000}' \
  --bounce probe.wav
```

3. The bounce result reports `lufs`. Add the difference to -14 as clip gain and bounce the master, saving the session:

```bash
soundcraft-cli run ...same --cmd steps... --cmd 'clip.gain={"clips":[3],"db":19.34}' --bounce master.wav --save master.scraft
```

4. Check with `ffmpeg -i master.wav -af ebur128=peak=true -f null -` if available. If the peak would go over 0 dBFS, put a `maximizer` insert on the master instead of more gain.

## Bring a whole mix to a loudness target

Example on the demo session (55.9 s, -19.4 LUFS as it stands; its master track is `Master 1` with a `maximizer` in slot 0). Put a `gain` plugin (-96 to +24 dB) in front of the maximizer, lower the maximizer ceiling so the true peak stays under -1 dBTP, and bounce with room for the reverb tail:

```bash
soundcraft-cli run --demo \
  --cmd 'mix.insert={"track":"Master 1","slot":1,"plugin":"gain","params":{"gain":5.6}}' \
  --cmd 'mix.insert_move={"track":"Master 1","from":1,"to":0}' \
  --cmd 'mix.insert_params={"track":"Master 1","slot":1,"params":{"ceiling":-2}}' \
  --bounce master.wav --start 0 --end 60 --save master.scraft
```

This measured -14.05 LUFS, true peak -1.03 dBTP. Read `lufs` from the bounce result, adjust the gain by the difference and bounce again. A large gain into the limiter squashes the mix; tell the user how much limiting the target needed.

## EQ and compression on tracks

Read the existing inserts first (`run --in band.scraft --cmd 'session.inspect={"detail":"full"}'`), because `mix.insert` replaces whatever is in the slot. Plugin parameter ids come from `run --demo --cmd engine.plugins`.

Example on the demo session: the Bass already has a compressor (slot 0) and a saturator (slot 1); put a 40 Hz high-pass EQ in front of them, compress the Snare, and lower the Keys and the Pad by 4 dB.

```bash
soundcraft-cli run --in band.scraft \
  --cmd 'mix.insert={"track":"Bass","slot":2,"plugin":"eq_7band","params":{"hpf_on":1,"hpf_freq":40,"hpf_slope":3}}' \
  --cmd 'mix.insert_move={"track":"Bass","from":2,"to":0}' \
  --cmd 'mix.insert_move={"track":"Bass","from":2,"to":1}' \
  --cmd 'mix.insert={"track":"Snare","plugin":"compressor"}' \
  --cmd 'mix.volume={"tracks":["Keys"],"delta_db":-4}' \
  --cmd 'automation.set_point={"track":"Pad","param":"volume","at":443072,"value":-12}' \
  --cmd 'automation.set_point={"track":"Pad","param":"volume","at":2215360,"value":-12}' \
  --bounce mix.wav --save band-mixed.scraft
```

- `mix.insert_move` swaps two slots, so moving the EQ from slot 2 to the front takes two swaps to keep the compressor before the saturator (result: EQ, compressor, saturator).
- `mix.insert` without `slot` uses the first empty slot. Change an existing plugin's settings with `mix.insert_params {"track","slot","params"}`.
- The Pad has volume automation in Read mode, so `mix.volume` would change nothing audible; its automation points (from `session.inspect {"detail":"full"}`) are lowered instead.

## Mute and a marker in the open session

The user launched `soundcraft --control 7802` with the session open.

```bash
soundcraft-cli app --port 7802 mix.mute '{"tracks":["Hats"],"value":true}'
soundcraft-cli app --port 7802 markers.add '{"name":"Chorus","at":"bars_beats:9|1|000"}'
soundcraft-cli app --port 7802 ui.screenshot '{"path":"C:/media/edit-window.png"}'
```

Check the session for an existing marker with the same name first (`app --port 7802 session.inspect`). Do not save; the user decides.
