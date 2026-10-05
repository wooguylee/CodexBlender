"""사용자가 승인한 다섯 코미디의 소품, 연기, 사건 타이밍. 모든 동작은 키프레임으로 저장한다."""
import math
from mathutils import Vector, Matrix
from production import KEYS, smooth, pulse, lerp, rgb

EPISODES = [
    {'id':1,'slug':'01-photo-chaos','title':'단체사진 대소동','duration':24,
     'beats':[1,5,9,12,16,18,22], 'sfx':[(3,'ding'),(8,'tick'),(9,'tick'),(10,'whoosh'),(13,'boing'),(16,'camera'),(21,'ding')],
     'captions':[(0,3,'단체사진 대소동'),(4,7,'몽실은 졸고… 또르는 숨고…'),(8,10,'하나, 둘…'),(11,15,'솔솔아! 살살 불어!'),(16,20,'찰칵!'),(20,24,'이 사진이 제일 마음에 들어!')]},
    {'id':2,'slug':'02-star-pillow','title':'몽실의 별 쿠션을 잡아라','duration':30,
     'beats':[2,5,9,15,19,24,28], 'sfx':[(4,'sneeze'),(5,'whoosh'),(9,'boing'),(13,'ice'),(16,'slide'),(20,'pop'),(25,'ding')],
     'captions':[(0,3,'몽실의 별 쿠션을 잡아라'),(4,7,'에… 에취!'),(8,12,'해롱! 조금만 더 높이!'),(13,18,'얼음길은 너무 미끄러워!'),(19,23,'별 쿠션, 돌아오는 중…'),(25,30,'몽실은 아무것도 몰랐대요.')]},
    {'id':3,'slug':'03-little-flower','title':'꽃 한 송이 키우기','duration':32,
     'beats':[2,7,12,17,23,27,30], 'sfx':[(3,'ding'),(7,'heat'),(11,'rain'),(16,'ice'),(23,'ding'),(27,'sneeze'),(28,'pop')],
     'captions':[(0,3,'꽃 한 송이 키우기'),(5,9,'햇살이 너무 뜨거워!'),(10,14,'물도 너무 많아!'),(15,19,'앗, 얼어 버렸어!'),(20,25,'이번에는 조금씩, 함께!'),(26,29,'꽃도 재채기를 한다고?'),(29,32,'오늘의 색깔은… 꽃가루 노랑!')]},
    {'id':4,'slug':'04-weather-report','title':'오늘의 날씨는 누구?','duration':28,
     'beats':[2,8,14,20,24,26], 'sfx':[(1,'ding'),(6,'rain'),(12,'ice'),(18,'whoosh'),(22,'boing'),(25,'snore')],
     'captions':[(0,3,'오늘의 날씨는 누구?'),(3,6,'오늘은 맑음입니다!'),(6,11,'잠깐, 비 소식도 있어요!'),(12,17,'눈 소식이 먼저야!'),(18,22,'이번엔 바람 차례!'),(24,28,'오늘은 낮잠 자기 좋은 날')]},
    {'id':5,'slug':'05-bubble-hats','title':'절대 터뜨리면 안 돼!','duration':26,
     'beats':[2,6,11,16,19,21,24], 'sfx':[(3,'bubble'),(7,'whoosh'),(12,'tick'),(18,'snore'),(20,'pop'),(23,'ding')],
     'captions':[(0,3,'절대 터뜨리면 안 돼!'),(4,8,'솔솔아, 아주 살살!'),(9,13,'송송아, 뾰족한 곳 조심!'),(14,17,'휴… 이제 안전해.'),(18,20,'몽실아, 그건 쿠션이…'),(21,26,'모자가 다섯 개 생겼네!')]},
]


def hidden(p,obj):
    p.move(obj,scale=.0001)


def weather(p,prefix,count,kind):
    return [p.ball(prefix+str(i),(0,0,0),(.04,.04,.13) if kind=='rain' else (.065,)*3,
                   'blue' if kind=='rain' else 'white',segments=12) for i in range(count)]


