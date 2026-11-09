"""Authored explanations, worked examples and minimal pairs for the core course.

The original lesson titles, examples, questions and unit IDs remain unchanged.
"""

DETAILS = {}


def _add(key, sections, analyses, comparisons):
    assert key not in DETAILS, key
    blocks = []
    for line in sections.strip().splitlines():
        title, text = line.strip().split(" | ", 1)
        blocks.append(dict(title=title, paragraphs=text.split(" // ")))
    notes = [line.strip() for line in analyses.strip().splitlines()]
    pairs = [line.strip().split(" | ") for line in comparisons.strip().splitlines()]
    assert len(blocks) >= 3 and len(notes) == 2 and len(pairs) == 2, key
    assert all(len(pair) == 3 for pair in pairs), key
    DETAILS[key] = dict(sections=blocks, notes=notes, comparisons=pairs)


def enrich_lessons(topic_id, topic):
    for index, lesson in enumerate(topic["lessons"]):
        key = f"{topic_id}:{index}"
        detail = DETAILS.get(key)
        if detail is None:
            if topic.get("reference"):
                raise ValueError(f"Missing detailed explanation: {key}")
            continue
        assert len(lesson["examples"]) == len(detail["notes"]), key
        lesson["sections"] = detail["sections"]
        lesson["exampleNotes"] = {example[0]: note for example, note in zip(lesson["examples"], detail["notes"])}
        lesson["comparisons"] = detail["comparisons"]


_add("bs:0", """
Türkçeden İngilizceye cümle kurmak | Türkçedeki 'Kardeşim hemşire' cümlesinde ayrı bir fiil görmeyebilirsin. İngilizcede bu tür kimlik, meslek ve durum bildirimlerinde be bağlantıyı kurar: My brother is a nurse. Önce kimin hakkında konuştuğunu, sonra onun hakkında ne söylediğini belirle.
Be biçimini seçmek | I ile am; he, she, it ve tek bir kişi/şey ile is; you, we, they ve çoğullarla are kullanılır. Olumsuz yaparken not ekle. Soru yaparken aynı be biçimini öznenin önüne taşı; ayrıca do ekleme. 'Is your brother a nurse?' ile 'Your brother is a nurse' aynı bilgiyi farklı amaçla kullanır.
Eylem cümlesiyle farkı | 'She is happy' bir durumu, 'She works' bir eylemi anlatır. Her İngilizce fiilin önüne is koyulmaz. 'She is working' ise başka bir yapıdır: is yardımcı fiil, working asıl fiilin -ing biçimidir. Kısa cevapta tamamlayıcı tekrarlanmaz: Yes, she is; No, she isn't.
""", """
My brother tek bir kişiyi gösterir; bu yüzden is seçilir. A nurse bir meslek grubuna üyeliği belirtir. Türkçede 'bir hemşire' demesek de İngilizcede tekil meslek adı a alır.
Your parents çoğuldur; are gerekir. Yer bilgisi at home aynen kalır, yalnızca are soru için başa taşınır. Kısa olumlu cevap Yes, they are olabilir.
""", """
She [is] a teacher. | O öğretmen. | Kimlik/meslek bildirimi: be cümlenin çekimli fiilidir.
She [teaches] English. | O İngilizce öğretir. | Eylem bildirimi: teach kendi başına çekimlenir; is eklenmez.
""")
_add("bs:1", """
Cümledeki göreve göre zamir | Aynı kişi farklı görevlerde farklı zamirle gösterilir. 'She called me' cümlesinde arayan she, aranan me'dir. 'I called her' dediğinde roller değişir. Fiilin önünde özne biçimi, birçok fiil ve edattan sonra nesne biçimi gerekir: with him, for us, to them.
My ile mine neden farklı? | My, her, our gibi sözcükler ardından gelen ismi belirler: my phone. Mine, hers, ours ismin yerini de üstlenir: This phone is mine. Her iki yapıyı üst üste kullanıp 'mine phone' denmez. His iki konumda da aynı yazılır; her ile hers ise farklıdır.
Sahiplik ve kısaltma ayrımı | Its 'onun ...sı', it's ise it is veya it has anlamındadır. Sözcüğü açarak kontrol et: 'The dog is wagging it is tail' anlamlı olmaz; burada its gerekir. Ours/yours/theirs gibi sahiplik zamirlerine apostrof eklenmez. Kendim/kendisi anlamındaki myself/herself farklı bir konudur.
""", """
Call eylemi emir biçimindedir; konuşulan kişiden bir kadını araması istenir. Aranan kişi fiilin nesnesi olduğu için she değil her kullanılır. Tonight, arama zamanını belirtir.
Seats ismi başta zaten söylenmiştir; ours hem sahipliği hem 'our seats' ifadesinin yerini taşır. Bu nedenle ours'tan sonra yeniden seats getirilmez.
""", """
This is [our] room. | Bu bizim odamız. | Our, room isminin önünde sahiplik belirler.
This room is [ours]. | Bu oda bizim. | Ours tek başına 'bizim odamız/bize ait' bilgisini verir.
""")
_add("bs:2", """
Sahip olmak mı, bir yerde bulunmak mı? | 'Bahçede bir kedi var' bir varlık tanıtır; 'Kız kardeşimin kedisi var' sahiplik bildirir. İlkinde There is a cat in the garden, ikincisinde My sister has a cat kullanılır. İngilizcede her Türkçe 'var' sözcüğünü have ile karşılayamazsın.
Yapıyı adım adım seçmek | Have cümlesinde gerçek özneyi bul: my sister üçüncü tekildir, has kullan. There is/are yapısında ardından gelen isim grubuna bak: a cat tekil, two cats çoğul, milk sayılamayandır. Bu nedenle there is milk ama there are two cats denir.
Soru ve olumsuzluk | 'Does she have a car?' sorusunda does tekil bilgisini taşır, have yalın kalır. 'Is there a car outside?' sorusunda is zaten fiildir; do eklenmez. Sahiplikte have got da yaygındır: Has she got a car? İki soru düzenini karıştırıp 'Does she has got' kurma.
""", """
Özne our house tekildir; bu nedenle has kullanılır. Sahip olunan şey a small garden'dır. Cümle bir evi tanımlıyor; bir yerde yeni bir nesne olduğunu tanıtmıyor.
There are ile masadaki üç fincan ilk kez tanıtılıyor. Three cups çoğul olduğu için are seçilir; on the desk yer bilgisidir. 'The desk has three cups' aynı doğal varlık anlatımı değildir.
""", """
We [have] a car. | Arabamız var. | Sahibi biziz; have sahiplik bildirir.
[There is] a car outside. | Dışarıda bir araba var. | Arabanın kime ait olduğu değil, dışarıdaki varlığı anlatılır.
""")
_add("bs:3", """
Do yardımcı fiilinin görevi | Asıl fiil like, live veya need olduğunda present simple soru ve olumsuzluğu çoğunlukla do/does taşır. Olumlu 'She lives here' cümlesindeki -s, soruda does'a geçer: Does she live here? Yardımcı geldikten sonra asıl fiilde aynı çekimi ikinci kez gösterme.
Sorunun parçaları | Yes/no sorusunda sıra yardımcı + özne + yalın fiildir. Wh- sorusunda soru sözcüğü bunun önüne gelir: Where does she live? Kısa cevapta asıl fiil tekrarlanmaz: Yes, she does. Be ve can gibi yapılar kendi sorusunu kurar: Is she ready? Can she swim?
Emrin öznesi neden görünmüyor? | 'Open the window' cümlesinde komutu alan you anlaşılır ama genellikle yazılmaz. Fiil yalındır. Olumsuz emirde don't kullanılır; bu düzen be ile de görülür: Don't be late. Please eklemek ifadeyi yumuşatabilir; her emir doğrudan kaba olmak zorunda değildir.
""", """
Need asıl fiildir ve özne you'dur; soru için do gelir. Ticket tekil sayılabilen bir nesne olduğu için a ticket denir. Cevap Yes, I do olabilir; Yes, I need demek yeterli kısa cevap değildir.
Konuşan sıcak tavaya dokunulmamasını istiyor. Bu bir şimdiki zaman durumu değil, olumsuz talimattır. Don't + touch kurulur; doesn't veya not touch kullanılmaz.
""", """
[Does] she work here? | O burada mı çalışıyor? | Work asıl fiildir; soru yardımcı does ile kurulur.
[Is] she at work? | O işte mi? | Yer/durum cümlesinin fiili is'tir; do eklenmez.
""")

