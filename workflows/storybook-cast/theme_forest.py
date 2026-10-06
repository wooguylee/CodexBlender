"""숲속 우체국의 다섯 친구: 종의 실루엣과 직업 소품으로 구분한다.

사용자 승인: 스토리북 캐릭터 실제 제작. 이 모듈은 Builder API만 사용한다.
좌표는 Z-up, 정면 -Y이며, 보조 귀/꼬리는 전용 흔들림 뼈에 연결한다.
Blender 연결, 저장, 렌더와 export는 공통 제작 파이프라인이 담당한다.
"""

from math import cos, sin


KEYS = (
    "PipiRabbit", "DodoBear", "ToriSquirrel", "BibiOwl", "MoriHedgehog",
)


def _palette(b, key, colors):
    """Seven authored materials leave room for the builder's facial materials."""
    names = ("fur", "cream", "dark", "uniform", "gold", "leather", "paper")
    return {name: b.mat(key + "_" + name, color)
            for name, color in zip(names, colors)}


def _letter(b, name, center, size, p, bone="DEF_Body", stamp=True):
    """A chunky envelope with a visible V-shaped fold on its front (-Y)."""
    x, y, z = center
    w, d, h = size
    b.box(name, center, size, p["paper"], bone=bone, bevel=.025)
    front = y - d / 2 - .012
    b.tube(name + "_fold", [(x - w * .43, front, z + h * .37),
                            (x, front - .003, z - h * .04),
                            (x + w * .43, front, z + h * .37)],
           .009, p["gold"], bone=bone, sides=8)
    if stamp:
        b.box(name + "_stamp", (x + w * .28, front - .009, z + h * .22),
              (w * .19, .018, h * .23), p["uniform"], bone=bone, bevel=.012)
        b.ell(name + "_stamp_mark", (x + w * .28, front - .021, z + h * .22),
              (w * .045, .008, h * .05), p["gold"], bone=bone,
              segments=12, rings=8)


def _satchel(b, p, side=1, z=.87, width=.47):
    """Oversized bag, raised flap, buckle and a cross-body leather strap."""
    x = side * .57
    b.box("Mailbag", (x, -.34, z), (width, .25, .49), p["leather"],
          bone="DEF_Body", bevel=.10)
    b.box("Mailbag_flap", (x, -.487, z + .105),
          (width * 1.015, .055, .23), p["uniform"],
          bone="DEF_Body", bevel=.045)
    b.box("Mailbag_buckle", (x, -.526, z + .045), (.105, .026, .085),
          p["gold"], bone="DEF_Body", bevel=.018)
    b.box("Mailbag_buckle_inset", (x, -.544, z + .045), (.054, .013, .037),
          p["leather"], bone="DEF_Body", bevel=.006)
    b.tube("Crossbody_strap", [(-side * .38, -.18, 1.40),
                               (-side * .22, -.369, 1.29),
                               (side * .11, -.41, 1.09),
                               (side * .37, -.44, z + .16),
                               (x, -.35, z + .21)],
           .041, p["leather"], bone="DEF_Body", sides=10)
    # A letter protrudes well above the flap and has its own readable outline.
    _letter(b, "Bag_letter", (x - side * .055, -.34, z + .29),
            (width * .69, .052, .28), p)
    for dx in (-width * .35, width * .35):
        b.ell("Bag_rivet", (x + dx, -.525, z + .15), (.019, .012, .019),
              p["gold"], bone="DEF_Body", segments=12, rings=8)


