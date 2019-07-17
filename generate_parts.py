#!/usr/bin/python
import os, shutil, copy, random, numpy as np, stl
from jinja2 import FileSystemLoader, Environment
from pytransform3d.transformations import transform_from, concat
from pytransform3d.rotations import matrix_from_euler_xyz, euler_xyz_from_matrix
from math import pi


def boxes(filename):
    import sys
    sys.path.append("/usr/lib/freecad/lib/")
    import FreeCAD, Part
    shape = Part.Shape()
    shape.read(filename)
    shapes = shape.childShapes()

    boxes = []
    # if name == "SR319-20x55-ASSEMBLY":  shapes = shapes[0].childShapes()[-3:-2]
    if name == "SR319-SERVO":  shapes = [shape]
    elif name == "SR319-FEET":  shapes = [shape]
    elif name == "SR319-HOE":  shapes = [shape]
    elif name == "SR319-BODY":  shapes = [shape]
    elif name == "SR319-CAM":  shapes = [shape]
    elif name == "SR319-AIY":  shapes = [shape]        
    else: shapes = []

    for c in shapes:
        boxes.append( {"size" : "%f %f %f" % (c.BoundBox.XLength / 1000.0, c.BoundBox.YLength / 1000.0, c.BoundBox.ZLength / 1000.0),
                      "pose" : "%f %f %f 0 0 0" % (c.BoundBox.Center.x / 1000.0, c.BoundBox.Center.y / 1000.0, c.BoundBox.Center.z / 1000.0),
                      "xyz"  : "%f %f %f" % (c.BoundBox.Center.x / 1000.0, c.BoundBox.Center.y / 1000.0, c.BoundBox.Center.z / 1000.0),
                      "rpy"  : "0 0 0"
                      })

    return boxes


def inertia(filename, mass):
    import stl
    mesh = stl.mesh.Mesh.from_file(filename)
    volume, cog, inertia = mesh.get_mass_properties()
    inertia = inertia  / volume * mass
    return ( "%f %f %f 0 0 0"  % (cog[0], cog[1], cog[2]),
             " ".join( ['ixx="%e"' % inertia[0,0], 'ixy="%e"' % inertia[0,1], 'ixz="%e"' % inertia[0,2],
                         'iyy="%e"' % inertia[1,1], 'iyz="%e"' % inertia[1,2], 'izz="%e"' % inertia[2,2]] ) )



def render_from_template(directory, template_name, **kwargs):
    loader = FileSystemLoader(directory)
    env = Environment(loader=loader)
    template = env.get_template(template_name)
    return template.render(**kwargs)

# total weight 1586 grams, servos 928 grams, cameras 240 grams, body 418 grams
parts = {
        "SR319-20x43"       : { "mass": "0.008",   "count" : 8, "material" : "aluminum"},
        "SR319-20x55"       : { "mass": "0.008",   "count" : 14, "material" : "aluminum"},
        "SR319-40x43"       : { "mass": "0.009",   "count" : 2, "material" : "aluminum"},
        "SR319-BODY"        : { "mass": "0.098",   "count" : 1, "material" : "aluminum"},
        "SR319-BATTERY"     : { "mass": "0.210",   "count" : 1, "material" : "plastic"},
        "SR319-AIY"         : { "mass": "0.050",   "count" : 1, "material" : "cardboard"},    # FIXME, weight!
        "SR319-CAM-HOLDER"  : { "mass": "0.001",   "count" : 12, "material" : "plastic"},
        "SR319-CAM"         : { "mass": "0.018",   "count" : 3, "material" : "plastic", "sensor" : "1"},
        "SR319-FEET"        : { "mass": "0.029",   "count" : 2, "material" : "aluminum"},
        "SR319-SERVO-ROTOR" : { "mass": "0.002",   "count" : 2, "material" : "aluminum"},
        "SR319-SERVO"       : { "mass": "0.058",   "count" : 16, "material" : "plastic"},
        "SR319-SERVO-WHEEL" : { "mass": "0.002",   "count" : 14, "material" : "aluminum"},
        "SR319-HOE"         : { "mass": "0.01",    "count" : 2, "material" : "aluminum"},
        "SR319-20x55-ASSEMBLY" : { "mass": "0.012",   "count" : 14, "material" : "aluminum"},
}

print("weight", sum([float(part["mass"]) * part["count"] for part in parts.values()]))