_add("tn:0", """
Geniş zamanın bakış açısı | Present simple, olayı şu anın içinden izlemek yerine kişinin düzeninin veya dünyanın genel bir özelliği olarak sunar. 'I work in a bank' dediğinde konuşma anında bankada olman gerekmez. Bu bir iş/durum bilgisidir. Alışkanlık, genel gerçek ve belirli tarifeler bu bakışla anlatılabilir.
Çekim ve yazım | I/you/we/they ile V1; he/she/it ile fiilin -s biçimi kullanılır. Watch → watches, study → studies; play → plays olur. Ünsüz + y değişir, ünlü + y değişmez. Soru ve olumsuzlukta does/doesn't tekil çekimi üstlenir: Does she study? She doesn't study. Asıl fiilde -s kalmaz.
Sıklık zarflarının yeri | Usually, often, never gibi zarflar çoğunlukla asıl fiilden önce gelir: I usually walk. Be ile ise arkasına gelir: She is usually early. Never zaten olumsuz anlam taşır; standart kullanımda ayrıca don't ekleme. Every day cümlenin başında veya sonunda bulunabilir.
Anlam sınırları | Türkçedeki '-yor' her zaman present continuous değildir: 'Bu müzikten hoşlanıyorum' çoğunlukla I like this music olur. Like/know gibi durum fiillerinde present simple doğaldır. 'The train leaves at six tomorrow' tarifeli gelecektir; bu nedenle present simple'ı yalnızca 'her gün' ile sınırlama.
""", """
The bakery tekil bir işletmedir; open fiili opens olur. Every morning ve at six, fırının düzenli açılış saatini verir. Cümle, kapının tam şu anda açılmasını değil çalışma düzenini anlatır.
Özne you olduğu için do kullanılır. Usually, düzenli davranışı sorar. Soru sırası do + you + usually + walk'tur; walk yalın kalır. Kısa cevap Yes, I do olabilir.
""", """
I [read] before bed. | Yatmadan önce kitap okurum. | Okuma benim genel alışkanlığım; şu anda kitap açık olmak zorunda değil.
I [am reading] before bed tonight. | Bu akşam yatmadan önce kitap okuyorum/okuyacağım. | Belirli bu akşama ait geçici faaliyet veya düzenleme öne çıkar.
""")
_add("tn:1", """
Sürmekte olan olay ne demek? | Present continuous olayı bir süreç olarak, belirli bir şimdiki dönem içinde gösterir. 'I am studying for an exam' dediğinde o saniye elinde kitap bulunmayabilir; bu günlerdeki geçici uğraşını anlatabilirsin. Şimdiki dönem, konuşma anından daha geniş olabilir.
Üç parçayı birlikte kurmak | Önce özneye uygun am/is/are seçilir; sonra asıl fiilin -ing biçimi gelir. 'He is working' yapısında zamanı ve özne uyumunu is taşır. Olumsuzda is not working, soruda Is he working? kurulur. -Ing tek başına çekimli fiil sayılmaz; 'He working' eksiktir.
Yazım ve durum fiilleri | Make → making, run → running, lie → lying olur; her fiilde rastgele harf düşürülmez. Know, own, believe temel durum anlamlarında genellikle continuous kullanılmaz. Bazı fiiller anlam değiştirir: I think you're right bir fikir; I'm thinking about it zihinsel bir uğraştır.
Geçici durum ve gelecek düzenlemesi | 'She is staying with us this week' geçici konaklamayı vurgular. 'She is staying with us next weekend' ise ayarlanmış gelecek düzenlemesi olabilir. Yapı aynı kalır; zaman ifadesi ve bağlam hangi anlamın seçildiğini gösterir. Bu nedenle yalnızca now görünce kullanılacak bir yapı değildir.
""", """
The children çoğuldur; are seçilir. Building, yapılmakta olan etkinliği gösterir. Now mevcut sürece odaklar. Yalnızca 'The children building' demek yardımcı fiili eksik bırakır.
Isn't, is not kısaltmasıdır; sleeping olumsuzlanan eylemdir. At the moment bu andaki durumu sınırlar. Bu cümle, onun genel uyku alışkanlığı hakkında bir hüküm vermez.
""", """
She [lives] in Ankara. | Ankara'da yaşıyor. | Yerleşik durum, düzenli yaşam bilgisi olarak sunulur.
She [is living] in Ankara for a few months. | Birkaç aylığına Ankara'da yaşıyor. | Aynı yaşam durumu bu kez geçici bir dönem olarak çerçevelenir.
""")
_add("tn:2", """
Aynı Türkçe çeviri neden yetmez? | 'Evden çalışıyorum' hem I work from home hem I'm working from home olabilir. İlkinde olağan çalışma düzenin, ikincisinde şu dönemki faaliyet/düzenin öne çıkar. İngilizce yapı seçimi, yalnızca Türkçe ekin değil konuşanın olaya nasıl baktığının sonucudur.
Karar vermek için sorular | Önce bunun genel alışkanlık/durum mu, yoksa belirli dönemdeki geçici faaliyet mi olduğunu sor. Sonra fiilin anlamına bak. Know bir bilgi durumu, work bir faaliyet olabilir. Son olarak zaman ifadesini kontrol et. Bir işaret sözcüğü tek başına bütün cümlenin anlamını belirlemez.
Anlamı değişen fiiller | Have a car sahipliktir: I have a car. Have lunch bir etkinliktir: I'm having lunch. See someone bazen görmek, bazen görüşmek demektir: I see your point / I'm seeing the doctor tomorrow. Fiilin sözlükteki başlığından çok o cümledeki anlamı önemlidir.
Özel kullanımlar | Always + continuous bazen tekrar eden davranışa yönelik duyguyu gösterir: You're always losing your keys! Buradaki yakınma, always sözcüğünün otomatik present simple gerektirmediğini gösterir. Başlangıçta temel ayrımı öğren; sonra bu duygusal vurguyu ayrı bir kullanım olarak tanı.
""", """
Usually kısmı alışkanlık olduğu için cycles; today kısmı alışkanlığın dışındaki belirli gün olduğu için is walking seçilir. He iki bölümde de aynı özne olsa da konuşanın zaman bakışı değişir.
Believe bu cümlede devam eden bir fiziksel faaliyet değil, bir kanaat durumudur. Türkçedeki 'inanıyorum' ekine bakıp am believing seçilmez; I believe doğal temel biçimdir.
""", """
I [have] two brothers. | İki erkek kardeşim var. | Have, sahiplik/aile ilişkisi bildirir; durum fiili gibi kullanılır.
I [am having] breakfast. | Kahvaltı yapıyorum. | Have bu kez bir etkinliğin parçasıdır; süreç olarak gösterilebilir.
""")
_add("tn:3", """
Geçmişe nereden bakıyoruz? | Past simple olayı bitmiş bir geçmiş çerçevenin içinde sunar. Yesterday, in 2020 gibi bir ifade bulunabilir; bazen geçmiş çerçeve konuşmadan zaten anlaşılır. 'How was the trip?' sorusundan sonra 'We visited a village' demek için tarihi her cümlede tekrar etmek gerekmez.
Düzenli ve düzensiz çekim | Düzenli fiillerde work → worked, study → studied olur. Düzensizlerde go → went, see → saw gibi V2 öğrenilir. Olumlu cümlede V2 kullanılır; did/didn't geldiyse fiil V1'e döner. Bütün öznelerde did aynıdır: Did she go? They didn't go.
Be neden ayrı? | Be fiilinin geçmişi I/he/she/it ile was, you/we/they ile were'dür. Bu fiil soru kurarken yer değiştirir: Were they tired? 'Did they be tired?' temel geçmiş durum sorusu değildir. Diğer asıl fiillerle soru kurma düzenini be'ye zorla uygulama.
Olay sırası ve bugünkü sonuç | 'She opened the door, entered and sat down' tamamlanmış olayları ilerletir. Geçmişte olan bir şeyin bugünkü sonucu bulunması past simple'ı yanlış yapmaz. 'I lost my key yesterday, so I can't get in' doğrudur; yesterday bitmiş zaman bakışını belirler.
""", """
Last Saturday olayın bittiği geçmiş günü verir. Visit düzenli fiildir, visited olur. We çoğul olsa da past simple'daki düzenli fiilin biçimi değişmez; visits kullanılmaz.
Soruyu kuran yardımcı did olduğu için send yalın kalır. Sent, olumlu geçmiş cümlede kullanılır: She sent the email. 'Did she sent' aynı geçmiş işaretini iki kez yükler.
""", """
I [lost] my key yesterday. | Dün anahtarımı kaybettim. | Kaybetme olayı bitmiş bir geçmiş güne yerleştirilir.
I [have lost] my key. | Anahtarımı kaybettim. | Şimdiye bağlı sonuç öne çıkar; bitmiş bir geçmiş gün belirtilmez.
""")
_add("tn:4", """
Geçmişte bir sahnenin içinde olmak | Past continuous, geçmişteki referans anında eylemin içindeymişiz gibi bakar. 'At ten, I was driving' sürüşün onda başladığını söylemez; onda sürüş devam ediyordu. Eylemin ne zaman başladığını veya sonra bitip bitmediğini bu yapı tek başına bildirmez.
Kuruluş ve kısa cevap | Was/were özneye göre seçilir, asıl fiil -ing alır. Olumsuzluk yardımcıya eklenir: wasn't driving. Soruda yardımcı öne gelir: Were you driving? Kısa cevap Yes, I was / No, I wasn't biçimindedir; driving'i tekrar etmen gerekmez.
Hikâyede arka plan | Yağmur, insanların yaptığı işler ve olay anındaki durumlar bu yapıyla sahne oluşturabilir: It was raining and people were running. İki uzun eylem de eş zamanlı olabilir: I was cooking while he was washing up. Her continuous cümlede bir kesinti olmak zorunda değildir.
Süre ve tamamlanma farkı | 'I worked for two hours' tamamlanan bir çalışma dönemini bildirir. 'At eight, I was working' bir anın içindeki faaliyeti gösterir. Süre uzun diye continuous seçilmez; geçmişte yıllar süren tamamlanmış işler de past simple ile anlatılabilir.
""", """
At midnight referans anıdır. Was reading o anda devam eden okumayı gösterir. Kitaba ne zaman başlandığı ve kaçta bitirildiği belirtilmemiştir; ikisini de kendiliğinden çıkaramayız.
The children çoğul olduğu için were kullanılır. Playing, senin varış anındaki faaliyeti; arrived o sahneye bağlanan tamamlanmış gelişi gösterir. Soru, çocukların o anda ne yaptığını kontrol eder.
""", """
At eight, I [was cooking] dinner. | Saat sekizde yemek pişiriyordum. | Sekizde pişirme sürecinin içindeydim.
I [cooked] dinner at eight. | Saat sekizde yemek pişirdim. | Pişirmeyi geçmişte gerçekleşen olay olarak sunuyorum.
""")
_add("tn:5", """
Uzun eylem ve kısa olay ilişkisi | İki yapıyı birlikte kullanırken asıl ayrım uzunluk saymak değil, arka plan ile tamamlanmış olay arasındadır. 'I was walking when I saw her' cümlesinde yürüyüş sahne, görme olaydır. Her uzun fiil continuous, her kısa fiil simple olmak zorunda değildir.
When ve while birer ipucu | While çoğu kez devam eden faaliyet tanıtır. When tek bir olay anını veya daha geniş dönemi tanıtabilir. 'When I lived in Izmir, I walked to work' cümlesinde lived ve walked past simple'dır. Bağlacı görüp otomatik zaman seçmek yerine iki eylemin ilişkisini çöz.
Kesinti, eş zamanlılık ve sıra | 'I was reading when she called' iki eylemin aynı ana bağlandığını söyler; okumanın tamamen bırakıldığını mutlaka söylemez. İki süreç 'while' ile yan yana ilerleyebilir. 'I opened the letter and read it' ise tamamlanan olayları art arda sıralar.
Bir cümleyi çözme yöntemi | Önce sahnenin hangi anda kurulduğunu bul. O anda devam eden iş için was/were + -ing düşün. Sonra gerçekleşen olayı V2 ile göster. Son olarak her iki bölümdeki özne ve yardımcı uyumunu kontrol et; 'they was' gibi ayrı bir çekim hatası yapma.
""", """
Painting devam eden arka plandır; was painting bu bakışı verir. Rang, zilin o sırada gerçekleşen çalmasıdır. Cümle, resim yapmanın ne kadar sürdüğünü veya zil yüzünden kesin bırakıldığını söylemez.
While we were walking ortak sahneyi kurar. Found, yürüyüş sırasında gerçekleşen bulma olayıdır. Find fiilinin V2'si found olduğu için 'were found' kullanmak burada yanlış bir passive anlamı doğurur.
""", """
When she arrived, I [was eating]. | O geldiğinde yemek yiyordum. | Geliş anında yemek yeme devam ediyordu.
When she arrived, I [ate]. | O gelince yemek yedim. | Yemek yemeyi o gelişle bağlantılı gerçekleşen olay olarak sunarım; önce başlamış olması gerekmez.
""")
_add("tn:6", """
Perfect neden yalnızca geçmiş zaman değildir? | Present perfect geçmişe bugünkü noktadan bakar. 'I have lost my ticket' cümlesinde bugünkü bilet sorunu önemlidir. Yapıyı yalnızca '-di' ekiyle eşleştirmek eksik kalır; Türkçe çeviri benzer görünse de konuşanın referans noktası şimdidir. // Üç temel kullanım vardır: şimdiye kadarki deneyim, şimdiki sonucu olan olay ve geçmişte başlayıp süren durum. 'I have visited Rome', 'I have broken my glasses' ve 'I have known her for years' aynı yapıyı farklı amaçlarla kullanır. Son örnekte tanışıklık bitmiş değildir.
Have/has ve V3 nasıl çalışır? | I/you/we/they have; he/she/it has alır. Asıl fiil V3'tür: see–saw–seen, write–wrote–written. Have burada sahiplik değil yardımcı fiildir. Soruda öne taşınır, olumsuzlukta not alır: Has she written? She hasn't written. Kısa cevap Yes, she has olur; V3 tekrar edilmez.
Bitmiş zaman, açık dönem ve deneyim | Yesterday veya in 2018 gibi bitmiş geçmiş zaman belirtilirse temel kullanımda past simple seçilir. Ever 'şimdiye kadar herhangi bir zaman', never 'şimdiye kadar hiç' anlamı verebilir. Today gibi bir dönem henüz açık olsa bile, konuşan geçmişte tamamlanmış bir bölümüne odaklanıyorsa past simple da mümkün olabilir.
Since, for ve been/gone ayrımı | For uzunluğu, since başlangıç noktasını verir: for five years / since 2020. Been to çoğunlukla gidip dönmüş olma deneyimini, gone to ise bir yere gitmiş ve henüz dönmemiş olmayı anlatır. Just/already/yet sık görülür ama bağlam ve dil çeşidi de önemlidir; Amerikan İngilizcesinde bazı yakın geçmiş kullanımlarında past simple yaygındır.
""", """
Have lost geçmişteki kaybı bugünkü içeri girememe sorununa bağlar. Lost, lose fiilinin hem V2 hem V3 biçimidir; bu cümlede have bulunduğu için V3 görevindedir. Kaybın tam tarihi sorulursa When did you lose it? denebilir.
Have you ever ridden sorusu şimdiye kadarki yaşam deneyimini sorar. Ridden, ride fiilinin V3 biçimidir; rode V2'dir. Olumlu cevaptan sonra ayrıntı verirken I rode one last summer gibi past simple'a geçmek doğaldır.
""", """
She [has been] to Madrid. | Madrid'e gitmişliği var; gidip dönmüş. | Deneyim anlatılır. Madrid'de şu anda bulunması gerektiği söylenmez.
She [has gone] to Madrid. | Madrid'e gitti; henüz geri dönmedi. | Gidişin mevcut sonucu öne çıkar; burada bulunmamasını açıklayabilir.
""")
_add("tn:7", """
Sürece neden odaklanıyoruz? | Present perfect continuous geçmişte başlayan faaliyeti şimdiye uzanan bir süreç olarak sunar. 'I've been waiting' beklemenin süresini, yükünü veya son etkisini öne çıkarabilir. Faaliyet hâlâ devam ediyor olabilir; az önce bitmiş de olabilir. Yapı tek başına 'kesinlikle hâlâ sürüyor' demek değildir.
Dört parçayı kontrol et | Have/has + been + V-ing birlikte gerekir. Have/has özne ve şimdiki referansı, been perfect zincirini, -ing süreç bakışını kurar. 'She has been working' soruda Has she been working? olur. Has sonrasındaki been, is veya was ile değiştirilemez.
Süre, başlangıç ve görünür kanıt | For twenty minutes süreyi, since nine başlangıcı verir. How long çoğu kez bu süreci sorar. 'You're wet. Have you been walking in the rain?' cümlesinde süre verilmez; şu anki ıslaklık yakın geçmiş faaliyetine kanıttır. Bu kullanımda kişinin hâlâ yürümesi gerekmez.
Simple ile ve durum fiilleriyle sınır | 'I've written three pages' tamamlanan miktarı, 'I've been writing' faaliyeti öne çıkarır. Know/own temel durum anlamlarında genellikle have known/have owned kullanılır. Live/work gibi fiillerde iki yapı da uygun olabilir: have lived ve have been living arasında vurgu farkı doğabilir.
""", """
Have been waiting geçmişten şimdiye uzanan beklemeyi süreç olarak gösterir. For twenty minutes bir uzunluktur; since twenty minutes denmez. Cümle, sıranın yeni geldiği anda söylense bekleme az önce bitmiş de olabilir.
Has been gardening yakın geçmiş faaliyetini açıklar; ellerin kirli olması şimdiki sonuçtur. Bahçeyle uğraşma eyleminin o saniye devam ettiği zorunlu değildir. Öznenin he olması has seçimini gerektirir.
""", """
I [have cleaned] the kitchen. | Mutfağı temizledim. | Tamamlanan iş veya elde edilen sonuç öne çıkar.
I [have been cleaning] the kitchen. | Bir süredir mutfağı temizliyorum/temizlemekle uğraşıyordum. | Uğraşın süreci öne çıkar; bütün mutfağın bittiği garanti edilmez.
""")
_add("tn:8", """
Referans noktası seçmek | Past simple olayı bitmiş bir geçmiş çerçevede; present perfect ise şimdiki noktaya kadar uzanan bakışla anlatır. Aynı olay hakkında önce deneyim, sonra geçmiş ayrıntı verilebilir: I've been to Rome. I went there in 2019. İkinci cümle birinciyle çelişmez.
Bitmiş zamanı tespit etmek | Last week, two days ago ve in 2018 açık bitmiş dönemlerdir. Şimdiyle ilgili sonuç bulunsa bile bu zamanları belirtirken genellikle past simple kullanılır. Present perfect'i 'sonucu varsa her zaman bu yapı' diye ezberlemek bu yüzden hatalıdır.
Since ile başlangıç bildirmek | 'I moved here in 2018' taşınma olayını tarihler. 'I have lived here since 2018' ise 2018'den bugüne uzanan yaşamı anlatır. Since sonrasında bir geçmiş olay da olabilir: since I moved here. Bu alt bölümde past simple bulunması ana cümlenin perfect olmasına engel değildir.
Bağlam ve dil çeşidi | Today/this week gibi henüz bitmemiş dönemlerde konuşanın hangi kısmı düşündüğü önemlidir. Amerikan İngilizcesinde just/already/yet ile past simple kullanımı da yaygındır. Temel alıştırmalarda verilen Türkçe anlamı ve açık zaman çerçevesini izle; gerçek kullanımın tek sözcüklük şifrelere sığmadığını unutma.
""", """
Moved tek bir taşınma olayını anlatır; in 2018 onun bitmiş geçmiş zamanıdır. Bu cümleden kişinin bugün hâlâ aynı yerde yaşadığını kesin çıkaramayız; ek bağlam gerekebilir.
Have lived, since 2018 ile başlayan yaşam dönemini bugüne bağlar. Burada 'yaşadık' diye bitmiş bir dönem değil, hâlen süren durum anlatılır. Aynı olay için önceki cümleden farklı bir bakış kurulmuştur.
""", """
I [didn't see] her yesterday. | Dün onu görmedim. | Kontrol edilen dönem dündür ve bitmiştir.
I [haven't seen] her today. | Bugün onu henüz görmedim. | Bugünün şimdiye kadarki kısmı düşünülür; daha sonra görme olasılığı açıktır.
""")
_add("tn:9", """
Bitmişlik ile süreç birer vurgu | Perfect simple her zaman 'bitmiş', continuous her zaman 'bitmemiş' demek değildir. I've known her for years bitmemiş bir durumdur; I've been running sözü koşu az önce bittikten sonra söylenebilir. Daha güvenli ayrım, tamamlanan sonuç/miktar ile faaliyetin sürecine hangi ölçüde odaklanıldığıdır.
How many ve how long | How many pages have you written? tamamlanan miktarı sorar. How long have you been writing? faaliyetin süresini sorar. Sayılabilir bir toplamı bitmiş olarak verirken simple daha uygundur. Süre ifadesi ise tek başına continuous zorunluluğu doğurmaz: I've lived here for years doğrudur.
Fiilin anlamı seçimi etkiler | Know, believe ve own gibi durum fiilleri çoğunlukla simple yapıda kalır. Live, work, study gibi fiillerle iki yapı da mümkün olabilir. 'I've worked here for years' iş geçmişini, 'I've been working here for years' süregelen faaliyeti ve bazen geçicilik hissini öne çıkarabilir.
Sonuç çıkarırken dikkat | 'She's been painting the door' dediğinde boya yapma faaliyeti var ama kapının bütünü bitmiş olmak zorunda değildir. 'She's painted the door' tipik bağlamda tamamlanan işi gösterir. Yalnızca cümle yapısından kişinin kaç dakika çalıştığını veya ne kadar yorulduğunu çıkaramayız.
""", """
Has painted iki kapının tamamlandığını sayar. Two doors belirli bir iş miktarıdır; konuşan tamamlanan sonucu öne çıkarır. Today henüz bitmemiş olabilir ve şimdiki toplam için present perfect uygundur.
Has been painting faaliyeti, since breakfast ise başlangıç noktasını belirtir. Kaç kapının bittiği söylenmez. Bu cümle, tamamlanan miktarı değil ne zamandan beri uğraşıldığını öğrenmemizi sağlar.
""", """
They [have repaired] four bikes. | Dört bisikleti tamir ettiler. | Tamamlanan miktar dört olarak belirtilir.
They [have been repairing] bikes all morning. | Bütün sabah bisiklet tamiriyle uğraşıyorlar. | Faaliyet ve süre öne çıkar; biten bisiklet sayısı verilmez.
""")

