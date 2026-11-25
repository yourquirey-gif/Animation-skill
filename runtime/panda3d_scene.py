#!/usr/bin/env python3
"""Blender-free Panda3D storyboard shot renderer."""
import argparse, json
from pathlib import Path
from panda3d.core import AmbientLight, DirectionalLight, Filename, LColor, PNMImage, Point3, loadPrcFileData

loadPrcFileData("", "audio-library-name null")
loadPrcFileData("", "window-type offscreen")
loadPrcFileData("", "sync-video false")

def v(value, default):
    value = default if value is None else value
    if len(value) != 3: raise ValueError("Expected 3D vector")
    return tuple(float(x) for x in value)

def sample(keys, t, defaults):
    if not keys: return defaults
    keys = sorted(keys, key=lambda x: float(x.get("time_seconds", 0)))
    left = keys[0]
    for right in keys[1:]:
        a, b = float(left.get("time_seconds", 0)), float(right.get("time_seconds", 0))
        if t <= b:
            f = max(0.0, min(1.0, (t-a)/max(1e-9,b-a)))
            return {k: tuple(x+(y-x)*f for x,y in zip(v(left.get(k), defaults[k]),v(right.get(k),defaults[k]))) for k in defaults}
        left = right
    return {k:v(left.get(k),defaults[k]) for k in defaults}