def rain_at(p,particles,t,active,span=5,center=0,snow=False,strength=1):
    for i,obj in enumerate(particles):
        if not active:
            hidden(p,obj);continue
        phase=(t*(.45 if snow else 1.30)+i*.173)%1
        x=center+span*math.sin(i*8.12)*.5+(.2*math.sin(t*2+i) if snow else .12*phase)
        z=5.6-phase*5.0
        p.move(obj,(x,-.25+.13*math.sin(i),z),rotation=(0,.17 if not snow else t+i,0),
               scale=((.060,)*3 if snow else (.025,.025,.15)))


def gusts(p):
    return [p.curve('Gust_'+str(i),[(-1,0,0),(-.35,0,.12),(.3,0,-.12),(1.0,0,.05),(1.3,0,.24)],.027,'mint') for i in range(4)]


def show_gust(p,objects,t,start,end,strength=1):
    for i,obj in enumerate(objects):
        if start<=t<=end:
            u=((t-start)*.65+i*.27)%1
            p.move(obj,(-7+14*u,-.5,1.35+i*.64),scale=(strength,.7,strength))
        else:hidden(p,obj)


def idle(p,t,positions=None):
    if positions is None:positions=[(i-2)*2.8 for i in range(5)]
    for i,(key,x) in enumerate(zip(KEYS,positions)):
        bob=.024*math.sin(t*2.3+i)
        if key=='Mongsil':bob=.055*math.sin(t*1.25)
        p.pose(key,x,z=max(0,bob),lean=.015*math.sin(t*1.6+i),arms=(.025*math.sin(t*2+i),-.025*math.sin(t*2+i)))
        close=1-.95*pulse((t+i*.47)%3.8,3.55,.07)
        p.blink(key,close)


def make_bubble(p,name):
    if 'bubble_blue' not in p.materials:
        p.material('bubble_blue','409CBF',emission=True)
        p.material('bubble_pink','D391C1',emission=True)
    root=p.empty(name)
    pieces=[]
    for j,(r,mat,thickness) in enumerate([(1,'bubble_blue',.030),(.973,'bubble_pink',.017),(1.023,'white',.011)]):
        points=[(r*math.cos(i*math.tau/64),0,r*math.sin(i*math.tau/64)) for i in range(65)]
        obj=p.curve(name+'_Rim'+str(j),points,thickness,mat)
        obj.parent=root;pieces.append(obj)
    for j,(a,b,r) in enumerate([(1.70,2.55,.87),(.1,.55,.92)]):
        points=[(r*math.cos(a+(b-a)*i/12),-.015,r*math.sin(a+(b-a)*i/12)) for i in range(13)]
        obj=p.curve(name+'_Highlight'+str(j),points,.040 if j==0 else .019,'white')
        obj.parent=root;pieces.append(obj)
    root.rotation_euler.x=-.278
    return root