_add("tn:10", """
İki geçmiş noktayı ayırmak | Past perfect'in referansı şimdi değil, geçmişteki başka bir andır. Önce geçmiş sahneyi kur: 'I arrived at nine.' Sonra o sahneden daha önce olanı anlat: 'The guests had left.' Had left, ayrılışın dokuzdaki varıştan önce tamamlandığını gösterir; aradaki sürenin uzun olması gerekmez.
Had ve V3 nasıl seçilir? | Bütün öznelerle had kullanılır. Olumsuzda hadn't + V3, soruda Had + özne + V3 gerekir. 'Had she gone?' yapısında gone V3'tür; went V2 olduğu için had went denmez. Had burada sahiplik anlamındaki geçmiş have fiiliyle karıştırılmamalıdır.
Her eski olayda gerekli mi? | Before/after gibi sözcükler sıra ilişkisini açıkça verebilir: After we ate, we left. İki past simple burada doğal olabilir. Past perfect önceki tamamlanmayı özellikle belirginleştirir; bir hikâyedeki bütün fiilleri past perfect yapmak anlatının referansını gereksiz yere bozabilir.
Türkçe karşılık ve çıkarım | Türkçedeki '-mişti' çoğu örnekte yardımcı olabilir ama İngilizcede bu yapı duyuma dayalı bilgi anlamına gelmez. 'He had left' onun gerçekten gittiğini aktaran bir geçmiş-öncelik cümlesidir. Dolaylı anlatım ve üçüncü koşul cümlelerinde de aynı had + V3 biçimi farklı görevlerle kullanılabilir.
""", """
Arrived varış anını kurar. Had left misafirlerin bu andan önce gittiğini gösterir; vardığında orada değillerdir. 'When I arrived, the guests left' dersen ayrılışı varış anına bağlayan farklı bir sıra anlatırsın.
Hadn't seen, o kışa kadar uzanan geçmiş deneyimin yokluğunu belirtir. Before that winter referans sınırıdır. Kişinin o kış kar gördüğü bağlamdan anlaşılabilir ama asıl yapı önceki döneme bakar.
""", """
When I got home, she [left]. | Eve geldiğimde o çıktı. | Çıkışı geliş anıyla bağlantılı sonraki olay olarak anlatır.
When I got home, she [had left]. | Eve geldiğimde o çıkmıştı. | Çıkış eve gelişten önce gerçekleşmiştir.
""")
_add("tn:11", """
Geçmişte biriken faaliyeti anlatmak | Past perfect continuous, geçmişteki bir referans anına kadar sürmüş faaliyeti süreç olarak gösterir. 'I was tired because I had been running' cümlesinde yorgunluk geçmiş sahnedir; koşma o sahneden öncesindeki uğraştır. Koşu o anda bitmiş olabilir veya hemen öncesine kadar sürmüş olabilir.
Yapının parçaları | Had + been + V-ing bütün öznelerde aynı kalır. Hadn't been working olumsuz; Had they been working? sorudur. Had tek başına past perfect simple ile ortaktır; been + -ing eklenmesi süreç vurgusunu sağlar. Son fiili V3 yapıp had been worked yazmak aynı aktif anlamı vermez.
Süre mi, biten miktar mı? | 'She had written three pages' biten miktarı, 'She had been writing for an hour' geçmişte bir ana kadar yapılan işi anlatır. Know gibi durum fiillerinde had known tercih edilir. Süre bulunması her durumda continuous zorunluluğu yaratmaz.
Past continuous'tan farkı | 'At ten, I was studying' doğrudan ondaki faaliyeti gösterir. 'By ten, I had been studying for two hours' ona kadar birikmiş iki saatlik çalışmaya bakar. Her ikisi geçmiş süreçtir ama gözlem noktası ve sürenin referansı aynı değildir.
""", """
Found shelter daha sonraki geçmiş olaydır. Had been hiking bu noktadan önce saatlerce süren yürüyüşü anlatır. For hours süreyi verir; sığınak bulmanın geçmişteki etkisiyle faaliyet arasında bağ kurulur.
Was exhausted geçmişteki sonuç/durumdur. Had been moving o yorgunluğu açıklayan önceki faaliyettir. Bütün mobilyaların taşınmasının bitmiş olması söylenmez; fiziksel uğraşın süreci önemlidir.
""", """
At noon, we [were driving]. | Öğlen araba sürüyorduk. | Öğlen anındaki süreç gösterilir; önceki süre bilinmez.
By noon, we [had been driving] for four hours. | Öğlene gelindiğinde dört saattir araba sürüyorduk. | Öğlen noktasından geriye bakılıp biriken süre ölçülür.
""")
_add("tn:12", """
Will'in temel işlevleri | Will geleceğe ilişkin tahmin, o anda verilen karar, teklif veya söz bildirebilir. 'I'll answer the phone' bir anda üstlenilen işi; 'I think it will snow' tahmini gösterebilir. Aynı will biçiminin bağlama göre farklı iletişim görevleri vardır; yalnızca 'gelecek zaman eki' değildir.
Kuruluş ve kısaltmalar | Will + V1 bütün öznelerle aynıdır. She will goes değil she will go denir. I'll, you'll, he'll gibi kısaltmalar konuşmada yaygındır. Olumsuzu won't'tur; bu, will not'un düzensiz kısaltmasıdır. Soruda will öne gelir: Will you come? Kısa cevap Yes, I will / No, I won't.
Plan ve düzenlemeyle karşılaştırma | Önceden verilen niyet için going to, kesinleşmiş kişisel düzenleme için present continuous çoğu bağlamda daha uygundur. Ancak gerçek hayatta kullanımlar örtüşebilir. Will'i 'planlarda asla kullanılmaz' diye yasaklamak yerine konuşanın kararı nasıl sunduğuna bak.
Gelecek yan cümleleri | 'I'll call when I arrive' cümlesinde gelecek ana cümlede will ile, zaman yan cümlesinde present simple ile anlatılır. Ayrıca will bazen istek/isteklilik veya ısrar bildirir. Başlangıç düzeyinde bütün will kullanımlarını tek bir zamansal kalıba indirgememek önemlidir.
""", """
Çantanın ağır olduğu o anda fark ediliyor ve yardım teklif ediliyor. Will carry konuşanın işi üstlendiğini gösterir. Geçmişten beri kesinleşmiş bir taşıma planı bulunduğunu varsaymamıza gerek yoktur.
I think, cümleyi konuşanın tahmini olarak çerçeveler. Will improve gelecekteki düzelmeyi öngörür. Improve yalın kalır; the weather tekil diye will improves yapılmaz.
""", """
The phone is ringing. I [will answer] it. | Telefon çalıyor. Ben açarım. | O anda üstlenilen iş/karar öne çıkar.
I [am going to call] her this evening. | Bu akşam onu aramayı planlıyorum. | Önceden düşünülmüş niyet öne çıkar.
""")
_add("tn:13", """
Niyet ile kanıtı ayırmak | Be going to iki sık bağlamda kullanılır: önceden düşünülen niyet ve şimdiki kanıta dayanan tahmin. 'I'm going to learn Italian' bir niyet; 'Look at the clouds; it's going to rain' mevcut işaretlerden doğan tahmindir. İkinci kullanımda insan planı bulunmaz.
Going to ile çekim | Öznenin ardından am/is/are, sonra going to + V1 gelir. Not, be'den sonra yerleşir: isn't going to leave. Soruda be öne çıkar: Are they going to leave? Going to'dan sonra fiil -ing almaz; 'going to leaving' hatalıdır.
Düzenleme ve tarife | Present continuous, zamanı/kişileri belirlenmiş randevuyu gösterebilir: I'm meeting Ana at six. Present simple ise bir tarife/kurum programını anlatabilir: The flight leaves at six. Aynı gelecek anı üç farklı bakışla anlatılabilir; yapıyı yalnızca tarih sözcüğü seçmez.
Örtüşme ve doğal kullanım | Bir plan aynı zamanda ayarlanmışsa going to ve present continuous ikisi de mümkün olabilir; vurgu değişir. 'I'm going to meet her' niyeti, 'I'm meeting her' düzenlemeyi öne çıkarabilir. Sınav sorusunda verilen randevu/kanıt bağlamını, konuşmada ise anlatmak istediğin bakışı kullan.
""", """
Clouds sözcüğü tahminin görülen kanıtını sağlar. Is going to rain, yağmurun başlamasını mevcut duruma bağlar; rain yalın fiildir. Cümle 'birinin yağmur yağdırma planı' anlamına gelmez.
At ten tomorrow belirli gelecek saati, the architect ise buluşulacak kişiyi verir. Are meeting kesinleşmiş düzenlemeyi doğal biçimde sunar. Gelecek zaman anlamı için ayrıca will eklenmez.
""", """
We [are going to visit] a museum. | Bir müzeyi ziyaret etmeyi düşünüyoruz/planlıyoruz. | Önceden verilen niyet anlatılır; ayrıntılar ayarlanmış olmak zorunda değildir.
We [are visiting] the museum at ten with our guide. | Rehberimizle saat onda müzeyi geziyoruz. | Belirli bir kişisel düzenleme öne çıkar.
""")
_add("tn:14", """
Gelecekte bir sahneye bakmak | Future continuous, gelecekteki bir anı düşünerek o anda sürecek faaliyetin içine bakar. 'At nine, I'll be studying' dersin dokuzda başlayacağını söylemez; dokuzda çalışma devam ediyor olacaktır. Başlangıç, bitiş ve toplam süre ayrıca belirtilmedikçe bilinmez.
Will be + -ing zinciri | Will + be + V-ing gerekir: will be travelling. Be yalın kalır; will is travelling denmez. Olumsuzda won't be travelling, soruda Will you be travelling? kurulur. Kısa cevap Yes, I will olabilir; yardımcı zincirinin tamamını tekrarlamak gerekmez.
Gelecek planıyla ilişki | Present continuous çoğu kez ayarlanmış düzenlemeyi, future continuous ise o gelecek anda sürecek faaliyeti öne çıkarır. Bazen 'Will you be using the car?' birinin planını nazikçe sormak için kullanılır. Bu, will you kullanarak doğrudan bir istek bildirmekten farklı bir odaktır.
Tamamlanmayla karıştırma | 'I'll be writing the report at six' altıdaki uğraşı; 'I'll have written it by six' altıya kadar bitmiş sonucu gösterir. At ve by farklı zaman bakışları verir. -Ing gördüğün için olayın daha uzun veya zor olduğunu otomatik çıkarma; burada seçilen bakış süreçtir.
""", """
This time tomorrow gelecekteki gözlem anını kurar. Will be flying o sırada uçuşun devam edeceğini gösterir. We çoğul olsa da will be zinciri değişmez; are veya were eklenmez.
Will you be using sorusu bu akşam arabanın kullanılıp kullanılmayacağını öğrenir. Cümle doğrudan 'arabayı kullan' talimatı vermez. Cevap, konuşanın araba için başka plan yapmasına yardımcı olabilir.
""", """
At six, I [will be writing] the report. | Altıda raporu yazıyor olacağım. | Altı anında yazma süreci devam ediyor olacak.
By six, I [will have written] the report. | Altıya kadar raporu yazmış olacağım. | Altı referansına kadar tamamlanmış sonuç beklenir.
""")
_add("tn:15", """
Gelecekten geriye bakmak | Future perfect'te önce gelecekte bir nokta düşünür, o noktaya gelindiğinde hangi işin tamamlanmış olacağını söylersin. 'By Friday, I'll have finished' cuma gününden geriye bakar. İş bugün, yarın veya cuma tamamlanabilir; temel bilgi o sınıra kadar bitmiş olmasıdır.
Will have + V3 kurulumu | Will ardından yalın have, sonra V3 gelir. Bütün öznelerde will have finished kullanılır; has gelmez. Olumsuz won't have finished, soru Will she have finished? biçimindedir. Have burada sahiplik değil perfect yardımcı fiilidir.
By ve until farkı | By a deadline 'en geç o ana kadar' tamamlanmayı; until çoğunlukla bir durumun o ana kadar sürmesini anlatır. 'I'll finish by Friday' bitirme sınırı, 'I'll work until Friday' çalışma devamının sınırıdır. İkisini yalnızca Türkçe '-e kadar' çevirisine bakarak eşitleme.
Süre ve gelecek yan cümlesi | By the time we arrive gibi zaman cümleciklerinde arrive present simple kalabilir. Future perfect durumlarla süre de verebilir: By May, I'll have known her for ten years. Bu yüzden yapı sadece kısa, bir kez biten işleri anlatmaz; o gelecek noktada birikmiş durumu da gösterebilir.
""", """
By June tamamlanma için gelecek sınırını verir. Will have completed, kursun o noktaya gelindiğinde tamamlanmış olacağını anlatır. Haziranda kursa yeni başlanacağı anlamı çıkmaz.
Won't have arrived, öğlen referansına kadar varışın gerçekleşmiş olmayacağını söyler. Bu cümle onların hiç gelmeyeceğini söylemez; öğlenden sonra varabilirler. V3 arrived zincirin son parçasıdır.
""", """
I'll [work] until five. | Beşe kadar çalışacağım. | Çalışma durumu beşe kadar devam eder.
I'll [have finished] by five. | Beşe kadar bitirmiş olacağım. | Beş, tamamlanma için son sınırdır; daha önce bitirmek de mümkündür.
""")
_add("tn:16", """
Gelecekte hesaplanan süre | Future perfect continuous, bir faaliyetin gelecekteki referans noktasına kadar ne kadar süredir devam ediyor olacağını gösterir. İşin başlangıcı geçmişte veya gelecekte olabilir; önemli olan seçilen gelecek anda birikecek süredir. Yapı 'gelecekte başlayacak her uzun iş' anlamına gelmez.
Uzun zinciri parçalara ayırmak | Will geleceğe bakışı, have perfect bağlantıyı, been + -ing süreç vurgusunu kurar. Bütün öznelerde will have been working kullanılır. Soruda sadece will öne taşınır: Will she have been working? Not, will'den sonra gelir; diğer parçalar aynı kalır.
Simple karşısında süre odağı | 'I'll have written ten articles by June' tamamlanan miktarı; 'I'll have been writing for ten years by June' faaliyetin birikmiş süresini anlatır. İkinci cümlede makale sayısı veya yazarlığın o gün biteceği belirtilmez. For süre, by gelecek referans sınırı olabilir.
Durum fiilleri ve kullanım sıklığı | Know gibi durum fiillerinde will have known tercih edilir. Live ve work ile simple/continuous seçimi bağlama göre değişebilir. Bu yapı günlük her gelecek cümlesine zorla eklenmez; gelecek referansı, süreç ve biriken süre birlikte önemliyse kullanılması anlamlıdır.
""", """
By July gelecekteki hesaplama anıdır; for five years o anda birikecek çalışma süresidir. Will have been working devam eden faaliyeti öne çıkarır. Cümle, kişinin temmuzda işi bırakacağını söylemez.
By midnight gelecekteki sınırı, for twelve hours yolculuğun o ana kadar geçecek süresini verir. Will have been travelling yolculuk sürecine odaklanır; gece yarısında hedefe kesin varılacağı bilgisi yoktur.
""", """
By July, I [will have completed] five projects. | Temmuza kadar beş projeyi tamamlamış olacağım. | Bitmiş iş sayısı verilir.
By July, I [will have been working] here for five years. | Temmuzda burada beş yıldır çalışıyor olacağım. | Çalışmanın gelecek noktaya kadar biriken süresi verilir.
""")
_add("tn:17", """
Ana cümle ve zaman yan cümlesi | 'I'll call when I arrive' iki parçadır: ana cümle bir gelecek davranışı, when bölümü onun zamanını bildirir. Zaman bölümünde geleceği anlatmak için genellikle present simple yeterlidir. Anlam gelecek olsa da her iki parçaya ayrı will yerleştirilmez.
Önce tamamlanmayı vurgulamak | 'After I have finished, I'll call' bitirmenin tamamlanmasını özellikle vurgular. 'After I finish, I'll call' da doğal olabilir. Present perfect burada gelecekteki bir öncelik ilişkisi kurabilir; yalnızca geçmiş deneyimi anlatan bir yapı olarak düşünülmemelidir.
Until ve as soon as | Until ana eylemin ne zamana kadar sürmeyeceği veya süreceği sınırını verir: We won't leave until she comes. As soon as iki olayın yakın zaman ilişkisini kurar: I'll call as soon as I land. Yan cümle başta ise çoğu kez ardından virgül gelir; sonda ise genellikle gerekmez.
When bir soru sözcüğü olduğunda | 'I don't know when she will arrive' bir zaman yan cümlesi değil, ne zaman sorusunun dolaylı anlatımıdır. Bu nedenle will mümkündür. Benzer görünen sözcüğü değil görevini tanı: davranışın zamanını mı belirtiyor, bilinmeyen bir sorunun içeriğini mi veriyor?
""", """
As soon as I land, mesaj atmanın zamanını belirler. Land bu zaman yan cümlesinde present simple kalır; ana bölüm I'll text you ile geleceği anlatır. Uçağın inmesi henüz gerçekleşmiş değildir.
Until everyone is ready, ayrılmanın gerçekleşmeyeceği sınırı verir. Everyone anlamca çok kişi içerse de dilbilgisel olarak tekil uyum ister; is ready olur. 'Until everyone will be ready' temel zaman cümleciği düzeni değildir.
""", """
I'll wait [until she arrives]. | O gelene kadar bekleyeceğim. | Until bölümü beklemenin zaman sınırını verir; present simple kullanılır.
I don't know [when she will arrive]. | Onun ne zaman geleceğini bilmiyorum. | When bölümü bilinmeyen bir sorunun içeriğidir; will kullanılabilir.
""")

