"""Original Turkish grammar lessons and contextual exercises for the single-file app.

Each lesson has its own examples, four explained questions, and an optional
form reference. Levels are study targets, not a certification or placement test.
"""

REFERENCE = "https://learnenglish.britishcouncil.org/free-resources/grammar/english-grammar-reference"
BASIC = "https://learnenglish.britishcouncil.org/free-resources/grammar/a1-a2"
INTERMEDIATE = "https://learnenglish.britishcouncil.org/free-resources/grammar/b1-b2"


def _topic(code, title, lead, badge, source=REFERENCE):
    return dict(id=code, title=title, lead=lead, badge=badge, source=source,
                reference=True, lessons=[], sets=[], levels=[])


def _rows(text):
    return [[part.strip() for part in line.split("|")] for line in text.strip().splitlines() if line.strip()]


def _lesson(topic, title, level, text, forms, signals, mistake, examples, questions):
    set_id = f"{topic['id']}-{len(topic['lessons']) + 1}"
    items = []
    for q, answer, wrong, tr, why in _rows(questions):
        options = [answer, *wrong.split(" / ")]
        assert len(options) == 4 and len({option.casefold() for option in options}) == 4, (title, q)
        assert q.count("___") == 1 and all((tr, why)), (title, q)
        items.append(dict(q=q, answer=answer, options=options, tr=tr, why=why))
    example_rows = _rows(examples)
    assert len(items) == 4 and len(example_rows) >= 2, title
    assert all(len(row) == 2 and "[" in row[0] and "]" in row[0] for row in example_rows), title
    topic["lessons"].append(dict(title=title, level=level, text=text,
        forms=[part.strip().split(": ", 1) for part in forms.split("|")], signals=signals,
        mistake=mistake, examples=example_rows, quiz=dict(set=set_id)))
    topic["sets"].append(dict(id=set_id, title=title + " · Alıştırma", hint="Türkçe anlamı ve verilen bağlamı dikkate alarak boşluğu tamamla.", items=items))
    if level not in topic["levels"]:
        topic["levels"].append(level)


