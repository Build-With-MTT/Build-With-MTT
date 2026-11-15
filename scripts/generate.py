import json, os, html, shutil, math, random, sys, re
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
MODE = sys.argv[1] if len(sys.argv)>1 else 'anim'
TS = float(sys.argv[2]) if len(sys.argv)>2 else 0.0
STATIC = MODE=='static'
OUT = os.environ.get('SS_OUT') or ROOT
if STATIC and not os.environ.get('SS_OUT'): sys.exit('static mode needs SS_OUT')
os.makedirs(OUT+'/assets', exist_ok=True)
DATA=json.load(open(os.path.join(HERE,'data.json'),encoding='utf-8'))
AV=(DATA.get('avatar_b64') or open(os.path.join(HERE,'avatar.b64')).read()).strip()
AV_MIME=DATA.get('avatar_mime') or 'image/jpeg'
esc=lambda s: html.escape(str(s), quote=True)
clip=lambda s,n: s if len(s)<=n else s[:n-1]+'…'
MONO="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS="'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
LOGIN='Build-With-MTT'; NAME='Muhammad Talal Tariq'; GOLD='#fcd34d'
COL0={'Jupyter Notebook':'#f97316','TypeScript':'#3b82f6','Kotlin':'#a855f7','JavaScript':'#facc15','Dart':'#2dd4bf','Python':'#38bdf8','HTML':'#f97316','CSS':'#ec4899','Java':'#f59e0b','C++':'#60a5fa','C#':'#22c55e','Solidity':'#94a3b8'}
PALETTE=['#38bdf8','#f472b6','#a3e635','#fb923c','#c084fc','#34d399']
class _C(dict):
    def __missing__(self,k): return PALETTE[sum(map(ord,k))%len(PALETTE)]
COL=_C(COL0)
ABBR={'Dart':'D','JavaScript':'JS','TypeScript':'TS','Python':'Py','Kotlin':'K','Jupyter Notebook':'J','HTML':'H','CSS':'C','Java':'Jv','Solidity':'S','C++':'C+','C#':'C#'}
ICONS=json.load(open(os.path.join(HERE,'icons.json')))
def icon(name,x,y,size,fill): return f'<g transform="translate({x} {y}) scale({size/24:.3f})"><path d="{ICONS[name]}" fill="{fill}"/></g>'
def W(n,s): open(f'{OUT}/assets/{n}','w',encoding='utf-8').write(s)
f1=lambda v: f'{v:.1f}'
def stars(w,h,n,seed,twinkle=0):
    rnd=random.Random(seed); s=''
    for i in range(n):
        x=rnd.uniform(8,w-8); y=rnd.uniform(8,h-8); r=rnd.choice([.6,.8,1,1.3]); o=rnd.uniform(.25,.8)
        if (not STATIC) and i<twinkle:
            d=rnd.uniform(2,5); s+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" opacity="{o:.2f}"><animate attributeName="opacity" values="{o:.2f};{min(1,o+.5):.2f};{max(.1,o-.3):.2f};{o:.2f}" dur="{d:.1f}s" begin="-{rnd.uniform(0,d):.1f}s" repeatCount="indefinite"/></circle>'
        else:
            s+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" opacity="{o:.2f}"/>'
    return s
def avatar(cx,cy,r,ring=3.5,cid='av',pulse=False):
    anim='<animate attributeName="stroke-opacity" values=".7;1;.7" dur="4s" repeatCount="indefinite"/>' if (pulse and not STATIC) else ''
    return f'''<defs><clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath></defs>
<circle cx="{cx}" cy="{cy}" r="{r+ring+2}" fill="#0b0f1f" stroke="{GOLD}" stroke-width="{ring}">{anim}</circle>
<image href="data:{AV_MIME};base64,{AV}" x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" clip-path="url(#{cid})" preserveAspectRatio="xMidYMid slice"/>'''

# ================= HERO (3D orbits) =================
Wd,Ht=960,540; cx,cy=480,288; T=96
LANGS=[(n,int(p)) for n,p in DATA['languages']][:5]
while len(LANGS)<5: LANGS.append(('Other',0))
RANKMAP=[2,1,3,0,4]; RR=[125,185,245,305,365]; PP=[16,24,32,48,96]; TH=[0.9,3.8,2.6,5.5,1.2]
PL=[None]*5
for rank,(n,p) in enumerate(LANGS):
    idx=RANKMAP[rank]; PL[idx]=(n,p,RR[idx],PP[idx],'',TH[idx])
LANG_SUMMARY=', '.join(f'{n} {p}%' for n,p in LANGS if p)
phi0=math.radians(62); dphi=math.radians(8); rho0=math.radians(9)
tilt=lambda t: phi0+dphi*math.sin(2*math.pi*t/T)
roll=lambda t: rho0*math.sin(2*math.pi*t/T+1.2)
def pstate(i,t):
    n,p,R,P,ab,th0=PL[i]; th=th0+2*math.pi*t/P; ph=tilt(t); ro=roll(t)
    u=R*math.cos(th); v=R*math.sin(th)*math.cos(ph)
    x=u*math.cos(ro)-v*math.sin(ro); y=u*math.sin(ro)+v*math.cos(ro)
    z=math.sin(th)*math.sin(ph)
    return cx+x, cy+y, 1+0.34*z, z>=0