_add("nn:0", """
Dinleyici hangi şeyi tanıyabiliyor? | A/an, bir grubun henüz belirlenmemiş tek üyesini tanıtır. The ise dinleyicinin hangi şeyden söz edildiğini ayırt edebildiğini varsayar. Bunun için nesnenin daha önce söylenmesi şart değildir: Close the door dediğinde odadaki belirli kapı bağlamdan anlaşılabilir.
Ses ve sayılabilirlik kontrolü | Önce isim tekil ve sayılabilir mi diye bak. Sonra a/an seçimini ilk harfe değil ilk sese göre yap: an honest person ama a European city. Sıfat varsa karar isme değil ardından gelen ilk sese göre verilir: an old car, a useful tool.
Türkçe çevirinin tuzağı | İngilizce tekil sayılabilir isim çoğunlukla bir belirleyici ister. Türkçede 'doktorum' veya 'arabam var' derken bir dememek, İngilizcede a/an'i düşürme nedeni değildir. Öte yandan the Türkçeye her zaman ayrı bir sözcükle çevrilmez; bağlamdaki belirliliği taşır.
""", """
İlk fox, daha önce tanıtılmamış bir hayvandır; a kullanılır. İkinci cümlede aynı tilkiye dönüldüğü için the seçilir. The fox ifadesi başka yeni bir tilkiyi değil tanıtılan hayvanı izler.
Engineer tekil bir meslek adıdır ve ilk sesi ünlüdür; an gerekir. He is engineer cümlesi meslek bildirimindeki tekil belirleyiciyi eksik bırakır. Türkçede 'bir' demeden çevirsek de an korunur.
""", """
I need [a] pen. | Bir kaleme ihtiyacım var. | Hangi kalem olduğu henüz belirli değil; uygun herhangi biri olabilir.
I need [the] pen on your desk. | Masandaki kaleme ihtiyacım var. | Yer bilgisi belirli kalemi ayırt eder; rastgele bir kalem istenmez.
""")
_add("nn:1", """
Sayılabilirlik bir çeviri meselesi değildir | Sayılabilir isim tek birimlere ayrılır: a chair, two chairs. Sayılamayan isim maddeyi veya soyut bilgiyi bütün olarak sunabilir. Türkçede 'bilgiler' denebilse de information temel kullanımında çoğul -s almaz. Sözcüğü İngilizcedeki anlamı ve kullanım kalıbıyla öğren.
Birim ekleyerek saymak | Sayılamayan bir şeyi saymak için birim kullanabilirsin: two pieces of information, three bottles of water. Çoğul eki bilgiye/suya değil pieces/bottles sözcüğüne gelir. Fiil uyumu da baş isme göre değişir: The water is cold; the bottles are cold.
Anlam değişince sınıf değişebilir | Coffee madde olarak sayılamaz; two coffees, iki fincan/sipariş kahve anlamında sayılabilir kullanılabilir. Chicken hayvanı veya etini, paper kâğıt maddesini veya bir gazeteyi/çalışmayı anlatabilir. Bu esneklik, advice/information gibi her sözcüğe otomatik çoğul ekleyebileceğin anlamına gelmez.
""", """
Children, child sözcüğünün zaten çoğul biçimidir; childrens veya childs yapılmaz. Çoğul özneyle are playing seçilir. Bir ismin çoğul görünmesi için mutlaka -s ile bitmesi gerekmez.
Advice sayılamaz; some advice doğal belirsiz miktardır. Could you give me bir rica kurar. Tek tek tavsiyeleri saymak istersen a piece of advice veya two pieces of advice kullanabilirsin.
""", """
There [is] some furniture in the room. | Odada biraz mobilya var. | Furniture topluca sayılamayan isim gibi davranır.
There [are] three chairs in the room. | Odada üç sandalye var. | Chairs sayılabilir çoğul birimlerdir; are kullanılır.
""")
_add("nn:2", """
Belirsiz miktarın yönü | Some genellikle var olan belirsiz miktarı, any ise soru veya olumsuzlukta varlığı/miktarı açık bir seçenek olarak sunar. We have some bread olumlu bilgi; Do we have any bread? stok sorusudur. Bu dağılım yararlı bir başlangıçtır ama bütün soru cümlelerinde any zorunlu değildir.
Teklif ve ricada some | Would you like some tea? tekliftir. Can I have some water? doğal bir ricadır ve olumlu karşılık beklentisi taşıyabilir. Sözcüğü seçerken yalnızca soru işaretini değil, konuşanın ne yaptığını düşün. Any olumlu cümlede serbest seçim de anlatabilir: Choose any seat.
No ile fiil olumsuzluğunu ayırmak | No + isim, isn't any veya don't have any gibi bir yapıyla benzer temel yokluk anlamı verebilir. Standart İngilizcede aynı olumsuzluğu iki kez kurmamak gerekir. Nothing ve anything de benzer bir ayrım gösterir: I saw nothing / I didn't see anything.
""", """
Would you like some soup bir teklif olduğu için some doğaldır. Konuşan çorba sunuyor; herhangi bir çorbanın var olup olmadığını tarafsız biçimde araştırmıyor. Soup bu bağlamda sayılamayan miktardır.
There aren't zaten olumsuzdur; any clean plates ile yokluk tamamlanır. Plates çoğul olduğu için aren't seçilir. No kullanmak istersen There are no clean plates biçiminde olumlu fiil kullanırsın.
""", """
You can choose [any] seat. | İstediğin herhangi bir koltuğu seçebilirsin. | Olumlu cümlede serbest seçim anlamı vardır.
There aren't [any] seats left. | Hiç koltuk kalmadı. | Olumsuz cümlede varlık/miktar yokluğu anlatılır.
""")
_add("nn:3", """
Önce isim türünü seçmek | Many kaç tane sorusuna uygun çoğul isimlerle; much ne kadar sorusuna uygun sayılamayan isimlerle gider. Many questions ama much homework denir. Cümlenin Türkçe çevirisindeki çok sözcüğü bu ayrımı tek başına göstermez; ismi kontrol etmek gerekir.
Olumlu ve olumsuz kullanım | A lot of hem çoğul hem sayılamayan isimle doğal günlük olumlu cümle kurar. Much çoğunlukla soru, olumsuzluk veya too/so gibi sözcüklerle görülür; olumlu kullanımı bazı resmî bağlamlarda mümkündür. 'Olumlu cümlede much asla olmaz' diye mutlak kural kurma.
Too ve fiyat soruları | Too much/too many ihtiyaçtan veya kabul edilenden fazlayı belirtir; yalnızca büyük miktar değildir. How much is it? fiyat sorabilir; burada sayılabilir bir ürünün fiyatı sorulsa da how much kullanılır. How many cars ise nesne sayısını sorar.
""", """
Time bu cümlede sayılamayan süredir; much kullanılır. Haven't got sahiplik/gereklilik bağlamında mevcut zaman eksikliğini anlatır. Many time yerine much time veya yeterli miktar için enough time seçilebilir.
Suitcases tek tek sayılabilen çoğul valizlerdir. How many bu yüzden uygundur. Are you taking ifadesi planlanan yolculukta götürülecek miktarı sorar; how much valiz sayısını doğrudan sormaz.
""", """
We have [a lot of] work. | Çok işimiz var. | Miktarın yüksek olduğunu belirtir; tek başına olumsuz değerlendirme yapmaz.
We have [too much] work. | Gereğinden fazla işimiz var. | Miktarın aşırı veya sorun yaratacak kadar fazla olduğu değerlendirilir.
""")
_add("nn:4", """
Miktar kadar konuşanın değerlendirmesi | A few/a little 'az ama bir miktar var' vurgusu taşır. Few/little ise çoğu bağlamda azlığı/yetersizliği öne çıkarır. A little time ile kahveye vakit bulunabilir; little time ile acele etmek gerekebilir. A sözcüğünün buradaki varlığı anlamı gerçekten değiştirir.
İsimle uyum | A few/few çoğul sayılabilir isim, a little/little sayılamayan isim alır. A few mistakes ama a little progress denir. Very few ve very little azlığı güçlendirir. A few people are... cümlesinde fiil çoğuldur; each person is... ifadesindeyse tekildir.
Each ve every'nin bakışı | Each, grup üyelerini tek tek düşünmeye; every grubun her üyesini kapsayan genellemeye uygundur. Arkalarındaki doğrudan isim tekildir: every student. Each of the students gibi yapıda ise of sonrasında çoğul isim gelir, standart fiil uyumu yine tekildir.
""", """
A little, time ile az ama kullanılabilir süreyi vurgular. Let's get a coffee sonucundan bu miktarın konuşan için yeterli olduğu anlaşılır. Yalnızca little time deseydi acele/yetersizlik vurgusu daha doğal olabilirdi.
Each guest her konuğu tek tek ele alır ve tekil yapı kurar; has bu yüzden gelir. Grubun çok kişiden oluşması, each guest ifadesini çoğul fiille kullanma nedeni değildir.
""", """
I have [a few] friends here. | Burada birkaç arkadaşım var. | Az da olsa arkadaş çevresinin bulunduğu vurgulanır.
I have [few] friends here. | Burada çok az arkadaşım var. | Arkadaş sayısının azlığı, çoğu bağlamda yetersizliği öne çıkarılır.
""")