def _uniform(b, p, body_scale=(.49, .36, .53), buttons=3):
    b.ell("Rounded_uniform", (0, .015, 1.02), body_scale, p["uniform"],
          bone="DEF_Body", segments=36, rings=24)
    for side in (-1, 1):
        b.ell("Collar", (side * .14, -.31, 1.37), (.16, .055, .10),
              p["cream"], bone="DEF_Body", rotation=(0, side * .22, 0),
              segments=24, rings=16)
    for i in range(buttons):
        b.ell("Coat_button", (-.12, -.355, 1.15 - i * .15),
              (.035, .027, .035), p["gold"], bone="DEF_Body",
              segments=16, rings=10)
    b.box("Breast_pocket", (.235, -.329, 1.22), (.15, .06, .13),
          p["uniform"], bone="DEF_Body", bevel=.025)
    b.star("Postal_badge", (.235, -.371, 1.25), .053, .018, p["gold"],
           bone="DEF_Body", points=5)


def _cap(b, p, center=(0, .025, 2.27), scale=(.45, .36, .14), tilt=0):
    x, y, z = center
    sx, sy, sz = scale
    b.ell("Post_cap_crown", center, scale, p["uniform"],
          rotation=(0, tilt, 0), segments=32, rings=20)
    b.ell("Post_cap_band", (x, y - .025, z - sz * .53),
          (sx * 1.02, sy * 1.015, .050), p["dark"],
          rotation=(0, tilt, 0), segments=28, rings=16)
    b.ell("Post_cap_visor", (x, y - sy * .75, z - sz * .68),
          (sx * .88, sy * .70, .036), p["uniform"],
          rotation=(0, tilt, 0), segments=28, rings=14)
    b.star("Cap_postal_star", (x, y - sy - .017, z + .01), .077, .025,
           p["gold"], points=5, rotation=(0, tilt, 0))


def _shoe_trim(b, p):
    for side, suffix in ((-1, "L"), (1, "R")):
        b.ell("Boot_cuff_" + suffix, (side * .25, -.01, .32),
              (.145, .13, .047), p["gold"], bone="DEF_Shin." + suffix,
              segments=20, rings=12)
        b.ell("Boot_toe_" + suffix, (side * .25, -.175, .14),
              (.115, .063, .064), p["dark"], bone="DEF_Foot." + suffix,
              segments=20, rings=12)


def _pipi(b, p):
    b.limbs(p["fur"], shoe=p["leather"], hand=p["fur"], radius=.105)
    _uniform(b, p)
    _shoe_trim(b, p)
    b.ell("Rabbit_head", (0, -.015, 1.80), (.565, .46, .535), p["fur"],
          segments=40, rings=28)
    b.ell("Rabbit_muzzle_patch", (0, -.418, 1.62), (.30, .088, .21),
          p["cream"], segments=28, rings=18)
    for side, suffix in ((-1, "L"), (1, "R")):
        ear = b.extra("RabbitEar." + suffix, (side * .24, .025, 2.12),
                      (side * .33, .025, 2.96))
        b.ell("Long_ear_" + suffix, (side * .29, .025, 2.60),
              (.145, .105, .445), p["fur"], bone=ear,
              rotation=(0, side * .12, 0), segments=28, rings=20)
        b.ell("Ear_lining_" + suffix, (side * .292, -.072, 2.61),
              (.078, .025, .342), p["leather"], bone=ear,
              rotation=(0, side * .12, 0), segments=24, rings=18)
    tail = b.extra("RabbitTail", (0, .29, .85), (0, .55, .91), parent="DEF_Body")
    b.ell("Cotton_tail", (0, .46, .91), (.22, .19, .22), p["cream"],
          bone=tail, segments=28, rings=18)
    b.face(center=(0, -.535, 1.80), spread=.215, scale=1.0)
    b.ell("Rabbit_nose", (0, -.558, 1.78), (.047, .031, .034),
          p["leather"], segments=16, rings=10)
    _cap(b, p, center=(0, -.005, 2.22), scale=(.40, .32, .125))
    _satchel(b, p, side=1, z=.83, width=.49)
    _letter(b, "Delivery_letter", (-.885, -.22, .865), (.36, .07, .26),
            p, bone="DEF_Hand.L")


