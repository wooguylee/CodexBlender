"""우주 공방 친구 5종: 사용자가 승인한 20종 캐릭터 제작의 독립 모델 소스.

정면은 -Y. 모든 형상과 부가 리그는 BUILDER_API.md의 b API로 생성한다.
불투명한 얼굴 앞 유리 대신 열린 헬멧 테두리, 목 칼라와 측면 장치를 쓴다.
Blender 실행, 장면 생성, 저장, 내보내기는 상위 제작 워크플로가 담당한다.
"""

from math import cos, pi, sin


KEYS = ("PokoAlien", "BoltRobot", "LunaRabbit", "TwinkleStar", "PingoPenguin")


def _palette(b, suit, skin, accent="FFD36B"):
    # 얼굴 API가 추가하는 눈/하이라이트/홍조 3종까지 총 12종 이내.
    return {
        "suit": b.mat("WorkshopSuit", suit, roughness=.62),
        "skin": b.mat("CharacterSkin", skin, roughness=.53),
        "trim": b.mat("WarmIvory", "FFF2D9", roughness=.47),
        "dark": b.mat("InkNavy", "243B58", roughness=.52),
        "accent": b.mat("SunshineAccent", accent, roughness=.43),
        "pink": b.mat("PeachDetails", "F699AF", roughness=.58),
        "metal": b.mat("ToolSilver", "B9CED8", roughness=.32, metallic=.48),
        "blue": b.mat("IceBlue", "8BDFE9", roughness=.34),
        "sole": b.mat("SoleBlue", "536C88", roughness=.76),
    }


def _ell(b, name, center, scale, material, bone="DEF_Head", rotation=(0, 0, 0)):
    return b.ell(name, center, scale, material, bone=bone,
                 rotation=rotation, segments=28, rings=18)


def _suit(b, p, squared=False):
    """짧은 작업복, 외부 장갑/부츠와 독립 가중치의 팔 부품."""
    if squared:
        b.box("SuitTorso", (0, 0, 1.02), (.84, .59, .76), p["suit"],
              bone="DEF_Body", bevel=.18)
    else:
        _ell(b, "SuitTorso", (0, 0, 1.03), (.45, .31, .43), p["suit"], "DEF_Body")
    _ell(b, "SuitHip", (0, .015, .74), (.37, .27, .20), p["suit"], "DEF_Body")
    b.limbs(p["suit"], shoe=p["trim"], hand=p["trim"], radius=.115)
    for sign, side in ((-1, "L"), (1, "R")):
        _ell(b, "Shoulder" + side, (sign * .48, 0, 1.25), (.17, .205, .18),
             p["suit"], "DEF_UpperArm." + side)
        _ell(b, "Cuff" + side, (sign * .82, -.105, .92), (.137, .137, .075),
             p["accent"], "DEF_Forearm." + side, (0, sign * .35, 0))
        b.box("BootSole" + side, (sign * .25, -.065, .038), (.34, .43, .076),
              p["sole"], bone="DEF_Foot." + side, bevel=.034)
        _ell(b, "BootToe" + side, (sign * .25, -.14, .13), (.17, .22, .10),
             p["trim"], "DEF_Foot." + side)
        b.box("BootBuckle" + side, (sign * .25, -.27, .19), (.16, .035, .07),
              p["accent"], bone="DEF_Foot." + side, bevel=.025)
    b.tube("FrontBelt", [(-.4, -.16, .85), (-.25, -.27, .84), (0, -.313, .84),
                         (.25, -.27, .84), (.4, -.16, .85)], .035,
           p["trim"], bone="DEF_Body", sides=12)
    b.box("BeltBuckle", (0, -.346, .85), (.135, .055, .095), p["accent"],
          bone="DEF_Body", bevel=.025)
    # Rear pack is narrow enough to preserve the character's front silhouette.
    b.box("AirPack", (0, .33, 1.13), (.55, .26, .50), p["trim"],
          bone="DEF_Body", bevel=.11)
    for sign in (-1, 1):
        _ell(b, "AirCanister" + str(sign), (sign * .27, .33, 1.14), (.09, .12, .23),
             p["blue"], "DEF_Body")


def _collar(b, p, z=1.42, radius=.36):
    b.ring("OpenHelmetCollar", (0, 0, z), radius, .075, p["trim"],
           bone="DEF_Body", rotation=(pi / 2, 0, 0))
    b.ring("CollarGasket", (0, 0, z - .052), radius - .012, .035, p["accent"],
           bone="DEF_Body", rotation=(pi / 2, 0, 0))