RADII=[15,18,26,17,14]; KIND={0:'saturn',1:'earth',2:'jupiter',3:'violet',4:'uranus'}
def S(p,r): return re.sub(r'-?\d*\.?\d+', lambda m: f'{float(m.group())*r:.1f}', p)
def texture(i):
    k=KIND[i]; r=RADII[i]
    def bands(cols,base):
        h=2*r/len(cols); return f'<rect x="{-r}" y="{-r}" width="{2*r}" height="{2*r}" fill="{base}"/>'+''.join(f'<rect x="{-r}" y="{-r+j*h:.2f}" width="{2*r}" height="{h+.5:.2f}" fill="{c}"/>' for j,c in enumerate(cols))
    if k=='jupiter':
        return bands(['#d9b48a','#a8643a','#ecd3ae','#b9774a','#f2e1c4','#9a5a36','#e0bf94','#b56d43','#d9b48a'],'#d9b48a')+f'<ellipse cx="{.38*r:.1f}" cy="{.32*r:.1f}" rx="{.3*r:.1f}" ry="{.16*r:.1f}" fill="#b2452a"/><ellipse cx="{.38*r:.1f}" cy="{.32*r:.1f}" rx="{.17*r:.1f}" ry="{.08*r:.1f}" fill="#d9775a" opacity=".75"/>'
    if k=='violet': return bands(['#7d52d4','#5c32a8','#9a74ea','#6b3fbf','#4f2a96','#8d63e0','#6b3fbf'],'#6b3fbf')
    if k=='saturn': return bands(['#d4b25f','#efd993','#dcbd6c','#c9a74f','#ecd18a'],'#e6c878')
    if k=='uranus': return bands(['#86e3ea','#a7eef2','#79d8e0','#9aeaf0'],'#86e3ea')
    s=f'<rect x="{-r}" y="{-r}" width="{2*r}" height="{2*r}" fill="#1b57b0"/>'
    conts=['M-.62 -.42 C-.4 -.7 -.05 -.6 .02 -.34 C-.08 -.12 -.3 -.02 -.5 -.08 C-.66 -.18 -.7 -.3 -.62 -.42Z','M.18 -.1 C.42 -.3 .72 -.15 .66 .1 C.6 .32 .34 .42 .22 .3 C.12 .2 .1 0 .18 -.1Z','M-.3 .38 C-.1 .3 .08 .45 0 .62 C-.12 .75 -.34 .66 -.3 .38Z']
    s+=''.join(f'<path d="{S(c,r)}" fill="#3f9150"/>' for c in conts)
    s+=f'<ellipse cx="0" cy="{-.92*r:.1f}" rx="{.5*r:.1f}" ry="{.16*r:.1f}" fill="#eef6ff" opacity=".9"/><ellipse cx="0" cy="{.95*r:.1f}" rx="{.45*r:.1f}" ry="{.14*r:.1f}" fill="#eef6ff" opacity=".85"/>'
    s+=''.join(f'<ellipse cx="{a*r:.1f}" cy="{b*r:.1f}" rx="{c*r:.1f}" ry="{d*r:.1f}" fill="#fff" opacity=".5"/>' for a,b,c,d in ((-.3,-.15,.4,.08),(.3,.25,.38,.07),(0,.55,.35,.06)))
    return s
def rings(i):
    k=KIND[i]; r=RADII[i]
    if k=='saturn':
        a,b=2.0*r,.52*r; a2,b2=1.55*r,.4*r
        back=f'<g transform="rotate(-18)"><ellipse rx="{a:.1f}" ry="{b:.1f}" fill="none" stroke="#cdb682" stroke-width="{.3*r:.1f}" opacity=".6"/><ellipse rx="{a2:.1f}" ry="{b2:.1f}" fill="none" stroke="#8f7d54" stroke-width="{.1*r:.1f}" opacity=".7"/></g>'
        front=f'<g transform="rotate(-18)"><path d="M{-a:.1f} 0 A{a:.1f} {b:.1f} 0 0 0 {a:.1f} 0" fill="none" stroke="#e0cd9b" stroke-width="{.3*r:.1f}" opacity=".9"/><path d="M{-a2:.1f} 0 A{a2:.1f} {b2:.1f} 0 0 0 {a2:.1f} 0" fill="none" stroke="#8f7d54" stroke-width="{.1*r:.1f}" opacity=".85"/></g>'
        return back,front
    if k=='uranus': return f'<g transform="rotate(75)"><ellipse rx="{1.7*r:.1f}" ry="{.3*r:.1f}" fill="none" stroke="#c8f1f5" stroke-width="{.07*r:.1f}" opacity=".55"/></g>',''
    return '',''
def planet_svg(i,shade_wrap):
    r=RADII[i]; back,front=rings(i)
    return back+f'<g clip-path="url(#pc{i})">{texture(i)}</g>'+shade_wrap(f'<circle r="{r}" fill="url(#shade)"/>')+f'<circle r="{r}" fill="none" stroke="#ffffff" stroke-opacity=".14"/>'+front
sun_angle=lambda x,y: math.degrees(math.atan2(cy-y,cx-x))+135
def moon_dot(i):
    r=RADII[i]
    if STATIC: return f'<circle cx="{r+9}" cy="-5" r="2.2" fill="#cbd5e1"/>'
    mr=r*1.6+6; return f'<circle r="2.2" fill="#cbd5e1"><animateMotion dur="{4+i}s" repeatCount="indefinite" path="M {mr:.1f} 0 A {mr:.1f} {mr*0.45:.1f} 0 1 1 {-mr:.1f} 0 A {mr:.1f} {mr*0.45:.1f} 0 1 1 {mr:.1f} 0"/></circle>'