def _dodo(b, p):
    b.limbs(p["fur"], shoe=p["dark"], hand=p["fur"], radius=.128)
    _uniform(b, p, body_scale=(.555, .405, .565), buttons=3)
    _shoe_trim(b, p)
    b.ell("Bear_head", (0, .005, 1.80), (.635, .49, .56), p["fur"],
          segments=40, rings=28)
    for side, suffix in ((-1, "L"), (1, "R")):
        ear = b.extra("BearEar." + suffix, (side * .48, .015, 2.15),
                      (side * .65, .01, 2.40))
        b.ell("Round_bear_ear_" + suffix, (side * .545, .016, 2.235),
              (.225, .15, .235), p["fur"], bone=ear, segments=28, rings=18)
        b.ell("Round_bear_lining_" + suffix, (side * .549, -.12, 2.238),
              (.132, .027, .147), p["cream"], bone=ear, segments=24, rings=16)
    b.ell("Bear_muzzle_patch", (0, -.433, 1.625), (.34, .088, .235),
          p["cream"], segments=32, rings=20)
    b.face(center=(0, -.546, 1.81), spread=.24, scale=1.09)
    b.ell("Bear_nose", (0, -.572, 1.80), (.088, .045, .051), p["dark"],
          segments=20, rings=12)
    _cap(b, p, center=(0, .015, 2.31), scale=(.455, .36, .14))
    # Wide bow and a pocket watch distinguish the unhurried postmaster.
    for side in (-1, 1):
        b.ell("Postmaster_bow", (side * .09, -.384, 1.385),
              (.105, .044, .075), p["leather"], bone="DEF_Body",
              rotation=(0, side * .2, 0), segments=24, rings=16)
    b.ell("Bow_knot", (0, -.407, 1.385), (.042, .032, .047), p["gold"],
          bone="DEF_Body", segments=16, rings=10)
    _satchel(b, p, side=1, z=.82, width=.48)
    b.box("Held_parcel", (-.87, -.235, .82), (.41, .31, .32), p["paper"],
          bone="DEF_Hand.L", bevel=.055)
    b.box("Parcel_vertical_ribbon", (-.87, -.399, .82), (.039, .021, .32),
          p["leather"], bone="DEF_Hand.L", bevel=.009)
    b.box("Parcel_horizontal_ribbon", (-.87, -.414, .82), (.41, .018, .036),
          p["leather"], bone="DEF_Hand.L", bevel=.009)
    b.box("Parcel_address", (-.959, -.403, .891), (.11, .015, .07),
          p["uniform"], bone="DEF_Hand.L", bevel=.01)
    b.ring("Pocket_watch", (-.32, -.411, .965), .074, .018, p["gold"],
           bone="DEF_Body")
    b.ell("Watch_face", (-.32, -.416, .965), (.061, .019, .061), p["paper"],
          bone="DEF_Body", segments=20, rings=12)
    b.tube("Watch_hands", [(-.32, -.439, 1.01), (-.32, -.439, .965),
                            (-.293, -.439, .951)], .009, p["dark"],
           bone="DEF_Body", sides=8)