def prepare(p,episode):
    n=episode['id'];props={}
    if n in (1,2,4,5):props['gusts']=gusts(p)
    if n in (1,2,4):
        props['zzz']=[p.text('Zzz'+str(i),'z',(-5.5+i*.30,-.1,3.65+i*.3),.28+i*.08,'purple') for i in range(3)]
    if n==1:
        props['camera']=p.cube('PhotoCamera',(-6.7,-1.2,1.12),(.62,.33,.46),'purple',.07)
        props['lens']=p.ball('CameraLens',(-6.7,-1.42,1.14),(.16,.08,.16),'dark')
        for i,x in enumerate((-.28,.28)):
            p.curve('CameraTripod'+str(i),[(-6.7,-1.12,1.0),(-6.7+x,-1.12,.28)],.035,'dark')
        props['numbers']=[p.text('Countdown'+str(k),str(k),(0,-.5,4.6),.8,'purple') for k in (3,2,1)]
    if n==2:
        star=p.objects['Mongsil_HuggedStar'];star.parent=None
        props['star']=star
        props['ice']=p.ball('IceSlide',(0,-.05,.30),(3.5,.67,.025),'ice')
        props['sparkles']=[p.ball('IceSparkle'+str(i),(0,0,0),(.045,)*3,'white',segments=12) for i in range(12)]
    if n==3:
        props['rain']=weather(p,'FlowerRain',26,'rain')
        props['snow']=weather(p,'FlowerSnow',18,'snow')
        props['heat']=[p.curve('Heat_'+str(i),[(0,0,0),(.13,0,.4),(-.13,0,.8),(0,0,1.2)],.04,'gold') for i in range(3)]
        props['puddle']=p.ball('FlowerPuddle',(0,-.65,.297),(1.65,.80,.018),'blue')
        props['pot']=p.ball('FlowerPot',(0,-.65,.47),(.57,.47,.30),'soil')
        p.ball('PotSoil',(0,-.65,.69),(.46,.37,.07),'dark')
        flower=p.empty('FlowerRoot',(0,-.65,.68));props['flower']=flower
        components=[]
        components.append(p.curve('FlowerStem',[(0,0,0),(.02,0,.55),(0,0,1.25)],.05,'leaf'))
        for i,x in enumerate((-.26,.27)):
            leaf=p.ball('FlowerLeaf'+str(i),(x,0,.55+i*.2),(.29,.065,.13),'leaf');leaf.rotation_euler.y=(-.4 if x<0 else .4);components.append(leaf)
        head=p.empty('FlowerHead',(0,0,1.36));head.parent=flower;props['head']=head
        petals=[]
        for i in range(8):
            a=i*math.tau/8
            obj=p.ball('Petal'+str(i),(.44*math.cos(a),-.03,.44*math.sin(a)),(.29,.12,.16),'pink')
            obj.rotation_euler.y=-a
            obj.parent=head;petals.append(obj)
        obj=p.ball('FlowerFace',(0,-.12,0),(.26,.13,.26),'gold');obj.parent=head
        for i,x in enumerate((-.09,.09)):
            obj=p.ball('FlowerEye'+str(i),(x,-.249,.055),(.024,.017,.035),'dark');obj.parent=head
        obj=p.curve('FlowerSmile',[(-.08,-.25,-.04),(0,-.26,-.085),(.08,-.25,-.04)],.019,'dark');obj.parent=head
        for obj in components:obj.parent=flower
        props['petals']=petals
        props['crystals']=[]
        for i in range(6):
            x=.7*math.cos(i*math.tau/6);y=-.65+.35*math.sin(i*math.tau/6)
            obj=p.cube('IceCrystal'+str(i),(x,y,1.0),(.2,.22,1.3),'ice',.05);obj.rotation_euler.y=.2*math.sin(i)
            props['crystals'].append(obj)
        props['pollen']=[p.ball('Pollen'+str(i),(0,0,0),(.055,)*3,'pollen',segments=12) for i in range(45)]
        props['tints']=[]
        for material in bpy_materials(p):
            if any(x in material.name for x in ('Cloud_marshmallow','Sun_butter','Sun_mango','Raindrop_blue','Snow_pearl','Snow_branches','Wind_mint')):
                inp=material.node_tree.nodes['Principled BSDF'].inputs['Base Color']
                props['tints'].append((inp,tuple(inp.default_value)))
    if n==4:
        p.cube('WeatherBackdrop',(0,1.35,2.75),(13,.18,5.0),'blue',.2)
        p.cube('BroadcastDesk',(0,-.72,.86),(7,.70,1.14),'purple',.18)
        p.text('StudioTitle','WEATHER NEWS',(0,1.14,4.58),.54,'white')
        props['mic']=p.curve('MicrophoneStem',[(-.9,-1.10,1.41),(-.9,-1.10,2.0)],.035,'dark')
        p.ball('Microphone',(-.9,-1.10,2.07),(.10,.10,.16),'dark')
        props['rain']=weather(p,'StudioRain',42,'rain')
        props['snow']=weather(p,'StudioSnow',35,'snow')
    if n==5:
        props['bubble']=make_bubble(p,'BigBubble')
        props['hats']=[make_bubble(p,'BubbleHat'+str(i)) for i in range(5)]
        props['burst']=[p.ball('BubbleBurst'+str(i),(0,0,0),(.055,)*3,'blue' if i%2 else 'pink',segments=12) for i in range(20)]
        # Retract the six crystals together without changing the face or limbs.
        root=p.controls['Songsong']['root']
        control=p.empty('Songsong_CrystalControl',(0,0,2.13));control.parent=root
        for obj in list(p.characters['Songsong'].objects):
            if 'Crystal' in obj.name:
                mat=obj.matrix_basis.copy();obj.parent=control;obj.matrix_parent_inverse=Matrix.Identity(4)
                obj.matrix_basis=Matrix.Translation((0,0,-2.13))@mat
        props['crystals']=control
    p.bind_rest()
    return props


