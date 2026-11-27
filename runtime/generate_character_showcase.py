#!/usr/bin/env python3
"""Generate a reusable stylized 3D hero and a 16-expression showcase in Blender."""
import argparse, json, math
from pathlib import Path
import bpy
from mathutils import Vector

EMOTIONS = [
 ("Happy","smile"),("Sad","frown"),("Angry","angry"),("Surprised","open"),
 ("Fearful","fear"),("Disgusted","disgust"),("Excited","big_smile"),("Confused","uneven"),
 ("Thinking","small"),("Shy","blush"),("Proud","smirk"),("Sleepy","closed"),
 ("Shocked","round"),("Crying","cry"),("Nervous","teeth"),("Calm","neutral")
]
def mat(name, color, rough=.55, metallic=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 bs=m.node_tree.nodes.get("Principled BSDF"); bs.inputs["Base Color"].default_value=(*color,1)
 bs.inputs["Roughness"].default_value=rough; bs.inputs["Metallic"].default_value=metallic
 return m
def uv(name, loc, scale, material, collection=None, segments=24, rings=16):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
 o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
 if material:o.data.materials.append(material)
 if collection:
  for c in list(o.users_collection): c.objects.unlink(o)
  collection.objects.link(o)
 return o
def cube(name, loc, scale, material, bevel=.08):
 bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale
 bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
 if material:o.data.materials.append(material)
 if bevel:
  mod=o.modifiers.new("Soft tailored edges","BEVEL"); mod.width=bevel; mod.segments=3
  o.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
 return o
def curve_line(name, points, material, radius=.025):
 c=bpy.data.curves.new(name,"CURVE"); c.dimensions="3D"; c.bevel_depth=radius; c.bevel_resolution=3
 s=c.splines.new("POLY"); s.points.add(len(points)-1)
 for p,co in zip(s.points,points): p.co=(*co,1)
 o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(material); return o
def face(prefix, x, z, scale, skin, hair, white, iris, dark, mouthmat, emotion):
 # Face looks toward camera at negative Y.
 uv(prefix+"_head",(x,0,z),(scale*.72,scale*.48,scale),skin)
 uv(prefix+"_hair_cap",(x,.015,z+scale*.63),(scale*.76,scale*.5,scale*.46),hair)
 for i in range(7):
  dx=(i-3)*scale*.19
  uv(prefix+"_fringe_%02d"%i,(x+dx,-.29,z+scale*(.78-.12*abs(i-3))),(scale*.17,scale*.18,scale*.28),hair)
 eye_mode = "closed" if emotion in ("closed",) else "wide" if emotion in ("open","fear","round","cry") else "normal"
 for side in (-1,1):
  ex=x+side*scale*.29; ey=-scale*.43
  if eye_mode=="closed":
   curve_line(prefix+"_eye_"+str(side),[(ex-scale*.15,ey,z+scale*.12),(ex,ey-.01,z+scale*.08),(ex+scale*.15,ey,z+scale*.12)],dark,scale*.035)
  else:
   h=scale*(.17 if eye_mode=="wide" else .12)
   uv(prefix+"_eye_white_"+str(side),(ex,ey,z+scale*.12),(scale*.145,scale*.065,h),white)
   uv(prefix+"_iris_"+str(side),(ex,ey-scale*.06,z+scale*.10),(scale*.075,scale*.04,h*.8),iris)
   uv(prefix+"_pupil_"+str(side),(ex,ey-scale*.09,z+scale*.10),(scale*.035,scale*.025,h*.55),dark)
  browz=z+scale*.34
  tilt=0
  if emotion=="angry": tilt=side*.35
  elif emotion in ("sad","fear","cry"): tilt=-side*.22
  elif emotion=="confused" and side==1: tilt=.25
  brow=uv(prefix+"_brow_"+str(side),(ex,-scale*.47,browz),(scale*.17,scale*.055,scale*.045),hair)
  brow.rotation_euler[1]=tilt
 # Mouth variants are actual geometry, not texture labels.
 my=-scale*.51; mz=z-scale*.30
 if emotion in ("smile","big_smile","smirk"):
  pts=[(x-scale*.20,my,mz),(x-scale*.10,my-scale*.025,mz-scale*.08),(x,my-scale*.03,mz-scale*.10),(x+scale*.12,my,mz-scale*.06),(x+scale*.20,my,mz)]
  curve_line(prefix+"_mouth",pts,mouthmat,scale*.035)
  if emotion=="big_smile": uv(prefix+"_teeth",(x,my-.015,mz-scale*.06),(scale*.13,.025,scale*.055),white)
 elif emotion in ("frown","sad","cry","fear"):
  curve_line(prefix+"_mouth",[(x-scale*.18,my,mz-scale*.06),(x,my,mz+scale*.05),(x+scale*.18,my,mz-scale*.06)],mouthmat,scale*.035)
 elif emotion in ("open","round"):
  uv(prefix+"_mouth",(x,my,mz-scale*.02),(scale*.11,.045,scale*.16 if emotion=="open" else scale*.11),mouthmat)
 elif emotion=="teeth":
  uv(prefix+"_mouth",(x,my,mz-scale*.04),(scale*.17,.035,scale*.07),white)
 elif emotion=="neutral":
  curve_line(prefix+"_mouth",[(x-scale*.14,my,mz),(x+scale*.14,my,mz)],mouthmat,scale*.025)
 else:
  curve_line(prefix+"_mouth",[(x-scale*.13,my,mz),(x,my-scale*.015,mz-scale*.02),(x+scale*.13,my,mz)],mouthmat,scale*.025)
 if emotion in ("blush","cry"):
  for side in (-1,1):
   uv(prefix+"_cheek_"+str(side),(x+side*scale*.43,-scale*.40,z-scale*.05),(scale*.11,.025,scale*.045),mat(prefix+"_blush",(.95,.28,.32)))
 if emotion=="cry":
  for side in (-1,1):
   uv(prefix+"_tear_"+str(side),(x+side*scale*.28,-scale*.49,z-scale*.08),(scale*.035,.02,scale*.11),mat(prefix+"_tear",(.18,.65,.95),.2))
def main():
 p=argparse.ArgumentParser(); p.add_argument("--output-dir",type=Path,default=Path("character-output")); a=p.parse_args()
 out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.read_factory_settings(use_empty=True)
 skin=mat("Warm skin",(0.72,.46,.31)); hair=mat("Espresso hair",(.025,.018,.028),.3)
 red=mat("Signature crimson hoodie",(.68,.025,.055),.42); white=mat("Cotton white",(.9,.91,.88))
 black=mat("Charcoal cargo",(.035,.045,.065)); shoe=mat("Red sneaker",(.72,.035,.045),.35)
 iris=mat("Warm brown eyes",(.20,.075,.025),.25); dark=mat("Pupil and brows",(.012,.008,.012))
 mouthmat=mat("Mouth",(.16,.025,.035)); blue=mat("Studio blue",(.025,.09,.20),.3,.25)
 # Hero full body, centered left.
 uv("Aryan_head",(-4,0,5.25),(.72,.48,.98),skin)
 uv("Aryan_hair",(-4,.02,5.88),(.77,.52,.55),hair)
 for i in range(9):
  dx=(i-4)*.16
  uv("Aryan_fringe_%02d"%i,(-4+dx,-.31,6.05-.10*abs(i-4)),(.18,.19,.34),hair)
 for side in (-1,1):
  ex=-4+side*.29
  uv("Aryan_eye_white_"+str(side),(ex,-.46,5.35),(.15,.06,.16),white)
  uv("Aryan_iris_"+str(side),(ex,-.52,5.34),(.075,.04,.09),iris)
  uv("Aryan_pupil_"+str(side),(ex,-.55,5.34),(.035,.025,.05),dark)
  uv("Aryan_brow_"+str(side),(ex,-.47,5.60),(.18,.05,.055),hair)
 curve_line("Aryan_smile",[(-4.18,-.51,5.02),(-4,-.54,4.97),(-3.82,-.51,5.02)],mouthmat,.035)
 cube("Aryan_hoodie_body",(-4,0,3.45),(1.55,.82,1.75),red,.28)
 cube("Aryan_white_Tshirt",(-4,-.43,3.5),(.70,.08,1.35),white,.12)
 uv("Aryan_hood",( -4,.18,4.10),(.72,.46,.55),red)
 for side in (-1,1):
  arm=cube("Aryan_sleeve_"+str(side),(-4+side*1.00,-.02,3.62),(.48,.58,1.45),red,.20); arm.rotation_euler[1]=side*.13
  uv("Aryan_hand_"+str(side),(-4+side*1.02,-.04,2.78),(.22,.20,.23),skin)
  cube("Aryan_trouser_"+str(side),(-4+side*.39,0,1.85),(.56,.72,1.65),black,.16)
  cube("Aryan_sneaker_"+str(side),(-4+side*.39,-.18,.82),(.68,1.0,.36),shoe,.13)
  cube("Aryan_sneaker_sole_"+str(side),(-4+side*.39,-.18,.64),(.70,1.02,.10),white,.035)
 cube("Aryan_waistband",(-4,0,2.62),(1.18,.75,.24),black,.08)
 # Hoodie details, stripes, zipper, pocket.
 curve_line("Hoodie_zipper",[(-4,-.49,4.22),(-4,-.49,2.75)],white,.018)
 for side in (-1,1):
  for k in range(2):
   curve_line("Sleeve_stripe_%s_%s"%(side,k),[(-4+side*1.13+k*.10,-.33,4.23),(-4+side*1.13+k*.10,-.33,3.05)],white,.025)
 cube("Hoodie_pocket",(-4,-.48,3.0),(.72,.07,.25),red,.07)
 # Expression grid, same head identity/hair proportions across all 16.
 labels=[]
 for i,(label,kind) in enumerate(EMOTIONS):
  col=i%4; row=i//4; x=1.2+col*2.05; z=6.0-row*1.75
  face("Expression_%02d_%s"%(i+1,label),x,z,.53,skin,hair,white,iris,dark,mouthmat,kind)
  # Text label under each expression.
  c=bpy.data.curves.new("Label_"+label,"FONT"); c.body="%02d  %s"%(i+1,label); c.size=.20; c.align_x="CENTER"
  ob=bpy.data.objects.new("Label_"+label,c); bpy.context.collection.objects.link(ob); ob.location=(x,-.65,z-.88)
 # Floor and studio lighting.
 floor=mat("Midnight navy floor",(.012,.025,.055),.42)
 cube("Studio_floor",(1,1,.15),(20,18,.25),floor,.1)
 world=bpy.context.scene.world or bpy.data.worlds.new("Studio World"); bpy.context.scene.world=world
 world.use_nodes=True; world.node_tree.nodes["Background"].inputs[0].default_value=(.012,.02,.045,1)
 world.node_tree.nodes["Background"].inputs[1].default_value=.45
 def area(name,loc,power,color,size,target):
  bpy.ops.object.light_add(type="AREA",location=loc); l=bpy.context.object; l.name=name; l.data.energy=power; l.data.color=color; l.data.shape="DISK"; l.data.size=size
  l.rotation_euler=(Vector(target)-l.location).to_track_quat("-Z","Y").to_euler()
 area("Key softbox",(-5,-8,10),1500,(1,.72,.58),7,(-2,0,3))
 area("Cool fill",(7,-5,8),1200,(.42,.62,1),6,(3,0,4))
 area("Hair rim",(-1,4,9),1800,(.25,.48,1),5,(0,0,4))
 bpy.ops.object.camera_add(location=(1,-23,8.0)); cam=bpy.context.object; cam.name="Character_Showcase_Camera"
 target=Vector((1.2,0,3.6)); cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
 cam.data.type="ORTHO"; cam.data.ortho_scale=17.8; bpy.context.scene.camera=cam
 scene=bpy.context.scene; scene.render.engine="BLENDER_EEVEE_NEXT"
 scene.eevee.taa_render_samples=64
 scene.render.resolution_x=1920; scene.render.resolution_y=1080; scene.render.resolution_percentage=100
 scene.view_settings.view_transform="AgX"
 scene.render.image_settings.file_format="PNG"; scene.render.filepath=str(out/"aryan_character_16_emotions.png")
 scene.camera.data.lens=50
 bpy.ops.wm.save_as_mainfile(filepath=str(out/"aryan_character.blend"))
 bpy.ops.render.render(write_still=True)
 report={"character":"Aryan","asset":"aryan_character.blend","preview":"aryan_character_16_emotions.png",
         "type":"procedural Blender 3D mesh character","emotion_count":len(EMOTIONS),
         "emotions":[x[0] for x in EMOTIONS],"notes":"Rendered 3D character showcase; expressions are separate modeled facial variants. Not yet a production skeletal/facial rig."}
 (out/"character_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
 print("CHARACTER_GENERATION_REPORT",json.dumps(report),flush=True)
if __name__=="__main__": main()