def core_topics():
    bs = _topic("bs", "Temel cümle yapıları", "Özne, fiil, to be, zamirler, sahiplik ve soru kurma. Zamanlardan önce sağlam bir temel.", "ABC", BASIC)
    _lesson(bs, "Cümle sırası ve to be", "A1",
        "İngilizce bir bildirme cümlesinde genellikle önce özne, sonra fiil gelir. Meslek, kimlik, durum ve yer bildirirken am/is/are kullanılır: I am, he/she/it is, you/we/they are. Türkçede açık bir fiil bulunmaması İngilizcede be fiilini kaldırmaz.",
        "Olumlu: Subject + am/is/are + complement | Olumsuz: Subject + am/is/are + not | Soru: Am/Is/Are + subject + complement?",
        "Bir durumu anlatırken be; bir eylemi anlatırken uygun asıl fiili kullan.",
        "I student değil I am a student. She is work değil She works.",
        "My brother [is] a nurse. | Erkek kardeşim hemşire.\n[Are] your parents at home? | Anne baban evde mi?",
        "I ___ ready. | am | is / are / be | Ben hazırım. | I öznesiyle am kullanılır.\nThe windows ___ open. | are | is / am / be | Pencereler açık. | Çoğul özne windows, are alır.\nShe ___ not tired. | is | are / am / be | O yorgun değil. | She ile is not kullanılır.\n___ he your teacher? | Is | Am / Are / Be | O senin öğretmenin mi? | Be ile soru kurarken is öznenin önüne gelir.")
    _lesson(bs, "Özne, nesne ve sahiplik zamirleri", "A1",
        "I, you, he, she, it, we, they özne; me, you, him, her, it, us, them nesne biçimleridir. My/your/his/her/its/our/their bir isimden önce gelir. Mine/yours/his/hers/ours/theirs ise ismin yerini alır. Its sahiplik, it's ise it is veya it has kısaltmasıdır.",
        "Özne: She knows me. | İsimden önce: This is my bag. | İsmin yerine: This bag is mine.",
        "Fiili yapanla fiilden etkileneni ayır; sahiplik sözcüğünden sonra isim gelip gelmediğine bak.",
        "This is mine book değil This is my book. Give it to I değil Give it to me.",
        "Please call [her] tonight. | Lütfen bu akşam onu ara.\nThose seats are [ours]. | Şu koltuklar bizim.",
        "Tom is kind. ___ helps everyone. | He | Him / His / Himself | Tom naziktir. O herkese yardım eder. | Fiilin öznesi için he gerekir.\nCan you help ___? | us | we / our / ours | Bize yardım edebilir misin? | Help fiilinden sonra nesne zamiri us kullanılır.\nThis is ___ jacket. | my | mine / me / I | Bu benim ceketim. | Jacket isminden önce my gelir.\nThe dog is wagging ___ tail. | its | it's / it / itself | Köpek kuyruğunu sallıyor. | Tail isminin sahibi için its kullanılır; apostrof yoktur.")
    _lesson(bs, "Have/has ve there is/are", "A1",
        "Have/has bir kişinin sahip olduğu şeyi anlatır; he/she/it ile has kullanılır. There is/are bir yerde bir şeyin var olduğunu söyler. There is tekil veya sayılamayan isimle, there are çoğul isimle kullanılır. Have sorularında do/does; there is/are sorularında is/are öne gelir.",
        "Sahiplik: She has a bike. / Does she have a bike? | Varlık: There is a shop. / There are two shops. | Olumsuz: She doesn't have a bike. / There isn't a shop.",
        "Kimin neye sahip olduğunu mu, bir yerde ne bulunduğunu mu söylediğini seç.",
        "Does she has değil Does she have. There is two books değil There are two books.",
        "Our house [has] a small garden. | Evimizin küçük bir bahçesi var.\n[There are] three cups on the desk. | Masada üç fincan var.",
        "My sister ___ two cats. | has | have / having / is have | Kız kardeşimin iki kedisi var. | My sister üçüncü tekil kişidir; has gerekir.\nThere ___ some milk in the fridge. | is | are / have / has | Buzdolabında biraz süt var. | Milk sayılamayan isimdir; there is kullanılır.\n___ there any chairs here? | Are | Is / Has / Have | Burada hiç sandalye var mı? | Chairs çoğuldur; Are there sorusu kurulur.\nDoes your flat ___ a balcony? | have | has / having / had | Dairenin balkonu var mı? | Does sonrasında fiil yalın biçimde have olur.")
    _lesson(bs, "Do/does soruları, olumsuzlar ve emirler", "A1",
        "Present simple içindeki asıl fiillerle soru kurarken do/does, olumsuzlukta don't/doesn't kullanılır. Yardımcı fiilden sonra asıl fiil yalın kalır. Emirlerde özne genellikle söylenmez: Open the door. Olumsuz emir Don't + fiil biçimindedir. Be ile sorularda do eklenmez.",
        "Soru: Do/Does + subject + base verb? | Olumsuz: Subject + don't/doesn't + base verb | Emir: Please + base verb. / Don't + base verb.",
        "She likes tea → Does she like tea? She is ready → Is she ready?",
        "Does she likes değil Does she like. Do you are ready değil Are you ready.",
        "[Do] you need a ticket? | Bilete ihtiyacın var mı?\n[Don't touch] the hot pan. | Sıcak tavaya dokunma.",
        "___ your brother speak English? | Does | Do / Is / Are | Erkek kardeşin İngilizce konuşur mu? | Speak asıl fiildir; tekil özneyle does kullanılır.\nWe ___ eat meat. | don't | doesn't / aren't / isn't | Biz et yemeyiz. | We ile don't + yalın fiil kullanılır.\nPlease ___ your name here. | write | writes / writing / to write | Lütfen adını buraya yaz. | Emirde fiil yalın biçimdedir.\n___ run in the corridor. | Don't | Doesn't / Not / Aren't | Koridorda koşma. | Olumsuz emir Don't + fiil ile kurulur.")

    tn = _topic("tn", "Zamanlar ve gelecek anlatımı (Tenses)", "Present, past, perfect ve continuous yapıları; will, going to ve karşılaştırmalı zaman dersleri.", "TIME", INTERMEDIATE)
    tn["keywords"] = "tenseler tense zaman şimdiki geniş geçmiş gelecek"
    _lesson(tn, "Present Simple · Geniş zaman", "A1",
        "Alışkanlık, düzenli eylem ve genel gerçekleri anlatır. He/she/it ile olumlu fiile -s/-es gelir. Soruda do/does, olumsuzda don't/doesn't kullanılır ve asıl fiil yalın kalır. V1 fiilin yalın biçimi, V2 geçmiş biçimi, V3 ise past participle biçimidir; örneğin go–went–gone.",
        "Olumlu: I/you/we/they work; he/she/it works | Olumsuz: Subject + don't/doesn't + V1 | Soru: Do/Does + subject + V1?",
        "Every day, usually ve often alışkanlığa işaret edebilir; asıl belirleyici cümlenin anlamıdır.",
        "He don't work değil He doesn't work. Does she works değil Does she work.",
        "The bakery [opens] at six every morning. | Fırın her sabah altıda açılır.\n[Do] you usually walk to school? | Okula genellikle yürüyerek mi gidersin?",
        "My father ___ coffee every morning. | drinks | drink / drinking / is drink | Babam her sabah kahve içer. | Üçüncü tekil öznenin olumlu fiiline -s gelir.\nThey ___ work on Sundays. | don't | doesn't / isn't / not | Onlar pazar günleri çalışmaz. | They ile don't kullanılır.\n___ she live near here? | Does | Do / Is / Has | O buralarda mı yaşar? | Present simple sorusu does + özne + yalın fiille kurulur.\nWater ___ at 100°C at sea level. | boils | boil / boiling / is boil | Su deniz seviyesinde 100°C'de kaynar. | Genel gerçek için present simple; water tekil uyum ister.")
    _lesson(tn, "Present Continuous · Şimdiki zaman", "A1",
        "Konuşma anında süren veya bu dönem için geçici olan eylemleri am/is/are + V-ing ile anlatırız. Soru için be öne gelir, olumsuzluk için be'den sonra not gelir. Know, believe, own gibi durum fiilleri temel anlamlarında genellikle continuous kullanılmaz.",
        "Olumlu: Subject + am/is/are + V-ing | Olumsuz: Subject + am/is/are + not + V-ing | Soru: Am/Is/Are + subject + V-ing?",
        "Now, at the moment ve this week geçici bir süreci gösterebilir.",
        "I working değil I am working. I am knowing değil I know.",
        "The children [are building] a sandcastle now. | Çocuklar şimdi kumdan kale yapıyor.\nShe [isn't sleeping] at the moment. | O şu anda uyumuyor.",
        "Listen! Someone ___ at the door. | is knocking | knocking / are knocking / is knock | Dinle! Biri kapıyı çalıyor. | Şu anda süren eylem is + V-ing ile anlatılır.\nI ___ studying right now. | am | is / are / be | Şu anda ders çalışıyorum. | I ile am gerekir.\n___ they waiting outside now? | Are | Do / Have / Does | Onlar şimdi dışarıda mı bekliyor? | Continuous sorusunda are öne gelir.\nHe is not ___ TV at the moment. | watching | watch / watches / watched | O şu anda televizyon izlemiyor. | Is not sonrasında V-ing gerekir.")
    _lesson(tn, "Present Simple mı, Present Continuous mı?", "A2",
        "Present simple kalıcı durum, alışkanlık veya genel gerçeğe; present continuous şimdi süren veya geçici eyleme odaklanır. Aynı fiil farklı bağlamlarda iki yapıda da kullanılabilir: I work from home (düzenim), I'm working from home this week (geçici). Have, think gibi bazı fiiller anlamlarına göre durum veya eylem olabilir.",
        "Düzenli: She works every weekday. | Geçici: She is working from home this week. | Durum: I understand. / I own this car.",
        "Her zaman olanla şu anda olanı karşılaştır; tek bir zaman zarfına ezbere bağlanma.",
        "I am understanding değil I understand. Durum fiillerini otomatik olarak -ing yapma.",
        "He usually [cycles], but today he [is walking]. | Genellikle bisiklete biner ama bugün yürüyor.\nI [believe] you. | Sana inanıyorum.",
        "Maya usually ___ to work by train. | travels | is travel / travelling / travel | Maya işe genellikle trenle gider. | Alışkanlık ve üçüncü tekil özne için travels gerekir.\nBe quiet! The baby ___ right now. | is sleeping | sleeps every day / sleeping / are sleeping | Sessiz ol! Bebek şu an uyuyor. | Şu anda süren eylem is sleeping olur.\nI ___ the answer. | know | am knowing / knowing / knows | Cevabı biliyorum. | Know burada durum fiilidir; present simple kullanılır.\nWe usually eat at home, but tonight we ___ at a restaurant. | are eating | is eating / eating / eats | Genellikle evde yeriz ama bu akşam restoranda yemek yiyoruz. | Geçici düzenleme için are eating kullanılır.")
    _lesson(tn, "Past Simple · Geçmiş zaman", "A1",
        "Geçmişte bitmiş eylemleri ve tamamlanmış olay dizilerini anlatır. Düzenli fiiller -ed alır; düzensizlerin V2 biçimi öğrenilir. Did/didn't sonrasında V1 kullanılır. Be fiilinin geçmişi was/were'dür ve be sorularına did eklenmez.",
        "Olumlu: Subject + V2 | Olumsuz: Subject + didn't + V1 | Soru: Did + subject + V1?",
        "Yesterday, last week, two days ago ve bitmiş tarihler geçmiş bağlamı kurar.",
        "Did you went değil Did you go. I didn't saw değil I didn't see.",
        "We [visited] the museum last Saturday. | Geçen cumartesi müzeyi ziyaret ettik.\n[Did] she [send] the email yesterday? | E-postayı dün gönderdi mi?",
        "I ___ my keys yesterday. | lost | lose / losing / have lose | Dün anahtarlarımı kaybettim. | Yesterday bitmiş geçmiş zamandır; lose fiilinin V2'si lost'tur.\nShe didn't ___ the bus this morning. | catch | caught / catching / catches | Bu sabah otobüse yetişemedi. | Didn't sonrası V1 catch olur.\n___ you finish the report last night? | Did | Do / Have / Were | Dün gece raporu bitirdin mi? | Bitmiş geçmişte asıl fiille soru did ile kurulur.\nThey ___ at home last night. | were | was / be / are being | Dün gece evdeydiler. | They ile be fiilinin geçmişi were olur.")
    _lesson(tn, "Past Continuous · Geçmişte devam", "A2",
        "Geçmişte belli bir anda sürmekte olan eylemi was/were + V-ing ile anlatır. Bir hikâyenin arka planını kurabilir. I/he/she/it ile was, you/we/they ile were kullanılır. Eylemin başlangıç veya bitişinden çok o andaki devamı önemlidir.",
        "Olumlu: Subject + was/were + V-ing | Olumsuz: Subject + wasn't/weren't + V-ing | Soru: Was/Were + subject + V-ing?",
        "At eight last night, at that moment ve while bir geçmiş anını veya arka planı verebilir.",
        "They was working değil They were working. Was he work değil Was he working.",
        "At midnight, I [was reading]. | Gece yarısında kitap okuyordum.\n[Were] the children [playing] when you arrived? | Sen vardığında çocuklar oynuyor muydu?",
        "At nine last night, she ___ for her exam. | was studying | were studying / studying / was study | Dün gece saat dokuzda sınavına çalışıyordu. | Geçmişte o anda süren eylem was studying olur.\nWe ___ not sleeping when the phone rang. | were | was / did / had | Telefon çaldığında uyumuyorduk. | We ile were not + V-ing kurulur.\n___ he driving at that moment? | Was | Did / Has / Does | O anda araba mı sürüyordu? | Past continuous sorusunda was öne gelir.\nThe workers were ___ the road at six yesterday. | repairing | repair / repaired / repairs | İşçiler dün altıda yolu onarıyordu. | Were sonrasında V-ing gerekir.")
    _lesson(tn, "Past Simple ve Past Continuous birlikte", "A2",
        "Past continuous devam eden arka planı, past simple ise tamamlanmış olayı gösterir. Kısa olay uzun eylemi kesebilir: I was cooking when the lights went out. While çoğu kez devam eden eylemi tanıtır; ancak bağlaç tek başına zamanı belirleyen değişmez bir kural değildir.",
        "Arka plan: Subject + was/were + V-ing | Olay: Subject + V2 | Birlikte: I was walking when it started to rain.",
        "Hangi eylemin sürmekte olduğunu, hangisinin o sırada gerçekleştiğini düşün.",
        "When gördüğün her yere past simple, while gördüğün her yere continuous koyma; anlamı kontrol et.",
        "She [was painting] when the doorbell [rang]. | Kapı zili çaldığında resim yapıyordu.\nWhile we [were walking], we [found] a wallet. | Yürürken bir cüzdan bulduk.",
        "I was taking a shower when the phone ___. | rang | ring / ringing / was ring | Duş alıyordum; o sırada telefon çaldı. | Tamamlanmış kısa olay için rang kullanılır.\nWhile they ___ dinner, the lights went out. | were cooking | was cooking / cooking / were cook | Akşam yemeği hazırlarken elektrik kesildi. | Hazırlama devam eden arka plandır; they ile were cooking olur.\nShe ___ off the bus, then walked home. | got | getting / was get / get | Otobüsten indi, ardından eve yürüdü. | Art arda tamamlanan olaylarda past simple kullanılır.\nWhen I saw him, he ___ across the street. | was running | were running / was run / running | Onu gördüğümde caddenin karşısına koşuyordu. | Görme anında devam eden eylem was running olur.")
    _lesson(tn, "Present Perfect · Geçmiş ile şimdi bağlantısı", "A2",
        "Have/has + V3; şimdiye kadarki deneyim, şu anki sonuç veya geçmişte başlayıp bugüne uzanan durumu anlatır. Bitmiş bir zaman dilimini söylemeden 'şimdiye kadar' bakışı verir. Düzenli fiillerde V2 ve V3 aynı olabilir; see–saw–seen gibi düzensizlerde farklıdır.",
        "Olumlu: Subject + have/has + V3 | Olumsuz: Subject + haven't/hasn't + V3 | Soru: Have/Has + subject + V3?",
        "Ever, never, already, yet, just ve so far sık görülür. Yesterday gibi bitmiş zamanlarla temel kullanımda past simple seçilir.",
        "I have went değil I have gone. I have seen him yesterday değil I saw him yesterday.",
        "I [have lost] my ticket, so I can't get in. | Biletimi kaybettim, bu yüzden içeri giremiyorum.\n[Have] you ever [ridden] a horse? | Hiç ata bindin mi?",
        "She has never ___ sushi. | eaten | ate / eat / eating | O hiç suşi yemedi. | Has sonrasında V3 eaten gerekir.\nWe ___ already finished the task. | have | has / are / did | Görevi çoktan bitirdik. | We ile have + V3 kullanılır.\n___ he called you yet? | Has | Did have / Is / Does | Seni henüz aradı mı? | Present perfect sorusunda has öne gelir.\nI haven't ___ that film before. | seen | saw / see / seeing | O filmi daha önce görmedim. | Haven't sonrasında see fiilinin V3 biçimi seen gelir.")
    _lesson(tn, "Present Perfect Continuous · Şimdiye uzanan süreç", "B1",
        "Have/has been + V-ing geçmişte başlayıp şimdiye uzanan veya az önce bitip etkisi görülen bir etkinliğin sürecini vurgular. Süreyi veya yakın zamandaki faaliyeti anlatırız. Know ve own gibi durum fiillerinde genellikle present perfect simple kullanılır.",
        "Olumlu: Subject + have/has been + V-ing | Olumsuz: Subject + haven't/hasn't been + V-ing | Soru: Have/Has + subject + been + V-ing?",
        "For süreyi, since başlangıç noktasını verir. How long süreç sorabilir.",
        "I have been knowing her değil I have known her. Has she been work değil Has she been working.",
        "I [have been waiting] for twenty minutes. | Yirmi dakikadır bekliyorum.\nHis hands are dirty because he [has been gardening]. | Bahçeyle uğraştığı için elleri kirli.",
        "She has been ___ English since January. | learning | learn / learned / learns | Ocaktan beri İngilizce öğreniyor. | Has been sonrasında V-ing kullanılır.\nThey ___ been working all morning. | have | has / are / did | Bütün sabah çalışıyorlar. | They ile have been gerekir.\nI have been waiting ___ two hours. | for | since / at / from | İki saattir bekliyorum. | Two hours bir süredir; for kullanılır.\nHe has been living here ___ 2022. | since | for / during / on | 2022'den beri burada yaşıyor. | 2022 başlangıç noktasıdır; since gerekir.")
    _lesson(tn, "Present Perfect mi, Past Simple mı?", "B1",
        "Past simple bitmiş geçmiş zamanın içine bakar; present perfect bugünden şimdiye kadarki döneme bakar. I visited Rome in 2020 bitmiş tarih verir. I have visited Rome deneyimi şimdiye kadar ele alır. Today gibi henüz bitmemiş dönemlerde seçim konuşanın bakışına da bağlıdır.",
        "Bitmiş zaman: I saw her yesterday. | Şimdiye kadar: I have seen her twice so far. | Soru: When did you go? / Have you ever been?",
        "Last year, in 2019 gibi bitmiş zamanlarla past simple; so far ile şimdiye kadarki toplamı düşün.",
        "Have you ever went değil Have you ever been. When have you finished yesterday değil When did you finish yesterday.",
        "We [moved] here in 2018. | 2018'de buraya taşındık.\nWe [have lived] here since 2018. | 2018'den beri burada yaşıyoruz.",
        "I ___ him yesterday afternoon. | met | have met / has met / meeting | Onunla dün öğleden sonra karşılaştım. | Yesterday bitmiş zaman olduğu için met kullanılır.\nShe ___ three books so far this month. | has read | read yesterday / have read / has reading | Bu ay şimdiye kadar üç kitap okudu. | So far şimdiye kadarki toplamı anlatır; has read uygundur.\nThey ___ to Spain in 2017. | went | have gone / has gone / going | 2017'de İspanya'ya gittiler. | Belirli, bitmiş tarih past simple ister.\n___ you ever been to Canada? | Have | Did / Are / Has | Hiç Kanada'da bulundun mu? | Şimdiye kadarki deneyim have + V3 ile sorulur.")
    _lesson(tn, "Perfect Simple ve Continuous farkı", "B1",
        "Perfect simple çoğu kez sonuca, bitmiş miktara veya duruma odaklanır; perfect continuous etkinliğin sürecine ve süresine. I've written three pages tamamlanan miktarı, I've been writing for an hour süreci anlatır. Bazı fiillerle iki yapı da mümkündür; anlam vurgusu değişir.",
        "Sonuç/miktar: I have written five emails. | Süreç: I have been writing emails all morning. | Durum: I have known her for years.",
        "How many tamamlanan miktarı, how long ise çoğu kez süreyi öne çıkarır.",
        "I have been writing five completed reports değil tamamlanan sayıyı anlatırken I have written five reports.",
        "She [has painted] two doors today. | Bugün iki kapıyı boyayıp bitirdi.\nShe [has been painting] since breakfast. | Kahvaltıdan beri boya yapıyor.",
        "He ___ five letters, and all five are ready to send. | has written | has been written / have written / has writing | Beş mektup yazdı; beşi de gönderilmeye hazır. | Tamamlanan miktar için perfect simple kullanılır.\nI've ___ her since primary school. | known | been knowing / knew / knowing | Onu ilkokuldan beri tanıyorum. | Know durum fiilidir; have known uygundur.\nThey have been ___ the house all day; it still isn't finished. | cleaning | cleaned / clean / cleans | Bütün gün evi temizliyorlar; hâlâ bitmedi. | Devam eden faaliyet have been cleaning ile anlatılır.\nHow many chapters ___ you finished so far? | have | has / are / did have | Şimdiye kadar kaç bölümü bitirdin? | Tamamlanan miktar have + finished ile sorulur.")
    _lesson(tn, "Past Perfect · Geçmişten önceki geçmiş", "B1",
        "Had + V3 geçmişteki bir referans noktasından daha önce olan eylemi gösterir. İki geçmiş olaydan hangisinin önce olduğunu netleştirir. Her eski olay için zorunlu değildir; before/after gibi sözcükler sıralamayı zaten açık ediyorsa past simple da kullanılabilir.",
        "Olumlu: Subject + had + V3 | Olumsuz: Subject + hadn't + V3 | Soru: Had + subject + V3?",
        "By the time ve already geçmiş referans anından önceki tamamlanmayı vurgulayabilir.",
        "Had went değil had gone. Hikâyedeki her fiili otomatik olarak past perfect yapma.",
        "When I arrived, the guests [had left]. | Vardığımda misafirler çoktan gitmişti.\nShe [hadn't seen] snow before that winter. | O kıştan önce hiç kar görmemişti.",
        "By the time we got there, the film had already ___. | started | start / starting / starts | Biz oraya vardığımızda film çoktan başlamıştı. | Had sonrasında V3 started gerekir.\nI couldn't open the door because I ___ lost the key. | had | have / am / did | Anahtarı önceden kaybettiğim için kapıyı açamadım. | Kaybetme, geçmişteki açamama anından önce gerçekleşti.\n___ they finished before the manager arrived? | Had | Have / Do / Were | Müdür gelmeden önce bitirmişler miydi? | Geçmiş referansından öncesi had + V3 ile sorulur.\nHe hadn't ___ breakfast when he left home. | eaten | ate / eat / eating | Evden çıktığında kahvaltı etmemişti. | Hadn't sonrasında V3 eaten gelir.")
    _lesson(tn, "Past Perfect Continuous · Geçmişe kadar süren", "B2",
        "Had been + V-ing geçmişteki bir ana kadar devam etmiş faaliyetin sürecini veya süresini anlatır. Bu faaliyet o ana kadar sürmüş veya hemen öncesinde bitmiş olabilir. Süreç ile daha sonraki geçmiş sonuç arasında bağlantı kurarız.",
        "Olumlu: Subject + had been + V-ing | Olumsuz: Subject + hadn't been + V-ing | Soru: Had + subject + been + V-ing?",
        "For two hours before… gibi ifadeler geçmişte bir referans anına kadar geçen süreyi verir.",
        "Had been work değil had been working. Durum fiillerinde had known gibi simple yapıyı seç.",
        "They [had been hiking] for hours before they found shelter. | Sığınak bulmadan önce saatlerdir yürüyüş yapıyorlardı.\nI was exhausted because I [had been moving] furniture. | Mobilyaları taşıdığım için çok yorgundum.",
        "She had been ___ for an hour when the bus finally came. | waiting | waited / wait / waits | Otobüs sonunda geldiğinde bir saattir bekliyordu. | Had been sonrasında V-ing gerekir.\nWe ___ been driving for six hours before we stopped. | had | have / are / did | Durmadan önce altı saattir araba sürüyorduk. | Geçmişteki durma anına kadar süren eylem had been driving olur.\n___ he been working there long before he resigned? | Had | Has / Did / Was | İstifa etmeden önce uzun süredir orada mı çalışıyordu? | Soru had + özne + been + V-ing ile kurulur.\nI had been studying ___ three hours before dinner. | for | since / at / on | Akşam yemeğinden önce üç saattir çalışıyordum. | Süre bildiren three hours önünde for gerekir.")
    _lesson(tn, "Will · Karar, tahmin ve gelecek", "A2",
        "Will + V1 konuşma anında verilen karar, teklif, söz ve tahminde kullanılır. Olumsuzu will not/won't'tur. Will'den sonra özneye göre -s gelmez. İngilizcede gelecek anlatımının tek bir biçimi yoktur; will, going to ve başka yapılar bağlama göre seçilir.",
        "Olumlu: Subject + will + V1 | Olumsuz: Subject + won't + V1 | Soru: Will + subject + V1?",
        "I think tahmini, I'll help teklif veya o an verilen kararı tanıtabilir.",
        "She will goes değil She will go. Her gelecek cümlesini will ile kurmak zorunda değilsin.",
        "That bag looks heavy. I [will carry] it for you. | O çanta ağır görünüyor. Senin için taşıyayım.\nI think the weather [will improve] tomorrow. | Bence yarın hava düzelecek.",
        "I'm cold. I think I ___ close the window. | will | am / have / did | Üşüdüm. Sanırım pencereyi kapatacağım. | O anda verilen karar will ile anlatılabilir.\nShe will ___ you later. | call | calls / called / calling | Seni daha sonra arayacak. | Will sonrasında yalın fiil call gelir.\n___ you help me with this box? | Will | Are / Have / Does | Bu kutu konusunda bana yardım eder misin? | Will you bir rica veya yardım isteği kurabilir.\nI promise I ___ tell anyone. | won't | don't to / am not / didn't to | Söz veriyorum, kimseye söylemeyeceğim. | Olumsuz gelecek sözü won't + V1 ile kurulur.")
    _lesson(tn, "Going to ve gelecek planları", "A2",
        "Be going to + V1 önceden verilen niyet/plan veya şu an görülen kanıta dayalı tahmin için kullanılır. Present continuous kesinleşmiş kişisel düzenlemeleri anlatabilir: I'm meeting the dentist tomorrow. Present simple tarifeli gelecek olaylarda kullanılabilir: The train leaves at six.",
        "Niyet/kanıt: Subject + am/is/are going to + V1 | Düzenleme: Subject + am/is/are + V-ing + future time | Tarife: The train leaves at six.",
        "Planın mı var, randevun mu ayarlı, yoksa bir tarife mi var? Yapıyı buna göre seç.",
        "She going to leave değil She is going to leave. Going to sonrasında V-ing değil V1 gelir.",
        "Look at those clouds. It [is going to rain]. | Şu bulutlara bak. Yağmur yağacak.\nWe [are meeting] the architect at ten tomorrow. | Yarın onda mimarla buluşuyoruz.",
        "We are going to ___ a new sofa next month. | buy | buying / bought / buys | Gelecek ay yeni bir kanepe almayı planlıyoruz. | Going to sonrasında V1 gerekir.\nLook! That glass ___ going to fall. | is | are / am / be | Bak! O bardak düşecek. | Tekil glass için is going to kullanılır.\nI ___ meeting the dentist tomorrow; the appointment is confirmed. | am | is / have / do | Yarın diş hekimiyle görüşüyorum; randevum kesinleşti. | Kesinleşmiş kişisel düzenleme am meeting ile anlatılır.\nAccording to the timetable, the train ___ at 6:15 tomorrow. | leaves | leave / leaving / is leave | Tarifeye göre tren yarın 6.15'te kalkıyor. | Tarifeli olayda present simple ve tekil train ile leaves kullanılır.")
    _lesson(tn, "Future Continuous · Gelecekte bir anda devam", "B1",
        "Will be + V-ing gelecekte belirli bir anda sürmekte olacak eylemi anlatır. O anın içindeymişiz gibi bakarız. Eylemin o zamana kadar bitmiş olmasından farklıdır; bitmişlik için future perfect kullanılır.",
        "Olumlu: Subject + will be + V-ing | Olumsuz: Subject + won't be + V-ing | Soru: Will + subject + be + V-ing?",
        "This time tomorrow, at nine tonight gibi ifadeler gelecekte bir referans anını belirler.",
        "Will be work değil will be working. Will working değil will be working.",
        "This time tomorrow, we [will be flying] over the sea. | Yarın bu saatlerde denizin üzerinde uçuyor olacağız.\n[Will] you [be using] the car tonight? | Bu akşam arabayı kullanıyor olacak mısın?",
        "At eight tomorrow evening, I will be ___ dinner. | cooking | cook / cooked / cooks | Yarın akşam sekizde yemek pişiriyor olacağım. | Will be sonrasında V-ing gelir.\nThey ___ be travelling at this time next week. | will | are / have / did | Gelecek hafta bu saatte seyahat ediyor olacaklar. | Gelecekte sürmekte olan eylem will be travelling olur.\nWill she ___ working when we arrive? | be | been / being / is | Biz vardığımızda çalışıyor olacak mı? | Future continuous sorusunda will + özne + be + V-ing gerekir.\nI won't be ___ my phone during the exam. | using | use / used / uses | Sınav sırasında telefonumu kullanıyor olmayacağım. | Won't be sonrasında using gerekir.")
    _lesson(tn, "Future Perfect · Geleceğe kadar tamamlanmış", "B2",
        "Will have + V3 gelecekte bir referans noktasına kadar tamamlanmış olacak işi anlatır. Önemli olan o anda sürmesi değil, o zamana kadar bitmesidir. By 'en geç o zamana kadar' anlamı taşır; until ise çoğunlukla bir durumun devam sınırını verir.",
        "Olumlu: Subject + will have + V3 | Olumsuz: Subject + won't have + V3 | Soru: Will + subject + have + V3?",
        "By Friday, by then ve by the time… tamamlanma için gelecek sınırı verir.",
        "Will have finish değil will have finished. Until Friday ile by Friday aynı anlama gelmez.",
        "By June, she [will have completed] the course. | Hazirana kadar kursu tamamlamış olacak.\nThey [won't have arrived] by noon. | Öğlene kadar varmış olmayacaklar.",
        "By next Friday, we will have ___ the project. | finished | finish / finishing / finishes | Gelecek cumaya kadar projeyi bitirmiş olacağız. | Will have sonrasında V3 finished gelir.\nShe ___ have left by the time we get there. | will | is / has / did | Biz oraya vardığımızda o gitmiş olacak. | Gelecek referansından önce tamamlanma will have left ile anlatılır.\nWill they ___ completed the work by Monday? | have | be / been / having | Pazartesiye kadar işi tamamlamış olacaklar mı? | Future perfect sorusunda will + özne + have + V3 gerekir.\nI will have read the book ___ tomorrow evening. | by | during / at / on | Yarın akşama kadar kitabı okumuş olacağım. | Bir son tarihe kadar tamamlanmayı by anlatır.")
    _lesson(tn, "Future Perfect Continuous · Geleceğe kadar geçen süre", "B2",
        "Will have been + V-ing gelecekteki bir ana kadar bir faaliyetin ne kadar süredir devam ediyor olacağını anlatır. Gelecek referans anı ve süre birlikte düşünülür. Durum fiilleriyle çoğunlukla future perfect simple tercih edilir: will have known.",
        "Olumlu: Subject + will have been + V-ing | Olumsuz: Subject + won't have been + V-ing | Soru: Will + subject + have been + V-ing?",
        "By next month … for ten years gibi bir bitiş referansı ve süre birlikte kullanılır.",
        "Will have been work değil will have been working. Her süre ifadesinde continuous zorunlu değildir.",
        "By July, I [will have been working] here for five years. | Temmuzda burada beş yıldır çalışıyor olacağım.\nBy midnight, they [will have been travelling] for twelve hours. | Gece yarısında on iki saattir yolculuk ediyor olacaklar.",
        "By June, she will have been ___ here for a year. | studying | study / studied / studies | Haziranda burada bir yıldır okuyor olacak. | Will have been sonrasında V-ing gerekir.\nNext month, we ___ have been living here for a decade. | will | are / did / were | Gelecek ay burada on yıldır yaşıyor olacağız. | Gelecek referansına kadar geçen süre will have been living ile anlatılır.\nWill he have ___ working for eight hours by then? | been | be / being / was | O zamana kadar sekiz saattir çalışıyor olacak mı? | Will have been working yapısında been gerekir.\nBy May, they will have been training ___ six months. | for | since / at / on | Mayısta altı aydır antrenman yapıyor olacaklar. | Six months bir süredir; for gerekir.")
    _lesson(tn, "Gelecek zaman cümlecikleri · when, until, as soon as", "B1",
        "Gelecekten söz eden zaman cümleciklerinde when, after, before, until ve as soon as sonrasında genellikle present simple; önce tamamlanmayı vurgulamak için present perfect kullanılır. Ana cümlede will bulunabilir. Bu kural zaman cümleciği içindir; I don't know when he will arrive gibi dolaylı sorular farklıdır.",
        "Zaman cümleciği: When + subject + present simple, subject + will + V1 | Tamamlanma: After I have finished, I'll call. | Dolaylı soru: I don't know when he will arrive.",
        "Önce zaman ilişkisi mi, 'ne zaman' sorusunun cevabı mı olduğunu ayır.",
        "I'll call when I will arrive değil I'll call when I arrive.",
        "I'll text you as soon as I [land]. | Uçağım iner inmez sana mesaj atacağım.\nWe won't leave until everyone [is] ready. | Herkes hazır olana kadar ayrılmayacağız.",
        "I'll call you when I ___ home. | get | will get / getting / got yesterday | Eve vardığımda seni arayacağım. | Gelecek zaman cümleciğinde when sonrasında present simple kullanılır.\nWe'll start as soon as she ___. | arrives | will arrive / arriving / arrive | O gelir gelmez başlayacağız. | Zaman cümleciğinde tekil she için arrives gerekir.\nDon't open the door until the train ___. | stops | will stop / stopping / stop | Tren durana kadar kapıyı açma. | Until sonrasında geleceği present simple ile anlatırız.\nI don't know when the next bus ___ arrive. | will | is / has / was | Sonraki otobüsün ne zaman geleceğini bilmiyorum. | Burada when bir dolaylı sorudur; will kullanılabilir.")

    nn = _topic("nn", "İsimler, articles ve miktar ifadeleri", "A/an/the, çoğullar, sayılabilen ve sayılamayan isimler; some, any, much, many, few ve little.", "N", BASIC)
    _lesson(nn, "A/an ve the · İlk kez mi, belirli mi?", "A1",
        "A/an tekil, sayılabilen ve henüz belirli olmayan bir isimle kullanılır. An seçimi harfe değil ilk sese bağlıdır: an hour ama a university. The, konuşanların hangi kişiden veya şeyden söz edildiğini bildiği durumlarda kullanılır. Meslek adları tekilken genellikle a/an alır.",
        "Belirsiz tekil: a book / an apple | Belirli: the book on this desk | Ses kuralı: an hour / a university",
        "İlk tanıtımda a/an; aynı şeyden yeniden veya açıkça belirli bir şeyden söz ederken the kullanılabilir.",
        "An university değil a university. She is teacher değil She is a teacher.",
        "We saw [a] fox. [The] fox ran into the trees. | Bir tilki gördük. Tilki ağaçların arasına koştu.\nHe is [an] engineer. | O bir mühendis.",
        "My aunt is ___ doctor. | a | an / some / any | Teyzem doktordur. | Tekil meslek adı doctor önünde a kullanılır.\nWe waited for ___ hour. | an | a / many / few | Bir saat bekledik. | Hour sözcüğünün ilk sesi ünlüdür; an gerekir.\nShe studies at ___ university. | a | an / many / any | O bir üniversitede okuyor. | University ünsüz /y/ sesiyle başlar; a kullanılır.\nI bought a lamp. ___ lamp is on my desk now. | The | A / An / Some | Bir lamba aldım. Lamba şimdi masamda. | Daha önce tanıtılan belirli lamba için the kullanılır.")
    _lesson(nn, "Çoğullar ve sayılamayan isimler", "A1",
        "Sayılabilen isimler tekil veya çoğul olabilir: a chair, two chairs. Bazı çoğullar düzensizdir: child–children, person–people. Advice, information, furniture ve homework temel anlamlarında sayılamaz; a/an veya doğrudan sayı almaz. Miktar için a piece of advice gibi birim kullanılır.",
        "Sayılabilen: one chair / three chairs | Sayılamayan: some information / some furniture | Birim: two pieces of advice",
        "Sözcüğün Türkçede sayılabilir olması İngilizcede aynı davranacağı anlamına gelmez.",
        "Informations ve an advice yerine information ve a piece of advice kullan.",
        "The [children] are playing outside. | Çocuklar dışarıda oynuyor.\nCould you give me [some advice]? | Bana biraz tavsiye verebilir misin?",
        "There are three ___ in the garden. | children | childs / childrens / child | Bahçede üç çocuk var. | Child sözcüğünün düzensiz çoğulu children'dır.\nI need some ___ about the course. | information | informations / an information / many information | Kurs hakkında biraz bilgiye ihtiyacım var. | Information sayılamayan isimdir.\nShe gave me two ___ of advice. | pieces | piece / advices / advice | Bana iki tavsiye verdi. | Sayı için pieces of advice birimi kullanılır.\nThe new furniture ___ expensive. | is | are / be / being | Yeni mobilyalar pahalı. | Furniture İngilizcede sayılamayan isimdir; tekil uyumla is alır.")
    _lesson(nn, "Some, any ve no", "A1",
        "Some genellikle olumlu cümlede, any çoğu soru ve olumsuz cümlede belirsiz miktar anlatır. Teklif ve olumlu cevap beklenen ricalarda some kullanılabilir. No + isim zaten olumsuzdur; ayrıca not eklenmez. Any olumlu cümlede 'hangisi olursa' anlamı da taşıyabilir.",
        "Olumlu: We have some rice. | Soru/olumsuz: Do you have any rice? / We don't have any rice. | Olumsuz belirleyici: We have no rice.",
        "Would you like some…? bir tekliftir; soru olduğu için otomatik any seçme.",
        "We don't have no milk yerine standart İngilizcede We don't have any milk veya We have no milk kullan.",
        "Would you like [some] soup? | Biraz çorba ister misin?\nThere aren't [any] clean plates. | Hiç temiz tabak yok.",
        "We bought ___ bread for breakfast. | some | an / many / few | Kahvaltı için biraz ekmek aldık. | Olumlu cümlede sayılamayan bread ile some kullanılabilir.\nI don't have ___ cash. | any | a / many / few | Yanımda hiç nakit yok. | Olumsuz cümlede cash ile any kullanılır.\nWould you like ___ water? | some | many / an / few | Biraz su ister misin? | Tekliflerde some doğal bir seçimdir.\nThere is ___ sugar left; the jar is completely empty. | no | a / many / few | Hiç şeker kalmadı; kavanoz tamamen boş. | No sugar zaten hiç şeker yok anlamı verir.")
    _lesson(nn, "Much, many, a lot of ve miktar soruları", "A2",
        "Many çoğul sayılabilen, much sayılamayan isimle kullanılır. A lot of her iki türle kullanılabilir ve olumlu günlük cümlelerde doğaldır. How many sayı, how much miktar veya fiyat sorar. Too many/too much gereğinden fazlayı anlatır.",
        "Sayılabilen: many books / How many books? | Sayılamayan: much time / How much time? | İkisiyle de: a lot of books / a lot of time",
        "Önce ismin sayılabilirliğini kontrol et; soru sayıya mı miktara mı odaklanıyor?",
        "Many money değil much money veya a lot of money. Much people değil many people.",
        "We haven't got [much] time. | Fazla zamanımız yok.\n[How many] suitcases are you taking? | Kaç valiz götürüyorsun?",
        "How ___ students are in your class? | many | much / little / any | Sınıfında kaç öğrenci var? | Students çoğul sayılabilir isimdir.\nWe don't have ___ money left. | much | many / a few / several | Fazla paramız kalmadı. | Money sayılamayan isimdir; much kullanılır.\nThere are too ___ cars on this road. | many | much / little / a little | Bu yolda gereğinden fazla araba var. | Cars çoğuldur; too many gerekir.\nShe drinks a lot ___ water after exercise. | of | for / to / at | Egzersizden sonra çok su içer. | A lot of bir bütün olarak kullanılır.")
    _lesson(nn, "A few/a little, few/little; each/every", "A2",
        "A few çoğul sayılabilen, a little sayılamayan isimle 'biraz' anlamı verir. A olmadan few/little çoğu kez yetersizliği vurgular: few friends, little time. Each/every ardından tekil isim ve tekil fiil gelir. Each tek tek üyeleri, every grubun tamamını düşünür.",
        "Biraz: a few friends / a little time | Yetersiz: few friends / little time | Tekil: Each student has a book. / Every room is clean.",
        "A few olumlu bir miktar, few ise çoğu bağlamda beklenenden az miktar ima eder.",
        "A little books değil a few books. Every students are değil Every student is.",
        "We have [a little] time, so let's get a coffee. | Biraz zamanımız var; kahve alalım.\n[Each] guest has a name badge. | Her konuğun bir isim kartı var.",
        "There are ___ apples left, enough for a snack. | a few | a little / much / an | Atıştırmak için yeterli birkaç elma kaldı. | Apples çoğul sayılabilir isimdir; a few kullanılır.\nAdd ___ salt to the soup. | a little | a few / many / an | Çorbaya biraz tuz ekle. | Salt sayılamayan isimdir; a little gerekir.\nEvery student ___ a locker. | has | have / are / having | Her öğrencinin bir dolabı var. | Every student tekil fiil alır.\nWe have very ___ time; we must leave now. | little | few / many / a few | Çok az zamanımız var; şimdi çıkmalıyız. | Time sayılamaz; yetersiz miktar little ile anlatılır.")

    aj = _topic("aj", "Sıfatlar, zarflar ve karşılaştırmalar", "Adjective/adverb farkı, comparative/superlative, as…as, too ve enough.", "-ER", BASIC)
    _lesson(aj, "Sıfat mı, zarf mı?", "A2",
        "Sıfat bir ismi veya be/seem gibi bağlayıcı fiillerin öznesini niteler. Zarf bir eylemin nasıl yapıldığını anlatabilir. Birçok zarf -ly alır ama fast ve hard hem sıfat hem zarftır; good sıfatının zarfı well'dir. Hardly 'neredeyse hiç' demektir ve hard ile aynı değildir.",
        "İsimle: a careful driver | Eylemle: She drives carefully. | Bağlayıcı fiille: The soup tastes good.",
        "Hangi sözcüğün nitelendiğini bul: kişi/şey mi, yaptığı eylem mi?",
        "She speaks English good değil She speaks English well. Fastly yerine fast kullan.",
        "He answered [politely]. | Kibarca cevap verdi.\nThe music sounds [beautiful]. | Müzik kulağa güzel geliyor.",
        "Please drive ___; the road is icy. | carefully | careful / care / carefulness | Lütfen dikkatli sür; yol buzlu. | Drive eylemini nitelemek için zarf carefully gerekir.\nShe is a ___ singer. | good | well / goodly / goodness | O iyi bir şarkıcıdır. | Singer ismini niteleyen sıfat good'dur.\nThis cake tastes ___. | delicious | deliciously / deliciousness / more deliciously | Bu kekin tadı lezzetli. | Taste burada bağlayıcı fiildir; sıfat delicious gelir.\nHe runs very ___. | fast | fastly / fasterly / fastness | O çok hızlı koşar. | Fast hem sıfat hem zarftır; fastly kullanılmaz.")
    _lesson(aj, "Comparative ve Superlative", "A2",
        "İki şeyi karşılaştırırken comparative (-er veya more), bir grubun en üstün üyesini belirtirken superlative (the -est veya the most) kullanılır. Good–better–best ve bad–worse–worst düzensizdir. Short sıfatlarda more taller gibi iki karşılaştırma işareti birlikte kullanılmaz.",
        "Karşılaştırma: taller than / more useful than | En üstün: the tallest / the most useful | Düzensiz: good – better – the best",
        "Than karşılaştırmayı, in/of ile belirtilen grup ise superlative bağlamını verebilir.",
        "More easier değil easier. The most cheapest değil the cheapest.",
        "This path is [safer than] the main road. | Bu patika ana yoldan daha güvenli.\nIt is [the most interesting] chapter in the book. | Kitaptaki en ilginç bölüm bu.",
        "My bag is ___ than yours. | heavier | heaviest / more heavier / heavyest | Çantam seninkinden daha ağır. | Heavy comparative biçimde heavier olur.\nThis is ___ building in the town. | the tallest | taller / most tall / the taller | Bu, kasabadaki en yüksek bina. | Grubun en üstünü için the tallest kullanılır.\nHer answer was ___ than mine. | better | best / more better / gooder | Onun cevabı benimkinden daha iyiydi. | Good sözcüğünün comparative biçimi better'dır.\nThis is the ___ expensive hotel in the area. | most | more / much / many | Bu, bölgedeki en pahalı otel. | Uzun sıfat expensive için the most kullanılır.")
    _lesson(aj, "As…as, too ve enough", "B1",
        "As + sıfat/zarf + as eşitlik; not as…as eşit olmama anlatır. Too gereğinden fazla, enough yeterli demektir. Enough sıfattan sonra ama isimden önce gelir: warm enough, enough money. Too ile very aynı değildir: too hot bir sorun doğurabilecek kadar sıcaktır.",
        "Eşitlik: as tall as | Aşırılık: too heavy to carry | Yeterlilik: light enough to carry / enough time",
        "Yalnızca dereceyi mi, bir işi engelleyen aşırılığı veya yeterliliği mi anlattığını kontrol et.",
        "Enough warm değil warm enough. Money enough yerine enough money kullan.",
        "The room isn't [big enough] for six people. | Oda altı kişi için yeterince büyük değil.\nThis tea is [too hot to drink]. | Bu çay içilemeyecek kadar sıcak.",
        "My car is as old ___ yours. | as | than / from / like to | Arabam seninki kadar eski. | Eşitlik as + sıfat + as ile kurulur.\nThe box is ___ heavy for me to lift. | too | enough / many / such | Kutu benim kaldıramayacağım kadar ağır. | İşi engelleyen aşırılık too ile anlatılır.\nHe isn't tall ___ to reach the shelf. | enough | too / very / much | Rafa yetişecek kadar uzun değil. | Enough sıfattan sonra gelir.\nWe have ___ chairs for everyone. | enough | too / much / little | Herkes için yeterli sandalyemiz var. | Enough bir isimden önce kullanılabilir.")

    pp = _topic("pp", "Edatlar ve soru yapıları", "Zaman/yer edatları, hareket, özne soruları, dolaylı sorular ve question tags.", "AT", BASIC)
    _lesson(pp, "Zaman edatları · at, on, in", "A1",
        "Saatlerde at, gün ve tarihlerde on, ay/yıl/mevsim gibi daha geniş dönemlerde in kullanılır. At night, in the morning sık kalıplardır. Last, next, this ve every ile başlayan zaman ifadelerinde çoğunlukla ayrıca at/on/in kullanılmaz: next Monday, every day.",
        "Saat: at seven | Gün/tarih: on Friday / on 5 May | Geniş dönem: in June / in 2025 / in winter",
        "At the weekend Britanya, on the weekend Amerikan İngilizcesinde yaygındır; ikisi de kendi kullanımında doğrudur.",
        "In Monday değil on Monday. On next Friday değil next Friday.",
        "The concert starts [at] half past eight. | Konser sekiz buçukta başlıyor.\nWe usually travel [in] September. | Genellikle eylülde seyahat ederiz.",
        "The lesson begins ___ nine o'clock. | at | on / in / to | Ders saat dokuzda başlıyor. | Belirli saat önünde at kullanılır.\nMy birthday is ___ Tuesday this year. | on | at / in / for | Doğum günüm bu yıl salı gününe denk geliyor. | Gün adında on gerekir.\nThey moved here ___ 2020. | in | on / at / until | 2020'de buraya taşındılar. | Yıl önünde in kullanılır.\nWe met ___ the morning. | in | on / at / to | Sabah buluştuk. | In the morning kalıbı kullanılır.")
    _lesson(pp, "Yer ve hareket edatları", "A2",
        "In kapalı alan veya bölgeyi, on yüzeyi, at ise nokta/etkinlik/konumu öne çıkarabilir. To bir hedefe hareketi, into içeri geçişi, out of dışarı çıkışı anlatır. Home ve here/there önünde hedef anlamında çoğunlukla to bulunmaz: go home. Edatlar bağlama göre değişebilir.",
        "Konum: in the room / on the table / at the door | Hareket: to school / into the room / out of the room | Kalıp: go home / arrive at a station / arrive in a city",
        "Bulunulan yerle sınırı geçerek yapılan hareketi ayır: in the room ve into the room.",
        "Go to home değil go home. Arrive to London yerine arrive in London kullan.",
        "The keys are [on] the shelf. | Anahtarlar rafın üzerinde.\nThe cat jumped [into] the box. | Kedi kutunun içine atladı.",
        "There is a picture ___ the wall. | on | into / through / out of | Duvarda bir resim var. | Yüzeye bağlı konum için on kullanılır.\nShe walked from the garden ___ the kitchen. | into | at / on / between | Bahçeden mutfağın içine yürüdü. | İçeri doğru hareket into ile anlatılır.\nWe arrived ___ Paris at noon. | in | to / at / on | Öğlen Paris'e vardık. | Şehir adlarıyla arrive in kullanılır.\nHe is ___ the bus stop, waiting for the bus. | at | into / onto / through | Otobüs durağında otobüsü bekliyor. | Bir konum noktası olarak at the bus stop kullanılır.")
    _lesson(pp, "Özne soruları, dolaylı sorular ve question tags", "B1",
        "Who broke it? gibi özneyi soran sorularda ayrıca do/does/did kullanılmaz. Nesne sorusu Who did you see? farklıdır. Dolaylı soruda iç cümle düz cümle sırasındadır: Do you know where she lives? Question tag'de yardımcı fiil ve özne zamiri ana cümleye uyar; olumlu cümle çoğunlukla olumsuz tag alır.",
        "Özne sorusu: Who called? | Dolaylı soru: Do you know where he is? | Tag: She is ready, isn't she? / They don't smoke, do they?",
        "Who fiili yapanı mı, etkilenen kişiyi mi soruyor? İç soru cümlesinde devrik sıra kullanma.",
        "Do you know where does he live değil Do you know where he lives.",
        "[Who opened] the window? | Pencereyi kim açtı?\nYou have a ticket, [don't you]? | Biletin var, değil mi?",
        "Who ___ the winning goal yesterday? | scored | did scored / scoring / score | Dün galibiyet golünü kim attı? | Who özneyi sorar; fiil doğrudan V2 olur.\nDo you know where she ___? | lives | live / is live / does lives | Onun nerede yaşadığını biliyor musun? | Dolaylı soruda özne + fiil sırası kullanılır.\nHe is your neighbour, ___? | isn't he | doesn't he / is it / isn't him | O senin komşun, değil mi? | Is ile olumlu cümle, isn't he tag'ini alır.\nThey didn't come, ___? | did they | didn't they / do them / were they | Gelmediler, değil mi? | Olumsuz did cümlesinin tag'i olumlu did they olur.")

    md = _topic("md", "Modal verbs · Yeterlilik, zorunluluk ve çıkarım", "Can/could, may/might, must/have to, should ve geçmişe yönelik modal yapıları.", "CAN", INTERMEDIATE)
    _lesson(md, "Can, could ve be able to", "A2",
        "Can şimdiki yeterlilik ve izin, could geçmişte genel yeterlilik veya kibar rica için kullanılabilir. Modal fiilden sonra to olmadan V1 gelir. Tek bir geçmiş olayda başarıyla bir işi yapmayı anlatırken olumlu cümlede was/were able to veya managed to çoğu zaman daha uygundur.",
        "Şimdi: Subject + can + V1 | Genel geçmiş: Subject + could + V1 | Gelecek yeterlilik: Subject + will be able to + V1",
        "Could geçmiş genel yeteneği anlatabilir; tek seferlik başarının bağlamını ayrıca düşün.",
        "She can to swim değil She can swim. Will can yerine will be able to kullan.",
        "My grandfather [could speak] four languages. | Dedem dört dil konuşabiliyordu.\nAfter several attempts, we [were able to unlock] the door. | Birkaç denemeden sonra kapının kilidini açmayı başardık.",
        "She can ___ very well. | swim | swims / to swim / swimming | O çok iyi yüzebilir. | Can sonrasında to almayan yalın fiil gelir.\n___ you pass me the salt, please? | Could | Able / Were / Have | Lütfen tuzu uzatabilir misin? | Could you kibar rica kurar.\nAfter the course, I'll be able ___ drive. | to | for / at / of | Kurstan sonra araba sürebileceğim. | Be able to + fiil yapısı gerekir.\nWe ___ able to fix the car yesterday after three attempts. | were | could / can / have | Dün üç denemeden sonra arabayı tamir etmeyi başardık. | We ile geçmiş yeterlilik were able to biçimindedir.")
    _lesson(md, "Must, have to ve should", "A2",
        "Must güçlü zorunluluk, have to gereklilik veya kurallardan doğan zorunluluk, should ise tavsiye anlatabilir. Must ile have to arasında kullanım örtüşür; ayrımı değişmez bir kişisel/dış kural gibi ezberleme. Geçmiş zorunluluk için had to kullanılır, musted denmez.",
        "Zorunluluk: must + V1 / have to + V1 | Geçmiş: had to + V1 | Tavsiye: should + V1",
        "Bir gerekliliği mi, yoksa daha iyi olacak davranışı mı anlattığını seç.",
        "Should to go değil should go. Geçmiş zorunluluk için musted değil had to kullan.",
        "You [should take] a break. | Mola vermelisin.\nVisitors [have to wear] a badge. | Ziyaretçiler isim kartı takmak zorunda.",
        "You should ___ more water. | drink | to drink / drinks / drinking | Daha fazla su içmelisin. | Should sonrasında yalın fiil gelir.\nYesterday I ___ to work late. | had | musted / have / must | Dün geç saate kadar çalışmak zorundaydım. | Geçmiş zorunluluk had to ile kurulur.\nShe ___ to wear a uniform at work. | has | have / must / should | İşte üniforma giymek zorunda. | She ile have to, has to olur.\nWe must ___ our passports. | bring | to bring / brings / bringing | Pasaportlarımızı getirmeliyiz. | Must sonrasında yalın fiil bring kullanılır.")
    _lesson(md, "Mustn't ve don't have to farkı", "A2",
        "Mustn't yasak veya yapılmaması gereken bir şeyi anlatır. Don't/doesn't have to ise zorunluluk bulunmadığını söyler; istersen yapılabilir. Needn't da gerek yok anlamındadır. Bu ayrım özellikle kurallar ve talimatlarda önemlidir.",
        "Yasak: You mustn't enter. | Gerek yok: You don't have to come. | Gerek yok: You needn't hurry.",
        "Yapmak yasak mı, yoksa yapmaya mecbur değil misin? Türkçe çeviride bu farkı koru.",
        "You mustn't pay 'ödemene gerek yok' demek değildir; ödeme yapmaman gerektiğini söyler.",
        "You [mustn't park] in front of this gate. | Bu kapının önüne park etmemelisin.\nWe [don't have to book] in advance. | Önceden rezervasyon yapmak zorunda değiliz.",
        "You ___ smoke here. It is strictly forbidden. | mustn't | don't have to / needn't / may | Burada sigara içmek kesinlikle yasak. | Yasak için mustn't kullanılır.\nYou ___ pay; admission is free. | don't have to | mustn't / must / have to | Ödeme yapman gerekmiyor; giriş ücretsiz. | Zorunluluk yokluğu don't have to ile anlatılır.\nShe ___ have to work tomorrow; it's her day off. | doesn't | don't / isn't / hasn't | Yarın çalışmak zorunda değil; izin günü. | She ile doesn't have to kullanılır.\nWe ___ hurry; we have plenty of time. | needn't | must / have to / need to | Acele etmemize gerek yok; bol vaktimiz var. | Needn't gerek olmadığını anlatır.")
    _lesson(md, "May/might/could ve şimdiki çıkarımlar", "B1",
        "May, might ve could bir olasılık bildirir; aralarına her durumda geçerli kesin yüzdeler koyamayız. Kanıta dayanan güçlü olumlu çıkarımda must, güçlü olumsuz çıkarımda can't kullanılır. Buradaki must zorunluluk değil, mantıksal çıkarımdır.",
        "Olasılık: may/might/could + V1 | Güçlü çıkarım: must + V1 | Olamaz: can't + V1",
        "Çıkarımın gücünü ve hangi kanıta dayandığını düşün; olabilir ile kesin olamaz farklıdır.",
        "Olumsuz çıkarım için mustn't kullanma; temel yapı can't'tir. Mustn't çoğu kez yasak demektir.",
        "The lights are off. They [might be] asleep. | Işıklar kapalı. Uyuyor olabilirler.\nYou've walked all day. You [must be] tired. | Bütün gün yürüdün. Çok yorgun olmalısın.",
        "She might ___ at the library. | be | to be / is / being | Kütüphanede olabilir. | Might sonrasında yalın be kullanılır.\nThat ___ be Sam; Sam is abroad and this is a live video from here. | can't | must / has to / should to | Bu Sam olamaz; Sam yurt dışında, bu ise buradan canlı görüntü. | Eldeki kanıt olasılığı dışlıyorsa can't kullanılır.\nYou've had nothing to eat all day. You ___ be hungry. | must | mustn't / are / have | Bütün gün bir şey yemedin. Aç olmalısın. | Burada must zorunluluk değil güçlü çıkarım anlatır.\nIt may ___ later, so take an umbrella. | rain | rains / to rain / raining | Daha sonra yağmur yağabilir; şemsiye al. | May sonrasında V1 rain gelir.")
    _lesson(md, "Modal + have + V3 · Geçmişe bakış", "B2",
        "Must have + V3 geçmiş hakkında güçlü çıkarım; might/may/could have + V3 geçmiş olasılık; can't have + V3 geçmişe dair güçlü olumsuz çıkarım anlatabilir. Should have + V3 tavsiye/pişmanlık bağlamında yapılması daha iyi olacak işi değerlendirir; başka bağlamlarda geçmişe ilişkin beklenti de bildirebilir. Shouldn't have geçmiş davranışa yönelik olumsuz değerlendirme yapabilir.",
        "Çıkarım: must/might/can't have + V3 | Geçmiş tavsiye: should have + V3 | Olumsuz değerlendirme: shouldn't have + V3",
        "Could have bazen gerçekleşmemiş fırsat veya yeterlilik de anlatır; bağlamı kontrol et.",
        "Must have went değil must have gone. Should had değil should have kullan.",
        "She [must have forgotten] the appointment. | Randevuyu unutmuş olmalı.\nI [should have saved] a copy. | Bir kopya kaydetmeliydim.",
        "You should have ___ me earlier. | told | tell / telling / tells | Bana daha önce söylemeliydin. | Should have sonrasında V3 told gerekir.\nHe must ___ missed the train. | have | has / had to / be | Treni kaçırmış olmalı. | Geçmiş çıkarım must have + V3 ile kurulur.\nThey might have ___ the wrong address. | written | wrote / write / writing | Yanlış adresi yazmış olabilirler. | Have sonrasında V3 written kullanılır.\nYou shouldn't have ___ so much money. | spent | spend / spending / spends | Bu kadar çok para harcamamalıydın. | Geçmiş davranış değerlendirmesi shouldn't have + V3 ister.")

    ps = _topic("ps", "Passive voice ve yaptırma yapıları", "Be + V3 ile edilgen cümleler; modal/perfect passive ve have/get something done.", "V3", INTERMEDIATE)
    _lesson(ps, "Passive · Odağı işi yapandan yapılan işe taşıma", "B1",
        "Passive cümlede işi yapan yerine işten etkilenen kişi/şey özne olur. Yapı be + V3'tür; zamanı be taşır. Yapanı söylemek gerekirse by kullanılır. Çoğu geçişsiz fiil doğrudan passive yapılamaz: happen ve arrive gibi fiillere bu yapıyı uygulama.",
        "Present: am/is/are + V3 | Past: was/were + V3 | Continuous: am/is/are being + V3",
        "The chef cooked dinner → Dinner was cooked by the chef. Cümlenin odağı değişir.",
        "The bridge built değil The bridge was built. It was happened yerine It happened kullan.",
        "These shirts [are made] from cotton. | Bu gömlekler pamuktan yapılır.\nThe station [was opened] in 1995. | İstasyon 1995'te açıldı.",
        "English ___ spoken in many countries. | is | are / has / does | İngilizce birçok ülkede konuşulur. | English tekil özne ve spoken V3 olduğu için is gerekir.\nThe windows were ___ yesterday. | cleaned | clean / cleaning / cleans | Pencereler dün temizlendi. | Were + V3 cleaned passive yapısını kurar.\nThe cake was made ___ my sister. | by | to / of / with | Kek kız kardeşim tarafından yapıldı. | İşi yapan kişi by ile belirtilir.\nThe road is being ___ at the moment. | repaired | repair / repairs / repairing | Yol şu anda onarılıyor. | Continuous passive is being + V3 ile kurulur.")
    _lesson(ps, "Perfect ve modal passive", "B2",
        "Perfect passive have/has/had been + V3; gelecek passive will be + V3 ile kurulur. Modal passive can/must/should gibi bir modalın ardından be + V3 alır. Aktif cümledeki zamanı ve anlamı korurken nesneyi yeni özneye taşı.",
        "Perfect: have/has/had been + V3 | Gelecek: will be + V3 | Modal: can/must/should + be + V3",
        "Has repaired aktif, has been repaired edilgendir. 'Been' eklenmesi anlamı değiştirir.",
        "It must repaired değil It must be repaired. Has been wrote değil has been written.",
        "The package [has been delivered]. | Paket teslim edildi.\nThe application [must be signed]. | Başvuru imzalanmalıdır.",
        "The letters have been ___. | sent | send / sending / sends | Mektuplar gönderildi. | Have been sonrasında V3 sent gelir.\nThis form must ___ completed in black ink. | be | been / being / is | Bu form siyah mürekkeple doldurulmalıdır. | Modal passive must be + V3 biçimindedir.\nThe results will be ___ tomorrow. | announced | announce / announcing / announces | Sonuçlar yarın açıklanacak. | Will be sonrasında V3 announced gerekir.\nThe room ___ been cleaned before we arrived. | had | was / did / is | Biz gelmeden önce oda temizlenmişti. | Geçmişten önceki passive olay had been cleaned ile anlatılır.")
    _lesson(ps, "Have/get something done · Bir işi yaptırmak", "B2",
        "Have/get + nesne + V3, bir işi başkasına yaptırmayı anlatabilir. I had my hair cut cümlesinde saçımı kendim kesmedim. Have fiili zamanı taşır. Aynı yapı istenmeyen bir deneyim için de kullanılabilir: She had her bag stolen; burada çaldırmayı istemiş olması gerekmez.",
        "Yapı: Subject + have/get + object + V3 | Geçmiş: I had my car repaired. | Plan: I'm having the windows replaced.",
        "İşi sen mi yapıyorsun, bir hizmet mi alıyorsun? Nesne ile V3 arasındaki ilişkiyi kontrol et.",
        "I cut my hair ile I had my hair cut aynı işi yapan kişiyi göstermez.",
        "We [had] the roof [repaired]. | Çatıyı tamir ettirdik.\nShe [gets] her eyes [tested] every year. | Her yıl gözlerini muayene ettirir.",
        "I had my phone ___ at the repair shop. | fixed | fix / fixing / fixes | Telefonumu tamircide tamir ettirdim. | Have + nesne + V3 kalıbı fixed gerektirir.\nShe is having her hair ___ today. | cut | cutting / cuts / to cut | Bugün saçını kestiriyor. | Cut fiilinin V3'ü de cut'tır.\nWe got the house ___ last summer. | painted | paint / painting / paints | Geçen yaz evi boyattık. | Get + nesne + V3 yapısında painted kullanılır.\nThey ___ their windows replaced yesterday. | had | have / has / having | Dün pencerelerini değiştirdiler, birine yaptırdılar. | Yesterday geçmiş zamanda have fiilini had yapar.")

    cn = _topic("cn", "Conditionals ve wish · Koşul cümleleri", "Zero, first, second, third ve mixed conditionals; gerçek, varsayımsal ve geçmişe dönük durumlar.", "IF", INTERMEDIATE)
    _lesson(cn, "Zero ve First Conditional", "A2",
        "Zero conditional genel sonuç ve düzenlilikte if + present, present yapısını kullanır. First conditional gerçekçi bir gelecek olasılığında if + present ve ana cümlede will + V1 ile kurulabilir. Ana cümlede modal veya emir de olabilir. If yan cümlesinde sıradan gelecek koşulu için genellikle will kullanılmaz.",
        "Genel kural: If + present simple, present simple | Gelecek: If + present simple, will + V1 | Emir: If you need help, call me.",
        "Her zaman olan sonuçla gelecekte mümkün bir sonucu ayır.",
        "If it will rain, we'll stay in yerine If it rains, we'll stay in kullan.",
        "If you [heat] ice, it [melts]. | Buzu ısıtırsan erir.\nIf the weather [improves], we [will eat] outside tomorrow. | Hava düzelirse yarın dışarıda yemek yiyeceğiz.",
        "If water reaches 100°C at sea level, it ___. | boils | boil / boiling / is boil | Su deniz seviyesinde 100°C'ye ulaşırsa kaynar. | Genel gerçek zero conditional ve tekil özneyle boils alır.\nIf she ___ early tomorrow, we'll have breakfast together. | arrives | will arrives / arriving / arrive | Yarın erken gelirse birlikte kahvaltı edeceğiz. | Gelecek koşul yan cümlesinde present simple kullanılır.\nIf it rains tomorrow, we will ___ at home. | stay | stayed / stays / staying | Yarın yağmur yağarsa evde kalacağız. | Will sonrasında V1 stay gelir.\nIf you need anything tonight, ___ me. | call | calls / called / calling | Bu gece bir şeye ihtiyacın olursa beni ara. | Ana cümle bir emir olabilir; yalın fiil kullanılır.")
    _lesson(cn, "Second Conditional · Şimdiki/gelecek varsayım", "B1",
        "If + past simple, would + V1 şimdiki veya gelecekteki hayali/uzak olasılıklı durumu anlatır. Past biçimi burada geçmiş zaman anlamı vermek zorunda değildir. Resmî varsayımlarda I/he/she/it ile were sık kullanılır; özellikle If I were you tavsiye kalıbıdır.",
        "Koşul: If + subject + past simple | Sonuç: Subject + would + V1 | Tavsiye: If I were you, I would ask.",
        "I don't have a car now → If I had a car, I would drive. Gerçek durumdan farklı bir varsayım kurulur.",
        "If I would have more time yerine If I had more time kullan. Would çoğunlukla sonuç kısmındadır.",
        "If I [knew] her number, I [would call] her. | Numarasını bilseydim onu arardım.\nIf I [were] you, I [would apologise]. | Senin yerinde olsam özür dilerdim.",
        "If I ___ a million euros, I would travel the world. | won | win / winning / would won | Bir milyon avro kazansaydım dünyayı gezerdim. | Şimdiki/gelecek hayali koşulda if sonrası past simple kullanılır.\nIf she had more free time, she would ___ a language. | learn | learned / learning / learns | Daha fazla boş zamanı olsa bir dil öğrenirdi. | Would sonrasında V1 learn gelir.\nIf we ___ closer, we would visit more often. | lived | live / living / would lived | Daha yakında yaşasak daha sık ziyaret ederdik. | Varsayımsal koşulda lived kullanılır.\nIf I were you, I ___ ask for help. | would | will / am / have | Senin yerinde olsam yardım isterdim. | If I were you kalıbının sonucu would + V1 ile verilebilir.")
    _lesson(cn, "Third Conditional · Geçmişte farklı olsaydı", "B2",
        "Geçmişte olmuş veya olmamış bir şeyi artık değiştiremeyeceğimiz varsayımıyla ele alır. Koşulda if + had + V3, sonuçta would have + V3 kullanılır. Could have ve might have sonucu yeterlilik veya olasılık açısından değiştirebilir.",
        "Koşul: If + subject + had + V3 | Sonuç: Subject + would have + V3 | Alternatif sonuç: could/might have + V3",
        "We missed the bus → If we had left earlier, we would have caught it. İki bölüm de geçmişe bakar.",
        "If I would have known yerine If I had known kullan. Had knew değil had known gerekir.",
        "If you [had called], I [would have helped]. | Aramış olsaydın yardım ederdim.\nWe [might have won] if we [had trained] harder. | Daha çok antrenman yapmış olsaydık kazanabilirdik.",
        "If I had ___ about the meeting, I would have come. | known | knew / know / knowing | Toplantıyı bilseydim gelirdim. | If had yapısından sonra V3 known gerekir.\nIf they had left earlier, they would have ___ the train. | caught | catch / catching / catches | Daha erken çıksalardı trene yetişirlerdi. | Would have sonrasında V3 caught gelir.\nShe ___ have passed if she had answered the last question correctly. | would | will / is / does | Son soruyu doğru cevaplasaydı geçerdi. | Geçmişte gerçek dışı sonuç would have + V3 ile anlatılır.\nIf we ___ booked ahead, we would have got seats. | had | have / were / would | Önceden rezervasyon yapsaydık yer bulurduk. | Geçmiş gerçek dışı koşul if + had + V3 ister.")
    _lesson(cn, "Mixed Conditionals ve wish/if only", "B2",
        "Mixed conditional koşul ve sonucu farklı zamanlara yerleştirir: If I had slept earlier, I wouldn't be tired now. Geçmiş davranışın şimdiki sonucu anlatılır. Wish + past şimdiki durumun farklı olmasını; wish + past perfect geçmişin farklı olmasını istemeyi anlatır. Wish + would davranış değişikliği veya rahatsızlık dile getirebilir.",
        "Geçmiş → şimdi: If + had + V3, would + V1 + now | Şimdiki dilek: I wish + past simple | Geçmiş pişmanlık: I wish + had + V3",
        "Önce her bölümün zamanını ayrı belirle: geçmişteki neden mi, şimdiki sonuç mu?",
        "I wish I knew yesterday yerine geçmiş pişmanlık için I wish I had known kullan.",
        "If I [had accepted] that job, I [would live] abroad now. | O işi kabul etmiş olsaydım şimdi yurt dışında yaşardım.\nI wish I [had saved] the file. | Keşke dosyayı kaydetmiş olsaydım.",
        "If I had gone to bed earlier, I ___ feel so tired now. | wouldn't | won't / didn't / hadn't | Daha erken yatsaydım şimdi bu kadar yorgun hissetmezdim. | Geçmiş koşulun şimdiki sonucu wouldn't + V1 ile anlatılır.\nI wish I ___ more free time now. | had | have / will have / having | Keşke şimdi daha çok boş zamanım olsa. | Şimdiki gerçek dışı dilekte past simple kullanılır.\nI wish I had ___ your advice last year. | taken | took / take / taking | Keşke geçen yıl tavsiyene uysaydım. | Geçmiş pişmanlık wish + had + V3 ile kurulur.\nIf only we ___ checked the address before leaving yesterday! | had | have / were / would | Keşke dün yola çıkmadan önce adresi kontrol etseydik! | Bitmiş geçmişe yönelik dilek had checked ister.")

    rs = _topic("rs", "Reported speech · Dolaylı anlatım", "Söyleneni aktarma, say/tell farkı, zaman/kişi değişimi, sorular ve talimatlar.", "SAID", INTERMEDIATE)
    _lesson(rs, "Statements · Say/tell ve zaman değişimi", "B1",
        "Birinin söylediğini kendi cümlemizle aktarırken kişi, yer ve zaman ifadeleri yeni bakış açısına uyarlanır. Geçmiş reporting verb ile present çoğunlukla past'a, will would'a dönüşür. Hâlâ doğru olan bilgide zaman geriye kaydırılmayabilir. Say doğrudan nesne kişi almaz; tell genellikle bir kişi nesnesi ister.",
        "Aktarım: She said (that) she was tired. | Kişi nesnesi: She told me (that) she was tired. | Sık değişim: am/is → was; will → would; have done → had done",
        "Today → that day, here → there gibi değişimler yalnızca aktarımın bağlamı gerektiriyorsa yapılır.",
        "She said me yerine She told me veya She said to me kullan. Zaman değişimini körü körüne uygulama.",
        "He said, 'I am busy.' → He said he [was] busy. | Meşgul olduğunu söyledi.\nShe told us she [would call] later. | Daha sonra arayacağını bize söyledi.",
        "She ___ me that she was ready. | told | said / spoke / talked | Hazır olduğunu bana söyledi. | Kişi nesnesi me ile told kullanılır.\nHe ___ that he had lost his ticket. | said | told / told to / said me | Biletini kaybettiğini söyledi. | Kişi nesnesi yoksa say biçimi said kullanılabilir.\n'I will help,' she said. → She said she ___ help. | would | will to / is / has | Yardım edeceğini söyledi. | Geçmiş aktarımda will çoğunlukla would olur.\n'I have finished,' he said. → He said he had ___. | finished | finish / finishing / finishes | Bitirmiş olduğunu söyledi. | Had sonrasında V3 gerekir.")
    _lesson(rs, "Reported questions · Soruları aktarmak", "B1",
        "Aktarılan soruda iç bölüm düz cümle sırasındadır; do/does/did soru yardımcısı kaldırılır ve fiil uygun zamanda çekimlenir. Yes/no soruları if veya whether ile; wh- soruları kendi soru sözcüğüyle aktarılır. Tüm cümle bir soru değilse sonuna soru işareti koymak gerekmez.",
        "Yes/no: He asked if/whether I was ready. | Wh-: She asked where I lived. | Sıra: question word + subject + verb",
        "Where do you live? → She asked where I lived. Aktarımda soru devrikliği korunmaz.",
        "She asked where did I live yerine She asked where I lived kullan.",
        "He asked [whether] I needed help. | Yardıma ihtiyacım olup olmadığını sordu.\nShe asked [what time the shop closed]. | Dükkânın saat kaçta kapandığını sordu.",
        "He asked ___ I was hungry. | whether | that / what / where | Aç olup olmadığımı sordu. | Yes/no sorusunu whether veya if aktarır.\nShe asked where I ___. | lived | did lived / live did / living | Nerede yaşadığımı sordu. | Aktarılan soruda düz cümle sırası gerekir.\nThey asked what time the film ___. | started | did started / start did / starting | Filmin saat kaçta başladığını sordular. | What time sonrasında özne + çekimli fiil gelir.\n'Are you ready?' → She asked if I ___ ready. | was | were / be / been | Hazır olup olmadığımı sordu. | Geçmiş aktarımda I ile was kullanılır.")
    _lesson(rs, "Reported commands ve requests", "B1",
        "Emir ve ricalar tell/ask + kişi + to + V1 ile aktarılabilir. Olumsuz talimat için not to kullanılır. Ask rica, tell talimat anlamını öne çıkarır. Advise/warn gibi fiiller de uygun bağlamda aynı nesne + to-infinitive düzenini alabilir.",
        "Talimat: tell + person + to + V1 | Rica: ask + person + to + V1 | Olumsuz: tell/ask + person + not to + V1",
        "'Don't wait.' → He told me not to wait. Not, to'dan önce gelir.",
        "She told to leave yerine kişi nesnesiyle She told me to leave kullan.",
        "The guide told us [to stay together]. | Rehber bir arada kalmamızı söyledi.\nI asked him [not to interrupt]. | Ondan sözümü kesmemesini rica ettim.",
        "The teacher told us ___ quietly. | to work | work / working / worked | Öğretmen sessizce çalışmamızı söyledi. | Tell + kişi + to-infinitive kullanılır.\nShe asked me ___ be late. | not to | don't / didn't / no | Geç kalmamamı rica etti. | Olumsuz aktarılan rica not to ile kurulur.\n'Please sit down.' → He asked me to ___. | sit down | sat down / sitting down / sits down | Oturmamı rica etti. | To sonrasında yalın fiil gelir.\nThe doctor advised him ___ smoking. | to stop | stop / stopped / stops | Doktor ona sigarayı bırakmasını tavsiye etti. | Advise + kişi + to + V1 yapısı kullanılır.")

    gi = _topic("gi", "Fiil kalıpları · -ing, infinitive ve used to", "Enjoy doing, decide to do; stop/remember farkları, used to ve amaç bildiren yapılar.", "TO", INTERMEDIATE)
    _lesson(gi, "Gerund ve to-infinitive", "B1",
        "Bazı fiillerden sonra -ing (enjoy, avoid, finish), bazılarından sonra to + V1 (decide, hope, plan) gelir. Bu kalıpları fiille birlikte öğrenmek gerekir. -Ing biçimi özne de olabilir: Swimming is good exercise. Bazı fiiller iki yapıyı da alabilir; anlam veya vurgu değişebilir.",
        "-Ing: enjoy/avoid/finish + V-ing | To-infinitive: decide/hope/plan + to + V1 | Özne: Reading helps me relax.",
        "Her fiili aynı kalıba sokma; fiilin kendisinden sonra hangi yapı geldiğini öğren.",
        "Enjoy to read değil enjoy reading. Decide going değil decide to go.",
        "I [enjoy cooking] for friends. | Arkadaşlarım için yemek yapmaktan hoşlanırım.\nWe [decided to leave] early. | Erken ayrılmaya karar verdik.",
        "She enjoys ___ in the sea. | swimming | to swim / swim / swims | Denizde yüzmekten hoşlanır. | Enjoy sonrasında -ing kullanılır.\nThey decided ___ a smaller flat. | to rent | renting / rent / rented | Daha küçük bir daire kiralamaya karar verdiler. | Decide sonrasında to-infinitive gelir.\nPlease avoid ___ noise. | making | to make / make / made | Lütfen gürültü yapmaktan kaçın. | Avoid sonrasında -ing gerekir.\nHe hopes ___ a pilot. | to become | becoming / become / became | Pilot olmayı umuyor. | Hope sonrasında to-infinitive kullanılır.")
    _lesson(gi, "Stop, remember ve try ile anlam farkı", "B2",
        "Stop doing yapılan işi bırakmak; stop to do başka bir işi yapmak için durmaktır. Remember doing geçmişte yaptığını hatırlamak; remember to do yapılacak işi unutmamaktır. Try doing bir yöntemi deneyip sonucuna bakmak; try to do bir işi başarmaya çalışmaktır.",
        "Stop: stop smoking / stop to buy bread | Remember: remember meeting her / remember to call | Try: try restarting / try to lift",
        "İkinci eylemin daha önce mi yapıldığını, amaç mı olduğunu veya bir deneme mi anlattığını kontrol et.",
        "Stopped smoking sigara içmeyi bıraktı; stopped to smoke sigara içmek için durdu demektir.",
        "We [stopped to take] a photo. | Fotoğraf çekmek için durduk.\nI [remember meeting] her at the conference. | Onunla konferansta tanıştığımı hatırlıyorum.",
        "He stopped ___ last year and hasn't had a cigarette since. | smoking | to smoke / smoke / smokes | Geçen yıl sigarayı bıraktı ve o zamandan beri hiç içmedi. | Yapılan işi bırakmak stop + -ing ile anlatılır.\nOn the way home, we stopped ___ some bread. | to buy | buying / buy / bought | Eve giderken ekmek almak için durduk. | Durmanın amacı stop + to-infinitive ile verilir.\nRemember ___ the door when you leave tomorrow. | to lock | locking / lock / locked | Yarın çıkarken kapıyı kilitlemeyi unutma. | Gelecekte yapılacak işi hatırlatmak remember to do ile kurulur.\nThe screen is frozen. Try ___ the computer; that may solve it. | restarting | restart / restarted / restarts | Ekran dondu. Bilgisayarı yeniden başlatmayı dene; belki çözülür. | Bir çözüm yöntemini denemek try + -ing ile anlatılır.")
    _lesson(gi, "Used to, be used to ve get used to", "B1",
        "Used to + V1 geçmişte olup şimdi sürmeyen alışkanlık veya durum anlatır. Be used to + isim/-ing alışkın olmak; get used to alışmaya başlamak/süreci anlatır. Son iki yapıdaki to bir edattır, bu nedenle ardından fiil gelirse -ing gerekir. Did ile soru/olumsuzda use to yazılır.",
        "Geçmiş alışkanlık: used to + V1 | Alışkın olmak: am/is/are used to + noun/V-ing | Alışmak: get used to + noun/V-ing",
        "I used to drive geçmiş alışkanlık; I'm used to driving alışkınlık durumudur.",
        "I'm used to drive değil I'm used to driving. Did you used to yerine Did you use to kullan.",
        "I [used to live] by the sea. | Eskiden deniz kenarında yaşardım.\nShe [is used to working] at night. | Gece çalışmaya alışkın.",
        "I used to ___ football every weekend, but I don't anymore. | play | playing / played / plays | Eskiden her hafta sonu futbol oynardım ama artık oynamıyorum. | Geçmiş alışkanlık used to + V1 ile anlatılır.\nShe is used to ___ early. | getting up | get up / got up / gets up | Erken kalkmaya alışkın. | Be used to sonrasında fiil -ing alır.\nDid you ___ to have long hair? | use | used / using / uses | Eskiden uzun saçın var mıydı? | Did sonrasında use to yazılır.\nIt took me weeks to get used to ___ on the left. | driving | drive / drove / drives | Soldan araba sürmeye alışmam haftalar aldı. | Get used to içindeki to edattır; -ing gerekir.")
    _lesson(gi, "Amaç, edat sonrası -ing ve yalın fiil", "B1",
        "Amaç bildirmek için to + V1 kullanılabilir: I went out to buy milk. Bir edattan sonra fiil geliyorsa genellikle -ing olur: interested in learning. Let/make + kişi ardından yalın fiil gelir; help sonrasında to'lu veya to'suz fiil kullanılabilir. Bu kalıplardaki to'nun görevini ayır.",
        "Amaç: to + V1 / in order to + V1 | Edattan sonra: in/at/without + V-ing | Let/make: let/make + person + V1",
        "Look forward to içindeki to bir edattır: I look forward to hearing from you.",
        "For buy yerine amaç için to buy kullan. Let me to go değil Let me go.",
        "We went to the market [to buy] fruit. | Meyve almak için pazara gittik.\nShe left [without saying] goodbye. | Hoşça kal demeden ayrıldı.",
        "I went to the shop ___ some milk. | to buy | for buying / buying / bought | Biraz süt almak için dükkâna gittim. | Amaç to + V1 ile anlatılır.\nHe's interested in ___ Japanese. | learning | learn / to learn / learned | Japonca öğrenmeye ilgi duyuyor. | In edatından sonra -ing gelir.\nPlease let me ___. | explain | to explain / explaining / explained | Lütfen açıklamama izin ver. | Let + kişi + yalın fiil kullanılır.\nWe look forward to ___ from you. | hearing | hear / heard / hears | Sizden haber almayı bekliyoruz. | Look forward to içindeki to edattır; hearing gerekir.")

    return [bs, tn, nn, aj, pp, md, ps, cn, rs, gi]
