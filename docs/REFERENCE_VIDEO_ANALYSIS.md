# Reference Video Analysis — User Supplied Clips

Two reference clips were supplied in this conversation and inspected from their actual frames.

## Reference assets

Copy the original video files into this repository using these exact paths before running Claude Code:

- `references/1000328716.mp4` — reference 1, portrait 720x1280, 30 fps, approximately 64.83 seconds.
- `references/1000328717.mp4` — reference 2, portrait 720x1280, 30 fps, approximately 60.23 seconds.

The source videos are not committed by this document. Keep the originals unchanged when adding them to the repository. Claude Code must verify the files exist and inspect the full clips before claiming a complete reference match.

## Observed visual language

The sampled frames show a stylized 3D animated story world with:
- Portrait 9:16 framing.
- Stylized simple, highly recognizable characters with large expressive heads/faces and compact bodies.
- Detailed dimensional palace/interior architecture, tall red columns, decorative lanterns, patterned walls, stone floors, stairs, throne-room elements, and outdoor palace/courtyard views.
- Strong contrast between character simplicity and richly built 3D environments.
- Warm red/gold palace palette in many shots, with cooler interior lighting in some scenes.
- Close-ups of faces and important story objects, medium character dialogue/reaction shots, and wide establishing shots for large locations.
- Large, centered, high-contrast subtitles near the lower-middle portion of the frame.
- Storytelling that alternates between character reactions, prop/creature reveals, and larger environmental views.

These are observed traits of the supplied clips, not rules that every future story must use the same palace, colors, props, or setting. Each new story must receive a newly designed 3D environment and palette appropriate to its own premise. Preserve only the user's approved recurring character identity across stories.

## Opening-hook analysis requirement

Claude Code must inspect both complete videos, especially:
- First frame and first 3 seconds.
- Exact first visible action and spoken/caption hook.
- Camera movement, framing, shake/impact accents, and cut timing.
- Whether captions appear word-by-word or in phrase chunks, their timing, font, placement, and emphasis.
- Facial expressions, reaction timing, and sound effects.
- How the opening creates a question that the rest of the story resolves.

Do not infer a camera shake or word-by-word caption behavior solely from this sampled contact sheet. Verify it by stepping through the actual first seconds frame by frame and listening to the audio. The user's explicit instruction is to use the second reference clip as the primary guide for the brief opening camera-shake treatment; tune the effect only after measuring the clip.

## Implementation guidance

- Match the visual quality principles, framing language, expressive acting, dimensional environments, and pacing—not exact copyrighted characters, dialogue, footage, logos, or music.
- Recreate the approved character using the user's own permitted character design/reference. Do not copy the reference clip's protected character designs.
- Build all practical environments, buildings, props, creatures, furniture, terrain, and scene objects as 3D assets wherever practical.
- Use fresh per-story backgrounds, lighting, camera plans, and hook ideas. Do not reuse the palace setting unless the new story calls for a palace.
- Keep vertical framing, strong character readability, carefully staged close-ups, and legible mobile captions.
- Create a short reference-matching test shot and ask for review before committing to the full production.

## Verification checklist

- [ ] Both original MP4 files are present in `references/`.
- [ ] Full clips inspected, not just sampled stills.
- [ ] First 3 seconds of each clip reviewed frame-by-frame.
- [ ] Audio and caption timing reviewed.
- [ ] Camera shake characteristics measured from reference 2.
- [ ] Character style and environment style documented separately.
- [ ] New story's setting is designed independently.
