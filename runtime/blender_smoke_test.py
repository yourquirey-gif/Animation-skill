"""Headless Blender integration test: animated 3D character, prop, terrain and camera."""
import argparse, math, os, sys
from pathlib import Path
import bpy
from mathutils import Vector

def args():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",required=True); p.add_argument("--blend-file",required=True)
    p.add_argument("--width",type=int,default=360); p.add_argument("--height",type=int,default=640)
    p.add_argument("--fps",type=int,default=24); p.add_argument("--frames",type=int,default=48)
    return p.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])

def mat(name,color,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(*color,1)
    m.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value=metal
    return m

def ball(name,loc,scale,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=1,location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(material)
    bpy.ops.object.shade_smooth(); return o

def aim(o,target): o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()

def main():
    a=args(); out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True); s=bpy.context.scene
    available_engines = bpy.context.scene.render.bl_rna.properties["engine"].enum_items.keys()
    requested_engine = os.environ.get("BLENDER_SMOKE_ENGINE", "BLENDER_WORKBENCH")
    if requested_engine in available_engines:
        s.render.engine = requested_engine
    elif "BLENDER_EEVEE_NEXT" in available_engines:
        s.render.engine = "BLENDER_EEVEE_NEXT"
    elif "BLENDER_EEVEE" in available_engines:
        s.render.engine = "BLENDER_EEVEE"
    else:
        s.render.engine = "BLENDER_WORKBENCH"
    eevee = getattr(s, "eevee", None)
    if eevee is not None and hasattr(eevee, "taa_render_samples"):
        eevee.taa_render_samples = 16
    s.render.resolution_x=a.width; s.render.resolution_y=a.height; s.render.resolution_percentage=100
    s.render.fps=a.fps; s.frame_start=1; s.frame_end=a.frames
    s.render.image_settings.file_format="PNG"; s.world=s.world or bpy.data.worlds.new("SmokeTest_World"); s.world.color=(0.025,0.025,0.04)
    ground=mat("Ground",(0.025,0.16,0.17)); skin=mat("Skin",(0.72,0.36,0.22))
    coat=mat("Coat",(0.85,0.31,0.075)); dark=mat("Boots",(0.035,0.045,0.065))
    gold=mat("Artifact",(0.95,0.63,0.16),0.35); rock=mat("Hills",(0.09,0.12,0.18))
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-0.2)); floor=bpy.context.object
    floor.name="Ground"; floor.dimensions=(20,20,0.3); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); floor.data.materials.append(ground)
    for i,x in enumerate((-5,-3,3,5)):
        bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=2,radius2=0,depth=4,location=(x,3,1.4))
        bpy.context.object.name="3D_Hill_"+str(i); bpy.context.object.data.materials.append(rock)
    root=bpy.data.objects.new("Character_Root",None); s.collection.objects.link(root)
    parts=[ball("Torso",(0,0,1.55),(.48,.34,.68),coat),ball("Head",(0,0,2.48),(.39,.36,.43),skin),
           ball("Left_Arm",(-.55,0,1.72),(.16,.18,.53),coat),ball("Right_Arm",(.55,0,1.72),(.16,.18,.53),coat),
           ball("Left_Leg",(-.2,0,.68),(.18,.2,.48),dark),ball("Right_Leg",(.2,0,.68),(.18,.2,.48),dark)]
    for o in parts: o.parent=root
    prop=bpy.data.objects.new("Artifact",None); s.collection.objects.link(prop); prop.parent=root
    bpy.ops.mesh.primitive_cube_add(size=1,location=(.88,-.08,1.9)); obj=bpy.context.object
    obj.name="Handheld_3D_Artifact"; obj.dimensions=(.24,.24,.58); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(gold); bevel=obj.modifiers.new("Soft_Edges","BEVEL"); bevel.width=.04; bevel.segments=3; obj.parent=root
    for x in (-.14,.14): ball("Eye",(x,-.337,2.53),(.045,.025,.055),dark)
    bpy.ops.object.camera_add(location=(4.7,-9.5,4.2)); cam=bpy.context.object; aim(cam,(0,0,1.4)); cam.data.lens=52; s.camera=cam
    bpy.ops.object.light_add(type="AREA",location=(1.5,-4.5,6)); key=bpy.context.object; key.data.energy=850; key.data.shape="DISK"; key.data.size=5
    bpy.ops.object.light_add(type="AREA",location=(-4,1.5,3.5)); rim=bpy.context.object; rim.data.energy=900; rim.data.color=(.22,.48,1); rim.data.size=4
    for f,x,z in ((1,-.65,0),(a.frames//2,0,.12),(a.frames,.7,0)):
        root.location=(x,0,z); root.rotation_euler[2]=x*.2
        root.keyframe_insert(data_path="location",frame=f); root.keyframe_insert(data_path="rotation_euler",frame=f)
        obj.location.z=1.9+(.35 if f==a.frames//2 else 0); obj.keyframe_insert(data_path="location",frame=f)
    for f in range(1,a.frames+1,max(1,a.fps//2)):
        parts[0].location.z=1.55+.035*math.sin(f*.35); parts[0].keyframe_insert(data_path="location",frame=f)
    s.view_settings.view_transform="AgX"; bpy.ops.wm.save_as_mainfile(filepath=a.blend_file)
    for f in range(1,a.frames+1):
        s.frame_set(f); s.render.filepath=str(out/("frame_%04d.png"%f)); bpy.ops.render.render(write_still=True)
if __name__=="__main__": main()
