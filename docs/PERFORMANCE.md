# Performance measurements

Measured on 2026-10-02 with Blender 4.5.4 LTS, Windows, an Intel Core i7-14700F, and an NVIDIA GeForce RTX 3050 OEM. Baseline: [v1.1.2 source](https://github.com/xz-blender/quick_crease_weight/tree/9d297512d790805eedbe28642d7404ae62a44518). Optimized implementation: v1.2.0.

## Results

### HUD

Median CPU time inside the actual viewport draw callback, after eight warm-up frames and over 80 measured frames:

| Scenario | Before (ms) | After (ms) | Reduction |
| --- | ---: | ---: | ---: |
| Unchanged HUD | 1.2810 | 0.0916 | 92.8% |
| Changing value | 1.2936 | 0.1969 | 84.8% |
| Moving cursor | 1.2909 | 0.0937 | 92.7% |

Each baseline frame rebuilt 20 GPU batches and measured text 16 times. After warm-up, the optimized HUD performs **zero text measurements** and builds **zero batches** for an unchanged value or cursor motion. Changing values builds only the progress fill batch. Static shapes share one GPU batch; drawing the fill requires at most one additional shape batch. Text drawing is separate.

### Mesh editing

A grid with 100,489 selected vertices or 200,344 selected edges. Each changed-value case alternates between 0.25 and 0.75 for 20 writes; times are medians.

| Attribute / selection | Changed value before (ms) | Changed value after (ms) | Identical value before (ms) | Identical value after (ms) |
| --- | ---: | ---: | ---: | ---: |
| Vertex crease | 3.9980 | 2.0095 | 3.9417 | 0.0007 |
| Edge crease | 8.1820 | 3.8296 | 7.9081 | 0.0006 |
| Vertex bevel weight | 3.9166 | 1.9512 | 3.8781 | 0.0006 |
| Edge bevel weight | 8.3620 | 3.8152 | 8.3068 | 0.0007 |

Repeated identical values produce **0 mesh updates instead of 20**. Every changed value still writes immediately, without a timer, debounce, or deferred confirmation. First writes still apply a uniform value even when it equals the original selection average; cancel restores each original value.

## Method and tradeoffs

- The same [benchmark script](../tests/blender_benchmark.py) was run before and after the changes in disposable factory-startup windows, using real BMesh attributes and the actual HUD draw function.
- HUD timings cover Python work and GPU draw submission. They do not measure GPU completion or the entire viewport frame. Mesh timings cover attribute writes and the edit-mesh update call, without a modifier stack or full scene evaluation.
- Selection snapshot setup is faster, but the first write takes longer because it binds reusable element references. For edge crease, setup changes from 27.80 to 16.75 ms and first write from 13.40 to 22.11 ms. Caching uses memory proportional to the selected element count and is released with the selection snapshot when the operation finishes or cancels.
- Timing varies with hardware, scene, selection, and system load. The test enforces work counts instead of fragile wall-clock thresholds. These are local samples, not a guarantee of frame rate.
- Integration checks cover mixed-value restoration, layer creation between writes, multi-object editing, duplicate values, snapping, navigation, and cache release. UI checks cover round/square styles, zero/full values, hidden hints, cursor placement, and narrow viewports.

Raw measurements: [before](performance/before.json) · [after](performance/after.json). The baseline's `success: false` records the expected work-budget failure: unchanged values still updated the mesh.

## Reproduce

Run from the repository root, with a Blender window available:

```powershell
$blender = 'C:\path\to\blender.exe'
& $blender --factory-startup --python tests/blender_benchmark.py -- --label current --verify
```

Results are written to `tests/artifacts/performance-current.json`. The window closes automatically and user preferences are not saved. `--verify` checks that identical values cause no mesh updates, changed values are applied, warm HUD frames do no text measurement, and static geometry is not rebuilt for cursor motion.