def _tori(b, p):
    b.limbs(p["fur"], shoe=p["dark"], hand=p["fur"], radius=.103)
    _uniform(b, p, body_scale=(.46, .335, .51))
    _shoe_trim(b, p)
    tail_points = [(0, .28, .78), (.32, .41, 1.03), (.67, .43, 1.40),
                   (.79, .43, 1.94), (.64, .40, 2.38), (.33, .36, 2.43),
                   (.235, .35, 2.18)]
    tail_chain = b.chain("SquirrelTail", tail_points, parent="DEF_Body")
    b.tube("Grand_curled_squirrel_tail", tail_points,
           [.12, .22, .285, .31, .29, .22, .09], p["fur"],
           bone="DEF_Body", chain=tail_chain, sides=16)
    # The cream curl is on the front of the visible upper tail, clear of the face.
    b.tube("Cream_tail_curl", [(.86, .18, 1.82), (.81, .155, 2.18),
                               (.60, .115, 2.43), (.35, .105, 2.44),
                               (.252, .105, 2.26)],
           [.06, .09, .10, .09, .035], p["cream"],
           bone="DEF_Body", chain=tail_chain[2:], sides=12)
    b.ell("Squirrel_head", (0, -.01, 1.79), (.555, .442, .513), p["fur"],
          segments=40, rings=28)
    for side, suffix in ((-1, "L"), (1, "R")):
        ear = b.extra("SquirrelEar." + suffix, (side * .335, .015, 2.105),
                      (side * .43, .015, 2.52))
        b.ell("Pointed_ear_base_" + suffix, (side * .37, .018, 2.26),
              (.148, .103, .237), p["fur"], bone=ear,
              rotation=(0, side * .2, 0), segments=24, rings=16)
        b.cone("Ear_tuft_" + suffix, (side * .405, .019, 2.35),
               (side * .454, .019, 2.575), .082, p["dark"],
               bone=ear, radius_end=.015, sides=16)
        b.ell("Squirrel_ear_lining_" + suffix, (side * .375, -.079, 2.268),
              (.083, .021, .151), p["cream"], bone=ear,
              rotation=(0, side * .2, 0), segments=24, rings=16)
        b.ell("Cheek_puff_" + suffix, (side * .365, -.273, 1.61),
              (.209, .164, .194), p["fur"], segments=24, rings=16)
    b.ell("Squirrel_face_patch", (0, -.402, 1.66), (.307, .085, .244),
          p["cream"], segments=28, rings=18)
    b.face(center=(0, -.516, 1.80), spread=.209, scale=.98)
    b.ell("Squirrel_nose", (0, -.548, 1.788), (.048, .03, .035),
          p["dark"], segments=16, rings=10)
    # A small sorting clerk visor sits between the ears; tail remains exposed.
    _cap(b, p, center=(-.06, -.01, 2.215), scale=(.32, .30, .102), tilt=-.10)
    _satchel(b, p, side=-1, z=.79, width=.45)
    b.box("Sorting_clipboard", (.888, -.245, .878), (.315, .074, .388),
          p["leather"], bone="DEF_Hand.R", bevel=.035)
    b.box("Sorting_list", (.888, -.289, .878), (.255, .017, .319),
          p["paper"], bone="DEF_Hand.R", bevel=.016)
    b.box("Clipboard_clip", (.888, -.314, 1.059), (.101, .035, .064),
          p["gold"], bone="DEF_Hand.R", bevel=.013)
    for row in range(4):
        z = .974 - row * .058
        b.box("Sorting_check", (.803, -.304, z), (.025, .012, .026),
              p["uniform"], bone="DEF_Hand.R", bevel=.005)
        b.box("Sorting_line", (.908, -.304, z), (.126, .012, .010),
              p["dark"], bone="DEF_Hand.R", bevel=.003)