def planet_group(i,front):
    n,p,R,P,ab,th0=PL[i]; r=RADII[i]
    label=f'<text x="0" y="{r*1.1+22:.0f}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="#e2e8f0">{n} {p}%</text>'
    if STATIC:
        x,y,s,fr=pstate(i,TS)
        if fr!=front: return ''
        body=planet_svg(i,lambda inner: f'<g transform="rotate({sun_angle(x,y):.1f})">{inner}</g>')
        return f'<g transform="translate({f1(x)},{f1(y)})"><g transform="scale({s:.3f})">{body}{moon_dot(i)}</g>{label}</g>'
    N=30*(T//P); xs=[];ss=[];op=[];kt=[];ang=[];prev=None
    for k in range(N+1):
        x,y,s,fr=pstate(i,k*T/N); xs.append(f'{x:.1f},{y:.1f}'); ss.append(f'{s:.3f}'); op.append('1' if fr==front else '0'); kt.append(f'{k/N:.4f}')
        a=sun_angle(x,y)
        if prev is not None:
            while a-prev>180: a-=360
            while a-prev<-180: a+=360
        prev=a; ang.append(f'{a:.1f}')
    kts=';'.join(kt)
    body=planet_svg(i,lambda inner: f'<g><animateTransform attributeName="transform" type="rotate" values="{";".join(ang)}" dur="{T}s" repeatCount="indefinite"/>{inner}</g>')
    return (f'<g opacity="{op[0]}"><animate attributeName="opacity" calcMode="discrete" values="{";".join(op)}" keyTimes="{kts}" dur="{T}s" repeatCount="indefinite"/>'
            f'<g><animateTransform attributeName="transform" type="translate" values="{";".join(xs)}" dur="{T}s" repeatCount="indefinite"/>'
            f'<g><animateTransform attributeName="transform" type="scale" values="{";".join(ss)}" dur="{T}s" repeatCount="indefinite"/>{body}{moon_dot(i)}</g>{label}</g></g>')
orb=''
for i,(n,p,R,P,ab,th0) in enumerate(PL):
    if STATIC:
        ry=R*math.cos(tilt(TS)); ro=math.degrees(roll(TS))
        orb+=f'<g transform="rotate({ro:.2f} {cx} {cy})"><ellipse cx="{cx}" cy="{cy}" rx="{R}" ry="{ry:.1f}" fill="none" stroke="#9fb0d6" stroke-opacity=".22" stroke-dasharray="3 5"/></g>'
    else:
        M=48; ts=[k*T/M for k in range(M+1)]
        rys=';'.join(f'{R*math.cos(tilt(t)):.1f}' for t in ts); ros=';'.join(f'{math.degrees(roll(t)):.2f} {cx} {cy}' for t in ts)
        orb+=(f'<g><animateTransform attributeName="transform" type="rotate" values="{ros}" dur="{T}s" repeatCount="indefinite"/>'
              f'<ellipse cx="{cx}" cy="{cy}" rx="{R}" ry="{R*math.cos(phi0):.1f}" fill="none" stroke="#9fb0d6" stroke-opacity=".22" stroke-dasharray="3 5"><animate attributeName="ry" values="{rys}" dur="{T}s" repeatCount="indefinite"/></ellipse></g>')
CG=[(60,150,300,236,0),(330,92,640,150,7),(520,505,790,432,13)]
cn=(DATA.get('comets') or [])[:3]
comets=[(cn[i],)+CG[i] for i in range(len(cn))]
cm=''
for n,x0,y0,x1,y1,b in comets:
    body=f'<line x1="-72" y1="-10" x2="0" y2="0" stroke="url(#tail)" stroke-width="2" stroke-linecap="round"/><circle r="3.4" fill="#fff"/><text x="10" y="-8" font-family="{MONO}" font-size="11.5" fill="#e2e8f0">{n}</text>'
    if STATIC:
        tt=((TS+b)%22)/22; cm+=f'<g transform="translate({f1(x0+(x1-x0)*tt)},{f1(y0+(y1-y0)*tt)})">{body}</g>'
    else:
        cm+=f'<g opacity="0">{body}<animateMotion dur="22s" begin="-{b}s" repeatCount="indefinite" path="M {x0} {y0} L {x1} {y1}"/><animate attributeName="opacity" dur="22s" begin="-{b}s" repeatCount="indefinite" values="0;1;1;0" keyTimes="0;.12;.8;1"/></g>'
# sun: glow pulses high <-> low
if STATIC:
    ph=(1+math.cos(2*math.pi*TS/4+math.pi))/2   # 0 at t=0 (low), 1 at t=2 (high)
    gr=88+30*ph; go=.35+.65*ph
    sun_glow=f'<circle cx="{cx}" cy="{cy}" r="{gr:.0f}" fill="url(#glow)" opacity="{go:.2f}"/><circle cx="{cx}" cy="{cy}" r="{50+34*ph:.0f}" fill="none" stroke="{GOLD}" stroke-opacity="{.5*(1-ph):.2f}" stroke-width="2"/>'
    rays=''.join(f'<path d="M{cx} {cy-52} L{cx-5} {cy-120} L{cx+5} {cy-120}Z" fill="{GOLD}" opacity=".13" transform="rotate({a+TS*9} {cx} {cy})"/>' for a in range(0,360,30))
    spark=''
else:
    sun_glow=(f'<circle cx="{cx}" cy="{cy}" r="88" fill="url(#glow)" opacity=".35"><animate attributeName="r" values="88;120;88" keyTimes="0;.5;1" calcMode="spline" keySplines=".4 0 .6 1;.4 0 .6 1" dur="4s" repeatCount="indefinite"/><animate attributeName="opacity" values=".35;1;.35" keyTimes="0;.5;1" calcMode="spline" keySplines=".4 0 .6 1;.4 0 .6 1" dur="4s" repeatCount="indefinite"/></circle>'
              f'<circle cx="{cx}" cy="{cy}" r="50" fill="none" stroke="{GOLD}" stroke-width="2" stroke-opacity=".5"><animate attributeName="r" values="50;86" dur="4s" repeatCount="indefinite"/><animate attributeName="stroke-opacity" values=".5;0" dur="4s" repeatCount="indefinite"/></circle>')
    rays=f'<g><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="40s" repeatCount="indefinite"/>'+''.join(f'<path d="M{cx} {cy-52} L{cx-5} {cy-120} L{cx+5} {cy-120}Z" fill="{GOLD}" opacity=".13" transform="rotate({a} {cx} {cy})"><animate attributeName="opacity" values=".06;.22;.06" dur="4s" repeatCount="indefinite"/></path>' for a in range(0,360,30))+'</g>'
    spark=''.join(f'<path d="M{cx+dx} {cy+dy-9} L{cx+dx+2} {cy+dy-2} L{cx+dx+9} {cy+dy} L{cx+dx+2} {cy+dy+2} L{cx+dx} {cy+dy+9} L{cx+dx-2} {cy+dy+2} L{cx+dx-9} {cy+dy} L{cx+dx-2} {cy+dy-2}Z" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1;0" dur="4s" begin="{b}s" repeatCount="indefinite"/></path>' for dx,dy,b in ((-34,-34,0),(36,-28,1.3),(-30,34,2.6),(38,32,0.7)))
sun_core=avatar(cx,cy,40,3.5,'avh',pulse=True)
rb=random.Random(5); dots=''
for _ in range(170):
    a=rb.uniform(0,6.283); rr=275+rb.uniform(-11,11); d=rb.choice(['#8b8478','#a89f91','#6e6a62','#c4b8a4','#7a7366'])
    dots+=f'<circle cx="{rr*math.cos(a):.1f}" cy="{rr*math.sin(a):.1f}" r="{rb.uniform(.6,1.7):.1f}" fill="{d}" opacity="{rb.uniform(.5,.95):.2f}"/>'
if STATIC:
    belt=f'<g transform="translate({cx} {cy}) rotate({math.degrees(roll(TS)):.2f}) scale(1 {math.cos(tilt(TS)):.3f}) rotate({TS*360/150:.1f})">{dots}</g>'
else:
    Mq=48; tsq=[k*T/Mq for k in range(Mq+1)]
    ros=';'.join(f'{math.degrees(roll(t)):.2f}' for t in tsq); scs=';'.join(f'1 {math.cos(tilt(t)):.3f}' for t in tsq)
    belt=(f'<g transform="translate({cx} {cy})"><g><animateTransform attributeName="transform" type="rotate" values="{ros}" dur="{T}s" repeatCount="indefinite"/><g><animateTransform attributeName="transform" type="scale" values="{scs}" dur="{T}s" repeatCount="indefinite"/><g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="150s" repeatCount="indefinite"/>{dots}</g></g></g></g>')
rm=random.Random(9); mw=''
for _ in range(150):
    t_=rm.random(); x=t_*Wd+rm.gauss(0,20); y=430-t_*300+rm.gauss(0,48)
    if 6<x<Wd-6 and 6<y<Ht-6: mw+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rm.choice([.5,.7,.9])}" fill="#cbd5ff" opacity="{rm.uniform(.2,.65):.2f}"/>'
