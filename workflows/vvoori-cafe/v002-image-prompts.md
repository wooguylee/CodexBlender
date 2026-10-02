# vvoori-cafe v002 이미지 생성 기록

2026-10-02. 사용자 정정: Blender 렌더 추출이 아니라 이미지 생성 도구로 공원과 카페를 새로 만든 후 활용한다.

생성 도구: built-in `image_gen` (CLI/API fallback 미사용).

최종 생성 원본은 `assets/vvoori-cafe/v002/ai-autumn-park.png`, `ai-cafe-foreground.png`이며, 모두 새 v002 Blender 원본에 pack한다. 생성 원본의 RGBA를 보존한다. v001은 의도와 달랐던 Blender 렌더 추출본으로 보존하며 v002와 구분한다.

## 공원 생성 프롬프트

```text
Use case: photorealistic-natural.
Asset type: BACKGROUND PLATE for vvoori-cafe, a 16:9 layered cinematic animation.
Create a brand-new photographic image, NOT a 3D render, of a beautiful real autumn park in clear warm 3 pm sunlight, seen straight across a narrow quiet two-way street from a cafe-height viewpoint. Natural Korean neighborhood park atmosphere, mature maple and ginkgo trees with irregular airy orange, amber, yellow and russet foliage, patches of green, inviting footpath, two modest empty wooden benches, authentic bark and scattered fallen leaves on the ground. Warm peaceful cozy atmosphere, convincing detailed photography, restrained color, no artificial bloom.
Composition is technically important: landscape 16:9, ideally 1920x1080 or larger. Static level camera, approximately 1.65m height, moderate wide-angle 35mm feel, straight vertical trees. The road runs horizontally from the LEFT edge to the RIGHT edge, parallel to the camera, NOT a road receding toward a vanishing point. Far curb at approximately 68 percent of image height; dark gray asphalt occupies approximately 69 to 85 percent height; near curb and sidewalk fill the bottom 15 percent. The park occupies the area ABOVE the far curb; branches and foliage fill much of the top, with soft clear pale blue sky visible between trees. The road must stay open and fully visible along its whole width for later animated cars. Late afternoon sun comes from upper left and casts soft coherent shadows to the right.
This is ONLY the outdoor plate: no cafe interior, NO window frame, NO glass overlay, no furniture in front of the camera. No cars, no people, no bicycles, no airborne leaves, no lettering, no watermarks, no split panels. Full-bleed opaque image.
```

## 카페 전경 생성 프롬프트

공원 생성 이미지는 광원/원근 참고로만 제공했다.

```text
Use case: photorealistic-natural with background-extraction.
Asset type: a newly generated photorealistic CAFE FOREGROUND RGBA OVERLAY for a 16:9 cinematic composite.
The supplied image is ONLY a supporting reference for the outdoor lighting and camera perspective. Design a NEW beautiful cozy cafe interior as a separate foreground layer. Output ONLY the interior cafe elements, with GENUINE ALPHA TRANSPARENCY through the entire window area. Do NOT paint the supplied park, road, trees or sky into the output.
Camera is a fixed seated/standing viewpoint inside the cafe at about 1.65m height, facing a large straight wall of floor-to-ceiling picture windows. Warm honey oak and softly textured cream plaster, slim dark bronze window mullions, a low oak sill at 82 percent image height, a ceiling/header occupying the top 7 percent, minimal side wall strips at the two edges. Two slim vertical mullions at approximately 18 and 82 percent of width. The vast middle window panes from about 10 to 82 percent of image height must be transparent, not white, black, grey or checkerboard. No glass reflections or tint over those openings.
An intimate round natural oak table enters from the lower left, reaching up to about 80 percent image height, with one elegant ivory cappuccino cup and saucer, a small croissant on a ceramic plate, one closed unlettered book and a delicate tiny vase. A soft olive-green upholstered cafe chair appears at the lower right, reaching to about 68 percent image height. Two tasteful cream linen pendant lights hang near the upper left and upper right corners and occupy only small areas near the edges. Sunlight entering from upper left warms the wood and soft fabrics. Calm sophisticated real interior photography, detailed realistic wood grain, linen and ceramic, optical realism, no cartoon forms and no plastic CGI appearance.
Landscape 16:9 frame, ideally 1920x1080 or larger. The foreground floor and interior lower wall fill the bottom area. The visible window should take up most of the frame and let the later separately composited park and cars show through. Preserve the unobstructed large central and lower-middle transparent area down to the sill.
CRITICAL: actual transparent alpha pixels in the window holes; no baked checkerboard, no outdoor view, no people, no text, no logo, no watermark, no decorative split-panel layout. This is a single ready-to-composite cafe foreground image.
```

## 카페 창턱 수정 프롬프트

초안 카페 이미지의 창턱이 도로를 가려 창문 영역을 넓혔다. 생성 도구의 알파 출력을 그대로 저장했다.

```text
Edit the supplied generated cafe foreground overlay. It is the edit target, not an outdoor reference.
Make ONE targeted composition correction: LOWER the horizontal window sill from its current roughly 70% image height to 83% image height, so the window opening extends much farther down and later composited cars on a road can be seen clearly. Keep the top window header, side walls, the two vertical mullions and pendant lights in their current positions. Keep the same beautiful photorealistic materials, warm light and color.
Recompose the lower cafe objects gracefully to fit the smaller bottom zone: the round oak table occupies the bottom left and reaches up to roughly 82% height; cup, croissant, closed book and little vase remain with accurate photo detail, without blocking the broad central window. Keep the olive fabric chair on the extreme lower right. Lower wall below the sill is now a narrow band. Most of the center from 7% to 83% image height is the open window.
Retain genuine ALPHA TRANSPARENCY in all window openings. The solid cafe furniture, wood, ceiling and walls must be fully opaque; only antialiased edges are semitransparent. Do not include any outside park, sky, road, glass reflection or solid window fill. Do not paint a checkerboard or fake transparency. No text. Preserve 16:9 framing.
```