_add("aj:0", """
Hangi sözcüğü açıklıyorsun? | Sıfat çoğunlukla bir isim veya özne hakkında özellik verir: a careful driver. Zarf ise eylemin nasıl gerçekleştiğini anlatabilir: drives carefully. Sözcüğün cümledeki görevini bulmadan yalnızca '-ly gördüm, zarftır' biçiminde karar verme; friendly gibi sıfatlar da -ly ile biter.
Bağlayıcı fiiller ve durum | Be, seem, look, sound, smell, taste bir özellik bildirirken ardından sıfat alabilir: She looks happy. Buradaki happy, bakma eyleminin nasıl yapıldığını değil kişinin durumunu açıklar. 'She looked carefully at the map' cümlesinde ise look gerçek bir bakma eylemidir; zarf kullanılır.
Düzensizler ve anlam tuzakları | Good → well temel eşleşmedir; well sağlık durumunda sıfat da olabilir. Fast hem sıfat hem zarftır. Hard 'sıkı/çok çaba göstererek', hardly ise 'neredeyse hiç' anlamına gelir. Bu iki sözcük, biçimleri benziyor diye birbirinin yerine kullanılamaz.
""", """
Politely, answered eyleminin nasıl yapıldığını açıklar: cevap vermek kibarcadır. Cümlede 'kibar bir adam' özelliği kurulmadığı için adjective polite yerine adverb politely seçilir.
Sounds burada bağlayıcı fiildir; müziğin nasıl algılandığını ve niteliğini verir. Beautiful özne music'i niteler. 'Music sounds beautifully' temel anlamda aynı doğal özellik cümlesi değildir.
""", """
She [looks careful]. | Dikkatli biri gibi görünüyor. | Look bağlayıcıdır; careful kişinin özelliğini verir.
She [looks carefully] at the painting. | Tabloya dikkatlice bakıyor. | Look bir eylemdir; carefully bakışın nasıl yapıldığını anlatır.
""")
_add("aj:1", """
İki şey mi, bir grubun en üstü mü? | Comparative bir şeyi başka bir şeyle karşılaştırır: taller than me. Superlative bir grupta uç noktayı gösterir: the tallest in the class. Karşılaştırılan diğer şey bağlamdan anlaşılırsa than bölümü söylenmeyebilir: This one is cheaper.
Biçimi doğru kurmak | Birçok kısa sıfat -er/-est alır: small–smaller–smallest. Ünsüz + y değişebilir: happy–happier. Big–bigger gibi son ünsüz çiftleşebilir. Daha uzun sıfatlarda more/most yaygındır. Bazı iki heceli sıfatlarda birden fazla biçim mümkündür; bunu sözcükle birlikte öğren.
Düzensizler ve ölçü | Good–better–best, bad–worse–worst düzensizdir. Karşılaştırmanın derecesi much/far/a little ile değiştirilebilir: much cheaper. 'More cheaper' iki comparative işaretini üst üste koyar. Eşitlik söylemek istediğinde comparative değil as…as yapısına geç.
""", """
İki güzergâh karşılaştırılıyor; safer comparative biçimdir ve than diğer yolu tanıtır. Path tek bir yol olduğu için is kullanılır. 'Safest than' comparative ve superlative görevlerini karıştırır.
Bir kitabın bölümleri içinde en ilginç olan seçiliyor. Interesting uzun sıfat olduğu için the most interesting kullanılır. In the book karşılaştırma grubunu belirler; her superlative cümlede than bulunmaz.
""", """
This exercise is [easier than] the last one. | Bu alıştırma öncekinden daha kolay. | İki alıştırma arasında karşılaştırma kurulur.
This is [the easiest] exercise in the book. | Bu, kitaptaki en kolay alıştırma. | Kitaptaki grubun en kolay üyesi seçilir.
""")
_add("aj:2", """
Eşitliğin iskeleti | As + sıfat/zarf + as aynı ölçüyü anlatır. 'As old as' yapısında old normal biçimindedir; older yapılmaz. Not as…as bir fark bildirir ama farkın miktarını söylemez. İsim miktarlarında as much/as many gibi başka biçimler gerekir.
Yeterlilik ve engel | Enough gerekli eşiğe ulaşıldığını, too ise çoğu bağlamda aşırılığın sorun yarattığını bildirir. 'Very hot' yalnızca yüksek derece olabilir; 'too hot to drink' içmeyi engelleyen sıcaklıktır. To-infinitive hangi iş için eşiğin yeterli/yetersiz olduğunu açıklayabilir.
Sözcüklerin sırası | Sıfat/zarf + enough: old enough, quickly enough. Enough + isim: enough money. Too + sıfat/zarf: too expensive. 'Too much money' gibi miktar yapısında much/many gerekir. Türkçe sıralamayı olduğu gibi taşıyıp enough old veya money enough kurma.
""", """
Big enough ifadesinde enough sıfatın arkasındadır. Isn't olumsuzluğu odanın altı kişilik kullanım için gerekli büyüklüğe ulaşmadığını söyler. 'Küçük' diye mutlak ölçü verilmez; ihtiyaçla karşılaştırılır.
Too hot, içme eylemi için aşırı sıcaklığı belirtir. To drink bu aşırılığın hangi işi engellediğini açıklar. Very hot aynı derecede bir engel anlamını kendiliğinden garanti etmez.
""", """
The coffee is [very hot]. | Kahve çok sıcak. | Yüksek sıcaklık belirtilir; içilemeyeceği kesin söylenmez.
The coffee is [too hot to drink]. | Kahve içilemeyecek kadar sıcak. | Sıcaklık, içme eylemi için aşırı bulunur.
""")