# remove and re-pupulate models directory
for name, data in parts.items():
    data["boxes"] = boxes(os.path.join("meshes", name + ".stp"))
    data["cog"], data["inertia"] = inertia(os.path.join("meshes", name + ".stl"), float(data["mass"]))
    data["cog_xyz"] = " ".join(data["cog"].split()[:3])
    data["cog_rpy"] = " ".join(data["cog"].split()[3:])

    # remove collisions/mass/inertia from sensor for now
    # if "sensor" in data: data["boxes"], data["mass"] = [], None


leg_left = [
    #{"model" : 'SR319-SERVO',         "pose" : "0.0 0.0 0.0 0.0 0.0 0.0", "name" : "leg0"}, "includes" : [
    {"model" : 'SR319-20x55-ASSEMBLY',"pose" : "0.0 0.0 0.0 0.0 0.0 1.570796", "name" : "leg1", "joint" : {"type" : "continuous"}, "includes" : [
    {"model" : 'SR319-40x43',         "pose" : "0.000 0.022 -0.017 -1.570796 0.0 0.0", "name" : "leg2", "includes" : [
    {"model" : 'SR319-SERVO',         "pose" : "0.018 0.010 0.016 0.0 1.570796 0.0", "name" : "leg3", "includes" : [
    {"model" : 'SR319-20x55-ASSEMBLY',"pose" : "0.0 0.0 0.0 0.0 0.0 1.570796", "name" : "leg4", "joint" : {"type" : "continuous"}, "includes" : [
    {"model" : 'SR319-20x43',         "pose" : "0.00 0.022 -0.017 0.0 1.570796 1.570796", "name" : "leg5", "includes" : [
    {"model" : 'SR319-SERVO',         "pose" : "0.018 0.00 0.038 1.570796 0.0 1.570796", "name" : "leg6", "includes" : [
    {"model" : 'SR319-20x55-ASSEMBLY',"pose" : "0.0 0.0 0.0 0.0 0.0 0.0", "name" : "leg7", "joint" : {"type" : "continuous"}, "includes" : [
    {"model" : 'SR319-20x43',         "pose" : "0.00 0.022 -0.017 0.0 1.570796 1.570796", "name" : "leg8", "includes" : [
    {"model" : 'SR319-SERVO',         "pose" : "-0.018 0.00 0.038 1.570796 0.0 -1.570796", "name" : "leg9", "includes" : [
    {"model" : 'SR319-20x55-ASSEMBLY',"pose" : "0.0 0.00 0.00 0.0 0.0 0.0", "name" : "leg10", "joint" : {"type" : "continuous"}, "includes" : [
    {"model" : 'SR319-20x55-ASSEMBLY',"pose" : "-0.02 0.044 -0.02 0.0 1.570796 3.141592", "name" : "leg11", "includes" : [
    {"model" : 'SR319-SERVO',         "pose" : "0.0 0.0 0.00 0.0 0.0 1.570796", "name" : "leg12", "joint" : {"type" : "continuous"}, "includes" : [
    {"model" : 'SR319-FEET',          "pose" : "-0.016 -0.01 -0.018 0.0 1.570796 0.0", "name" : "leg13", "collision" : "1", "includes" : []}
    ]}]}]}]}]}]}]}]}]}]}]}]}]


leg_right = [
    #{"model" : 'SR319-SERVO',         "pose" : "0.0 0.0 0.0 0.0 0.0 0.0", "name" : "leg0"}, "includes" : [
    {"model" : 'SR319-20x55-ASSEMBLY',"pose" : "0.0 0.0 0.0 0.0 0.0 1.570796", "name" : "leg1", "joint" : {"type" : "continuous"}, "includes" : [
    {"model" : 'SR319-40x43',         "pose" : "0.000 0.022 -0.017 -1.570796 3.141592 0.0", "name" : "leg2", "includes" : [
    {"model" : 'SR319-SERVO',         "pose" : "0.018 0.010 0.016 0.0 1.570796 0.0", "name" : "leg3", "includes" : [
    {"model" : 'SR319-20x55-ASSEMBLY',"pose" : "0.0 0.0 0.0 0.0 0.0 1.570796", "name" : "leg4", "joint" : {"type" : "continuous"}, "includes" : [
    {"model" : 'SR319-20x43',         "pose" : "0.00 0.022 -0.017 0.0 1.570796 1.570796", "name" : "leg5", "includes" : [
    {"model" : 'SR319-SERVO',         "pose" : "-0.018 0.00 0.038 1.570796 0.0 -1.570796", "name" : "leg6", "includes" : [
    {"model" : 'SR319-20x55-ASSEMBLY',"pose" : "0.0 0.0 0.0 0.0 0.0 0.0", "name" : "leg7", "joint" : {"type" : "continuous"}, "includes" : [
    {"model" : 'SR319-20x43',         "pose" : "0.00 0.022 -0.017 0.0 1.570796 1.570796", "name" : "leg8", "includes" : [
    {"model" : 'SR319-SERVO',         "pose" : "-0.018 0.00 0.038 1.570796 0.0 -1.570796", "name" : "leg9", "includes" : [
    {"model" : 'SR319-20x55-ASSEMBLY',"pose" : "0.0 0.00 0.00 0.0 0.0 0.0", "name" : "leg10", "joint" : {"type" : "continuous"}, "includes" : [
    {"model" : 'SR319-20x55-ASSEMBLY',"pose" : "-0.02 0.044 -0.02 0.0 1.570796 3.141592", "name" : "leg11", "includes" : [
    {"model" : 'SR319-SERVO',         "pose" : "0.0 0.0 0.00 0.0 0.0 1.570796", "name" : "leg12", "joint" : {"type" : "continuous"}, "includes" : [
    {"model" : 'SR319-FEET',          "pose" : "-0.016 -0.01 -0.018 0.0 1.570796 0.0", "name" : "leg13", "collision" : "1", "includes" : []}
    ]}]}]}]}]}]}]}]}]}]}]}]}]