def bpy_materials(p):
    import bpy
    return [m for m in bpy.data.materials if m.name.startswith(p.prefix)]


def zzz(p,props,t,x=-5.6):
    for i,obj in enumerate(props.get('zzz',[])):
        u=(t*.35+i*.32)%1
        p.move(obj,(x+.25+i*.3,-.05,3.4+u*.9),scale=.6+.45*u)


def photo(p,s,t):
    idle(p,t);zzz(p,s,t)
    for i,obj in enumerate(s['numbers']):
        p.move(obj,scale=1 if 7+i<=t<8+i else .0001)
    if 3<t<10:
        p.pose('Mongsil',-5.6,lean=-.08*math.sin(t),squash=1+.035*math.sin(t*1.7))
        u=smooth(4,6,t);p.pose('Ttorr',lerp(0,-2.55,u),y=.85*u,lean=.09*u,arms=(-.1,.1))
        p.pose('Songsong',2.8,z=.16*abs(math.sin(t*3)),lean=.20*math.sin(t*2.5),arms=(.4*math.sin(t*3),-.35*math.cos(t*3)))
        p.pose('Solsol',5.6,lean=-.17,arms=(-.4,-.25))
    if t>=10:
        u=smooth(10,15.8,t);recover=smooth(20,22,t)
        pile=[(-1.8,.45,.70,-.22),(-.6,-.15,0,.15),(.1,-.45,1.1,-.30),(1.20,.15,.2,.38),(2.3,.2,.50,-.22)]
        for i,key in enumerate(KEYS):
            x0=(i-2)*2.8;x,y,z,lean=pile[i]
            approach=1-smooth(10,15.8,t)
            if key=='Ttorr':x0=-2.55*approach
            blend=u*(1-recover)
            wobble=.10*math.sin(t*13+i)*math.sin(blend*math.pi)
            y0=.85*approach if key=='Ttorr' else 0
            p.pose(key,lerp(x0,x,blend),y=lerp(y0,y,blend),z=z*blend+max(0,wobble),lean=lean*blend+wobble,
                   arms=(.42*blend,-.5*blend),legs=(wobble*2,-wobble*2))
        if t>22:
            for i,key in enumerate(KEYS):
                hop=.22*max(0,math.sin((t-22)*5+i*.5))*smooth(22,22.3,t)
                p.pose(key,(i-2)*2.8,z=hop,lean=.06*math.sin(t*4+i),arms=(.25,-.25),squash=1+.025*math.sin(t*6))
    show_gust(p,s['gusts'],t,10,15.8,1.5)


