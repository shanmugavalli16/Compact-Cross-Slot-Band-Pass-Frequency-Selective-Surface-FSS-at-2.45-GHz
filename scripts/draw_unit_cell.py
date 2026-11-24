"""Draws the dimensioned unit cell (images/unit_cell_dimensions.png). Parameters in mm as in the CST parameter list."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Patch
from shapely.geometry import box
from shapely.ops import unary_union
from shapely.affinity import rotate

CU="#FFFF00"; PI="#D6A99D"; INK="#1a1a1a"; DIM="#0b2a8a"
P,L=25.0,24.6; W,L1,W1,L2,G1,L3,G2,L4=0.6,3.6,0.5,8.0,0.3,7.0,0.5,1.22; WN,LN=0.4,1.1; H=L/2
r=[box(-WN/2,0,WN/2,LN),box(-W/2,LN,W/2,H)]; y=H
bars=[]
for ln,gap in ((L1,G1),(L2,G2),(L3,G2),(L4,0)):
    bars.append((ln,y-W1,y)); r.append(box(-ln/2,y-W1,ln/2,y)); y-=W1+gap
arm=unary_union(r)
cross=unary_union([rotate(arm,k*90,origin=(0,0)) for k in range(4)]+[box(-LN,-WN/2,LN,WN/2),box(-WN/2,-LN,WN/2,LN)])

fig,ax=plt.subplots(figsize=(13,13)); fig.patch.set_facecolor("white")
ax.add_patch(Rectangle((-P/2,-P/2),P,P,fc=CU,ec=INK,lw=1.4,zorder=1))
gs=cross.geoms if hasattr(cross,"geoms") else [cross]
for g in gs: ax.add_patch(Polygon(list(g.exterior.coords),fc=PI,ec=INK,lw=1.0,zorder=3))
ax.set_xlim(-19,16.5); ax.set_ylim(-17,18.5); ax.set_aspect("equal"); ax.axis("off")

def dim(p1,p2,ms=8,lw=1.0):
    ax.annotate("",xy=p2,xytext=p1,arrowprops=dict(arrowstyle="<|-|>",color=DIM,lw=lw,mutation_scale=ms,shrinkA=0,shrinkB=0),zorder=6)
def txt(x,y,s,ha="left",va="center",fs=11,rot=0):
    ax.text(x,y,s,ha=ha,va=va,fontsize=fs,color=DIM,style="italic",fontweight="bold",rotation=rot,zorder=7)
def leader(xy,xyt,s,ha="left",fs=11):
    ax.annotate(s,xy=xy,xytext=xyt,ha=ha,va="center",fontsize=fs,color=DIM,style="italic",fontweight="bold",
                arrowprops=dict(arrowstyle="-|>",color=DIM,lw=0.9,mutation_scale=9),zorder=7)

# overall dims
dim((-P/2,-P/2-1.8),(P/2,-P/2-1.8),ms=10); txt(0,-P/2-2.9,"Px = 25 mm","center",fs=13)
dim((-P/2-1.8,-P/2),(-P/2-1.8,P/2),ms=10); txt(-P/2-2.9,0,"Py = 25 mm","center",fs=13,rot=90)
for x in (-H,H): ax.plot([x,x],[0.4,15.1],color=DIM,lw=0.7,ls=":",zorder=5)
dim((-H,14.6),(H,14.6),ms=10); txt(0,15.5,"l = 24.6 mm","center",fs=13)
# half length
ax.plot([2.0,8.9],[H,H],color=DIM,lw=0.7,ls=":",zorder=5)
dim((8.5,0.25),(8.5,H),ms=8); txt(9.2,6.5,"l/2 = 12.3 mm","center",fs=11,rot=90)

# bar lengths
names=["l1 = 3.6 mm","l2 = 8 mm","l3 = 7 mm","l4 = 1.22 mm"]
for (ln,lo,hi),nm in zip(bars,names):
    ym=(lo+hi)/2
    dim((-ln/2+0.03,ym),(ln/2-0.03,ym),ms=6,lw=0.9)
    txt(ln/2+0.2,ym,nm,fs=11)
# vertical chain (w1,g1,g2)
xc=-5.0; yt=H
seq=[("w1",W1),("g1",G1),("w1",W1),("g2",G2),("w1",W1),("g2",G2),("w1",W1)]
e=[yt]
for _,v in seq: e.append(e[-1]-v)
for i,(n,v) in enumerate(seq):
    dim((xc,e[i+1]+0.01),(xc,e[i]-0.01),ms=5,lw=0.9)
    txt(xc-0.45,(e[i]+e[i+1])/2,f"{n} = {v} mm",ha="right",fs=9.5)
for v in e: ax.plot([xc-0.25,xc+0.25],[v,v],color=DIM,lw=0.7,zorder=6)
# stem and narrow section
leader((0.3,6.0),(2.8,6.0),"w = 0.6 mm")
leader((0.2,0.6),(3.2,2.3),"0.4 mm wide,\n1.1 mm long\n(centre link)")

# axes + legend
ox,oy=13.6,-14.8
ax.annotate("",xy=(ox+1.8,oy),xytext=(ox,oy),arrowprops=dict(arrowstyle="-|>",color=INK,lw=1.3))
ax.annotate("",xy=(ox,oy+1.8),xytext=(ox,oy),arrowprops=dict(arrowstyle="-|>",color=INK,lw=1.3))
ax.text(ox+2.0,oy-0.3,"x",fontsize=14,style="italic",fontweight="bold"); ax.text(ox+0.3,oy+2.0,"y",fontsize=14,style="italic",fontweight="bold")
ax.legend(handles=[Patch(fc=CU,ec=INK,label="Copper (t = 0.035 mm)"),Patch(fc=PI,ec=INK,label="Polyimide (h = 0.05 mm)")],
          loc="upper left",bbox_to_anchor=(0.0,1.0),fontsize=13,frameon=False,handlelength=2.2,handleheight=1.4)
plt.tight_layout()
plt.savefig(ROOT / "images" / "unit_cell_dimensions.png", dpi=200, facecolor="white")
