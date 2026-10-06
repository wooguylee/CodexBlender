"""한입 디저트 마을: 질감 대신 실루엣과 재료 층으로 구분한 다섯 친구."""
import math

def build(b,key):
    cream=b.mat('Vanilla','FFF1CE',.68);caramel=b.mat('Caramel','BD733F',.48);pink=b.mat('Berry','EC91A7',.62)
    mint=b.mat('Mint','92CDB7',.66);gold=b.mat('BakedGold','E6B37A',.66);red=b.mat('Cherry','D75770',.4)
    white=b.mat('Sugar','FFF9EC',.66);purple=b.mat('Lilac','B8A1D6',.62)
    if key=='PuruPudding':
        b.cone('Custard',(0,0,.75),(0,0,1.92),.67,cream,radius_end=.50,sides=32)
        b.ell('SoftBase',(0,0,.78),(.65,.64,.12),cream)
        b.ell('CaramelTop',(0,0,1.93),(.52,.51,.09),caramel)
        for i,x in enumerate((-.38,.29)):
            b.tube('CaramelDrip'+str(i),[(x,-.32,1.94),(x,-.43,1.86),(x*.98,-.49,1.74 if i else 1.66)],[.075,.06,.04],caramel)
        cherry=b.extra('CherryStem',(0,0,1.99),(.09,0,2.24))
        b.ell('Cherry',(0,-.025,2.11),(.16,.15,.15),red,cherry)
        b.tube('CherryStalk',[(0,0,2.24),(.07,0,2.38),(.13,0,2.41)],.024,mint,cherry)
        b.face((0,-.566,1.48),spread=.21,scale=.9)
        b.limbs(cream,shoe=caramel,hand=cream)
        b.box('NeckRibbon',(0,-.57,1.03),(.13,.07,.13),pink,bevel=.035)
        for s in (-1,1):b.ell('Bow'+str(s),(s*.12,-.56,1.04),(.13,.055,.09),pink,rotation=(0,s*.3,0))
    elif key=='MomoMochi':
        b.ell('StrawberryMochi',(0,0,1.42),(.71,.54,.71),pink)
        b.ell('DustyRiceBase',(0,.03,.90),(.62,.48,.23),white)
        for i in range(5):
            a=i*math.tau/5;name=b.extra('Leaf'+str(i),(0,0,1.98),(.35*math.sin(a),.30*math.cos(a),2.12))
            b.ell('Leaf'+str(i),(.23*math.sin(a),.23*math.cos(a),2.03),(.12,.31,.065),mint,name,rotation=(.1,0,-a))
        b.ell('TopBerry',(0,.015,2.19),(.20,.16,.23),red)
        for i,(x,z) in enumerate([(-.43,1.67),(.44,1.66),(-.46,1.30),(.47,1.30),(-.33,1.04),(.33,1.04)]):
            y=-.54*math.sqrt(max(.12,1-(x/.71)**2-((z-1.42)/.71)**2))-.013
            b.ell('RiceSeed'+str(i),(x,y,z),(.023,.018,.045),cream,rotation=(0,.35 if x>0 else -.35,0),segments=12,rings=8)
        b.face((0,-.554,1.56),spread=.20,scale=.92);b.limbs(pink,shoe=mint,hand=white)
    elif key=='PanBread':
        b.box('GoldenCrust',(0,0,1.45),(1.37,.77,1.43),gold,bevel=.24)
        b.ell('LoafCrownL',(-.25,0,2.06),(.44,.38,.24),gold)
        b.ell('LoafCrownR',(.25,0,2.06),(.44,.38,.24),gold)
        b.box('SoftBreadFace',(0,-.386,1.50),(1.13,.075,1.18),cream,bevel=.21)
        b.face((0,-.440,1.71),spread=.23,scale=.95)
        b.box('MintApron',(0,-.445,.98),(.78,.075,.37),mint,'DEF_Body',bevel=.065)
        b.box('ApronPocket',(0,-.492,.94),(.26,.045,.17),white,'DEF_Body',bevel=.025)
        b.limbs(cream,shoe=caramel,hand=cream)
    elif key=='RoniMacaron':
        for points in b.legs.values():points[0].z=.98
        b.ell('MacaronLower',(0,0,1.15),(.70,.49,.30),purple)
        b.ell('VanillaFilling',(0,0,1.43),(.65,.465,.17),cream)
        b.ell('MacaronUpper',(0,0,1.75),(.70,.49,.32),purple)
        for i in range(20):
            a=i*math.tau/20
            for j,z in enumerate((1.34,1.54)):b.ell('Ruffle'+str(i)+'_'+str(j),(.64*math.cos(a),.42*math.sin(a),z),(.08,.065,.055),purple,segments=12,rings=8)
        b.face((0,-.490,1.62),spread=.23,scale=.87)
        b.ell('BerryBeret',(-.19,.01,2.04),(.39,.33,.115),red,rotation=(0,-.22,0))
        b.ell('BeretNib',(-.22,.01,2.16),(.065,.055,.075),red)
        b.limbs(purple,shoe=red,hand=cream)
        for s in (-1,1):b.ell('BowTie'+str(s),(s*.115,-.42,.95),(.13,.07,.085),mint,'DEF_Body',rotation=(0,s*.25,0))
        b.ell('TieButton',(0,-.49,.95),(.055,.035,.055),red,'DEF_Body')
    elif key=='ShushuPuff':
        for points in b.legs.values():points[0].z=.98
        b.ell('PuffHeart',(0,0,1.39),(.64,.51,.60),gold)
        for i in range(7):
            a=i*math.tau/7
            b.ell('BakedFold'+str(i),(.34*math.sin(a),.28*math.cos(a),1.33),(.37,.32,.49),gold,rotation=(0,.12*math.sin(a),0),segments=16,rings=10)
        b.ell('CreamLayer',(0,0,1.80),(.46,.38,.19),cream)
        points=[]
        for i in range(19):
            t=i/18;r=.33*(1-t);a=t*math.tau*2;points.append((r*math.sin(a),r*.83*math.cos(a),1.90+t*.46))
        b.tube('CreamSwirl',points,[.12*(1-i/22) for i in range(19)],white,sides=10)
        b.face((0,-.575,1.48),spread=.21,scale=.92)
        b.limbs(gold,shoe=mint,hand=white)
        b.box('ChefScarf',(0,-.48,.94),(.58,.085,.13),red,'DEF_Body',bevel=.04)
        b.ell('ScarfKnot',(.19,-.55,.93),(.08,.06,.10),red,'DEF_Body')
    else:raise KeyError(key)
