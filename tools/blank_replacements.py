# Mapping of (original_en) -> (filled_en, filled_tr)
REPLACEMENTS = {
  "Hello _________! (Insert name of person)": (
    "Hello John!",
    "Merhaba John!"
  ),
  "Hello, I’m ___________.": (
    "Hello, I’m Alex.",
    "Merhaba, ben Alex."
  ),
  "I am ____________.": (
    "I am Sarah.",
    "Ben Sarah."
  ),
  "Hey, I’m _____": (
    "Hey, I’m David.",
    "Merhaba, ben David."
  ),
  "Hey, I’m _____.": (
    "Hey, I’m David.",
    "Merhaba, ben David."
  ),
  "This is ______. He/She is my co-worker.": (
    "This is Lisa. She is my co-worker.",
    "Bu Lisa. O benim iş arkadaşımdır."
  ),
  "This is ___________. He/She is _______________.": (
    "This is Tom. He is an engineer.",
    "Bu Tom. O bir mühendistir."
  ),
  "I’d like to introduce you to _______, the _______at ________.": (
    "I’d like to introduce you to Mark, the manager at Apple.",
    "Sizi Apple'daki yönetici Mark ile tanıştırmak istiyorum."
  ),
  "I would like you to meet ________.": (
    "I would like you to meet Emma.",
    "Emma ile tanışmanızı isterim."
  ),
  "This is ___________.": (
    "This is Michael.",
    "Bu Michael."
  ),
  "This is my friend _______.": (
    "This is my friend Jack.",
    "Bu benim arkadaşım Jack."
  ),
  "My favorite _________ is…": (
    "My favorite hobby is reading.",
    "En sevdiğim hobi kitap okumaktır."
  ),
  "My least favorite ________ is…": (
    "My least favorite chore is cleaning.",
    "En az sevdiğim ev işi temizlik yapmaktır."
  ),
  "I ____________ every day.": (
    "I exercise every day.",
    "Ben her gün egzersiz yaparım."
  ),
  "On _________ and ___________, I _____________.": (
    "On Saturdays and Sundays, I relax at home.",
    "Cumartesi ve Pazar günleri evde dinlenirim."
  ),
  "Every _________, I ___________.": (
    "Every morning, I drink a cup of coffee.",
    "Her sabah bir fincan kahve içerim."
  ),
  "I ___________ three times a week.": (
    "I go running three times a week.",
    "Haftada üç kez koşuya giderim."
  ),
  "I like ___________ in my free time.": (
    "I like playing the guitar in my free time.",
    "Boş zamanlarımda gitar çalmayı severim."
  ),
  "I ___________ every week.": (
    "I read a new book every week.",
    "Ben her hafta yeni bir kitap okurum."
  ),
  "There are ____ people in my family.": (
    "There are four people in my family.",
    "Ailemde dört kişi var."
  ),
  "I live with my ___________ and ____________.": (
    "I live with my parents and my sister.",
    "Annem, babam ve kız kardeşimle yaşıyorum."
  ),
  "I have _______ brothers and sisters.": (
    "I have two brothers and one sister.",
    "İki erkek ve bir kız kardeşim var."
  ),
  "I have ______ children.": (
    "I have two children.",
    "İki çocuğum var."
  ),
  "My favorite food is________________.": (
    "My favorite food is homemade pasta.",
    "En sevdiğim yemek ev yapımı makarnadır."
  ),
  "My least favorite food is ____________.": (
    "My least favorite food is sushi.",
    "En az sevdiğim yemek sushidir."
  ),
  "I like to eat ___________________.": (
    "I like to eat grilled salmon with salad.",
    "Salata ile ızgara somon yemeyi severim."
  ),
  "I don’t like to eat _________.": (
    "I don’t like to eat raw onions.",
    "Çiğ soğan yemeyi sevmiyorum."
  ),
  "I have never tried ______________.": (
    "I have never tried octopus.",
    "Ahtapot yemeyi hiç denemedim."
  ),
  "I like to cook _______________.": (
    "I like to cook Italian pasta.",
    "İtalyan makarnası pişirmeyi seviyorum."
  ),
  "My _______ cooks the best ______________.": (
    "My mother cooks the best apple pie.",
    "Annem en güzel elmalı turtayı pişirir."
  ),
  "I don’t know how to cook _____________.": (
    "I don’t know how to cook steak properly.",
    "Nasıl düzgün biftek pişireceğimi bilmiyorum."
  ),
  "I would like to learn to cook ________.": (
    "I would like to learn to cook traditional paella.",
    "Geleneksel paella yapmayı öğrenmek istiyorum."
  ),
  "I only know how to cook __________ and ___________.": (
    "I only know how to cook scrambled eggs and soup.",
    "Sadece çırpılmış yumurta ve çorba yapmayı biliyorum."
  ),
  "3- Do you like _______ food?": (
    "Do you like Mexican food?",
    "Meksika yemeklerini sever misiniz?"
  ),
  "6- Have you ever tried __________?": (
    "Have you ever tried authentic sushi?",
    "Hiç otantik sushi denediniz mi?"
  ),
  "I hate ____ weather. (cold, hot, rainy, etc.)": (
    "I hate cold and rainy weather.",
    "Soğuk ve yağmurlu havadan nefret ediyorum."
  ),
  "Is it going to ______? (rain, snow, be hot, be cold, storm, etc.)": (
    "Is it going to rain this afternoon?",
    "Bu öğleden sonra yağmur yağacak mı?"
  ),
  "Is it supposed to _______ tomorrow? (rain, snow, be hot, etc.)": (
    "Is it supposed to snow tomorrow?",
    "Yarın kar yağması bekleniyor mu?"
  ),
  "I take the bus to _____ every day.": (
    "I take the bus to work every day.",
    "Her gün işe gitmek için otobüse biniyorum."
  ),
  "I drive to ________ every day.": (
    "I drive to the office every day.",
    "Her gün ofise arabayla gidiyorum."
  ),
  "I rarely ________ to work. It is too far away.": (
    "I rarely walk to work. It is too far away.",
    "İşe nadiren yürüyerek giderim. Çok uzakta."
  ),
  "I don’t take the ______. It does not have a reliable schedule.": (
    "I don’t take the train. It does not have a reliable schedule.",
    "Trene binmiyorum. Güvenilir bir saat tarifesi yok."
  ),
  "Does this bus/train go to ___________?": (
    "Does this bus go to Central Station?",
    "Bu otobüs Merkez İstasyona gidiyor mu?"
  ),
  "What time does the next _____ come? (bus, train, etc.)": (
    "What time does the next bus come?",
    "Bir sonraki otobüs saat kaçta gelecek?"
  ),
  "It’s almost _____.": (
    "It’s almost six o’clock.",
    "Saat neredeyse altı."
  ),
  "I need to get to _______.": (
    "I need to get to the airport on time.",
    "Havaalanına zamanında varmam gerekiyor."
  ),
  "Where is ___________?": (
    "Where is the nearest pharmacy?",
    "En yakın eczane nerede?"
  ),
  "How do you get to _______?": (
    "How do you get to the city museum?",
    "Şehir müzesine nasıl gidilir?"
  ),
  "Where is the nearest _______?": (
    "Where is the nearest metro station?",
    "En yakın metro istasyonu nerede?"
  ),
  "Can you tell me how to get to _____?": (
    "Can you tell me how to get to the central library?",
    "Merkez kütüphaneye nasıl gideceğimi söyler misiniz?"
  ),
  "Could you tell me where the _______ is?": (
    "Could you tell me where the post office is?",
    "Postanenin nerede olduğunu söyleyebilir misiniz?"
  ),
  "Is there a ________ close by?": (
    "Is there an ATM close by?",
    "Yakınlarda bir bankamatik var mı?"
  ),
  "Today is _____.": (
    "Today is Monday.",
    "Bugün Pazartesi."
  ),
  "Yesterday was _______.": (
    "Yesterday was Sunday.",
    "Dün Pazardı."
  ),
  "Tomorrow will be ________.": (
    "Tomorrow will be Tuesday.",
    "Yarın Salı olacak."
  ),
  "What day do you ___________?": (
    "What day do you go to the gym?",
    "Hangi gün spor salonuna gidersin?"
  ),
  "How many days do you _____ a week? (work, go to school, study, etc.)": (
    "How many days do you work a week?",
    "Haftada kaç gün çalışıyorsunuz?"
  ),
  "What year did you _______? (go to Brazil, move to New York, etc.)": (
    "What year did you move to London?",
    "Hangi yıl Londra'ya taşındın?"
  ),
  "When talking about numbers or the amount of something you will say… ‘How many __________?’ For example:": (
    "When talking about numbers or the amount of something you will say… 'How many books do you have?' For example:",
    "Sayılardan veya bir şeyin miktarından bahsederken… 'Kaç tane kitabın var?' diyeceksiniz. Örneğin:"
  ),
  "I am___________.": (
    "I am Turkish.",
    "Ben Türküm."
  ),
  "I am from ___________.": (
    "I am from Istanbul.",
    "Ben İstanbulluyum."
  ),
  "I live in ___________.": (
    "I live in Ankara.",
    "Ankara'da yaşıyorum."
  ),
  "Soap Opera- fictional show that goes on for a long time and is often very dramatic I like to watch ____________shows.": (
    "Soap Opera: Fictional dramatic show. I like to watch comedy and drama shows.",
    "Pembe Dizi: Kurgusal dramatik dizi. Komedi ve drama programları izlemeyi severim."
  ),
  "My favorite TV program is _______________.": (
    "My favorite TV program is Planet Earth.",
    "En sevdiğim televizyon programı Planet Earth belgeselidir."
  ),
  "Did you see the last episode of _____________?": (
    "Did you see the last episode of Stranger Things?",
    "Stranger Things dizisinin son bölümünü izledin mi?"
  ),
  "What happened last night on ____________?": (
    "What happened last night on the evening news?",
    "Dün gece akşam haberlerinde ne oldu?"
  ),
  "I heard ______ is a good/bad movie.": (
    "I heard Inception is a fantastic movie.",
    "Inception'ın harika bir film olduğunu duydum."
  ),
  "__________ was a great movie.": (
    "Interstellar was a great movie.",
    "Interstellar muhteşem bir filmdi."
  ),
  "I really want to see ____________.": (
    "I really want to see the new sci-fi movie.",
    "Yeni bilim kurgu filmini gerçekten görmek istiyorum."
  ),
  "What time is ________ movie showing?": (
    "What time is the evening movie showing?",
    "Akşam seansı filmi saat kaçta başlıyor?"
  ),
  "How much does it cost to see ______?": (
    "How much does it cost to see the new show?",
    "Yeni gösteriyi izlemenin ücreti ne kadar?"
  ),
  "Do you want to go to _______ with me?": (
    "Do you want to go to the cinema with me?",
    "Benimle sinemaya gitmek ister misin?"
  ),
  "Did you like the ending of _____________?": (
    "Did you like the ending of that mystery movie?",
    "O gizem filminin sonunu beğendin mi?"
  ),
  "I rent ____________.": (
    "I rent a modern two-bedroom apartment.",
    "İki yatak odalı modern bir daire kiralıyorum."
  ),
  "I live in ____________ .": (
    "I live in a peaceful neighborhood.",
    "Huzurlu bir mahallede yaşıyorum."
  ),
  "I pay $______ per month for rent.": (
    "I pay $750 per month for rent.",
    "Kira için ayda 750 dolar ödüyorum."
  ),
  "I live with ________________ in a ________________.": (
    "I live with my best friend in a cozy flat.",
    "En yakın arkadaşımla sıcak bir dairede yaşıyorum."
  ),
  "Do you have ____________?": (
    "Do you have fresh organic milk?",
    "Taze organik sütünüz var mı?"
  ),
  "Where can I find ___________?": (
    "Where can I find extra virgin olive oil?",
    "Sızma zeytinyağını nerede bulabilirim?"
  ),
  "have sliced cheese and meats and salads available for purchase Out of Stock : there are no more left When will you get more ____________?": (
    "When will you get more fresh whole wheat bread?",
    "Ne zaman daha fazla taze tam buğday ekmeği gelecek?"
  ),
  "I would like a table for _____.": (
    "I would like a table for two, please.",
    "İki kişilik bir masa rica ediyorum, lütfen."
  ),
  "I have a reservation for ____________.": (
    "I have a reservation for David Miller.",
    "David Miller adına bir rezervasyonum var."
  ),
  "I would like to have _________.": (
    "I would like to have grilled chicken breast.",
    "Izgara tavuk göğsü almak istiyorum."
  ),
  "Can I get ____________?": (
    "Can I get a glass of sparkling water?",
    "Bir bardak maden suyu alabilir miyim?"
  ),
  "You forgot to add the _________.": (
    "You forgot to add the salad dressing.",
    "Salata sosunu eklemeyi unuttunuz."
  ),
  "Could you bring me more ___________?": (
    "Could you bring me some more paper napkins?",
    "Bana biraz daha kağıt peçete getirebilir misiniz?"
  ),
  "I am looking for _____________. Can you tell me where to find it?": (
    "I am looking for warm winter jackets. Can you tell me where to find them?",
    "Sıcak kışlık ceket arıyorum. Nerede bulabileceğimi söyleyebilir misiniz?"
  ),
  "Where can I find _______________?": (
    "Where can I find comfortable running shoes?",
    "Rahat koşu ayakkabılarını nerede bulabilirim?"
  ),
  "Do you have this in size ____?": (
    "Do you have this shirt in size medium?",
    "Bu gömleğin medium (M) bedeni var mı?"
  ),
  "Do you have a _____________ one? (bigger, smaller, shorter, longer, etc.)": (
    "Do you have a slightly larger size?",
    "Bunun biraz daha büyük bedeni var mı?"
  ),
  "There is a fire at __________________. (state location or address)": (
    "There is a fire at 42 Oak Avenue.",
    "Oak Avenue 42 numarada yangın var!"
  ),
  "Someone has been hurt at _____________. (state location or address)": (
    "Someone has been hurt at City Center Park.",
    "Şehir Merkezi Parkı'nda biri yaralandı!"
  ),
  "Charged with _____": (
    "Charged with armed robbery.",
    "Silahlı soygun ile suçlandı."
  ),
  "I am __________.": (
    "I am feeling very tired today.",
    "Bugün kendimi çok yorgun hissediyorum."
  ),
  "You should ____________.": (
    "You should consult a specialist doctor.",
    "Bir uzman doktora danışmalısın."
  ),
  "If I were you, I would __________.": (
    "If I were you, I would take a few days off.",
    "Senin yerinde olsaydım birkaç gün izin alırdım."
  ),
  "Maybe you should ____________.": (
    "Maybe you should talk to your manager.",
    "Belki de yöneticinle açıkça konuşmalısın."
  ),
  "Do you want to ___________?": (
    "Do you want to have a quick coffee?",
    "Hızlıca bir kahve içmek ister misin?"
  ),
  "Would you like to __________?": (
    "Would you like to join us for a weekend brunch?",
    "Hafta sonu kahvaltısında bize katılmak ister misin?"
  ),
  "Can you please ___________?": (
    "Can you please give me a hand with these boxes?",
    "Lütfen bu kutularda bana bir el atabilir misin?"
  ),
  "I’d like to but __________.": (
    "I’d like to but I have an urgent client deadline.",
    "Çok isterdim ama acil bir müşteri teslim tarihim var."
  ),
  "I can’t because ___________.": (
    "I can’t because I have an exam tomorrow morning.",
    "Gelemiyorum çünkü yarın sabah önemli bir sınavım var."
  ),
  "Sorry, that won’t work because ____________.": (
    "Sorry, that won’t work because I will be traveling abroad.",
    "Kusura bakma bu uymaz çünkü yurt dışına seyahat ediyor olacağım."
  ),
  "Would you like to ________ with me?": (
    "Would you like to go to the concert with me?",
    "Benimle konsere gitmek ister misin?"
  ),
  "Would you like to go ____________ on Saturday?": (
    "Would you like to go hiking on Saturday?",
    "Cumartesi günü doğa yürüyüşüne gitmek ister misiniz?"
  ),
  "I’m going to ________. Do you want to come with?": (
    "I’m going to the farmer's market. Do you want to come with?",
    "Semt pazarına gidiyorum. Sen de gelmek ister misin?"
  ),
  "Are you free on _______________?": (
    "Are you free on Friday evening around seven?",
    "Cuma akşamı saat yedi civarında müsait misin?"
  ),
  "I’m sorry I can’t _______________.": (
    "I’m sorry I can’t attend the meeting today.",
    "Üzgünüm, bugünkü toplantıya katılamayacağım."
  ),
  "I don’t like when you ____________.": (
    "I don’t like when you speak without listening first.",
    "Önce dinlemeden konuşmandan hoşlanmıyorum."
  ),
  "I feel ____________ when _____________.": (
    "I feel motivated when I achieve my daily study goals.",
    "Günlük çalışma hedeflerime ulaştığımda motive hissediyorum."
  ),
  "I don’t like it when it _____________. It makes me feel __________.": (
    "I don’t like it when it rains continuously. It makes me feel gloomy.",
    "Sürekli yağmur yağmasından hoşlanmıyorum. Bu beni kasvetli hissettiriyor."
  ),
  "___________ is like _________.": (
    "Learning English is like building a house brick by brick.",
    "İngilizce öğrenmek tuğla tuğla ev inşa etmek gibidir."
  ),
  "__________ is similar to ___________.": (
    "Online shopping is similar to visiting a store catalogue.",
    "İnternetten alışveriş yapmak bir mağaza kataloğunu gezmeye benzer."
  ),
  "They both ____________.": (
    "They both speak three different languages fluently.",
    "Her ikisi de üç farklı dili akıcı konuşur."
  ),
  "They don’t ____________.": (
    "They don’t eat fast food during weekdays.",
    "Hafta içi günlerinde hazır yemek (fast food) yemezler."
  ),
  "They can’t _____________.": (
    "They can’t finish all these tasks alone.",
    "Tüm bu görevleri tek başlarına bitiremezler."
  ),
  "__________ is bigger than __________.": (
    "An elephant is much bigger than a horse.",
    "Fil, attan çok daha büyüktür."
  ),
  "__________ is smaller than __________.": (
    "A laptop is much smaller than a desktop computer.",
    "Dizüstü bilgisayar masaüstü bilgisayardan çok daha küçüktür."
  ),
  "__________ is better than ___________.": (
    "Early morning study is better than late night cramming.",
    "Sabah erken çalışmak gece geç saatte sıkışarak çalışmaktan daha iyidir."
  ),
  "__________ is more expensive than ____________.": (
    "A direct flight is more expensive than a bus ride.",
    "Aktarmasız uçuş, otobüs yolculuğundan daha pahalıdır."
  ),
  "__________ is nicer than ___________.": (
    "Sunny spring weather is nicer than cold winter days.",
    "Güneşli bahar havası soğuk kış günlerinden daha hoştur."
  ),
  "__________ is more helpful than _________.": (
    "Interactive practice is more helpful than passive reading.",
    "Etkileşimli pratik yapmak pasif okumadan çok daha faydalıdır."
  ),
  "Is _____?": (
    "Is the coffee shop open on Sundays?",
    "Kafe Pazar günleri açık mı?"
  ),
  "Are_____?": (
    "Are you ready to order lunch?",
    "Öğle yemeği siparişi vermeye hazır mısınız?"
  ),
  "Do_____?": (
    "Do you speak English during the day?",
    "Gün içinde İngilizce konuşuyor musunuz?"
  ),
  "Did_____?": (
    "Did you receive my email yesterday?",
    "Dün gönderdiğim e-postayı aldınız mı?"
  )
}
