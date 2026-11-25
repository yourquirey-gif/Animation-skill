# Reference videos

The two original reference clips supplied in the ChatGPT conversation are:

- `1000328716.mp4` — 64.833 sec, 720×1280, 30 fps, H.264 + AAC.
- `1000328717.mp4` — 60.233 sec, 720×1280, 30 fps, H.264 + AAC.

## Required local paths

Copy the original MP4 binaries into this folder with these exact names:

- `references/1000328716.mp4`
- `references/1000328717.mp4`

**Important:** the GitHub connector available for this task can create/update text files and Git blobs, but does not expose a binary file-upload operation or accept the uploaded local MP4 bytes as a file argument. Therefore, the two MP4 binaries are not yet committed to this repository. Do not mistake this README or the analysis notes for the actual video files.

## Analysis already committed

- `../docs/REFERENCE_VIDEO_ANALYSIS.md` — reference analysis and inspection requirements.
- `../docs/FRAME_BY_FRAME_REFERENCE_NOTES.md` — chronological visual review of both complete clips sampled at one frame per second, plus shared character, environment, camera, lighting, caption and sound rules.

The second-by-second review is a visual overview, not a native-frame-accurate motion study or complete audio transcript. Once the original MP4s are copied here, Claude Code must inspect native 30 fps footage and complete audio/transcript alignment before claiming exact frame-level replication.

Read both analysis documents before producing a story.