def _bibi(b, p):
    b.limbs(p["fur"], shoe=p["gold"], hand=p["fur"], radius=.105,
            omit_arms=True)
    _uniform(b, p, body_scale=(.47, .35, .49), buttons=2)
    b.ell("Baby_owl_head", (0, .015, 1.83), (.605, .425, .598), p["fur"],
          segments=40, rings=28)
    for side, suffix in ((-1, "L"), (1, "R")):
        ear = b.extra("OwlTuft." + suffix, (side * .40, .026, 2.17),
                      (side * .51, .026, 2.57))
        b.ell("Owl_tuft_" + suffix, (side * .459, .025, 2.365),
              (.138, .101, .232), p["fur"], bone=ear,
              rotation=(0, side * .36, 0), segments=24, rings=16)
        b.ell("Owl_tuft_lining_" + suffix, (side * .464, -.066, 2.373),
              (.066, .023, .132), p["leather"], bone=ear,
              rotation=(0, side * .36, 0), segments=20, rings=12)
        b.ell("Heart_face_disc_" + suffix, (side * .223, -.343, 1.858),
              (.303, .119, .37), p["cream"],
              rotation=(0, -side * .13, 0), segments=32, rings=22)
        b.ell("Wing_upper_" + suffix, (side * .631, -.019, 1.182),
              (.22, .128, .297), p["fur"], bone="DEF_UpperArm." + suffix,
              rotation=(0, -side * .51, 0), segments=28, rings=18)
        b.ell("Wing_forearm_" + suffix, (side * .796, -.095, .984),
              (.162, .10, .255), p["fur"], bone="DEF_Forearm." + suffix,
              rotation=(0, -side * .47, 0), segments=24, rings=16)
        for feather in range(3):
            b.ell("Wing_feather_" + suffix + str(feather),
                  (side * (.745 + feather * .069), -.174, .966 - feather * .032),
                  (.045, .029, .137), p["cream"],
                  bone="DEF_Forearm." + suffix, rotation=(0, -side * .47, 0),
                  segments=16, rings=12)
    b.face(center=(0, -.496, 1.889), spread=.237, scale=1.12)
    # Beak is between the eye line and the builder's smiling mouth.
    b.cone("Little_owl_beak", (0, -.505, 1.895), (0, -.583, 1.803),
           .068, p["gold"], radius_end=.018, sides=20)
    _cap(b, p, center=(.095, .025, 2.352), scale=(.325, .285, .118), tilt=-.20)
    _satchel(b, p, side=-1, z=.775, width=.445)
    # The upside-down route map is a recognizable prop without requiring text.
    b.box("Lost_route_map", (.904, -.238, .889), (.35, .055, .32),
          p["paper"], bone="DEF_Hand.R", bevel=.025)
    b.tube("Meandering_map_route", [(.78, -.276, .98), (.88, -.278, .974),
                                    (.844, -.278, .873), (.972, -.276, .795)],
           .013, p["leather"], bone="DEF_Hand.R", sides=8)
    b.star("Map_destination", (.973, -.282, .797), .034, .014, p["gold"],
           bone="DEF_Hand.R", points=5)
    for x, z in ((.793, .820), (.967, .970)):
        b.cone("Map_tree", (x, -.282, z - .02), (x, -.282, z + .033),
               .025, p["uniform"], bone="DEF_Hand.R", radius_end=.004, sides=8)
    tail = b.extra("OwlTail", (0, .30, .77), (0, .57, .59), parent="DEF_Body")
    for dx in (-.11, 0, .11):
        b.ell("Owl_tail_feather", (dx, .413, .681), (.09, .219, .09),
              p["fur"], bone=tail, rotation=(.28, 0, -dx),
              segments=20, rings=14)