def pillow(p,s,t):
    idle(p,t);zzz(p,s,t)
    p.pose('Mongsil',-5.6,z=.035*math.sin(t*1.3),lean=.025*math.sin(t*.8))
    sneeze=pulse(t,4,.20)
    p.pose('Solsol',5.6,lean=-.35*sneeze,arms=(.25*sneeze,-.3*sneeze),squash=1-.13*sneeze)
    show_gust(p,s['gusts'],t,4,7,1.4)
    if t<4:pos=(-5.6,-.69,1.38)
    elif t<7:
        u=smooth(4,7,t);pos=(lerp(-5.6,2.8,u),-.68,lerp(1.38,4.0,u)+.5*math.sin(u*math.pi))
    elif t<12:
        u=(t-7)/5;pos=(2.8-4*u,-.6,4.0-.9*u+.3*math.sin(u*math.tau))
    elif t<20:
        u=(t-12)/8;pos=(-1.2+4.3*u,-.6,3.1-.8*u+.25*math.sin(u*math.tau*2))
    elif t<25:
        u=smooth(20,25,t);pos=(lerp(3.1,-5.6,u),-.69,lerp(2.3,1.38,u)+1.1*math.sin(u*math.pi))
    else:pos=(-5.6,-.69,1.38)
    p.move(s['star'],pos,rotation=(0,0,.25*math.sin(t*4) if 4<t<25 else -.0))
    if 5<=t<12:
        u=smooth(5,8,t);jump=.85*pulse(t,9.3,.6)
        p.pose('Haerong',lerp(-2.8,.5,u),z=jump,lean=-.14*math.sin(t*4),arms=(-.6,-.65),legs=(.12,-.12))
    if t>=12:
        if t<14:p.pose('Haerong',lerp(.5,-2.8,smooth(12,14,t)),arms=(-.2,-.2),legs=(.16*math.sin(t*8),-.16*math.sin(t*8)))
        slide=smooth(12,14,t)*(1-smooth(24,26,t))
        p.move(s['ice'],scale=(3.7*slide,.60*slide,.025*slide))
        if 14<=t<23:
            x=3.6*math.sin((t-14)*.73)
            enter=smooth(14,14.6,t)
            p.pose('Ttorr',x,y=-.5*enter,z=.08*enter,lean=.38*math.cos((t-14)*.73)*enter,turn=.14*math.sin(t*3)*enter,arms=(.6*enter,-.6*enter),legs=(.32*enter,-.32*enter))
            gesture=smooth(14,15,t)*(1-smooth(22,23,t))
            p.pose('Songsong',2.8+.5*math.sin(t)*gesture,lean=-.25*gesture,arms=(.4*gesture,-.3*gesture))
        if 23<=t<25:
            u=smooth(23,25,t)
            p.pose('Ttorr',lerp(3.6*math.sin(9*.73),0,u),y=lerp(-.5,0,u),z=.08*(1-u),lean=.38*math.cos(9*.73)*(1-u),turn=.14*math.sin(23*3)*(1-u),arms=(.6*(1-u),-.6*(1-u)),legs=(.32*(1-u),-.32*(1-u)))
        for i,obj in enumerate(s['sparkles']):
            if slide>.1:p.move(obj,(-3.2+i*.6,-.45+.3*math.sin(i),.35),scale=.035*(.7+.3*math.sin(t*5+i)))
            else:hidden(p,obj)
    else:
        hidden(p,s['ice'])
        for obj in s['sparkles']:hidden(p,obj)
    if t>25:
        for i,key in enumerate(KEYS[1:]):
            u=smooth(25,26,t)
            p.pose(key,lerp((i-1)*2.8,(i-1)*2.65,u),z=0,lean=.12*u,squash=lerp(1,.90+.02*math.sin(t*5+i),u),arms=(.10*u,-.1*u))