def _helmet(b, p, center_z=1.94, radius=.655, pods=True):
    """얇은 테두리는 머리 뒤에 놓아 눈/입을 가리지 않는다."""
    b.ring("OpenHelmetRim", (0, .055, center_z), radius, .042, p["trim"])
    if pods:
        for sign, side in ((-1, "L"), (1, "R")):
            _ell(b, "HelmetPod" + side, (sign * (radius - .005), .045, center_z),
                 (.115, .185, .17), p["trim"])
            _ell(b, "HelmetPodFace" + side, (sign * (radius - .005), -.12, center_z),
                 (.077, .035, .105), p["blue"])
            _ell(b, "HelmetPodLight" + side, (sign * (radius - .005), -.151, center_z),
                 (.032, .013, .042), p["accent"])


def _panel(b, p, emblem="star"):
    b.box("ChestPanel", (0, -.31, 1.10), (.40, .08, .29), p["trim"],
          bone="DEF_Body", bevel=.06)
    b.box("PanelDisplay", (-.08, -.362, 1.145), (.16, .022, .105), p["blue"],
          bone="DEF_Body", bevel=.025)
    for index, material in enumerate((p["pink"], p["accent"], p["blue"])):
        _ell(b, "PanelButton" + str(index), (-.10 + index * .10, -.367, 1.025),
             (.027, .018, .025), material, "DEF_Body")
    if emblem == "star":
        b.star("PanelStar", (.115, -.372, 1.14), .062, .022, p["accent"],
               bone="DEF_Body")
    else:
        _ell(b, "PanelIndicator", (.105, -.375, 1.145), (.049, .018, .049),
             p["accent"], "DEF_Body")


def _wrench(b, p):
    bone = "DEF_Hand.R"
    b.cone("WrenchHandle", (.88, -.205, .76), (1.04, -.205, 1.16), .048,
           p["metal"], bone=bone, radius_end=.048)
    _ell(b, "WrenchGrip", (.915, -.205, .85), (.065, .061, .15), p["pink"],
         bone, (0, .37, 0))
    # Open jaw reads as a wrench instead of a closed ring or microphone.
    b.tube("WrenchJaw", [(1.00, -.205, 1.30), (.955, -.205, 1.22),
                         (1.015, -.205, 1.16), (1.105, -.205, 1.18),
                         (1.145, -.205, 1.26)], .048, p["metal"], bone=bone, sides=12)


def _poko(b):
    p = _palette(b, "F2A674", "97DAB8")
    _suit(b, p)
    _collar(b, p)
    _ell(b, "AlienHead", (0, -.005, 1.94), (.585, .475, .545), p["skin"])
    # The little side fins and asymmetric aerials give Poko an alien silhouette.
    for sign, side in ((-1, "L"), (1, "R")):
        ear = b.extra("AlienEar" + side, (sign * .43, 0, 1.98),
                      (sign * .68, .015, 2.06))
        _ell(b, "AlienEar" + side, (sign * .54, .00, 2.00), (.22, .105, .13),
             p["skin"], ear, (0, -sign * .23, 0))
        _ell(b, "AlienEarInset" + side, (sign * .57, -.088, 2.005), (.12, .027, .065),
             p["pink"], ear, (0, -sign * .23, 0))
    _helmet(b, p, radius=.675)
    for side, points in (
        ("L", [(-.27, .02, 2.37), (-.34, .015, 2.58), (-.44, -.02, 2.70)]),
        ("R", [(.27, .02, 2.37), (.31, .015, 2.67), (.39, -.02, 2.83)]),
    ):
        bone = b.extra("Antenna" + side, points[0], points[-1])
        b.tube("AntennaStem" + side, points, [.061, .050, .044], p["skin"],
               bone=bone, sides=12)
        _ell(b, "AntennaGlow" + side, points[-1], (.11, .10, .115), p["accent"], bone)
        _ell(b, "AntennaHighlight" + side,
             (points[-1][0] - .026, points[-1][1] - .082, points[-1][2] + .028),
             (.028, .020, .035), p["trim"], bone)
    for index, (x, z, radius) in enumerate(((-.18, 2.28, .05), (0, 2.33, .066), (.18, 2.28, .05))):
        _ell(b, "AlienForeheadSpot" + str(index), (x, -.405, z),
             (radius, .023, radius * .75), p["blue"])
    b.face(center=(0, -.496, 1.975), spread=.213, scale=1.02)
    _panel(b, p)
    b.star("ShoulderCrewBadge", (-.525, -.184, 1.28), .084, .029, p["accent"],
           bone="DEF_UpperArm.L")
    _wrench(b, p)