_add("pp:0", """
Zamanı hangi ölçekte veriyorsun? | At bir saat/nokta, on bir gün/tarih, in daha geniş bir dönem çerçevesi kurar. Bu, yararlı bir zihinsel haritadır; bütün kalıpları açıklayan matematik kuralı değildir. At night, at noon, in the evening gibi sık birliktelikleri bütün olarak öğren.
Günle genişleyen ifadeler | In the morning genel bir gün bölümüdür. On Monday morning dediğinde belirli güne bağlandığı için on olur. In June ve on 3 June ayrımı da dönemden tarihe geçiştir. Yalnızca ifadenin son sözcüğüne bakıp 'morning her zaman in' deme.
Edat kullanılmayan yerler | Next week, last Friday, this evening ve every day önünde temel kullanımda ayrıca in/on/at bulunmaz. 'I'll see you on Friday' ama 'I'll see you next Friday' denir. At the weekend ve on the weekend gibi dil çeşidine bağlı doğal farklılıklar da vardır.
""", """
Half past eight belirli saattir; at kullanılır. Starts present simple ile bir program saati anlatabilir. Burada at, fiilin zamanı değil konserin başlangıç saatinin nasıl belirtileceğiyle ilgilidir.
September bir ay/dönem adı olduğundan in kullanılır. Usually yolculuğun genel alışkanlık olduğunu gösterir. 'In September' cümlenin geçmiş veya gelecek olmasını tek başına belirlemez; fiil bağlamına bakılır.
""", """
We meet [in the morning]. | Sabahları/sabah buluşuruz. | Günün bölümü genel biçimde söylenir.
We meet [on Monday morning]. | Pazartesi sabahı buluşuruz. | Gün bölümü belirli bir güne bağlandığı için on kullanılır.
""")
_add("pp:1", """
Konum ve bakış açısı | In bir alanın içinde olmayı; on yüzey/hat üzerinde olmayı; at bir nokta, etkinlik veya işlevsel konumu öne çıkarabilir. 'At school' okulda bulunma/etkinlik, 'in the school' binanın içi bakışı verebilir. Fiziksel büyüklüğe bakarak tek bir edat seçmek yetmez.
Bir sınıra doğru hareket | To hedefi, into içeri geçişi, onto yüzeye geçişi anlatabilir. 'Walk in the room' odanın içindeki yürüyüş; 'walk into the room' dışarıdan içeri giriş olabilir. Hareket fiili görmek otomatik to kullanmak demek değildir; inside/outside bakışı önemlidir.
Fiille birlikte öğrenilen kalıplar | Arrive in bir şehir/ülkeyle, arrive at bir nokta/istasyonla kullanılır. Reach doğrudan nesne alabilir: reach the station. Home/here/there hedef olarak çoğunlukla to almaz. Bu yüzden Türkçedeki yönelme ekini her yerde tek bir İngilizce edatla karşılamaya çalışma.
""", """
On the shelf anahtarların rafın yüzeyindeki konumunu verir. Cümle hareket anlatmadığı için onto seçilmez. Are, çoğul keys ile uyumludur; edat fiil uyumundan ayrı bir seçimdir.
Into the box kedinin kutu dışından içine geçmesini vurgular. Jumped hareket fiilidir ama asıl anlamı into'daki sınır geçişi netleştirir. In kullanılsaydı kutu içindeki atlama anlamı da doğabilirdi.
""", """
He walked [in] the room. | Odanın içinde yürüdü. | Yürüyüşün gerçekleştiği yer oda içidir.
He walked [into] the room. | Odanın içine girdi/yürüdü. | Odanın sınırından içeri geçiş anlatılır.
""")
_add("pp:2", """
Soruda hangi öğe eksik? | Who opened the window? sorusunda pencereyi açan özne bilinmez; who doğrudan öznenin yerindedir. Who did you call? sorusunda ise yapan you bellidir, aranan nesne bilinmez. İlkinde olağan olumlu özne sorusuna ayrıca did eklenmez; ikinci soruda did gerekir.
İç soruda düz sıra | Do you know where she lives? dışarıda yes/no sorusu, içeride 'onun nerede yaşadığı' bilgisini taşır. İç bölüm where + subject + verb sırasındadır; does she live diye yeniden soru kurulmaz. Kibar dolaylı sorularda bu ayrım çok önemlidir.
Question tag seçme | Önce ana cümlenin yardımcı fiilini ve olumlu/olumsuz oluşunu bul. Sonra özneyi zamire çevir. 'She works, doesn't she?' asıl fiilli present simple için do ailesini kullanır. 'She is ready, isn't she?' be'yi kullanır. I'm late, aren't I? gibi özel kalıplar ayrıca öğrenilir; tonlama gerçek soruyu veya onay beklentisini değiştirebilir.
""", """
Who, opened eylemini yapan bilinmeyen kişinin yerindedir. Past simple fiil doğrudan opened olur. 'Who did opened' hem soru düzenini hem fiil çekimini yanlış birleştirir.
Have burada sahiplik bildiren asıl fiildir; modern yaygın kullanımda tag don't you olabilir. Have got yapısında ise haven't you beklenir. Ana cümlenin gerçek yapısını çözmeden yalnızca have sözcüğüne bakma.
""", """
[Who called] you? | Seni kim aradı? | Bilinmeyen öğe fiili yapan öznedir; ek did kullanılmaz.
[Who did you call]? | Sen kimi aradın? | Özne you bellidir; bilinmeyen nesne için did ile soru kurulur.
""")

_add("md:0", """
Yeterlilik, izin ve rica | Can yüzebilmek gibi yetenek; Can I leave? gibi izin veya Can you help? gibi rica anlatabilir. Could geçmişte genel yeterlilik veya daha dolaylı/kibar rica olabilir. Aynı sözcük her cümlede 'geçmiş can' anlamına gelmez; iletişim görevini tanı.
Modalın biçimi ve eksik yerleri | Can/could sonrasında to almayan V1 gelir, üçüncü tekil -s eklenmez. Can'ın her zaman yapısında çekimi yoktur; will can yerine will be able to, have been able to gibi be able to biçimleri kullanılır. Able tek başına yardımcı fiil değildir.
Genel yetenek ve tek başarı | 'I could swim at six' çocukluktaki genel yeteneği anlatır. 'After three attempts, I was able to open it' belirli olayda gerçekleşen başarıyı vurgular. Olumsuzda couldn't tek bir başarısız olay için de doğaldır. Bu eğilimleri bütün could kullanımlarını yasaklayan mutlak kurala çevirmemek gerekir.
""", """
Could speak, dedenin genel dil yeteneğini geçmiş çerçevede verir. Four languages yeteneğin kapsamıdır; tek bir günkü konuşma başarısı anlatılmaz. Speak modal sonrasında yalın kalır.
After several attempts belirli bir başarı olayını kurar. Were able to unlock, kapının gerçekten açılabildiğini gösterir. We çoğul olduğu için were seçilir; could able to biçimi kullanılmaz.
""", """
I [could swim] when I was five. | Beş yaşındayken yüzebiliyordum. | Geçmiş genel yeterlilik anlatılır.
I [was able to rescue] the child. | Çocuğu kurtarmayı başardım. | Belirli olayda gerçekleşen başarı öne çıkar.
""")
_add("md:1", """
Gereklilik ile tavsiye aynı değildir | Must/have to çoğu bağlamda zorunluluk, should ise öneri veya doğru olacağı düşünülen davranışı bildirir. 'You should rest' dinlenmeyi önerir; 'You must show your passport' bir gereklilik koyar. Dil seçimi konuşanın otoritesi ve bağlama göre daha yumuşak/sert duyulabilir.
Must ve have to esnekliği | Must daha çok konuşanın güçlü vurgusu, have to dış koşul/kural ile ilişkilendirilir; ancak kullanımlar örtüşür. Her kişisel zorunluluğu must, her dış kuralı have to diye kesin ayırma. Have to çekimlenebilir: she has to, we had to, they will have to.
Soru, geçmiş ve olumsuzluk | Have to sorusu Do you have to…?, geçmişi Did you have to…? olabilir. Musted yoktur; geçmiş zorunluluk had to ile anlatılır. Should bütün öznelerde aynı kalır ve V1 alır. Olumsuz anlamda mustn't ile don't have to'nun zıt görevleri sonraki derste ayrıca ayrılır.
""", """
Should take, mola vermeyi iyi bir seçenek olarak önerir. Take yalın fiildir; should to take yapılmaz. Cümle bir resmî izin/ceza kuralını zorunlu olarak bildirmez.
Visitors çoğul olduğundan have to kullanılır. Wear a badge giriş/işleyiş gerekliliğidir. Tekil ziyaretçi için A visitor has to wear… denir; has çekimi ana fiile değil have yapısına aittir.
""", """
You [should] wear a helmet. | Kask takmalısın; bunu tavsiye ederim. | Tavsiye veya doğru davranış değerlendirmesi öne çıkar.
You [have to] wear a helmet here. | Burada kask takmak zorundasın. | Kural veya koşuldan doğan gereklilik öne çıkar.
""")
_add("md:2", """
İki ayrı olumsuz anlam | Mustn't 'bunu yapma' yönünde yasak/güçlü olumsuz talimattır. Don't have to ise 'bunu yapmak zorunda değilsin' diyerek zorunluluğu kaldırır. İkinci yapıda kişi isterse yapabilir. Türkçedeki '-mamalısın' ve '-mana gerek yok' farkını bilinçli kur.
Yapı ve kişi uyumu | Mustn't sonrasında doğrudan V1 gelir. Don't/doesn't have to yapısında do ailesi özneye göre çekimlenir; have yalın kalır. Geçmişte zorunluluğun olmaması didn't have to ile anlatılır. Bu, işin gerçekten yapılıp yapılmadığını tek başına kesinleştirmez.
Needn't ve geçmiş ayrıntısı | Needn't + V1 şimdiki/gelecek gereksizliği anlatabilir. Needn't have + V3 ise gerekmeyen bir işin yapılmış olduğunu gösterir: You needn't have bought bread. Didn't need to buy bread cümlesi temel olarak gereklilik yokluğunu bildirir; yapılmışlık bağlama bağlıdır.
""", """
Mustn't park, park etme eylemini yasaklar; 'park etmek zorunda değilsin' anlamı yoktur. In front of this gate yasağın yer sınırıdır. Bu tür talimatlarda yanlış modal seçimi anlamı tersine çevirebilir.
Don't have to book, rezervasyonun zorunlu olmadığını söyler. İstersen yine rezervasyon yapabilirsin. Cümle, önceden rezervasyon yapmanın yasak olduğunu bildirmez.
""", """
You [mustn't pay] that person. | O kişiye ödeme yapmamalısın. | Ödeme yapma yönünde olumsuz talimat vardır.
You [don't have to pay]. | Ödeme yapman gerekmiyor. | Ödeme zorunluluğu yoktur; temel anlam yasak değildir.
""")
_add("md:3", """
Bir olasılık değerlendirmesi yapmak | May/might/could konuşanın bilginin kesinliğini sınırladığını gösterir: He might be at home. Bu sözcüklere her durumda geçerli sabit yüzdeler vermek doğru değildir. Bağlam, tonlama ve eldeki kanıt değerlendirmeyi değiştirir; might her cümlede matematiksel olarak may'den düşük bir sayı demek değildir.
Güçlü olumlu ve olumsuz çıkarım | Must bu kullanımda 'yapmak zorunda' değil 'öyle olmalı' anlamıdır. Can't ise kanıtla uyuşmayan olasılığı dışlar. 'He can't be the driver' onun sürme yeteneğini değil, sürücü olduğuna inanılmadığını da anlatabilir. Sözcüğün o cümledeki görevini çöz.
Olumsuz olasılık ve süreç | May not/might not 'olmayabilir', can't 'olamaz' anlamı verebilir; aynı güçte değildir. Şu anda süren tahmini eylem için modal + be + -ing de kullanılır: She might be working. Bu yapıya ayrıca is eklenmez.
""", """
Işıkların kapalı olması uyuma ihtimaline kanıttır ama kesin kanıt değildir; might be bu belirsizliği korur. They might asleep eksiktir, çünkü asleep sıfatını bağlayan be gerekir.
Gün boyu yürümüş olma, yorgunluk çıkarımını güçlü kılar. Must be tired tavsiye veya zorunluluk değildir. 'Yorgun olmayı yapmak zorundasın' değil 'büyük olasılıkla yorgunsun' anlamı taşır.
""", """
She [might not be] at home. | Evde olmayabilir. | Olumsuz olasılık vardır; evde olması dışlanmaz.
She [can't be] at home. | Evde olamaz. | Konuşan, evde olma olasılığını elindeki bilgiyle dışlar.
""")
_add("md:4", """
Geçmiş olay, şimdiki değerlendirme | Modal + have + V3 yapısında olay geçmişe yerleşir; konuşan o olay hakkında çıkarım veya değerlendirme yapar. Must have forgotten 'unutmuş olmalı', might have forgotten 'unutmuş olabilir' anlamını verebilir. Modal burada mutlaka fiilin geçmiş çekimi değildir.
Tavsiye, eleştiri ve beklenti | Should have + V3 pişmanlık/eleştiri bağlamında yapılması daha iyi olacak işi anlatabilir. Ama 'The train should have arrived by now' geçmişe ilişkin beklenti de olabilir; her should have cümlesi kesin yapılmamış iş demek değildir. Bağlam olmadan bu anlamları tek bir kurala indirgeme.
Biçim ve gerçekleşmişlik | Must/might/should/can't sonrasında have sabit kalır, son fiil V3 olur. Could have bazen geçmiş olasılık, bazen kullanılmamış fırsat/yeterlilik anlatır. 'I could have helped, but you didn't ask' yardım etme imkânının gerçekleşmemesini bağlamıyla açıklar.
""", """
Must have forgotten, randevunun unutulmuş olduğu yönünde güçlü çıkarım kurar. Forgotten, forget fiilinin V3'üdür. Cümle, onu unutmaya mecbur bırakılmış biri olarak anlatmaz; must burada zorunluluk değildir.
Should have saved bu bağlamda geçmişe yönelik pişmanlık/değerlendirmedir: kopya kaydetmek daha iyi olurdu. Have sonrasında saved V3 görevindedir. I should had saved biçimi doğru modal zinciri değildir.
""", """
She [must have left]. | Gitmiş olmalı. | Geçmiş olay hakkında güçlü olumlu çıkarım yapılır.
She [should have left] earlier. | Daha erken gitmeliydi. | Davranışın zamanlaması değerlendirilir; temel odak çıkarım değildir.
""")

