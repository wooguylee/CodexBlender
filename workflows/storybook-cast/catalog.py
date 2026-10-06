THEMES={
 'Forest':{'ko':'숲속 우체국 친구들','module':'theme_forest','color':'DCEADB','characters':[
  ('PipiRabbit','삐삐','토끼 집배원'),('DodoBear','도도','곰 우체국장'),('ToriSquirrel','토리','다람쥐 분류원'),('BibiOwl','비비','아기 부엉이'),('MoriHedgehog','모리','우표 수집 고슴도치')]},
 'Dessert':{'ko':'한입 디저트 마을','module':'theme_dessert','color':'F5E2DC','characters':[
  ('PuruPudding','푸루','수줍은 푸딩'),('MomoMochi','모모','딸기 찹쌀떡'),('PanBread','팡이','다정한 식빵'),('RoniMacaron','로니','멋쟁이 마카롱'),('ShushuPuff','슈슈','슈크림 요리사')]},
 'Space':{'ko':'꼬마 우주 정비소','module':'theme_space','color':'DDE1F3','characters':[
  ('PokoAlien','포코','아기 외계인'),('BoltRobot','볼트','네모 로봇'),('LunaRabbit','루나','별 모으는 달토끼'),('TwinkleStar','반짝','별 생물'),('PingoPenguin','핑고','우주 길잡이 펭귄')]},
 'Sea':{'ko':'바닷속 작은 구조대','module':'theme_sea','color':'D8ECEE','characters':[
  ('OctoOctopus','옥토','겁 많지만 용감한 문어'),('TutuTurtle','투투','느긋한 거북이'),('BobaPuffer','보바','성급한 복어'),('KikiHermit','키키','소라게 수리공'),('HaniSeahorse','하니','해마 응급대원')]}}
CLIPS=[('Idle',49,True),('Walk',49,True),('Run',49,True),('SitDown',37,False),('SitIdle',49,True),('StandUp',37,False),('Wave',49,False),('Celebrate',49,False)]
SWIMMERS={'BobaPuffer','HaniSeahorse'}

def clip_ranges():
    result=[];start=1
    for name,length,loop in CLIPS:
        result.append({'name':name,'first':start,'last':start+length-1,'loop':loop,'fps':24});start+=length
    return result