back=''.join(planet_group(i,False) for i in range(5)); front=''.join(planet_group(i,True) for i in range(5))
clips=''.join(f'<clipPath id="pc{i}"><circle r="{RADII[i]}"/></clipPath>' for i in range(5))
W('solar-system.svg',f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd} {Ht}" width="100%" role="img" aria-label="Animated 3D Solar System for @{LOGIN}: the sun is Muhammad Talal Tariq; planets orbit as languages ({LANG_SUMMARY}); comets are recent pushes.">
<defs><radialGradient id="glow"><stop offset="0" stop-color="#fcd34d" stop-opacity=".6"/><stop offset=".5" stop-color="#f59e0b" stop-opacity=".2"/><stop offset="1" stop-color="#f59e0b" stop-opacity="0"/></radialGradient>
<radialGradient id="corona"><stop offset="0" stop-color="#ffd36b" stop-opacity=".55"/><stop offset=".35" stop-color="#ff9a2e" stop-opacity=".16"/><stop offset="1" stop-color="#ff7a00" stop-opacity="0"/></radialGradient>
<radialGradient id="shade" cx=".32" cy=".32" r=".85"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset=".5" stop-color="#000" stop-opacity=".12"/><stop offset="1" stop-color="#000" stop-opacity=".8"/></radialGradient>
<radialGradient id="neb1"><stop offset="0" stop-color="#5b3fd0" stop-opacity=".28"/><stop offset="1" stop-color="#5b3fd0" stop-opacity="0"/></radialGradient>
<radialGradient id="neb2"><stop offset="0" stop-color="#1e6fd9" stop-opacity=".22"/><stop offset="1" stop-color="#1e6fd9" stop-opacity="0"/></radialGradient>
<radialGradient id="neb3"><stop offset="0" stop-color="#c2410c" stop-opacity=".16"/><stop offset="1" stop-color="#c2410c" stop-opacity="0"/></radialGradient>
<linearGradient id="milky" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#9db4ff" stop-opacity="0"/><stop offset=".5" stop-color="#9db4ff" stop-opacity=".09"/><stop offset="1" stop-color="#9db4ff" stop-opacity="0"/></linearGradient>
<linearGradient id="tail" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity=".9"/></linearGradient>{clips}</defs>
<rect x="1" y="1" width="{Wd-2}" height="{Ht-2}" rx="18" fill="#04060f" stroke="#1b2236" stroke-width="1.5"/>
<ellipse cx="170" cy="150" rx="330" ry="190" fill="url(#neb1)"/><ellipse cx="800" cy="430" rx="340" ry="200" fill="url(#neb2)"/><ellipse cx="860" cy="120" rx="240" ry="140" fill="url(#neb3)"/>
<rect x="-80" y="200" width="1120" height="120" fill="url(#milky)" transform="rotate(-17 480 260)"/>{mw}
{stars(Wd,Ht,110,7,40)}
<text x="32" y="44" font-family="{MONO}" font-size="14" letter-spacing="3" fill="#e2e8f0">SOLAR SYSTEM · @{LOGIN.upper()}</text>
{orb}{belt}{cm}<circle cx="{cx}" cy="{cy}" r="175" fill="url(#corona)"/>{rays}{back}{sun_glow}{sun_core}{spark}{front}
<text x="32" y="516" font-family="{MONO}" font-size="11" font-weight="700" fill="#64748b">{LOGIN.lower()}</text>
<text x="928" y="516" text-anchor="end" font-family="{MONO}" font-size="11.5" fill="#94a3b8">planets = languages · asteroid belt · comets = recent pushes</text>
</svg>''')

# ================= CARDS =================
def card(w,h,body,seed,tw=0):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%">
<defs><radialGradient id="shade" cx=".32" cy=".32" r=".85"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset=".5" stop-color="#000" stop-opacity=".12"/><stop offset="1" stop-color="#000" stop-opacity=".7"/></radialGradient><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1330"/><stop offset="1" stop-color="#070a18"/></linearGradient></defs>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="16" fill="url(#bg)" stroke="#1b2236" stroke-width="1.5"/>
{stars(w,h,max(10,w*h//9000),seed,tw)}{body}</svg>'''
lab=lambda x,y,t: f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="3" fill="{GOLD}">{t}</text>'
W('sun.svg',card(960,176,f'''{lab(32,40,'THE SUN')}
<text x="32" y="84" font-family="{SANS}" font-size="30" font-weight="800" fill="#f8fafc">{NAME}</text>
<text x="32" y="112" font-family="{SANS}" font-size="14.5" fill="#cbd5e1">CS student building full-stack, Flutter and blockchain apps.</text>
<text x="32" y="134" font-family="{SANS}" font-size="14.5" fill="#cbd5e1">Founder of MTT Digital Studio. Working on Web3 and AI projects right now.</text>
<text x="32" y="158" font-family="{MONO}" font-size="11" fill="#64748b">MTT DIGITAL STUDIO · {DATA['followers']} followers · {DATA['repo_count']} repositories · ★ {DATA['stars']} stars</text>
<circle cx="868" cy="88" r="62" fill="url(#glow2)"><animate attributeName="opacity" values=".4;1;.4" dur="4s" repeatCount="indefinite"/></circle>
{avatar(868,88,50,4,'avs',pulse=True)}<defs><radialGradient id="glow2"><stop offset="0" stop-color="#fcd34d" stop-opacity=".45"/><stop offset="1" stop-color="#fcd34d" stop-opacity="0"/></radialGradient></defs>''',11,12))
FEATURED=[('zehn-ai','Bilingual AI assistant for Pakistani students.'),
 ('web3-realestate-platform','Real estate investment platform with crypto payments.'),
 ('thokkhata','B2B wholesale ordering and retailer credit app.'),
 ('medichain','On-chain medicine supply chain with IoT logs.')]