def _bolt(b):
    p = _palette(b, "91BBD9", "9DDDCB", accent="F9CC74")
    _suit(b, p, squared=True)
    _collar(b, p, z=1.40, radius=.325)
    b.box("RobotHeadShell", (0, .01, 1.94), (1.10, .85, 1.02), p["accent"], bevel=.19)
    b.box("RobotScreenRim", (0, -.443, 1.95), (.93, .09, .77), p["dark"], bevel=.135)
    b.box("RobotScreen", (0, -.495, 1.95), (.80, .052, .65), p["skin"], bevel=.115)
    for sign, side in ((-1, "L"), (1, "R")):
        b.box("RobotEarBlock" + side, (sign * .575, .02, 1.94), (.18, .43, .38),
              p["trim"], bevel=.055)
        _ell(b, "RobotEarHub" + side, (sign * .595, -.21, 1.95), (.078, .037, .10), p["blue"])
        for offset in (-.085, .085):
            _ell(b, "RobotFaceBolt" + side + str(offset),
                 (sign * .458, -.472, 1.95 + offset * 3.6), (.026, .018, .026), p["metal"])
        b.box("RobotKnee" + side, (sign * .25, -.11, .46), (.23, .09, .15), p["blue"],
              bone="DEF_Shin." + side, bevel=.045)
    bone = b.extra("RobotAerial", (.20, .055, 2.42), (.36, .055, 2.75))
    b.tube("RobotAerialStem", [(.20, .055, 2.42), (.20, .055, 2.60), (.36, .055, 2.68)],
           .033, p["metal"], bone=bone, sides=12)
    _ell(b, "RobotSignalLamp", (.36, .055, 2.72), (.09, .09, .105), p["pink"], bone)
    b.box("RobotTopCap", (-.22, .035, 2.473), (.26, .33, .075), p["trim"], bevel=.035)
    # Pale mint screen keeps the facial shape keys visible and approachable.
    b.face(center=(0, -.539, 2.00), spread=.20, scale=.91)
    b.box("RobotScreenGlint", (-.29, -.53, 2.175), (.085, .012, .024), p["trim"], bevel=.01)
    _panel(b, p)
    for index in range(3):
        b.box("RobotVent" + str(index), (-.25 + index * .08, -.307, .91),
              (.035, .035, .063), p["dark"], bone="DEF_Body", bevel=.012)
    hand = "DEF_Hand.L"
    _ell(b, "ScrewdriverHandle", (-.89, -.22, .86), (.075, .07, .16), p["pink"],
         hand, (0, -.22, 0))
    b.cone("ScrewdriverShaft", (-.915, -.22, .98), (-.995, -.22, 1.32), .023,
           p["metal"], bone=hand, radius_end=.023, sides=12)
    b.box("ScrewdriverFlatTip", (-1.004, -.22, 1.34), (.066, .032, .078), p["metal"],
          bone=hand, bevel=.008, rotation=(0, -.22, 0))
    # A small rivet on each glove reinforces the toy robot's material language.
    for sign, side in ((-1, "L"), (1, "R")):
        _ell(b, "GloveRivet" + side, (sign * .87, -.24, .84), (.040, .018, .040),
             p["blue"], "DEF_Hand." + side)


def _crescent(b, p):
    # A closed crescent with shared horn vertices, avoiding intersecting arcs.
    steps = 16
    outer = [(.06 - .18 * sin(pi * i / steps),
              1.12 + .135 * cos(pi * i / steps)) for i in range(steps + 1)]
    inner = [(.06 - .10 * sin(pi * i / steps),
              1.12 + .135 * cos(pi * i / steps)) for i in range(steps - 1, 0, -1)]
    outline = outer + inner
    count = len(outline)
    vertices = [(x, y, z) for y in (-.388, -.365) for x, z in outline]

    def inner_index(i):
        return i if i in (0, steps) else 2 * steps - i

    faces = []
    for i in range(steps):
        face = list(dict.fromkeys((i, i + 1, inner_index(i + 1), inner_index(i))))
        faces.append(tuple(face))
        faces.append(tuple(v + count for v in reversed(face)))
    for i in range(count):
        nxt = (i + 1) % count
        faces.append((i, i + count, nxt + count, nxt))
    b.mesh("MoonCrewPatch", vertices, faces, p["accent"], bone="DEF_Body")


