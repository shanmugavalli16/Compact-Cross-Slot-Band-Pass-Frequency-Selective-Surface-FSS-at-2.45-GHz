"""Draws the equivalent-circuit figure (images/equivalent_circuit.png). Needs schemdraw."""
import schemdraw, schemdraw.elements as elm
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
import matplotlib; matplotlib.use("Agg")
from matplotlib.patches import Rectangle, Polygon, Ellipse, FancyBboxPatch
from shapely.geometry import box
from shapely.ops import unary_union
from shapely.affinity import rotate, scale, translate

CU="#FFFF00"; PI="#D6A99D"; OR="#E8873A"; INK="#111"
# geometry (mm)
W,L1,W1,L2,G1,L3,G2,L4=0.6,3.6,0.5,8.0,0.3,7.0,0.5,1.22; H=12.3; LN=1.1; WN=0.4
r=[box(-WN/2,0,WN/2,LN),box(-W/2,LN,W/2,H)]; y=H
for ln,gap in ((L1,G1),(L2,G2),(L3,G2),(L4,0)):
    r.append(box(-ln/2,y-W1,ln/2,y)); y-=W1+gap
arm=unary_union(r)
cross=unary_union([rotate(arm,k*90,origin=(0,0)) for k in range(4)]+[box(-LN,-WN/2,LN,WN/2),box(-WN/2,-LN,WN/2,LN)])

schemdraw.config(fontsize=13, lw=1.8)
d=schemdraw.Drawing(show=False); d.config(unit=3)
YT,YB=8.0,0.0
xs=[12.0,19.0,26.0]; XL,XR=1.0,44.0
d+=elm.Line().at((XL,YT)).to((XR,YT))
d+=elm.Line().at((XL,YB)).to((XR,YB))
for x in xs:
    d+=elm.Dot().at((x,YT)); d+=elm.Dot().at((x,YB))
d+=elm.Capacitor().at((xs[0],YT)).down(YT)
d+=elm.Resistor().at((xs[1],YT)).down(4)
d+=elm.Inductor2(loops=4).down(4)
d+=elm.Inductor2(loops=3).at((xs[2],YT)).down(4)
d+=elm.Capacitor().down(4)
fg=d.draw(show=False); ax=fg.ax; fig=fg.fig
fig.set_size_inches(18,10.5)

def tl(x0,x1,txt,fs=12.5):
    ax.add_patch(Rectangle((x0,YB-0.55),x1-x0,1.1,fc='white',ec=INK,lw=1.6,zorder=5))
    ax.text((x0+x1)/2,YB-1.7,txt,ha='center',va='top',fontsize=fs,fontweight='bold',zorder=6)
tl(2.0,8.0,'Air   $Z_0$'); tl(32.0,38.0,'Polyimide'); tl(39.0,43.0,'Air   $Z_0$')
ax.text(35.0,YB-3.0,'$h$ = 0.05 mm',ha='center',va='top',fontsize=11.5)
# top-rail boxes to mimic two-wire line
ax.add_patch(Rectangle((32.0,YT-0.55),6.0,1.1,fc='white',ec=INK,lw=1.6,zorder=5))
ax.add_patch(Rectangle((2.0,YT-0.55),6.0,1.1,fc='white',ec=INK,lw=1.6,zorder=5))
ax.add_patch(Rectangle((39.0,YT-0.55),4.0,1.1,fc='white',ec=INK,lw=1.6,zorder=5))

# labels
def lab(x,y,s,fs=13): ax.text(x,y,s,ha='left',va='center',fontsize=fs,fontweight='bold',zorder=7)
lab(xs[0]+0.8,YT/2,'$C_1$\n0.567 pF')
lab(xs[1]+0.8,3*YT/4,'$R$ = 0.58 $\\Omega$'); lab(xs[1]+0.8,YT/4,'$L_1$ = 3.31 nH')
lab(xs[2]+0.8,3*YT/4,'$L_2$ = 0.44 nH'); lab(xs[2]+0.8,YT/4,'$C_2$ = 0.66 pF')

# dashed boxes around branches
for x in xs:
    ax.add_patch(FancyBboxPatch((x-1.3,0.9),5.6,YT-1.8,boxstyle='round,pad=0.0,rounding_size=0.5',fc='none',ec=OR,ls='--',lw=1.6,zorder=4))

# unit cell
s=9.0/25.0; cx,cy=5.2,16.2
ax.add_patch(Rectangle((cx-12.5*s,cy-12.5*s),25*s,25*s,fc=CU,ec='#555',lw=1.2,zorder=2))
cg=scale(cross,s,s,origin=(0,0)); cg=translate(cg,cx,cy)
for g in (cg.geoms if hasattr(cg,'geoms') else [cg]):
    ax.add_patch(Polygon(list(g.exterior.coords),fc=PI,ec='#333',lw=0.5,zorder=3))
# highlights
def ell(mx,my,w,h,**k): ax.add_patch(Ellipse((cx+mx*s,cy+my*s),w*s,h*s,fc='none',ec=OR,ls='--',lw=1.8,zorder=8))
ell(0,0,4.6,4.6)            # centre junction -> C1
ell(0,5.8,2.6,9.6)          # stem -> R,L1
ell(0,10.6,10.8,4.8)        # T-bars -> L2,C2
ax.text(cx,cy+13.4*s+0.35,'Unit cell (25 × 25 mm)',ha='center',fontsize=11.5,fontweight='bold')
def arrow(p,q,rad):
    ax.annotate('',xy=q,xytext=p,arrowprops=dict(arrowstyle='-|>',color=OR,ls='--',lw=1.8,connectionstyle=f'arc3,rad={rad}',mutation_scale=16),zorder=9)
arrow((cx+2.3*s,cy-0.9*s),(xs[0]-0.3,YT-0.9),0.12)
arrow((cx+1.5*s,cy+8*s),(xs[1]-0.3,YT-0.9),-0.12)
arrow((cx+5.6*s,cy+10.6*s),(xs[2]-0.3,YT-0.9),-0.12)
# small region captions
ax.text(0.7,10.5,'centre junction + slot edges  →  $C_1$',fontsize=9.5,color=OR,fontweight='bold',ha='left')
ax.text(0.7,9.8,'stem / copper paths  →  $R$, $L_1$',fontsize=9.5,color=OR,fontweight='bold',ha='left')
ax.text(0.7,9.1,'loading T-bars (l1–l4)  →  $L_2$, $C_2$',fontsize=9.5,color=OR,fontweight='bold',ha='left')
ax.add_patch(Rectangle((33.0,19.2),1.2,0.7,fc=CU,ec='#555')); ax.text(34.6,19.55,'Copper',fontsize=11.5,va='center')
ax.add_patch(Rectangle((33.0,18.0),1.2,0.7,fc=PI,ec='#333')); ax.text(34.6,18.35,'Polyimide',fontsize=11.5,va='center')
ax.text(22.5,-5.6,'FIGURE.  The equivalent circuit of the proposed 2.45 GHz cross-slot FSS layer (circuit parameters:\n'
        '$L_1$ = 3.31 nH,  $R$ = 0.58 $\\Omega$,  $C_1$ = 0.567 pF,  $L_2$ = 0.44 nH,  $C_2$ = 0.66 pF).',
        ha='center',va='top',fontsize=14,fontweight='bold')
ax.set_xlim(-1.5,45.5); ax.set_ylim(-8.6,21.2)
fig.savefig(str(ROOT / "images" / "equivalent_circuit.png"),dpi=200,facecolor='white',bbox_inches='tight')
print('ok')
