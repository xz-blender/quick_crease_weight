# Quick Crease Weight media kit

[English README](../../README.md) · [中文 README](../../README.zh-CN.md)

**[Download the upload media ZIP](../../downloads/quick_crease_weight-media.zip)** — icon exports, cover exports, GIF, MP4, and notes.

Orange represents **crease**, blue represents **bevel weight**. These files are prepared for the repository and a future Blender Extensions listing.

The icon shows one connected mesh patch with visible vertices. The orange shared edge represents crease, and the blue outer edge represents bevel weight. Both highlights describe mesh attributes on selected elements.

## Files

| File | Dimensions / format | Use |
| --- | --- | --- |
| [icon.png](icon.png) | 256 × 256, RGBA PNG | Small listing icon; transparent outside the tile |
| [icon-512.png](icon-512.png) | 512 × 512, RGBA PNG | Larger icon export |
| [cover.png](cover.png) | 1920 × 1080, RGB PNG | Featured cover image, 16:9 |
| [cover.jpg](cover.jpg) | 1920 × 1080, JPEG | Lightweight README and web cover |
| [demo.gif](demo.gif) | 960 × 640, looping GIF, about 10.8 seconds | Inline GitHub demonstration |
| [demo.mp4](demo.mp4) | 1200 × 800, H.264 MP4, about 10.7 seconds | Video demonstration |
| [icon-source.png](icon-source.png) | 1254 × 1254, RGBA PNG | Original generated icon |
| [cover-source.png](cover-source.png) | 1672 × 941, RGB PNG | Original generated cover |

The cover and icons are conceptual brand artwork generated with the built-in image generation tool. Export sizes were normalized with ImageMagick. The actual add-on interface is shown in the GIF, MP4, and screenshots. [Generation prompts](PROMPTS.md) are included for future revisions.

## Demonstration

The recording runs the real add-on in a disposable Blender 4.5.4 factory-startup window:

1. **Shift + E:** increase vertex crease from 0 to 1 with a Subdivision Surface preview.
2. **Ctrl + Shift + E:** increase edge bevel weight from 0 to 0.75 with a Bevel modifier preview.
3. **Ctrl / Alt:** set weights to 1 / 0.

English titles above the viewport are recording annotations. The numeric card and right-hand shortcut list are the actual add-on HUD. Frames come from Blender screenshots; FFmpeg encodes the GIF and MP4.

To reproduce the recording from the repository root:

```powershell
$blender = 'C:\path\to\blender.exe'
& $blender --factory-startup --enable-event-simulate --window-geometry 50 50 1200 800 --python tests/capture_demo.py
```

After the window closes, encode the captured frames with FFmpeg:

```powershell
ffmpeg -y -f concat -safe 0 -i tests/artifacts/demo/frames.txt -filter_complex "[0:v]fps=12.5,scale=960:-2:flags=lanczos,split[a][b];[a]palettegen=max_colors=192:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle" -loop 0 docs/media/demo.gif
ffmpeg -y -f concat -safe 0 -i tests/artifacts/demo/frames.txt -r 30 -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -movflags +faststart docs/media/demo.mp4
```

Media and capture scripts are excluded from the installable add-on ZIP by the existing extension build configuration.

## Future platform submission

Use `icon.png` for the icon, `cover.png` or `cover.jpg` for the featured image, and `demo.mp4` for the video preview. Check the current upload form for accepted formats, dimensions, and file-size limits when submitting. The live upload requirements could not be verified from the public pages during preparation, so the dimensions above are export targets.

The [official Blender Extensions overview](https://extensions.blender.org/about/) describes uploading and review. These assets are ready for that later submission; this media update does not create a platform listing.

## 中文说明

小图标使用 `icon.png`（256 × 256，透明圆角外部），封面使用 `cover.png` 或 `cover.jpg`（1920 × 1080，16:9）。`demo.gif` 已用于中英文 README，`demo.mp4` 保留为后续平台视频素材。图标和封面为 AI 生成的品牌概念图，演示为真实 Blender 操作录制。正式提交时，请以官方上传表单当时显示的格式、尺寸和大小要求为准。