_add("ps:0", """
Neyi konu başlığı yapıyorsun? | Aktifte işi yapan özne olur: Someone repaired the bridge. Passive'de etkilenen şey başa gelir: The bridge was repaired. Bu, yalnızca sözcükleri ters çevirme işlemi değildir; konuşanın bilgi odağı değişir. Yapan bilinmiyorsa veya önemli değilse by bölümü söylenmeyebilir.
Dönüşümü adım adım yapmak | Aktif cümlenin nesnesini bul, yeni özne yap, zamanı uygun be biçimine taşı, asıl fiili V3 kullan. 'They clean the room' → 'The room is cleaned'. Yeni özne çoğulsa are gerekir. Olumsuzlukta be'den sonra not; soruda ilk yardımcı öne gelir.
Hangi fiiller uygun? | Doğrudan nesne almayan arrive, happen, sleep gibi fiiller normal anlamlarında bu şekilde passive yapılamaz. 'The accident was happened' hatalıdır. Ayrıca V3 bazen sıfat gibi durum da bildirebilir: The door is closed, bağlama göre kapının durumunu veya edilgen işi anlatabilir.
""", """
Shirts işten etkilenen çoğul nesneler olarak konu edilir; are made passive yapısıdır. From cotton malzemeyi belirtir, yapan kişiyi değil. Made, make fiilinin V3 biçimidir.
Was opened geçmişteki açılma olayını gösterir; in 1995 bitmiş tarih verir. Station tekil olduğu için was seçilir. Açan kişi/kurum bu cümlede önemli olmadığı için by ile belirtilmemiştir.
""", """
The workers [repaired] the bridge. | İşçiler köprüyü onardı. | İşçiler özne ve bilgi odağıdır.
The bridge [was repaired]. | Köprü onarıldı. | Etkilenen köprü konu edilir; yapanı söylemek zorunlu değildir.
""")
_add("ps:1", """
Zaman ve edilgenlik ayrı katmanlardır | Has repaired, has been repaired ve will be repaired farklı yardımcı zincirleri taşır. Perfect bağlantısını have/has/had, edilgenliği be/been + V3 kurar. Son fiilin V3 olması tek başına bir cümleyi passive yapmaz; yardımcı zinciri de doğru olmalıdır.
Modal passive oluşturmak | Modal + be + V3 kullanılır: must be checked. Modalın ardından be yalındır; must is checked denmez. Perfect passive'de have/has/had been + V3 gerekir. Soruda ilk yardımcı öne gelir: Has it been checked? Olumsuzda not ilk yardımcıdan sonra gelir.
Yardımcıları çözerek anlamak | 'The car has been repaired' onarımın şimdiki sonucunu; 'was being repaired' geçmişte sürmekte olan onarımı gösterir. 'Will have been repaired' gelecekteki sınıra kadar tamamlanmış passive iş olabilir. Uzun zinciri tek parça ezberlemek yerine her yardımcının işlevini ayır.
""", """
Has been delivered, teslim edilen paketi özne yapar ve teslimin şimdiki bağlantısını verir. Has been zincirinde been passive be'nin V3 biçimidir; son delivered ise asıl fiilin V3'üdür.
Must be signed, başvurunun imzalanmasının zorunlu olduğunu anlatır. Application imzalayan kişi değil, imzalanan belgedir. Yapanın kim olduğu bağlamdan anlaşılabilir; by bölümü gerekli olmayabilir.
""", """
They [have repaired] the car. | Arabayı tamir ettiler. | They işi yapan öznedir; yapı aktiftir.
The car [has been repaired]. | Araba tamir edildi. | Araba etkilenen öznedir; has been + V3 edilgenliği kurar.
""")
_add("ps:2", """
Hizmeti kim gerçekleştiriyor? | 'I repaired my car' tamiri benim yaptığımı söyler. 'I had my car repaired' ise tamiri birine yaptırdığımı/organize ettiğimi anlatabilir. Türkçedeki '-dır/-tir' yaptırma eki yararlı bir karşılıktır; İngilizcede have + nesne + V3 dizilişi gerekir.
Çekimi doğru yere koymak | Zamanı have/get taşır; nesneden sonraki fiil V3 kalır. 'I have my car washed every week', 'I had it washed yesterday', 'I'm having it washed now' farklı zamanlardır. I had washed my car ise past perfect active'dir; kelime sırası anlamı değiştirir.
İstenmeyen deneyim ve kişi nesnesi | 'She had her bag stolen' bir hırsızlık deneyimini de anlatabilir; kişi çalınmasını istemiş olmak zorunda değildir. 'Have someone do something' başka bir kalıptır: I had the mechanic check it. Birinde işten etkilenen nesne + V3, diğerinde işi yapan kişi + V1 vardır.
""", """
Had geçmiş zamanı, roof yapılan işten etkilenen nesneyi, repaired V3'ü verir. Cümle çatıyı bizzat bizim onardığımızı söylemez; hizmeti yaptırma/organize etme anlamı taşır.
Gets her eyes tested düzenli bir muayene hizmetini anlatır. Every year düzenlilik verir; gets üçüncü tekil çekimidir. Eyes çoğul olsa da asıl özne she olduğu için get değil gets seçilir.
""", """
I [had washed] my car. | Arabamı yıkamıştım. | Past perfect active: işi yapan benim.
I [had my car washed]. | Arabamı yıkattım. | Have + nesne + V3: yıkama işi bir başkasına yaptırılmış olabilir.
""")

_add("cn:0", """
Genel ilişki ile tek gelecek ihtimali | Zero conditional 'bu koşul olduğunda genel olarak şu sonuç olur' ilişkisini kurar. First conditional ise belirli bir gelecekteki mümkün koşulu ve sonucunu ele alır. Aynı fiillerle iki yapı kurulabilir; değişen, olayın tekrar eden kural mı yoksa belirli ihtimal mi olduğudur.
İki cümle parçasını kurmak | Önce koşul bölümünü if + present simple olarak kur. Genel sonuçsa present simple, belirli gelecekteki sonuçsa will + V1 kullanabilirsin. Ana bölümde can/may veya emir de bulunabilir. If bölümü baştaysa genellikle ardından virgül gelir; sona gelirse çoğu kez gerekmez.
Will yasağının sınırı | Sıradan gelecek koşulunda 'If it rains' denir; if bölümüne otomatik will konmaz. Ancak will isteklilik/ısrar gibi başka bir anlam taşıyabilir. İleri bağlamlardaki bu kullanımı temel gelecek koşulu kuralıyla karıştırma. Unless çoğu kez if not anlamı verir ama her bağlamda mekanik eşanlamlı değildir.
""", """
Heat ve melts genel fiziksel ilişkiyi anlatır. It tekil olduğu için melts -s alır. Cümle belirli bir yarın olayını değil genel sonucu sunduğundan iki bölüm de present simple'dır.
Improves yarın için mümkün koşuldur; if sonrasında present simple kalır. Will eat o koşul gerçekleşirse yapılacak davranışı anlatır. Tomorrow tüm olayın geleceğe ait olduğunu gösterir; if bölümüne ayrı will gerekmez.
""", """
If it rains, the ground [gets] wet. | Yağmur yağarsa yer ıslanır. | Genel koşul-sonuç ilişkisi kurulur.
If it rains tomorrow, we [will stay] inside. | Yarın yağmur yağarsa içeride kalacağız. | Belirli bir gelecekteki olasılık ve planlanan sonuç ele alınır.
""")
_add("cn:1", """
Geçmiş biçim, şimdiki varsayım | Second conditional'da past simple biçimi çoğu kez geçmiş bir tarih değil, gerçeklikten uzaklık bildirir. 'If I had more money' şimdi paramın daha çok olması hayalini kurabilir. Bunu past simple gördüğün için otomatik 'eskiden daha çok param vardı' diye yorumlama.
Koşul ve sonuç | If + past simple, would + V1 temel düzendir. Could sonuçtaki yeterliliği, might olasılığı değiştirebilir: If I had a car, I could drive there. Would çoğunlukla sonuç bölümündedir. Olumsuzluk her bölümde kendi yardımcı düzenine göre kurulur: If I didn't work, I wouldn't earn money.
Were, was ve konuşanın bakışı | Varsayımsal be ile resmî kullanımda bütün öznelerde were yaygındır. If I were you yerleşik tavsiye kalıbıdır. Konuşmada bazı öznelerle was da duyulur. First/second ayrımı matematiksel bir ihtimal yüzdesi değil, konuşanın koşulu ne kadar gerçekçi/uzak sunduğuyla ilgilidir.
""", """
Knew burada geçmiş bir tanışıklık olayı anlatmak zorunda değildir; mevcut numara bilgisinin olmadığını varsayar. Would call bu hayali durumda yapılacak eylemdir. Koşul değişse arama mümkün olurdu.
If I were you, gerçek hayatta sen olduğumu değil senin yerindeki hayali bakışı kurar. Would apologise tavsiyeyi verir. I ile were seçimi bu yerleşik gerçek dışı kalıpta doğaldır.
""", """
If I [have] time tomorrow, I'll help. | Yarın vaktim olursa yardım edeceğim. | Koşul, gerçekçi bir gelecek ihtimali olarak sunulur.
If I [had] more time, I'd help. | Daha çok vaktim olsa yardım ederdim. | Mevcut durumdan farklı, daha uzak/varsayımsal koşul kurulur.
""")
_add("cn:2", """
Değiştirilemeyen geçmişi yeniden kurmak | Third conditional geçmişte gerçekleşmiş durumu farklı hayal eder: 'If we had left earlier...' gerçekte daha erken çıkmadığımızı ima edebilir. Sonuç da geçmiştedir. Bu, bugün hâlâ değiştirebileceğimiz bir plan değil, geçmişe dönük alternatif senaryodur.
İki perfect zinciri | Koşulda had + V3, sonuçta would have + V3 kullanılır. Had known ve would have helped iki farklı yardımcı zinciridir. I'd, koşulda had; sonuçta would kısaltması olabilir: If I'd known, I'd have called. Kısaltmayı sonraki fiile bakarak çöz.
Sonucun gücü değişebilir | Would have varsayılan sonucu, might have olası sonucu, could have ise yeterlilik/fırsat anlamını öne çıkarabilir. 'If we had trained, we might have won' antrenmanın kesin zafer garantisi verdiğini söylemez. Geçmişteki gerçek koşulu ve hayali sonucu iki ayrı bölüm olarak takip et.
""", """
Had called, gerçekte olmayan/geçmişte farklı hayal edilen aramayı kurar. Would have helped bunun geçmişteki alternatif sonucudur. Helped burada V3'tür; would helped veya would had helped kullanılmaz.
Had trained önceki koşulu, might have won olası geçmiş sonucu gösterir. Might seçimi kazanmanın kesinliğini azaltır. Won, win fiilinin V3 biçimidir; would have won ile aynı kesinlik vurgusu yoktur.
""", """
If I [had] time now, I [would help]. | Şimdi vaktim olsa yardım ederdim. | Şimdiki hayali koşul ve sonuç anlatılır.
If I [had had] time yesterday, I [would have helped]. | Dün vaktim olsaydı yardım ederdim. | Geçmişteki koşul farklı hayal edilir; had had, have fiilinin past perfect biçimidir.
""")
_add("cn:3", """
Her bölümün zamanını ayrı bulmak | Mixed conditional'da koşul ve sonuç aynı zamana ait olmak zorunda değildir. 'If I had studied medicine, I would be a doctor now' geçmişteki eğitim seçimini şimdiki mesleğe bağlar. Fiil zincirlerini seçmeden önce nedenin ve sonucun hangi zamana baktığını belirle.
Diğer karışık yön | Şimdiki/genel bir özellik geçmiş sonucu da etkileyebilir: If I were more careful, I wouldn't have made that mistake. Burada genel dikkatlilik varsayımı geçmiş hataya bağlanır. Her mixed cümleyi otomatik had + V3 / would + V1 kalıbına sokma; zaman mantığına bak.
Wish ve gerçek dışı bakış | Wish + past simple mevcut durumun farklı olmasını ister; wish + past perfect geçmiş pişmanlık anlatır. Wish + would çoğu kez değişmesini istediğimiz davranışı/olayı gündeme getirir. 'I wish I knew' ile 'I wish I had known' aynı zaman noktasını anlatmaz. If only benzer dileği daha güçlü verebilir.
""", """
Had accepted geçmişteki iş kabulünü farklı varsayar; would live abroad now ise bunun şimdiki yaşam sonucudur. Now sözcüğü sonucu geçmişten ayırır. Would have lived seçilseydi sonuç da geçmişe taşınırdı.
Had saved, artık geride kalmış dosya kaydetme eylemine yönelik pişmanlığı verir. Konuşan geçmişi değiştiremez. I wish I saved temel bağlamda aynı geçmiş pişmanlık yapısı değildir.
""", """
I wish I [knew] the answer. | Keşke cevabı bilsem. | Şimdiki bilgi durumunun farklı olması istenir.
I wish I [had known] the answer yesterday. | Keşke dün cevabı bilseydim. | Bitmiş geçmişteki bilgi durumu farklı hayal edilir.
""")

