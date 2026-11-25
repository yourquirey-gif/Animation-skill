# Video Engine Application Implementation Specification

This repository is a Claude Code Skill package with a reusable rendering runtime. It is not, by itself, a hosted video-generation SaaS application. Implement an application only inside the user's separately connected target repository.

## Required user experience
Support idea, script, audio, script-plus-audio, reference-image and supplied-asset inputs. Ask only for missing duration and output format. For audio-led projects, inspect the audio first and treat its duration as the authoritative timeline.

Output profiles:
- YouTube Shorts: 9:16, normally 1080x1920.
- YouTube Long: 16:9, normally 1920x1080.
- Custom dimensions/fps when supported by the execution budget.

## Mandatory rendering architecture
- Panda3D is the primary Python 3D engine.
- Python handles story analysis data, storyboard validation, scene orchestration and automation.
- panda3d-gltf handles supported GLB/glTF assets.
- FFmpeg/ffprobe handles encoding, audio/subtitle processing and technical verification.
- Three.js may provide optional browser previews, never as a replacement for actual cloud frame rendering.
- Blender and bpy are prohibited everywhere in the active runtime and CI.

## Pipeline
1. Inspect the connected repository, its Git state, existing features and deployment architecture.
2. Convert story/script/audio into timed scenes and a reusable JSON storyboard.
3. Select stylized 3D or realistic documentary style, with a user override.
4. Resolve licensed assets and validate their formats/rigs.
5. Build Panda3D scene graphs, geometry, materials, lights, cameras and keyframe/asset animation.
6. Render real frames per shot.
7. Add narration, music and captions with FFmpeg while preserving user audio.
8. Validate frame count, PNG signatures/dimensions, MP4 streams, codecs, fps and duration.
9. Inspect representative frames and correct visual defects.
10. Publish MP4 and QA report as downloadable artifacts.

## Engineering requirements
Preserve existing application functionality. Reuse modules and avoid duplicate implementations. Add setup scripts, dependency manifests, tests, CI and documentation. Do not commit secrets. Do not assume GPU availability. Bound memory, disk, render resolution, job duration and artifact retention.

## Integration test gates
At minimum, execute actual Panda3D rendering and FFmpeg encoding for:
- a stylized subject in an environment;
- a realistic landscape with camera movement;
- an object interaction with a visible geometry/state change;
- narration/subtitles with final audio mux.

Compilation and unit tests are not proof of rendering. A successful render command is not proof of visual quality. Retain logs and inspect output frames. Report failures and limitations honestly.

## Explicit limitations
Panda3D is a general-purpose real-time 3D engine, not an automatic professional character modeller or universal auto-rigger. Rigged character animation, facial controls, retargeting, cloth, advanced physics, global illumination and realistic documentary assets require compatible assets, additional systems and separate integration tests. Never claim these features are complete merely because the architecture mentions them.