def flower(p,s,t):
    idle(p,t,[-5.7,-3.0,3.0,5.7,0])
    p.pose('Solsol',0,y=1.65,lean=.04*math.sin(t*2),arms=(.1,-.1))
    growth=.32+.1*smooth(0,4,t);bend=0;head_scale=.34
    hot=5<=t<10;wet=10<=t<15;cold=15<=t<20;team=20<=t<26
    hot_move=smooth(4.5,5.5,t)*(1-smooth(9.5,10.5,t))
    wet_move=smooth(9.5,10.5,t)*(1-smooth(14.5,15.5,t))
    cold_move=smooth(14,15.5,t)*(1-smooth(19,20.5,t))
    team_move=smooth(19.5,20.5,t)*(1-smooth(25.5,26.5,t))
    p.pose('Haerong',-3+.9*hot_move+.5*team_move,lean=-.22*hot_move-.13*team_move,arms=(.2*hot_move+.1*team_move,-.65*hot_move-.45*team_move),z=.1*abs(math.sin(t*3))*hot_move)
    p.pose('Ttorr',3-1.1*wet_move-.5*team_move,lean=.22*wet_move+.13*team_move,arms=(-.6*wet_move-.45*team_move,.2*wet_move+.1*team_move))
    p.pose('Songsong',5.7-3.6*cold_move-.3*team_move,z=.1*abs(math.sin(t*4))*cold_move,arms=(-.6*cold_move+.15*team_move,.4*cold_move-.1*team_move))
    if hot:
        u=smooth(5,9,t);bend=.75*u;head_scale=.34-.12*u
    if wet:
        bend=lerp(.75,-.55,smooth(10,14,t));head_scale=.3
    if cold:
        bend=-.55*(1-smooth(15,17,t))+.07*math.sin(t*25);head_scale=.25
    if t>=20:
        u=smooth(20,26,t);growth=lerp(.4,1.3,u);head_scale=lerp(.25,1,u)
    sneeze=pulse(t,27,.17)
    p.move(s['flower'],rotation=(0,bend-.25*sneeze,0),scale=growth*(1-.10*sneeze))
    p.move(s['head'],scale=(head_scale*(1+.25*sneeze),head_scale,head_scale*(1-.2*sneeze)))
    rain_at(p,s['rain'],t,wet,span=1.1)
    if team:rain_at(p,s['rain'][:8],t,True,span=.8)
    rain_at(p,s['snow'],t,cold,span=1.4,snow=True)
    puddle=smooth(10,14,t)*(1-smooth(19,22,t))
    p.move(s['puddle'],scale=(1.8*puddle,.78*puddle,.019*puddle))
    for i,obj in enumerate(s['heat']):
        if hot or team:p.move(obj,(-.55+i*.55,-.4,1.15+.18*math.sin(t*4+i)),scale=.7 if hot else .23)
        else:hidden(p,obj)
    for i,obj in enumerate(s['crystals']):
        u=smooth(15,17,t)*(1-smooth(20,22,t));p.move(obj,scale=(u,u,u))
    for i,obj in enumerate(s['pollen']):
        u=t-27
        if 0<=u<2.8:
            ang=i*2.39996;speed=1.4+(i%7)*.38
            p.move(obj,(speed*u*math.cos(ang),-.8+.28*u*math.sin(ang),2.65+speed*.34*u-.65*u*u),scale=.045*(1-u/3.0))
        else:hidden(p,obj)
    tint=smooth(27.3,28.4,t)
    for inp,original in s['tints']:
        target=(*rgb('F4D357'),1)
        inp.default_value=tuple(lerp(a,b,tint) for a,b in zip(original,target))
        inp.keyframe_insert('default_value',frame=round(t*24)+1)
    if t>27:
        for i,key in enumerate(KEYS):
            x=[-5.7,-3,3,5.7,0][i];y=1.65 if key=='Solsol' else 0
            p.pose(key,x,y=y,z=.2*pulse(t,27.5,.25),lean=(-1 if i%2 else 1)*.12*pulse(t,27.5,.5),arms=(.2,-.2))