def _luna(b):
    p = _palette(b, "B2A2E2", "FFF2D9")
    _suit(b, p)
    _collar(b, p, z=1.39)
    _ell(b, "RabbitHead", (0, -.01, 1.87), (.56, .455, .48), p["skin"])
    _helmet(b, p, center_z=1.88, radius=.60)
    for sign, side in ((-1, "L"), (1, "R")):
        bone = b.extra("MoonEar" + side, (sign * .24, .015, 2.18),
                       (sign * .36, .015, 2.94))
        rotation = (0, sign * .13, 0)
        _ell(b, "LongRabbitEar" + side, (sign * .285, .015, 2.57), (.145, .125, .45),
             p["skin"], bone, rotation)
        _ell(b, "RabbitEarVelvet" + side, (sign * .292, -.098, 2.60), (.084, .027, .335),
             p["pink"], bone, rotation)
        _ell(b, "EarBaseSeal" + side, (sign * .23, .02, 2.22), (.17, .14, .075),
             p["accent"], bone, rotation)
    _ell(b, "RabbitLeftCheek", (-.22, -.34, 1.74), (.22, .145, .15), p["skin"])
    _ell(b, "RabbitRightCheek", (.22, -.34, 1.74), (.22, .145, .15), p["skin"])
    b.face(center=(0, -.486, 1.91), spread=.20, scale=.97)
    _ell(b, "RabbitTinyNose", (0, -.512, 1.815), (.045, .035, .029), p["pink"])
    b.box("MoonPatchBacking", (0, -.31, 1.12), (.40, .09, .34), p["trim"],
          bone="DEF_Body", bevel=.085)
    _crescent(b, p)
    for sign in (-1, 1):
        _ell(b, "MoonPatchRivet" + str(sign), (sign * .15, -.365, 1.005), (.025, .016, .025),
             p["blue"], "DEF_Body")
    _ell(b, "RabbitTail", (0, .415, .78), (.17, .15, .17), p["skin"], "DEF_Body")
    hand = "DEF_Hand.R"
    b.cone("MoonHammerHandle", (.87, -.20, .75), (1.005, -.20, 1.19), .041,
           p["accent"], bone=hand, radius_end=.041)
    _ell(b, "HammerGrip", (.893, -.20, .825), (.065, .06, .12), p["pink"],
         hand, (0, .29, 0))
    b.box("MoonHammerHead", (1.01, -.20, 1.23), (.33, .19, .18), p["blue"],
          bone=hand, bevel=.055, rotation=(0, -.24, 0))
    b.box("HammerSoftCap", (.866, -.20, 1.196), (.055, .21, .19), p["trim"],
          bone=hand, bevel=.027, rotation=(0, -.24, 0))
    b.star("HammerStar", (1.025, -.303, 1.25), .060, .018, p["trim"], bone=hand)


def _twinkle(b):
    p = _palette(b, "F59CA6", "FFE58D", accent="F7C15F")
    _suit(b, p)
    _collar(b, p, z=1.38, radius=.335)
    b.star("LivingStarHead", (0, .015, 1.98), .73, .43, p["skin"])
    # A softly convex central face carries readable cheeks on the solid star.
    _ell(b, "StarFace", (0, -.16, 1.955), (.455, .285, .415), p["skin"])
    _helmet(b, p, center_z=1.96, radius=.765)
    b.face(center=(0, -.465, 2.005), spread=.21, scale=1.0)
    for sign in (-1, 1):
        b.star("StarFreckle" + str(sign), (sign * .365, -.349, 1.94), .05, .015,
               p["accent"], rotation=(0, sign * .12, 0))
    bone = b.extra("StarReceiver", (.38, .07, 2.35), (.61, .07, 2.67))
    b.tube("StarReceiverStem", [(.38, .07, 2.35), (.49, .07, 2.55), (.62, .07, 2.64)],
           .031, p["metal"], bone=bone, sides=12)
    b.star("ReceiverLittleStar", (.65, .07, 2.70), .112, .10, p["blue"], bone=bone,
           rotation=(0, -.12, 0))
    _panel(b, p)
    b.star("PocketStar", (-.275, -.286, 1.18), .074, .025, p["blue"], bone="DEF_Body")
    # A toy optical scanner is short and stubby so it remains within the rig's hands.
    hand = "DEF_Hand.R"
    b.cone("ScannerBarrel", (.885, -.21, .82), (1.065, -.21, 1.125), .088,
           p["blue"], bone=hand, radius_end=.115)
    _ell(b, "ScannerGrip", (.881, -.21, .815), (.092, .082, .108), p["accent"], hand)
    _ell(b, "ScannerLensRim", (1.075, -.21, 1.145), (.13, .13, .052), p["trim"],
         hand, (0, .53, 0))
    _ell(b, "ScannerLens", (1.096, -.217, 1.184), (.102, .10, .018), p["dark"],
         hand, (0, .53, 0))
    _ell(b, "ScannerLensGlint", (1.104, -.254, 1.201), (.031, .031, .013), p["blue"],
         hand, (0, .53, 0))