def _mori(b, p):
    b.limbs(p["cream"], shoe=p["leather"], hand=p["cream"], radius=.107)
    _uniform(b, p, body_scale=(.50, .37, .52), buttons=2)
    _shoe_trim(b, p)
    # Soft capsule quills fan around the head and continue over the back.
    # They sit behind the pale face and never cover the eyes or mouth.
    for row, y in enumerate((.07, .255, .383)):
        count = 13 if row < 2 else 11
        for i in range(count):
            a = -1.39 + 2.78 * i / (count - 1)
            spread = .545 if row < 2 else .45
            cx = spread * sin(a)
            cz = 1.80 + (.493 if row < 2 else .40) * cos(a)
            b.ell("Soft_quill_%d_%02d" % (row, i), (cx, y, cz),
                  (.092, .105, .232 if row < 2 else .21),
                  p["dark"] if (i + row) % 3 else p["fur"],
                  rotation=(0, a, 0), segments=16, rings=12)
    b.ell("Hedgehog_head", (0, -.004, 1.77), (.545, .422, .498), p["fur"],
          segments=36, rings=24)
    b.ell("Pale_hedgehog_face", (0, -.378, 1.767), (.468, .139, .43),
          p["cream"], segments=36, rings=24)
    for side, suffix in ((-1, "L"), (1, "R")):
        ear = b.extra("HedgehogEar." + suffix, (side * .394, -.018, 2.024),
                      (side * .477, -.015, 2.18))
        b.ell("Hedgehog_ear_" + suffix, (side * .45, -.039, 2.092),
              (.12, .08, .145), p["fur"], bone=ear, segments=24, rings=16)
        b.ell("Hedgehog_ear_lining_" + suffix, (side * .451, -.112, 2.094),
              (.066, .020, .088), p["leather"], bone=ear,
              segments=20, rings=12)
    b.face(center=(0, -.548, 1.789), spread=.196, scale=.94)
    b.ell("Hedgehog_button_nose", (0, -.584, 1.777), (.056, .035, .044),
          p["dark"], segments=20, rings=12)
    # A tiny tilted beret leaves the distinctive quill crown clearly visible.
    b.ell("Collector_beret", (-.20, -.022, 2.228), (.268, .26, .102),
          p["uniform"], rotation=(0, -.18, 0), segments=28, rings=18)
    b.ell("Beret_nub", (-.22, -.022, 2.332), (.04, .04, .053),
          p["gold"], segments=16, rings=10)
    b.star("Beret_badge", (-.20, -.273, 2.231), .05, .018, p["gold"])
    _satchel(b, p, side=-1, z=.79, width=.46)
    # A large stamp album provides six broad, readable stamp motifs.
    b.box("Stamp_album", (.89, -.217, .884), (.37, .12, .416), p["dark"],
          bone="DEF_Hand.R", bevel=.038)
    b.box("Album_page", (.89, -.288, .884), (.322, .029, .372), p["paper"],
          bone="DEF_Hand.R", bevel=.018)
    for row in range(3):
        for col in range(2):
            x = .811 + col * .153
            z = .991 - row * .108
            color = p["uniform"] if (row + col) % 2 else p["gold"]
            b.box("Collected_stamp_%d_%d" % (row, col), (x, -.315, z),
                  (.111, .018, .081), color, bone="DEF_Hand.R", bevel=.011)
            b.star("Stamp_motif_%d_%d" % (row, col), (x, -.329, z),
                   .022, .012, p["paper"], bone="DEF_Hand.R", points=5)
    tail = b.extra("HedgehogTail", (0, .31, .75), (.055, .50, .68),
                   parent="DEF_Body")
    b.ell("Tiny_hedgehog_tail", (.026, .421, .714), (.075, .155, .078),
          p["fur"], bone=tail, rotation=(.22, 0, -.1), segments=20, rings=12)


_DESIGNS = {
    "PipiRabbit": (_pipi, ("F4DEC4", "FFF0DC", "415956", "498F87",
                            "E4B759", "CA8065", "FFF5DB")),
    "DodoBear": (_dodo, ("BA8658", "F1D1A0", "684A43", "738C69",
                         "E9BE67", "B96545", "FFF0CF")),
    "ToriSquirrel": (_tori, ("DE975C", "F8DCAC", "69452E", "6D97A0",
                             "E4BB63", "914E43", "F9F1DC")),
    "BibiOwl": (_bibi, ("928CB0", "F3E5CE", "55496D", "5C999B",
                        "E6B666", "BE8090", "FFF2D7")),
    "MoriHedgehog": (_mori, ("B08B69", "F4D7AD", "665046", "B87963",
                             "80A391", "8C604B", "FFF0D2")),
}


def build(b, key):
    """Build one forest post-office character using the documented builder API."""
    if key not in _DESIGNS:
        raise ValueError("Unknown forest character: %s; expected %s" % (key, KEYS))
    fn, colors = _DESIGNS[key]
    fn(b, _palette(b, key, colors))