moons=[]
for n,d in FEATURED:
    r=DATA.get('repos',{}).get(n,{}); l=r.get('language') or 'Code'
    moons.append((n,l,ABBR.get(l,l[:2]),d,r.get('stars',0),r.get('forks',0)))
for i,(n,l,ab,dsc,stc,frk) in enumerate(moons,1):
    col=COL[l]
    ring_anim='' if STATIC else f'<animateTransform attributeName="transform" type="rotate" values="-18 420 44;-8 420 44;-18 420 44" dur="6s" repeatCount="indefinite"/>'
    W(f'moon-0{i}.svg',card(468,170,f'''{lab(28,42,f'MOON 0{i}')}
<ellipse cx="420" cy="44" rx="30" ry="9" transform="rotate(-18 420 44)" fill="none" stroke="{col}" stroke-opacity=".7" stroke-width="1.5">{ring_anim.replace('<animateTransform','<animateTransform') if False else ''}</ellipse>
<circle cx="420" cy="44" r="16" fill="{col}"/><circle cx="420" cy="44" r="16" fill="url(#shade)"/><text x="420" y="49.5" text-anchor="middle" font-family="{SANS}" font-size="14" font-weight="800" fill="#0b0f1f">{ab}</text>
<text x="28" y="92" font-family="{MONO}" font-size="18" font-weight="700" fill="#f8fafc">{esc(clip(n,28))}</text>
<text x="28" y="118" font-family="{SANS}" font-size="13" fill="#cbd5e1">{esc(clip(dsc,58))}</text>
<text x="28" y="150" font-family="{MONO}" font-size="11.5" fill="#94a3b8">★ {stc}   ⑂ {frk}</text><circle cx="112" cy="146" r="5" fill="{col}"/><text x="124" y="150" font-family="{MONO}" font-size="11.5" fill="#94a3b8">{l}</text>''',20+i,4))
MICRO=[('#e0bf94','#a8643a'),('#4f8fe0','#16418a'),('#9a74ea','#4f2a96'),('#efd993','#b9962f'),('#a7eef2','#3fb8c4')]
MICRODEFS=''.join(f'<radialGradient id="mp{k}" cx=".32" cy=".3" r=".8"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></radialGradient>' for k,(a,b) in enumerate(MICRO))
def micro(k,y):
    ring='<ellipse cx="39" cy="%d" rx="14" ry="4" fill="none" stroke="#e0cd9b" stroke-width="1.6" transform="rotate(-18 39 %d)"/>'%(y-1,y-1) if k==3 else ''
    return f'<circle cx="39" cy="{y-1}" r="9" fill="url(#mp{k})"/>{ring}'
rows=''
for i,(n,p) in enumerate(LANGS):
    y=78+i*36; col=COL[n]
    bar=f'<rect x="250" y="{y-6}" width="{max(18,630*p/100)}" height="10" rx="5" fill="{col}">'+('' if STATIC else f'<animate attributeName="width" values="0;{max(18,630*p/100)}" dur="1.6s" fill="freeze" begin="{i*0.15}s"/>')+'</rect>'
    rows+=f'''{micro(i,y)}
<text x="60" y="{y+4}" font-family="{SANS}" font-size="13.5" font-weight="600" fill="#e2e8f0">{n}</text>
<rect x="250" y="{y-6}" width="630" height="10" rx="5" fill="#161b2e"/>{bar}
<text x="928" y="{y+4}" text-anchor="end" font-family="{MONO}" font-size="12" fill="#94a3b8">{p}%</text>'''
W('planets.svg',card(960,270,lab(32,40,'PLANETS')+MICRODEFS+rows,31,6))

# ================= ORBIT LOG + SNAKE =================
days=DATA['days']; last=days[-182:]
def heat(c): return '#111a33' if c<=0 else '#3730a3' if c<=2 else '#4f46e5' if c<=5 else '#6366f1' if c<=9 else '#a5b4fc'
latest=max((i for i,d in enumerate(last) if d['count']>0),default=-1)
cells=''
for i,d in enumerate(last):
    wk,dy=divmod(i,7); fill='#fcd34d' if i==latest else heat(d['count'])
    cells+=f'<rect x="{32+wk*23}" y="{66+dy*23}" width="18" height="18" rx="4" fill="{fill}"/>'
cur=0; seq=list(reversed(last))
if seq and seq[0]['count']==0: seq=seq[1:]
for d in seq:
    if d['count']>0: cur+=1
    else: break
lon=run=0
for d in days[-365:]:
    run=run+1 if d['count']>0 else 0; lon=max(lon,run)
# --- snake route (closed loop, food-seeking, avoids own body)
COLS,ROWS,L=26,7,7; rnd=random.Random(2026)
def bfs(a,b,blocked):
    from collections import deque
    q=deque([a]); prev={a:None}
    while q:
        c=q.popleft()
        if c==b: break
        nb=[(c[0]+1,c[1]),(c[0]-1,c[1]),(c[0],c[1]+1),(c[0],c[1]-1)]; rnd.shuffle(nb)
        for n in nb:
            if 0<=n[0]<COLS and 0<=n[1]<ROWS and n not in prev and n not in blocked:
                prev[n]=c; q.append(n)
    if b not in prev: return None
    path=[]; c=b
    while c!=a: path.append(c); c=prev[c]
    return path[::-1]
