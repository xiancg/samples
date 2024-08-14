Live Deltas deformer - (Maya C++ API)
======================================

This is a Maya C++ deformer that's part of the MetaHuman facial expressions workflow. All facial expressions and correctives in the MetaHuman DNA spec are controlled by two deformation layers: A skinning layer which controls most of the deformation and a blendshapes layer which is only used for finer detail in LOD0.

All targets in the blendshapes layer are stored as deltas from the base mesh. This deformer is used in a non-destructive workflow to extract these deltas from the blenshape data and to present them to the artist in their original shape, keeping a live connection to the rig (hence the name). The deformer also implements per-vertex weights, which helps the artist further control the influence of the deltas.

Only relevant parts of the code are shown here, with permission from the owners.