arm = [
    #{"model" : 'SR319-SERVO',         "pose" : "0.0 0.0 0.0 0.0 0.0 0.0", "name" : "arm0"}, "includes" : [
    {"model" : 'SR319-SERVO-ROTOR',   "pose" : "0.0 0.0 0.009 3.141592 0.0 1.570796", "name" : "arm1", "joint" : {"type" : "continuous"}, "includes" : [
    {"model" : 'SR319-20x55-ASSEMBLY',"pose" : "0.0 -0.0169 -0.022 1.570796 0.0 0.0", "name" : "arm2", "includes" : [
    {"model" : 'SR319-SERVO',         "pose" : "0.0 0.0 0.00 0.0 0.0 -1.570796", "name" : "arm3", "joint" : {"type" : "continuous"}, "includes" : [
    {"model" : 'SR319-20x43',         "pose" : "0.00 -0.038 -0.018 0.0 1.570796 1.570796", "name" : "arm4", "includes" : [
    {"model" : 'SR319-20x43',         "pose" : "0.00 0.00 0.00 0.0 3.141592 0.0", "name" : "arm5", "includes" : [
    {"model" : 'SR319-SERVO',         "pose" : "0.018 0.0 0.038 1.570796 0.0 1.570796", "name" : "arm6", "includes" : [
    {"model" : 'SR319-20x55-ASSEMBLY',"pose" : "0.0 0.00 0.00 0.0 0.0 0.0", "name" : "arm7", "joint" : {"type" : "continuous"}, "includes" : [
    {"model" : 'SR319-HOE',           "pose" : "0.0 0.022 -0.017 0.0 1.570796 1.570796", "name" : "arm8", "collision" : "1", "includes" : [
    {"model" : 'SR319-CAM',        "pose" : "0.0 0.01 0.0 1.570796 0.0 0.0", "name" : "cam0", "includes" : []}
    ]}]}]}]}]}]}]}]}]

head = [
    #{"model" : 'SR319-SERVO',         "pose" : "0.0 0.0 0.0 0.0 0.0 0.0", "name" : "arm0"}, "includes" : [
    {"model" : 'SR319-SERVO-ROTOR',   "pose" : "0.0 0.0 0.0 0.0 3.141592 0.0", "name" : "head1", "includes" : [
    {"model" : 'SR319-SERVO',         "pose" : "0.0 0.0 0.009 0.0 3.141592 -1.570796", "name" : "head2", "joint" : {"type" : "continuous"}, "includes" : [
            {"model" : 'SR319-CAM',        "pose" : "0.0 0.04 -0.03 1.5 0.0 0.0", "name" : "cam0", "includes" : []},
            {"model" : 'SR319-AIY',       "pose" : "0.0 0.00 -0.039 1.570796 3.141592 0.0", "name" : "aiy0", "collision" : "1", "includes" : []},

        ]}
    ]}]