def _pingo(b):
    p = _palette(b, "7AC9C0", "344F74", accent="F9CB6D")
    _suit(b, p)
    _collar(b, p)
    _ell(b, "PenguinHead", (0, .005, 1.93), (.565, .445, .54), p["skin"])
    # Two large pale lobes form the unmistakable penguin face mask.
    for sign, side in ((-1, "L"), (1, "R")):
        _ell(b, "PenguinMask" + side, (sign * .205, -.32, 1.925), (.30, .18, .383),
             p["trim"], rotation=(0, sign * .07, 0))
    _ell(b, "PenguinMaskChin", (0, -.323, 1.72), (.30, .17, .205), p["trim"])
    _helmet(b, p, center_z=1.95, radius=.642)
    b.face(center=(0, -.525, 1.995), spread=.213, scale=.98)
    # Tiny beak sits between eyes and mouth; the Smile shape key stays exposed.
    _ell(b, "PenguinBeak", (0, -.569, 1.895), (.084, .080, .044), p["accent"])
    bone = b.extra("PenguinCrest", (0, .02, 2.39), (.075, -.01, 2.68))
    _ell(b, "PenguinCrestOne", (-.04, .025, 2.485), (.072, .086, .18),
         p["skin"], bone, (0, -.31, 0))
    _ell(b, "PenguinCrestTwo", (.072, .023, 2.47), (.067, .075, .147),
         p["skin"], bone, (0, .29, 0))
    _panel(b, p)
    # Navigator's warm kerchief drapes clear of the chest display and facial rig.
    b.tube("NavigatorScarfBand", [(-.32, -.14, 1.395), (-.18, -.275, 1.385),
                                 (0, -.31, 1.38), (.23, -.25, 1.395)],
           .055, p["pink"], bone="DEF_Body", sides=12)
    _ell(b, "NavigatorScarfKnot", (.25, -.26, 1.39), (.092, .061, .082), p["pink"], "DEF_Body")
    b.box("NavigatorScarfTail", (.31, -.285, 1.275), (.11, .06, .235), p["pink"],
          bone="DEF_Body", bevel=.043, rotation=(0, -.24, 0))
    hand = "DEF_Hand.L"
    b.box("NavigatorCompassCase", (-.91, -.235, .985), (.30, .14, .35), p["accent"],
          bone=hand, bevel=.08, rotation=(0, -.12, 0))
    _ell(b, "NavigatorCompassDial", (-.91, -.319, .995), (.116, .025, .13), p["trim"], hand)
    b.star("NavigatorCompassRose", (-.91, -.348, .995), .087, .022, p["blue"],
           bone=hand, points=4, rotation=(0, -.12, 0))
    b.cone("CompassNeedle", (-.918, -.371, .970), (-.887, -.371, 1.064), .016,
           p["pink"], bone=hand, radius_end=.006, sides=10)
    _ell(b, "CompassPivot", (-.91, -.38, .995), (.021, .010, .021), p["dark"], hand)
    b.ring("CompassLoop", (-.91, -.235, 1.19), .052, .016, p["metal"], bone=hand)


def build(b, key):
    """Build one approved space-workshop character using only the shared API."""
    builders = {
        "PokoAlien": _poko,
        "BoltRobot": _bolt,
        "LunaRabbit": _luna,
        "TwinkleStar": _twinkle,
        "PingoPenguin": _pingo,
    }
    try:
        builder = builders[key]
    except KeyError:
        raise ValueError("Unknown space character: " + str(key)) from None
    builder(b)
