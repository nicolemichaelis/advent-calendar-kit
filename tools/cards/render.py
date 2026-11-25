import sys, os, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
from playwright.sync_api import sync_playwright
FPS=25; DUR=3.2; N=int(FPS*DUR)
mode=sys.argv[1]; days=[int(x) for x in sys.argv[2:]] or list(range(1,25))
os.makedirs("out",exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':720,'height':720})
    for d in days:
        pg.goto(f"file://{HERE}/build/day{d:02d}.html"); pg.wait_for_timeout(400)
        pg.evaluate("document.fonts.ready")
        if mode=="still":
            pg.evaluate("t=>document.getAnimations().forEach(a=>{a.pause();a.currentTime=t})",1100)
            pg.screenshot(path=f"out/still{d:02d}.jpg",type="jpeg",quality=88); continue
        fd=f"frames{d:02d}"; shutil.rmtree(fd,ignore_errors=True); os.makedirs(fd)
        pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
        for i in range(N):
            pg.evaluate("t=>document.getAnimations().forEach(a=>{a.currentTime=t})", i*1000/FPS)
            pg.screenshot(path=f"{fd}/f{i:03d}.jpg",type="jpeg",quality=90)
        pg.evaluate("t=>document.getAnimations().forEach(a=>{a.currentTime=t})",1100)
        pg.screenshot(path=f"out/{d:02d}.jpg",type="jpeg",quality=88)
        subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{fd}/f%03d.jpg","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-movflags","+faststart","-an",f"out/{d:02d}.mp4"],check=True)
        shutil.rmtree(fd)
    b.close()
