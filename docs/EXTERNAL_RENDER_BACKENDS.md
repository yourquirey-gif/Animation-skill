# External render backends

## SheepIt
Run:
python runtime/export_sheepit.py --storyboard tests/fixtures/your_story.json --output /tmp/sheepit-package.zip --engine CYCLES --width 1080 --height 1920 --fps 30

The exporter builds each shot in Blender, packs external resources and saves a self-contained .blend. Upload each shot project through SheepIt's official website. SheepIt renders frames, not MP4s; retrieve the frames and assemble/mux them with the normal FFmpeg pipeline.

Automation limitation: no SheepIt credentials or supported official project-submission API are configured here. This exporter intentionally does not scrape/login or pretend upload/download is automatic. SheepIt does not execute owner-authored render scripts, so scene construction is baked into the .blend.

## Kaggle GPU
Kaggle provides a free GPU notebook option subject to queue and quota. For NVIDIA GPU acceleration on Kaggle, export the scene with Blender Cycles; this worker configures CUDA/OptiX. Eevee remains available as a separate rendering choice. Upload/extract the package in a Kaggle Notebook, then run:
blender -b path/to/shot.blend --python cloud/kaggle_gpu_render.py -- --output-dir /kaggle/working/shot_frames

The worker tries CUDA then OptiX and reports the detected device. It falls back to CPU if no compatible GPU is visible. It does not bypass Kaggle quotas or session limits.

## Backend selection
- GitHub Actions: integrated end-to-end orchestration, but standard hosted runners are CPU/software rendered and may be too slow for high-resolution complex scenes.
- SheepIt: free distributed rendering, but requires user-side account/project upload and frame retrieval.
- Kaggle: free shared GPU option for Cycles, but requires a Kaggle account/session and is quota/availability limited.
- Final assembly, audio mix, captions, ffprobe validation and visual review remain part of production; a render backend alone does not guarantee artistic quality.