start=(3,3); route=[start]; foods=[]
cand=[(rnd.randrange(2,COLS-1),rnd.randrange(0,ROWS)) for _ in range(30)]
for f in cand:
    if len(foods)==7: break
    if f in foods or abs(f[0]-route[-1][0])+abs(f[1]-route[-1][1])<6: continue
    seg=bfs(route[-1],f,set(route[-(L-1):]))
    if seg: route+=seg; foods.append((f,len(route)-1))
seg=bfs(route[-1],start,set(route[-(L-1):]))
while seg is None:  # wander one step then retry
    c=route[-1]; opts=[(c[0]+dx,c[1]+dy) for dx,dy in((1,0),(-1,0),(0,1),(0,-1)) if 0<=c[0]+dx<COLS and 0<=c[1]+dy<ROWS and (c[0]+dx,c[1]+dy) not in route[-(L-1):]]
    route.append(rnd.choice(opts)); seg=bfs(route[-1],start,set(route[-(L-1):]))
route+=seg; route=route[:-1]; N=len(route)  # last cell adjacent to start
SPS=6; DUR=N/SPS
cx_=lambda c:32+c*23; cy_=lambda r:66+r*23
def segcol(j): return ['#fcd34d']+['#34d399']*0+[f'#34d399' for _ in range(L-1)] if False else None
snake=''; foodsvg=''
for (fc,idx) in foods:
    fx,fy=cx_(fc[0])+9,cy_(fc[1])+9
    if STATIC:
        k=int(TS*SPS)%N
        if idx>k or (k<idx): foodsvg+=f'<circle cx="{fx}" cy="{fy}" r="4.5" fill="#fcd34d"/>'
    else:
        t0=idx/N
        foodsvg+=f'<circle cx="{fx}" cy="{fy}" r="4.5" fill="#fcd34d"><animate attributeName="opacity" calcMode="discrete" values="1;0;1" keyTimes="0;{t0:.4f};{min(.9999,1-1/N):.4f}" dur="{DUR:.1f}s" repeatCount="indefinite"/><animate attributeName="r" values="3.5;5.5;3.5" dur="1.2s" repeatCount="indefinite"/></circle>'
for j in range(L-1,-1,-1):
    op=1-0.1*j; colr='#fcd34d' if j==0 else '#34d399'
    if STATIC:
        k=int(TS*SPS)%N; c=route[(k-j)%N]
        snake+=f'<rect x="{cx_(c[0])-1}" y="{cy_(c[1])-1}" width="20" height="20" rx="5" fill="{colr}" opacity="{op:.2f}"/>'
        if j==0: snake+=f'<circle cx="{cx_(c[0])+5}" cy="{cy_(c[1])+6}" r="2" fill="#0b0f1f"/><circle cx="{cx_(c[0])+13}" cy="{cy_(c[1])+6}" r="2" fill="#0b0f1f"/>'
    else:
        xs=';'.join(str(cx_(route[(k-j)%N][0])-1) for k in range(N+1)); ys=';'.join(str(cy_(route[(k-j)%N][1])-1) for k in range(N+1))
        snake+=f'<rect x="{cx_(route[(-j)%N][0])-1}" y="{cy_(route[(-j)%N][1])-1}" width="20" height="20" rx="5" fill="{colr}" opacity="{op:.2f}"><animate attributeName="x" values="{xs}" dur="{DUR:.1f}s" repeatCount="indefinite"/><animate attributeName="y" values="{ys}" dur="{DUR:.1f}s" repeatCount="indefinite"/></rect>'
        if j==0:
            for ex in (6,14):
                exs=';'.join(str(cx_(route[k%N][0])+ex-1) for k in range(N+1)); eys=';'.join(str(cy_(route[k%N][1])+5) for k in range(N+1))
                snake+=f'<circle r="2" fill="#0b0f1f" cx="{cx_(route[0][0])+ex}" cy="{cy_(route[0][1])+6}"><animate attributeName="cx" values="{exs}" dur="{DUR:.1f}s" repeatCount="indefinite"/><animate attributeName="cy" values="{eys}" dur="{DUR:.1f}s" repeatCount="indefinite"/></circle>'
stat=lambda y,k,v: f'<text x="668" y="{y}" font-family="{MONO}" font-size="10" letter-spacing="1" fill="#94a3b8">{k}</text><text x="668" y="{y+27}" font-family="{SANS}" font-size="23" font-weight="800" fill="#f8fafc">{v}</text>'
W('orbit-log.svg',card(960,244,lab(32,40,'ORBIT LOG · 26 WEEKS')+f'<text x="360" y="40" font-family="{MONO}" font-size="10.5" fill="#64748b">snake mode: eating stars in orbit</text>'+cells+foodsvg+snake+f'<line x1="636" y1="62" x2="636" y2="222" stroke="#1b2236"/>'+stat(84,'DAYS IN ORBIT',f'{cur} days')+stat(136,'LONGEST ORBIT',f'{lon} days')+stat(188,'REVOLUTIONS THIS YEAR',DATA['total_contributions']),41,5))

# ================= FOOTER (CTA, no chips) =================
def pill(x,y,text,col,delay):
    w=len(text)*8.0+44
    dot=f'<circle cx="{x+16}" cy="{y+13}" r="4" fill="{col}">'+('' if STATIC else f'<animate attributeName="opacity" values="1;.25;1" dur="1.6s" begin="{delay}s" repeatCount="indefinite"/>')+'</circle>'
    return f'<rect x="{x}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="#0d1330" stroke="{col}" stroke-opacity=".6"/>{dot}<text x="{x+28}" y="{y+17.5}" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1" fill="#e2e8f0">{text}</text>', w
p1,w1=pill(32,126,'OPEN TO PROJECTS','#34d399',0)
p2,w2=pill(32+w1+14,126,'OPEN TO COLLABORATION','#38bdf8',.8)
fx,fy=812,92
if STATIC:
    fo=[(70,26,'#a78bfa',5,.9),(105,38,'#fb923c',4,3.6),(140,50,'#2dd4bf',6,5.4)]
    pls=''.join(f'<circle cx="{rx*math.cos(a):.1f}" cy="{ry*math.sin(a):.1f}" r="{r}" fill="{c}"/>' for rx,ry,c,r,a in fo)
    anim_sun=''
