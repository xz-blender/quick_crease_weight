# Image generation prompts

Created with the built-in `image_gen` tool. Orange crease / blue bevel matches the add-on defaults. The current icon depicts mesh vertices and selected attribute edges. The cover was generated separately using the earlier cube motif as its reference.

## Icon

```text
Use case: logo-brand.
Asset type: finished square application icon for Quick Crease Weight, a Blender Mesh Edit Mode add-on.
Functional meaning: the tool assigns crease or bevel-weight attributes to selected mesh vertices or edges, with orange meaning crease and blue meaning bevel weight. The icon must communicate EDITABLE MESH, SELECTED EDGES and VERTEX DATA. It must not imply two abstract corners, an unrelated logo, or a command that directly rounds geometry.
Design: one beautifully composed, simple polygon mesh patch with two quadrilateral faces meeting along a shared straight vertical-ish fold edge. Six mesh vertices total, like a minimal folded sheet viewed obliquely, NOT a cube. Two subdued slate-gray flat faces make the surface legible. The common central crease edge is a strong warm orange stroke. One outer edge on the right face is a strong clear blue stroke indicating bevel weight on that edge. All remaining topology is restrained light gray, strong enough at small size. Small flat circular vertex points at the six real mesh corners, aligned precisely with their connecting edges; selected vertices match their colored edge. Every point belongs to the mesh, no floating dots. Both faces remain polygonal with straight edges: show attribute selection, not an actual rounded surface. The single connected mesh is the whole symbol.
Style: precise contemporary CAD / modeling-tool icon, flat vector-like graphic, generous spacing, elegant optical balance, crisp antialiasing, no plastic rendering. Coherent perspective and clean topology. Do not add topology subdivisions. The mesh occupies about 68 percent of the canvas and is centered. Distinct silhouette and high contrast readable at 32 pixels.
Background: deep charcoal #171D27 rounded-square tile occupying 92 percent of the canvas with generous safe margin. Real transparent alpha outside the rounded-square tile.
Palette: orange #FF872D selected crease, blue #37B8F4 selected bevel-weight edge, neutral slate surfaces, pale gray mesh outline. Broad controlled strokes and small FLAT vertex nodes. No gradients, glossy shading, reflections, 3D spherical beads, decorative shadows, glow or textures.
No text, letters, numbers, UI panels, sliders, arrows, logo badges, Blender logo, watermark, border, comparison sheet, extra icons, mockups or scene. One finished square icon only.
```

### Small-size readability refinement

```text
Use case: precise-object-edit.
Edit target: the supplied Quick Crease Weight mesh icon.
Keep the exact existing concept and composition: a single connected patch of two quadrilateral mesh faces, six real corner vertices, shared central ORANGE straight crease edge and outer-right BLUE straight bevel-weight edge, subdued gray other edges, dark rounded square, and transparency outside the tile.
Make one targeted readability improvement for a 32 pixel application icon: increase the thickness of the orange and blue selected edges to about THREE times their current thickness (roughly 4 percent of the full canvas width, strong broad strokes). Increase the gray mesh-outline stroke to about 1.6 times its current thickness. Keep the six flat circular vertex markers only slightly wider than the colored strokes; they must read as precise mesh vertices, not large spheres. Darken both gray face fills substantially toward charcoal slate, preserving the slight tonal distinction between faces so the bright colored edge attributes become the focal point. Keep all mesh lines straight and all nodes exactly at the connected corners. Preserve perspective, positions, tile size and layout.
Style: crisp flat antialiased vector-like UI asset with solid colors. Warm orange crease, bright sky-blue bevel-weight selection. No glow, no 3D beads, no texture or added elements. No letters or numbers. Genuine transparent alpha outside the rounded square. Output one finished square icon.
```

## Cover

```text
Use case: ads-marketing. Asset type: polished cover / featured image for the open-source Blender add-on Quick Crease Weight. Generate a finished wide 16:9 landscape cover, exactly 2560 x 1440 pixels, suitable for a Blender Extensions listing and GitHub README. Input image is a BRAND REFERENCE ONLY: use its original orange sharp-corner / blue rounded-corner mesh-cube motif consistently; do not reproduce a giant app tile. Deep charcoal navy studio background. Elegant editorial product art, meticulous spacing, clean legible typography, subtle dimensional mesh geometry. Compose a strong left typography block and one large refined isometric mesh cube on the right: its orange edges stay sharp to symbolize crease, blue edges are smoothly beveled to symbolize bevel weight. Show a few intentional vertex nodes and a soft grounded glow, with tasteful subdued topology lines. Use only exact text: headline 'QUICK' on one line, then 'CREASE WEIGHT' on the next two balanced lines if needed; subtitle 'Creases & bevel weights. Two shortcuts.'; a small orange label 'Shift + E  /  Crease' and a blue label 'Ctrl + Shift + E  /  Bevel Weight'. Typography must be large, impeccably spelled, readable at thumbnail size. Generous safe margins at least 8 percent on all sides; no tiny text. Colors: orange #FF7D2D, blue #38BDF8, soft off-white, deep charcoal. A small version of the reference cube mark may accompany the title. No screenshot or invented UI; this is conceptual branded cover art. No Blender official logo, no official endorsement badge, no price, no watermark, no unrelated objects. Confident restrained composition, not noisy sci-fi. Preserve a true 16:9 aspect ratio with no border or letterboxing.
```