class Renderer:
    def __init__(self, width, height, fps, out):
        from direct.showbase.ShowBase import ShowBase
        loadPrcFileData("", f"win-size {width} {height}")
        self.base=ShowBase(windowType="offscreen"); self.base.disableMouse()
        self.fps=fps; self.out=Path(out); self.out.mkdir(parents=True,exist_ok=True)
        self.animated=[]
        ambient=AmbientLight("ambient"); ambient.setColor(LColor(.42,.44,.5,1))
        self.base.render.setLight(self.base.render.attachNewNode(ambient))
        sun=DirectionalLight("key"); sun.setColor(LColor(.95,.9,.82,1))
        sun_np=self.base.render.attachNewNode(sun); sun_np.setHpr(-35,-55,0); self.base.render.setLight(sun_np)
    def color(self, val):
        val=val or [.5,.5,.5]; return LColor(*(list(val)+[1])[:4])
    def object(self, spec, parent, root_path):
        root=parent.attachNewNode(spec.get("name","object"))
        if spec.get("asset"):
            path=Path(spec["asset"]); path=path if path.is_absolute() else root_path/path
            if not path.is_file(): raise FileNotFoundError(path)
            if path.suffix.lower() in (".gltf", ".glb"):
                try:
                    from panda3d_gltf import load_model
                except ImportError as exc:
                    raise RuntimeError("Install panda3d-gltf to load GLB/glTF assets") from exc
                model=load_model(str(path))
            else:
                model=self.base.loader.loadModel(Filename.fromOsSpecific(str(path)))
        else:
            names={"cube":"models/box","box":"models/box","uv_sphere":"models/misc/sphere","sphere":"models/misc/sphere","ico_sphere":"models/misc/sphere","cylinder":"models/misc/cylinder","cone":"models/misc/cone","plane":"models/plane"}
            name=names.get(spec.get("primitive","cube"))
            if not name: raise ValueError("Unsupported primitive: "+str(spec.get("primitive")))
            model=self.base.loader.loadModel(name)
        if model.isEmpty(): raise RuntimeError("Could not load model for "+spec.get("name","object"))
        model.reparentTo(root); model.setColor(self.color(spec.get("color",spec.get("material",{}).get("color")))); model.setTwoSided(True)
        model.setScale(*v(spec.get("scale"),(1,1,1)))
        pos=v(spec.get("location"),(0,0,0)); rot=v(spec.get("rotation"),(0,0,0))
        root.setPos(*pos); root.setHpr(rot[2],rot[0],rot[1])
        if spec.get("keyframes"): self.animated.append((root,spec["keyframes"],{"location":pos,"rotation":rot,"scale":(1,1,1)}))
        return root
    def build(self, shot, root_path):
        env=shot.get("environment",{}); self.base.setBackgroundColor(*(env.get("world_color",[.025,.03,.05])),1)
        for obj in env.get("objects",[]): self.object(obj,self.base.render,root_path)
        for subject in shot.get("subjects",[]):
            root=self.base.render.attachNewNode(subject.get("name","subject"))
            defaults={"location":v(subject.get("location"),(0,0,0)),"rotation":v(subject.get("rotation"),(0,0,0)),"scale":v(subject.get("scale"),(1,1,1))}
            root.setPos(*defaults["location"]); root.setHpr(defaults["rotation"][2],defaults["rotation"][0],defaults["rotation"][1]); root.setScale(*defaults["scale"])
            for part in subject.get("parts",[]): self.object(part,root,root_path)
            if subject.get("asset"):
                asset_spec={"name":subject.get("name","subject")+"-asset","asset":subject["asset"],"location":[0,0,0],"rotation":[0,0,0],"scale":subject.get("asset_scale",[1,1,1]),"color":[1,1,1]}
                self.object(asset_spec,root,root_path)
            if subject.get("keyframes"):
                self.animated.append((root,subject["keyframes"],defaults))
        for prop in shot.get("props",[]): self.object(prop,self.base.render,root_path)
        cam=shot.get("camera",{}); self.cam_keys=cam.get("keyframes",[])
        self.cam_defaults={"location":v(cam.get("location"),(5,-10,4)),"target":v(cam.get("target"),(0,0,1))}
        self.base.camLens.setFov(float(cam.get("fov",42))); self.base.camLens.setNearFar(.05,10000)
        for light in shot.get("lighting",[]):
            lamp=DirectionalLight(light.get("name","fill")); lamp.setColor(self.color(light.get("color",[.7,.7,.8])))
            node=self.base.render.attachNewNode(lamp); node.setPos(*v(light.get("location"),(2,-4,6))); node.lookAt(Point3(0,0,0)); self.base.render.setLight(node)
    def render(self, duration):
        total=max(1,round(float(duration)*self.fps))
        for frame in range(total):
            t=frame/self.fps
            for node,keys,defaults in self.animated:
                vals=sample(keys,t,defaults); node.setPos(*vals["location"]); r=vals["rotation"]; node.setHpr(r[2],r[0],r[1]); node.setScale(*vals["scale"])
            cam=sample(self.cam_keys,t,self.cam_defaults); self.base.cam.setPos(*cam["location"]); self.base.cam.lookAt(Point3(*cam["target"]))
            self.base.graphicsEngine.renderFrame()
            img=PNMImage()
            if not self.base.win.getScreenshot(img): raise RuntimeError("Screenshot capture failed")
            path=self.out/("frame_%04d.png"%frame)
            if not img.write(Filename.fromOsSpecific(str(path))): raise RuntimeError("PNG write failed: "+str(path))
        return total
    def close(self): self.base.destroy()

def main():
    p=argparse.ArgumentParser(); p.add_argument("--storyboard",required=True,type=Path); p.add_argument("--shot-index",type=int,required=True); p.add_argument("--output-dir",required=True,type=Path); p.add_argument("--width",type=int,default=1080); p.add_argument("--height",type=int,default=1920); p.add_argument("--fps",type=int,default=24); a=p.parse_args()
    data=json.loads(a.storyboard.read_text(encoding="utf-8")); shots=data.get("shots",[])
    if a.shot_index<0 or a.shot_index>=len(shots): raise IndexError("Invalid shot index")
    shot=shots[a.shot_index]
    if float(shot.get("duration_seconds",0))<=0: raise ValueError("Shot duration must be positive")
    renderer=Renderer(a.width,a.height,a.fps,a.output_dir)
    try:
        renderer.build(shot,a.storyboard.resolve().parent); count=renderer.render(shot["duration_seconds"])
        print(json.dumps({"status":"RENDERED","frames":count,"output_dir":str(a.output_dir.resolve())}))
    finally: renderer.close()

if __name__=="__main__": main()