# hack includes, because joints in Gazebo are broken, if they are not defined in the same model?
bot =        [ {"model" : 'SR319-BODY', "pose" : "0.0 0.0 0.0 0.0 0.0 0.0", "name" : "chassis_center", "collision" : "1", "includes" : [
               {"model" : 'SR319-BATTERY', "pose" : "-0.02 0.011 0.035 0.0 1.570796 0.0", "name" : "battery", "includes" : []},
               {"model" : 'SR319-20x43',  "pose" : "-0.001 0.097 0.0 1.570796 0.0 0.0",          "name" : "head0", "position" : "center", "includes" : copy.deepcopy(head)},
	           {"model" : 'SR319-SERVO',  "pose" : "0.018 0.0 0.033 1.570796 0.0 1.570796",    "name" : "leg0", "position" : "left", "includes" : copy.deepcopy(leg_left)},
               {"model" : 'SR319-SERVO',  "pose" : "-0.018 0.0 -0.033 -1.570796 0.0 1.570796", "name" : "leg0", "position" : "right", "includes" : copy.deepcopy(leg_right)},
               {"model" : 'SR319-SERVO',  "pose" : "-0.001 0.102 0.0682 0.0 0.0 0.0",          "name" : "arm0", "position" : "left", "includes" : copy.deepcopy(arm)},
               {"model" : 'SR319-SERVO',  "pose" : "-0.001 0.102 -0.0682 0.0 3.141592 0.0",        "name" : "arm0", "position" : "right", "includes" : copy.deepcopy(arm)} ]}]

# hack includes, because joints in Gazebo are broken, if they are not defined in the same model?
# bot =        [ {"model" : 'SR319-BODY', "pose" : "0.0 0.0 0.0 0.0 0.0 0.0", "name" : "chassis_center", "includes" : []} ]


def set_properties(item, name = None, position = None):
    """populates properties to includes. recursive call"""
    item.update(parts[item["model"]])  # add model properties
    if "joint" not in item: item["joint"] = {"type" : "fixed"}
    item["xyz"] = " ".join(item["pose"].split()[:3])
    item["rpy"] = " ".join(item["pose"].split()[3:])

    if name:
        item["parent"] = name
        if position: item["name"] += "_" + position

    for child in item["includes"]:
        set_properties(child, item["name"], child.get("position", position))

def merge_fixed_links(parent):
    """Merge fixed links"""

    # if child doesn't have 'joint|collision' attributes, merge it to parent
    #  * add child pose to grandchild
    #  * add child position to grandchild
    #  * add child includes to includes
    #  * add child mesh to parent
    #  * add child weight to parent
    #  * remove child
    merged = []

    for child in parent["includes"]:                                # this is actually a recursion
        if not "joint" in child and not 'collision' in child:
            for grandchild in child["includes"]:
                # calculate grandchild_to_parent transform (so we can remove 'child' link )
                T = lambda pose: transform_from(matrix_from_euler_xyz(pose[3:]).T, pose[:3])
                child_to_parent = T(np.fromstring(child['pose'], sep = ' '))
                grandchild_to_child = T(np.fromstring(grandchild['pose'], sep = ' '))
                grandchild_to_parent = concat(grandchild_to_child, child_to_parent)
                pose = np.concatenate([grandchild_to_parent[:3, 3], euler_xyz_from_matrix(grandchild_to_parent[:3, :3].T)])
                grandchild['pose'] = str(pose)[1:-1]

                # save position (left/right) modifier to grandchild
                if 'position' in child: grandchild['position'] = child['position']

                # recourse into descendents
                parent['includes'].append(grandchild)

                merged.append((child['model'], child_to_parent))

    if merged:
        meshes = [stl.mesh.Mesh.from_file('meshes/%s.stl' % parent['model']).data]
        for part, child_to_parent in merged:
            mesh = stl.mesh.Mesh.from_file('meshes/%s.stl' % part)
            mesh.transform(child_to_parent)     # ?? inverse?
            meshes.append(mesh.data)

        combined = stl.mesh.Mesh(np.concatenate(meshes))
        name = parent['name'] + '_' + parent.get('position', '')
        combined.save('meshes/%s.stl' % name, mode=stl.Mode.BINARY)

        parts[name] = { "mass": "0.008",   "count" : 1, "material" : parts[parent['model']]['material']}
        # TODO: fix mass, intertia, etc
        #parent['model'] = name




    # remove merged children
    parent["includes"] = [child for child in parent["includes"] if "joint" in child or 'collision' in child]

    # recourse into joints
    for child in parent["includes"]:
        merge_fixed_links(child)



# generate bot model
name = "minis"
data = {"name" : name, "includes" : bot, "joints" : []}


for item in bot:
    merge_fixed_links(item)
    set_properties(item)
    # collect_joints(item)      # rotating joints to  top level
    # insert_cameras(item)      # add cameras randomly


# generate world model
with open(os.path.join("data", "%s.urdf" % name), "w") as f:
    f.write(render_from_template("templates", "model.urdf", **data))



