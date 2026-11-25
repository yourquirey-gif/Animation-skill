# Reference Style Guide — Two User-Supplied Videos

## Reference files noted in the production conversation
- `1000328716.mp4` — approximately 64.83 seconds.
- `1000328717.mp4` — approximately 60.23 seconds.

The original MP4 binaries were not present in the repository at the time this guide was written. The descriptions below are from the earlier visual review (approximately one sampled frame per second), not a native-frame or audio analysis. Reinspect the actual files if they are later supplied.

## Shared visual target
- Stylized cinematic 3D storytelling with expressive human characters and readable facial reactions.
- Detailed, coherent architecture and dressed environments rather than empty primitive stages.
- Dramatic composition with varied wide, medium, over-the-shoulder and close-up shots.
- Clear visual storytelling, strong subject separation, motivated lighting and atmospheric changes.
- Captions that are high-contrast, legible and placed inside mobile-safe margins.
- Strong opening hook, purposeful scene transitions and a clear visual payoff.
- Vertical 9:16 is the default short-form framing; preserve important faces/actions in the center-safe area.

## Reference 1 — `1000328716.mp4`
Observed story elements: emperor, palace, dragon-head object, castle, night sequence, cage, explosion and pendulum.
Production implications:
- Build a royal palace/castle environment with pillars, lanterns, rich materials and layered depth.
- Emperor/royal character needs a recognizable costume silhouette, expressive face and acting close-ups.
- Props such as the dragon-head object, cage and pendulum must be separate modeled objects with correct scale and interaction.
- Night, explosion and pendulum beats need distinct lighting, atmosphere, camera and timed motion.

## Reference 2 — `1000328717.mp4`
Observed story elements: red-column palace, carpenter, character reactions, day-to-night transition, workshop and miniature construction.
Production implications:
- Build a red-column palace and a separate workshop with detailed tools/materials.
- Carpenter needs believable body mechanics and correct tool handling; miniature construction should be a readable object with progressive state changes.
- Character reaction shots require facial shape keys or an equivalent facial rig, not only body movement.
- Day-to-night transition should change environment lighting and color coherently, not just switch a flat background.

## Asset and animation direction
- Start with a real, textured, rigged stylized humanoid asset; keep each story character's appearance consistent across shots.
- Use a compatible humanoid motion library with explicit skeleton mapping and per-rig axis offsets.
- Create custom expressions and mouth shape keys for close-ups. Body-only rigs cannot deliver the target facial performance.
- Retargeting and lip-sync are separate tracks: retarget body actions onto the target armature; map Rhubarb mouth cues to that model's exact facial shape-key names.
- Build palace architecture, furniture, workshop props, lanterns and fantasy objects as modular reusable assets; do not reuse one generic set for every story.

## Acceptance tests before claiming reference-quality output
1. A textured rigged character turntable and facial close-up.
2. A 5–10 second acting shot with walk/gesture/turn and a held prop.
3. A speaking close-up with actual voice, viseme animation and synchronized captions.
4. A palace wide shot, a workshop shot and a day-to-night transition.
5. A full vertical short with varied camera scale, coherent continuity and audio mix.
6. Visual inspection of the rendered MP4, not only successful workflow status.

## Important limitation
This guide captures the available visual observations; it does not establish exact frame timing, camera paths, dialogue, music, sound effects or lip-sync timing. Those require the original media files and dedicated analysis.