else:
    pls=''.join(f'<circle r="{r}" fill="{c}"><animateMotion dur="{d}s" repeatCount="indefinite" path="M {rx} 0 A {rx} {ry} 0 1 1 {-rx} 0 A {rx} {ry} 0 1 1 {rx} 0"/></circle>' for rx,ry,c,r,d in ((70,26,'#a78bfa',5,7),(105,38,'#fb923c',4,12),(140,50,'#2dd4bf',6,19)))
glowanim='' if STATIC else '<animate attributeName="r" values="52;72;52" keyTimes="0;.5;1" calcMode="spline" keySplines=".4 0 .6 1;.4 0 .6 1" dur="4s" repeatCount="indefinite"/><animate attributeName="opacity" values=".45;1;.45" keyTimes="0;.5;1" calcMode="spline" keySplines=".4 0 .6 1;.4 0 .6 1" dur="4s" repeatCount="indefinite"/>'
orbs=''.join(f'<ellipse rx="{rx}" ry="{ry}" fill="none" stroke="#9fb0d6" stroke-opacity=".25" stroke-dasharray="3 4"/>' for rx,ry in ((70,26),(105,38),(140,50)))
W('footer.svg',card(960,176,f'''<defs><radialGradient id="glow2"><stop offset="0" stop-color="#fcd34d" stop-opacity=".6"/><stop offset=".5" stop-color="#f59e0b" stop-opacity=".2"/><stop offset="1" stop-color="#f59e0b" stop-opacity="0"/></radialGradient><radialGradient id="sunf" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#fff3b0"/><stop offset=".5" stop-color="#fcd34d"/><stop offset="1" stop-color="#f59e0b"/></radialGradient></defs>
{lab(32,40,'MISSION CONTROL · LET’S CONNECT')}
<text x="32" y="84" font-family="{SANS}" font-size="31" font-weight="800" fill="#f8fafc">Got a project? Let’s launch it.</text>
<text x="32" y="110" font-family="{SANS}" font-size="14" fill="#cbd5e1">MTT Digital Studio · full-stack apps, Flutter, Web3, branding and video editing.</text>
{p1}{p2}
<circle cx="{fx}" cy="{fy}" r="52" fill="url(#glow2)">{glowanim}</circle>
<g transform="translate({fx} {fy}) rotate(-12)">{orbs}{pls}</g>
<circle cx="{fx}" cy="{fy}" r="20" fill="url(#sunf)"/>''',51,10))
print('ok',MODE,TS,'route',N,'dur',round(DUR,1),'foods',len(foods))