def forecast(p,s,t):
    # Every presenter enters the same marked spot; rivals remain visible at the edges.
    positions={'Mongsil':(-5.8,.7),'Haerong':(0,0),'Ttorr':(6.4,0),'Songsong':(-6.6,.1),'Solsol':(6.9,.5)}
    if t>=6:
        u=smooth(6,7.4,t);positions['Ttorr']=(lerp(6.4,.8,u),-.1*u);positions['Haerong']=(-1.6*u,.2*u)
    if t>=12:
        u=smooth(12,13.5,t);positions['Songsong']=(lerp(-6.6,-.5,u),lerp(.1,-.25,u));positions['Ttorr']=(.8+1.2*u,lerp(-.1,.1,u))
    if t>=18:
        u=smooth(18,19.7,t);positions['Solsol']=(lerp(6.9,.2,u),lerp(.5,-.4,u))
    for i,key in enumerate(KEYS):
        x,y=positions[key];lean=.05*math.sin(t*4+i)
        sway=smooth(19,19.5,t)*(1-smooth(22.5,23,t))
        x+=.40*math.sin(t*5+i)*sway;lean+=.2*math.sin(t*6+i)*sway
        p.pose(key,x,y=y,lean=lean,arms=(.14*math.sin(t*3+i),-.16*math.sin(t*3+i)),z=.07*max(0,math.sin(t*4+i)))
        p.blink(key,1-.94*pulse((t+i*.4)%3.8,3.5,.08))
    rain_at(p,s['rain'],t,6<t<12,span=10)
    rain_at(p,s['snow'],t,12<t<18,span=10,snow=True)
    show_gust(p,s['gusts'],t,18,23,1.3)
    zzz(p,s,t)
    if t>=23:
        u=smooth(23,25,t)
        root=p.controls['Mongsil']['root']
        p.move(root,(lerp(-5.8,0,u),lerp(.7,-2.1,u),lerp(0,-9.2,u)),rotation=(0,0,0),scale=lerp(1,6,u))
        for obj in s['zzz']:hidden(p,obj)


def bubble(p,s,t):
    idle(p,t,[-5.6,-3.0,-.9,2.6,5.4])
    bx=.35*math.sin(t*.9);bz=3.15+.18*math.sin(t*1.3)
    if t<20:
        size=1.15*smooth(1,4,t)
        p.move(s['bubble'],(bx,-.52,bz),rotation=(-.278,0,.03*math.sin(t)),scale=size)
    else:hidden(p,s['bubble'])
    p.pose('Ttorr',-.9,lean=-.12 if t<5 else .05,arms=(-.4,.45))
    gentle=smooth(5,6,t)*(1-smooth(9,10,t))
    p.pose('Solsol',5.4-.9*gentle,lean=-.20*gentle,arms=(-.42*gentle,.10*gentle),squash=1+(-.05+.015*math.sin(t*3))*gentle)
    show_gust(p,s['gusts'],t,5.5,8,.35)
    retract=smooth(9,10,t)*(1-smooth(21,23,t))
    p.move(s['crystals'],scale=1-.5*retract)
    careful=smooth(9,10,t)*(1-smooth(14,15,t))
    p.pose('Songsong',2.6-.25*careful,lean=.16*careful,arms=(-.45*careful,.5*careful),squash=1-.05*careful)
    warm=smooth(13,14,t)*(1-smooth(16,17,t))
    p.pose('Haerong',-3-.2*warm,lean=-.17*warm,arms=(.45*warm,-.7*warm))
    if 17<t<23:
        u=smooth(17,19.7,t)
        u*=1-smooth(20.4,23,t)
        p.pose('Mongsil',lerp(-5.6,-.45,u),y=-.5*u,z=.35*u,lean=-.07*u,
               arms=(-.75*u,.75*u),squash=1-.07*pulse(t,20,.15))
    for i,obj in enumerate(s['burst']):
        u=t-20
        if 0<=u<.65:
            a=i*math.tau/20
            p.move(obj,(bx+(1.15+u*2.2)*math.cos(a),-.52,bz+(1.15+u*2.2)*math.sin(a)),scale=.06*(1-u/.65))
        else:hidden(p,obj)
    for i,obj in enumerate(s['hats']):
        if t>20.5:
            u=smooth(20.5,22.6,t);x=[-5.6,-3.0,-.9,2.6,5.4][i]
            head=[3.20,3.54,2.89,3.50,3.75][i]
            p.move(obj,(lerp(bx,x,u),-.05,lerp(4.8,head+.18,u)),rotation=(-.278,0,.12*math.sin(t*2+i)),scale=.32*smooth(20.5,21.2,t))
        else:hidden(p,obj)
    if t>=23:
        for i,key in enumerate(KEYS):
            x=[-5.6,-3.0,-.9,2.6,5.4][i]
            p.pose(key,x,z=.035*math.sin(t*3+i),lean=.05*math.sin(t*4+i),arms=(.2,-.2))


TICKS={1:photo,2:pillow,3:flower,4:forecast,5:bubble}