_add("rs:0", """
Sözü yeni bir bakıştan aktarmak | Direct speech kişinin kendi sözcüklerini, reported speech ise o içeriği aktaran kişinin cümlesini verir. 'I am busy' diyen kişi he olarak anlatılınca I → he olur. Zamir, yer ve zaman sözcükleri konuşan/dinleyen ve aktarım anına göre ayarlanır; ezber bir sözcük değiştirme listesi yeterli değildir.
Backshift nasıl çalışır? | Geçmiş reporting verb ile present simple → past simple, present continuous → past continuous, will → would gibi geri kaymalar sık görülür. Present perfect çoğunlukla past perfect olur. Past perfect genellikle bir adım daha geriye kaydırılmaz. That çoğu bildirme aktarımında isteğe bağlıdır.
Hâlâ doğru bilgi ve say/tell | Aktarılan bilgi hâlâ geçerliyse veya gelecek olay henüz olmadıysa her zaman zorunlu backshift gerekmez. 'She said she lives in Ankara' güncel doğruluğu öne çıkarabilir. Tell doğrudan kişi nesnesi alır: told me; say için said to me veya yalnızca said that kullanılır.
""", """
İlk I am busy sözü he bakışından aktarılır; I → he, am → was olur. Was kullanımı, o kişinin şimdi kesinlikle meşgul olmadığını tek başına kanıtlamaz; aktarımın geçmiş çerçevesini kurar.
Told doğrudan us nesnesini alır. Would call, geçmişte verilen will call sözünün aktarımı olabilir. Later'ın hangi zamanı işaret ettiği aktarım bağlamından anlaşılır; her zaman otomatik ertesi gün demek değildir.
""", """
She [said] that she was tired. | Yorgun olduğunu söyledi. | Kişi nesnesi gerekmeyen say yapısı kullanılır.
She [told me] that she was tired. | Yorgun olduğunu bana söyledi. | Tell doğrudan me nesnesiyle kime söylendiğini belirtir.
""")
_add("rs:1", """
Soru içeriği artık yan cümledir | 'Where do you live?' doğrudan soru düzenidir. 'She asked where I lived' ise bir sorunun içeriğini bildirir. İç bölümde özne + fiil sırası kullanılır; doğrudan sorunun do/does/did yardımcısı normalde kaldırılır. Asıl fiil yeni zaman ve özneye göre çekimlenir.
Yes/no ve wh- ayrımı | Yes/no sorusunu aktarırken if/whether gerekir: asked if I was ready. Wh- sorusunda kendi soru sözcüğü korunur: asked why I was late. Whether ile or not gibi yapılar da mümkündür. That, temel reported yes/no question yerine geçmez.
Soru işareti ve emirden farkı | 'He asked where she was' bir bildirme cümlesidir; sonuna soru işareti gerekmez. 'Do you know where she is?' tümüyle bir sorudur, işaret alır. 'He asked me to wait' ise bilgi sorusunu değil ricayı aktarır. Ask fiilini görünce tek bir yapı varsayma.
""", """
Whether, doğrudan 'Do you need help?' yes/no sorusunu aktarabilir. I needed help düz cümle sırasıdır. Needed geçmiş aktarım uyumudur; do I needed gibi ikinci soru düzeni kurulmaz.
What time soru sözcük grubudur. The shop closed özne + fiil sırasını korur; what time did the shop close düzeni aktarımın içinde kullanılmaz. Tüm cümle bir geçmiş bildirimidir.
""", """
[Where does] she live? | O nerede yaşıyor? | Doğrudan soruda yardımcı ve özne yer değiştirir.
He asked [where she lived]. | Onun nerede yaşadığını sordu. | Aktarılan iç soruda düz cümle sırası kullanılır.
""")
_add("rs:2", """
Sözün görevini önce tanımak | Birinin 'Sit down' demesi bilgi sorusu değil talimattır. Bunu aktarırken cümlenin bütün soru/fiil düzenini taşımak yerine tell/ask + kişi + to + V1 kullanılır. Ask daha çok rica, tell talimat anlamını öne çıkarabilir; ton ve bağlam yine önemlidir.
Olumsuz talimatı kurmak | 'Don't interrupt' → told me not to interrupt. Not, to'dan önce gelir; don't aynı biçimde aktarımın içinde bırakılmaz. Kişi nesnesi kime talimat verildiğini gösterir. 'She told to wait' temel tell kalıbında bu nesneyi eksik bırakır.
Aktarım fiilinin kendi kalıbı | Advise/warn/remind gibi fiiller nesne + to-infinitive alabilir. Ancak bütün reporting verbs aynı düzeni almaz: suggest doing, suggest that… doğaldır; 'suggest me to go' temel standart kalıp değildir. Yalnızca 'birisi söyledi' Türkçesine bakarak bütün fiilleri aynı şablona koyma.
""", """
The guide işi yapacak grubu us ile belirtir; to stay together aktarılmış talimatın içeriğidir. Geçmişi told taşır, stay yalın kalır. 'Told us to stayed' ikinci bir geçmiş çekimi ekler.
Asked him, ricayı kime yönelttiğini gösterir. Not to interrupt, yapılmaması istenen davranıştır. Bu cümle, kişinin gerçekten söz kesip kesmediğini tek başına bildirmez; ricayı aktarır.
""", """
He asked me [whether I could wait]. | Bekleyip bekleyemeyeceğimi sordu. | Yeterliliğe/uygunluğa ilişkin soru içeriği aktarılır.
He asked me [to wait]. | Beklememi rica etti. | Bekleme davranışının yapılması istenir; yalnızca bir soru aktarımı değildir.
""")

_add("gi:0", """
İkinci fiilin biçimi neden değişir? | İngilizcede bir fiilden sonra başka fiil geldiğinde, ikinci fiil ilk fiilin istediği kalıba uyar. Enjoy doing, decide to do birlikte öğrenilir. Bu seçim yalnızca ikinci eylemin geçmiş/gelecek olmasıyla açıklanmaz; asıl fiilin söz dizimsel kalıbı önemlidir.
Gerund, infinitive ve özne | -Ing biçimi isim benzeri görev alabilir: Swimming is fun. To-infinitive amaç, plan veya fiil tamamlayıcısı olabilir. 'I want to leave' cümlesinde to leave, want'ın tamamlayıcısıdır; ana zamanı want taşır. 'I wanted to leave' geçmiş olsa da to leave aynı kalır.
İki yapıyı kabul eden fiiller | Like/love/begin gibi bazı fiiller iki yapıyla da kullanılabilir; bağlam ve vurgu değişebilir. Stop/remember/try gibi fiillerde anlam farkı daha belirgindir ve sonraki derste ayrılır. İngilizcedeki bütün -ing biçimlerini yalnızca 'şimdiki zaman' diye düşünmek bu kalıpları anlamayı zorlaştırır.
""", """
Enjoy ardından cooking -ing biçimini ister; bu cümlede am/is/are olmadığı için present continuous oluşmaz. Enjoy ana çekimli fiildir. For friends yemek yapmanın kimin için olduğunu belirtir.
Decided, geçmişteki karar eylemini taşır. To leave, decide fiilinin istediği tamamlayıcı biçimidir ve geçmişe göre left yapılmaz. Early ayrılmanın zamanlamasıyla ilgilidir.
""", """
She [enjoys reading]. | Okumaktan hoşlanır. | Enjoy, -ing tamamlayıcısıyla kullanılır.
She [wants to read]. | Okumak istiyor. | Want, to-infinitive tamamlayıcısıyla kullanılır; okuma eylemi aynı olsa da kalıp değişir.
""")
_add("gi:1", """
Stop: bırakılan iş mi, durmanın amacı mı? | Stop doing'de ikinci fiil bırakılan faaliyettir: stop talking konuşmayı bırak. Stop to do'da ise önceki hareket durdurulup yeni bir amaç yapılır: stop to talk konuşmak için dur. Türkçede her ikisinin çevirisinde 'durmak' görünebilse de eylem ilişkisi ters olabilir.
Remember: geçmiş anı mı, yapılacak görev mi? | Remember doing, daha önce yaşanan eylemin anısını hatırlamaktır. Remember to do, yapılacak işi akılda tutup unutmamaktır. 'I remembered locking the door' bir anı; 'I remembered to lock the door' kilitlemeyi unutmadım anlamı taşır. Hangi eylemin önce geldiğini izle.
Try: çaba mı, çözüm denemesi mi? | Try to do bir işi başarmaya çalışmayı; try doing bir yöntem deneyip işe yarayıp yaramadığına bakmayı öne çıkarır. 'Try opening the window' bir çözüm önerisi; 'I tried to open it, but it was stuck' başarısız çaba olabilir. Bu örnekte başarısızlığı but bölümü belirginleştirir.
""", """
Stopped, önceki hareketin durmasını; to take a photo, durmanın amacını verir. Fotoğraf çekmeyi bırakmak istense stopped taking photos denirdi. To burada hangi iş için durulduğunu ayırır.
Remember meeting geçmişteki tanışmayı bir anı olarak hatırlatır. Bu, gelecekte onunla tanışmayı unutmama talimatı değildir. Meeting, remember'ın ardından anısı hatırlanan eylemi gösterir.
""", """
He [stopped smoking]. | Sigara içmeyi bıraktı. | Bırakılan faaliyetin kendisi sigara içmektir.
He [stopped to smoke]. | Sigara içmek için durdu. | Başka bir faaliyet durdurulur; sigara içmek yeni amaçtır.
""")
_add("gi:2", """
Üç benzer görünümlü yapı | Used to + V1 geçmişteki alışkanlık/durumu; be used to + isim/-ing alışkın olma durumunu; get used to ise alışma sürecini anlatır. Yazılışları benzer olsa da to'nun görevi ve zaman çekiminin yeri farklıdır. Önce be/get bulunup bulunmadığını kontrol et.
Geçmiş alışkanlık ile durum | 'I used to live there' çoğu bağlamda artık orada yaşamadığımı gösterir. 'I was used to living there' geçmişte oradaki yaşama alışkındım der; aynı anlam değildir. Used to sorusu did ile kurulduğunda yazıda Did you use to…? biçimi standarttır.
Would ile ve şimdiki alışkanlıkla fark | Would geçmişte tekrar eden davranışları anlatabilir; geçmişteki sahiplik/durum için used to daha uygundur: I used to own a bike. Şimdiki alışkanlık için normally/usually + present simple kullanılır. Be/get used to sonrasında to edat olduğu için driving gibi -ing gelir; to drive yapılmaz.
""", """
Used to live geçmişteki yaşam durumunu şimdiki durumdan ayırır. Burada be yoktur; 'alışkın olmak' anlatılmıyor. Live yalındır, used to living temel geçmiş alışkanlık kalıbı değildir.
Is used to working, şimdiki alışkınlık durumudur. To bu kalıpta edat olduğu için working kullanılır. Cümle geçmişte artık bırakılmış gece çalışmasını değil, onunla rahat/alışık olmayı anlatır.
""", """
I [used to drive] at night. | Eskiden geceleri araba sürerdim. | Geçmiş alışkanlık/düzen anlatılır.
I [am used to driving] at night. | Gece araba sürmeye alışkınım. | Şimdiki alışkınlık durumu anlatılır; sürme işi yeni veya zor gelmeyebilir.
""")
_add("gi:3", """
Amaç ile fiil tamamlayıcısını ayırmak | 'I went out to buy milk' cümlesinde to buy neden dışarı çıktığını, yani amacı anlatır. 'I want to buy milk' cümlesinde ise want'ın tamamlayıcısıdır. Biçimleri benzer olsa da görevleri farklıdır. Her Türkçe '-mek için' ifadesi for + yalın fiil olarak çevrilmez.
To bazen edattır | Interested in learning, without speaking, before leaving gibi yapılarda edattan sonra -ing gelir. Look forward to hearing kalıbındaki to da edattır; bu nedenle hear yalın biçimine dönülmez. To'nun her görüldüğü yerde infinitive başlatmadığını öğrenmek bu hatayı çözer.
Yalın fiil ve passive istisnası | Let/make + kişi aktif yapıda yalın fiil alır: let me go, made me wait. Help ile to'lu veya to'suz biçim olabilir. Make passive olduğunda to geri gelir: I was made to wait. Bu nedenle bir kalıbı öğrenirken aktif/pasif yapısını da kontrol et.
""", """
To buy fruit, pazara gitmenin amacını açıklar. Went ana geçmiş fiildir; buy yalın kalır ve bought yapılmaz. Amaç cümlesinin kendi ayrı bir zaman çekimi yoktur.
Without bir edattır; ardından saying -ing biçimi gelir. Left ana olayın geçmişini taşır. Saying burada şimdiki zaman oluşturmaz; hoşça kal deme eyleminin yapılmadığını belirten yapının parçasıdır.
""", """
The teacher [made us wait]. | Öğretmen bizi bekletti. | Aktif make + kişi yapısında yalın wait kullanılır.
We [were made to wait]. | Bekletildik/beklemeye zorlandık. | Make edilgenleşince to-infinitive kullanılır.
""")
