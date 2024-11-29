#!/usr/bin/env python3

"""
Convert meshes to formats compatible with Drake.
"""

import pathlib
import math
import ruamel.yaml
from trimesh import load_mesh,transformations
from trimesh.exchange.gltf import export_gltf
from trimesh.exchange.obj import export_obj


MESH_DIR = pathlib.Path('./meshes')
CONFIG_DIR = pathlib.Path('./config')

# Convert visual meshes to GLTF
for mesh_file in MESH_DIR.glob('*/visual/*.dae'):
    mesh = load_mesh(mesh_file)
    # DAE import seems to Swap the Y and Z axes, so undo that
    mesh.apply_transform(transformations.rotation_matrix(math.pi / 2, [-1, 0, 0]))
    files = export_gltf(mesh, include_normals=True)
    out_dir = mesh_file.with_suffix('')
    out_dir.mkdir(exist_ok=True)
    for filename, data in files.items():
        output_file = out_dir / filename
        with open(output_file, 'wb') as f:
            f.write(data)

# Convert collision meshes to OBJ
for mesh_file in MESH_DIR.glob('*/collision/*.stl'):
    mesh = load_mesh(mesh_file)
    obj_data = export_obj(mesh, include_color=False, include_texture=False)
    out_file = mesh_file.with_suffix('.obj')
    with open(out_file, 'w') as f:
        f.write(obj_data)

# Edit all visual_parameters.yaml to point to the new meshes
yaml = ruamel.yaml.YAML()
yaml.preserve_quotes = True
for visual_parameters_file in CONFIG_DIR.glob('*/visual_parameters.yaml'):
    with open(visual_parameters_file, 'r') as f:
        visual_parameters = yaml.load(f)
    for link, params in visual_parameters["mesh_files"].items():
        params["visual"]["mesh"]["path"] = params["visual"]["mesh"]["path"].replace(".dae", "/model.gltf")
        params["collision"]["mesh"]["path"] = params["collision"]["mesh"]["path"].replace(".stl", ".obj")
    with open(visual_parameters_file, 'w') as f:
        yaml.dump(visual_parameters, f)