BTN=[('fiverr','fiverr','Hire me on Fiverr','#1DBF73','#fff'),('linkedin','linkedin','LinkedIn','#0A66C2','#fff'),('instagram','instagram','Instagram','url(#ig)','#fff'),('behance','behance','Behance','#1769FF','#fff'),('gumroad','gumroad','Gumroad','#FF90E8','#111'),('discord','discord','Discord','#5865F2','#fff'),('email','email','Email','#EA4335','#fff')]
for key,ic,label,bg,fg in BTN:
    w=int(len(label)*8.8+68); P=10; tw=w+2*P
    W(f'btn-{key}.svg',f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="44" viewBox="0 0 {tw} 44" role="img" aria-label="{label}"><defs><linearGradient id="ig" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#feda75"/><stop offset=".35" stop-color="#fa7e1e"/><stop offset=".6" stop-color="#d62976"/><stop offset="1" stop-color="#4f5bd5"/></linearGradient></defs><rect x="{P+.5}" y=".5" width="{w-1}" height="43" rx="10" fill="{bg}" stroke="#ffffff" stroke-opacity=".2"/>{icon(ic,P+16,10,24,fg)}<text x="{P+50}" y="27.5" font-family="{SANS}" font-size="15" font-weight="700" fill="{fg}">{label}</text></svg>')

import textwrap
def wrap(t,n=62): return textwrap.wrap(t,n)
def hexicon(x,y,col,r=16):
    pts=' '.join(f'{x+r*math.cos(math.radians(60*k-30)):.1f},{y+r*math.sin(math.radians(60*k-30)):.1f}' for k in range(6))
    return f'<polygon points="{pts}" fill="none" stroke="{col}" stroke-width="2"/><polygon points="{" ".join(f"{x+r*.5*math.cos(math.radians(60*k-30)):.1f},{y+r*.5*math.sin(math.radians(60*k-30)):.1f}" for k in range(6))}" fill="{col}" opacity=".85"/>'
def bcard(label,title,sub,desc,chips,url,cta,col,h):
    lines=wrap(desc)
    body=lab(28,42,label)+hexicon(424,40,col)
    body+=f'<text x="28" y="82" font-family="{SANS}" font-size="17" font-weight="800" fill="#f8fafc">{esc(title)}</text>'
    if sub: body+=f'<text x="28" y="104" font-family="{SANS}" font-size="12.5" font-weight="600" fill="{col}">{esc(sub)}</text>'
    y0=132 if sub else 112
    for k,ln in enumerate(lines): body+=f'<text x="28" y="{y0+k*17}" font-family="{SANS}" font-size="12.5" fill="#cbd5e1">{esc(ln)}</text>'
    cy0=y0+len(lines)*17+4; x=28
    for c in chips:
        w=len(c)*6.9+18; body+=f'<rect x="{x:.0f}" y="{cy0}" width="{w:.0f}" height="22" rx="11" fill="#0d1330" stroke="{col}" stroke-opacity=".55"/><text x="{x+w/2:.0f}" y="{cy0+15}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="#e2e8f0">{esc(c)}</text>'; x+=w+8
    by=h-44
    cw=len(cta)*7.4+34
    body+=f'<text x="28" y="{by+17}" font-family="{MONO}" font-size="10" fill="#64748b">{esc(clip(url,int((440-cw-28-14)/6.1)))}</text>'
    live = cta.startswith('Open')
    body+=f'<rect x="{440-cw:.0f}" y="{by}" width="{cw:.0f}" height="26" rx="13" fill="{"#16a34a" if live else col}"/>'
    if live: body+=f'<circle cx="{440-cw+14:.0f}" cy="{by+13}" r="3.5" fill="#bbf7d0">'+('' if STATIC else '<animate attributeName="opacity" values="1;.3;1" dur="1.5s" repeatCount="indefinite"/>')+'</circle>'
    body+=f'<text x="{440-cw/2+(6 if live else 0):.0f}" y="{by+17.5}" text-anchor="middle" font-family="{SANS}" font-size="12" font-weight="700" fill="{"#fff" if live else "#0b0f1f"}">{esc(cta)}</text>'
    return body
def hlines(desc): return len(wrap(desc))
def H(desc,sub): return (132 if sub else 112)+hlines(desc)*17+4+22+20+44
REPOS=[('REPO 01 · BLOCKCHAIN','MediChain','On-chain medicine supply chain',"Every medicine batch is registered on-chain by the manufacturer. Each handoff, from manufacturer to distributor to pharmacy, is a signed on-chain transaction. IoT temperature sensors log cold-chain data on-chain. The patient scans the medicine's QR code and sees the verified chain of custody and temperature log.",['On-chain','IoT','Cold-chain','QR verify'],'github.com/Build-With-MTT/medichain','View repo on GitHub','#2dd4bf'),
 ('REPO 02 · BLOCKCHAIN','web3-realestate-platform','Real estate investment platform',"A full-stack real estate investment platform (React + Node.js) with crypto payment integration and interactive 3D property visualization.",['React','Node.js','Crypto pay','3D view'],'github.com/Build-With-MTT/web3-realestate-platform','View repo on GitHub','#facc15')]
LIVE=[('LIVE 01 · DAPP','University Complaint Management System','Blockchain-Verified Complaint Tracking',"A full-stack decentralized complaint management platform built for Air University. Every complaint, from submission to resolution, is permanently recorded on-chain via a Solidity smart contract on the Ethereum Sepolia testnet. No complaint can be silently deleted, edited or lost in email threads: the whole lifecycle is transparent and tamper-proof.",['Solidity','Sepolia','Air University'],'airu-cms-235154-muhammad-talal-tariq.netlify.app','Open live demo','#38bdf8'),
 ('LIVE 02 · DAPP','SkillBridge','Blockchain-Powered University Skill Marketplace',"A full-stack decentralized freelancing platform built for university students to buy and sell skill-based services using Ethereum smart contracts: no middlemen, no payment disputes, no trust issues. Every transaction, review and payout is handled transparently on-chain via a Solidity smart contract deployed on the Sepolia testnet.",['Solidity','Sepolia','Marketplace'],'skill-bridge-marketplace-for-students.netlify.app','Open live demo','#a855f7'),
 ('LIVE 03 · DAPP','PakVote','Blockchain-Based Election Simulation for Pakistan',"A full-stack decentralized application that simulates Pakistan's national election system on the blockchain, to show how transparent, tamper-proof digital voting could work at national scale. Every vote is an immutable on-chain transaction via a Solidity smart contract on Sepolia, with an interactive Three.js and GSAP frontend.",['Solidity','Three.js','GSAP','Sepolia'],'pakvote-muhammad-talal-tariq-235154.netlify.app','Open live demo','#22c55e'),
 ('LIVE 04 · DAPP','Crowdfunding DApp','Trustless, Vote-Governed Crowdfunding Smart Contract',"A full-stack crowdfunding platform where campaign funds are never fully controlled by one person. Every spending request must be voted on and approved by the contributors themselves. Built with a Solidity smart contract and a Web3.js frontend, deployed on the Ethereum network.",['Solidity','Web3.js','Ethereum'],'talaldapp235154.netlify.app','Open live demo','#f97316')]
hr=max(H(r[3],r[2]) for r in REPOS); hl1=max(H(l[3],l[2]) for l in LIVE[:2]); hl2=max(H(l[3],l[2]) for l in LIVE[2:])
for i,r in enumerate(REPOS,1): W(f'chain-repo-0{i}.svg',card(468,hr,bcard(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],hr),60+i,6))
for i,l in enumerate(LIVE,1):
    h=hl1 if i<=2 else hl2; W(f'chain-live-0{i}.svg',card(468,h,bcard(l[0],l[1],l[2],l[3],l[4],l[5],l[6],l[7],h),70+i,6))
# animated header: a chain of blocks with a data packet
hdr=lab(32,40,'BLOCKCHAIN LAB')+f'<text x="32" y="84" font-family="{SANS}" font-size="30" font-weight="800" fill="#f8fafc">Smart contracts, shipped live.</text><text x="32" y="110" font-family="{SANS}" font-size="14" fill="#cbd5e1">Solidity · Ethereum Sepolia · Web3.js · ethers.js · React. Every record on-chain, every demo one click away.</text>'
rh=random.Random(3); bx=[32+k*134 for k in range(7)]; chain=''
for k,x in enumerate(bx):
    hx='0x'+''.join(rh.choice('0123456789abcdef') for _ in range(4))
    if k<6: chain+=f'<line x1="{x+108}" y1="152" x2="{x+134}" y2="152" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="4 3" opacity=".7"/>'
    anim='' if STATIC else f'<animate attributeName="stroke-opacity" values=".35;1;.35" dur="4.2s" begin="{k*0.6:.1f}s" repeatCount="indefinite"/>'
    chain+=f'<rect x="{x}" y="132" width="108" height="40" rx="8" fill="#0d1330" stroke="#2dd4bf" stroke-width="1.6" stroke-opacity=".6">{anim}</rect><text x="{x+10}" y="148" font-family="{MONO}" font-size="9.5" fill="#64748b">BLOCK {k+1}</text><text x="{x+10}" y="163" font-family="{MONO}" font-size="12" font-weight="700" fill="#5eead4">{hx}…</text>'
if STATIC: pk='<circle cx="500" cy="152" r="6" fill="#fcd34d"/>'
else: pk=f'<circle r="6" fill="#fcd34d"><animateMotion dur="8s" repeatCount="indefinite" path="M 32 152 L 928 152"/></circle><circle r="12" fill="#fcd34d" opacity=".25"><animateMotion dur="8s" repeatCount="indefinite" path="M 32 152 L 928 152"/></circle>'
W('chain-header.svg',card(960,196,hdr+chain+pk,81,14))
