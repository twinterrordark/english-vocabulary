"""Assemble the Turkish audit report from measured results, with integrity checks."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'audits' / '2026-11-09'


def read(relative):
    return json.loads((OUT / relative).read_text(encoding='utf-8'))


def esc(value):
    return html.escape(str(value))


def table(headers, rows):
    return '<div class="table-wrap"><table><thead><tr>' + ''.join(f'<th>{esc(v)}</th>' for v in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{esc(v)}</td>' for v in row) + '</tr>' for row in rows) + '</tbody></table></div>'


before, after = read('baseline/audit.json'), read('after/audit.json')
original, current = read('baseline/inventory.json'), read('after/inventory.json')
regression = read('after/regression.json')
assert after['bytes'] == current['bytes'] == (ROOT / 'index.html').stat().st_size
assert not after['errors'] and not regression['errors']
assert not read('after/dark-accessibility.json')
integrity_keys = ['word_cards', 'word_card_markup_sha256', 'embedded_images_sha256', 'vocab-data', 'sentence-data', 'phrase-data', 'work-data', 'novel-dict', 'grammar-data']
assert all(original[k] == current[k] for k in integrity_keys), 'Learning content changed'
assert all(r['overflow'] <= 1 for r in after['routes'])
assert all(not r.get('accessibility') for r in after['routes'])
violations = [(r['route'], v['id'], v['count']) for r in before['routes'] for v in r.get('accessibility', [])]
summary = {'before_nodes': before['initial']['nodes'], 'after_nodes': after['initial']['nodes'],
           'content_unchanged': True, 'tested_route_width_combinations': len(after['routes']),
           'light_route_audits': 13, 'dark_route_audits': 13, 'automated_violations_before_light': len(violations),
           'automated_violations_after_light': 0, 'regression_checks': len(regression['results']),
           'published_when_audited': False, 'clarity_active': False}
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')

score_rows, metric_rows, links = [], [], []
for mode, label in [('mobile', 'Mobil'), ('desktop', 'Masaüstü')]:
    live = read(f'baseline/lighthouse-live-{mode}.json')
    baseline = read(f'baseline/lighthouse-{mode}.json')
    final = read(f'after/lighthouse-{mode}.json')
    for key, category in [('performance', 'Performans'), ('accessibility', 'Erişilebilirlik'), ('seo', 'SEO')]:
        score_rows.append([label, category, round(live['categories'][key]['score'] * 100), round(baseline['categories'][key]['score'] * 100), round(final['categories'][key]['score'] * 100)])
    for key, metric in [('largest-contentful-paint', 'LCP'), ('total-blocking-time', 'Toplam engelleme süresi'), ('cumulative-layout-shift', 'CLS')]:
        metric_rows.append([label, metric, baseline['audits'][key]['displayValue'], final['audits'][key]['displayValue']])
    for folder, prefix, text in [('baseline', 'lighthouse-live-', 'Canlı başlangıç'), ('baseline', 'lighthouse-', 'Yerel başlangıç'), ('after', 'lighthouse-', 'Yerel son sürüm')]:
        links.append(f'<li><a href="{folder}/{prefix}{mode}.html">{text} · {label}</a></li>')

route_names = {'home':'Ana sayfa','words':'Kelimeler','review':'Tekrar','practice':'Pratik','rankings':'Sıralama','phrases':'İfadeler','grammar':'Gramer','quiz':'Test','reading':'Okuma','novel':'Roman','speak':'Konuşma','tutor':'Hoca','settings':'Ayarlar'}
route_rows = [[route_names[r['route']], 'Geçti', 'Geçti', 'Yok'] for r in after['routes'] if r['width'] == 390]
reduction = (1 - after['initial']['nodes'] / before['initial']['nodes']) * 100

document = '''<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WordFlow · Kullanılabilirlik denetimi · 9 Kasım 2026</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f4f6fa;color:#162038;font:16px/1.65 system-ui,Segoe UI,sans-serif}main{max-width:1080px;margin:auto;padding:48px 24px 80px}h1,h2,h3{line-height:1.2}h1{font-size:clamp(2rem,5vw,3.2rem);letter-spacing:-.04em;margin:12px 0 20px}h2{margin-top:0;font-size:1.5rem}h3{font-size:1.08rem}a{color:#005a45;text-underline-offset:3px}a:focus-visible,summary:focus-visible{outline:3px solid #7136bd;outline-offset:4px}.eyebrow{color:#005a45;font-weight:800;letter-spacing:.1em;font-size:.8rem}.intro{max-width:800px;color:#44536c;font-size:1.1rem}.status{display:inline-block;background:#fff0d3;color:#694000;border-radius:99px;padding:6px 12px;font-size:.83rem;font-weight:700}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:28px 0}.card,section{background:white;border:1px solid #dde3ec;border-radius:18px;padding:24px}.card strong{display:block;font-size:2rem;color:#005a45}.card span{color:#44536c;font-size:.9rem}section{margin-top:22px}p:last-child{margin-bottom:0}.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:.9rem}th,td{padding:12px;text-align:left;border-bottom:1px solid #dde3ec}th{background:#eef3f7;color:#34435c}small,.note{color:#44536c}.note{font-size:.9rem}.callout{border-left:4px solid #ad6500;background:#fff5e4;padding:16px 20px;border-radius:6px;margin-top:18px}li{margin:8px 0}.bar{height:18px;border-radius:5px;background:#e7ebf4;margin:7px 0 20px}.bar>span{display:block;height:100%;border-radius:5px;background:#007553}.shots{display:grid;grid-template-columns:1fr 1fr;gap:20px}.shots img{display:block;max-width:100%;max-height:650px;margin:auto;border:1px solid #dce2ec;border-radius:12px}.shots figcaption{margin:10px 0;color:#44536c;font-size:.9rem}figure{margin:0}summary{cursor:pointer;min-height:44px;padding:10px 0;font-weight:700}code{font-size:.88em;overflow-wrap:anywhere}pre{padding:16px;background:#eef3f7;overflow:auto;font-size:.85rem;border-radius:8px}.pass{color:#005a45}footer{padding-top:24px;color:#44536c;font-size:.85rem}@media(max-width:650px){main{padding:28px 16px 48px}.grid{grid-template-columns:1fr}.card,section{padding:20px}.shots{grid-template-columns:1fr}th,td{padding:9px}h1{font-size:2.2rem}}@media print{body{background:white}section,.card{break-inside:avoid}.shots img{max-height:400px}main{padding:0}a{color:inherit}}
</style><main>
<div class="eyebrow">WORDFLOW / 9 KASIM 2026</div><h1>Kullanılabilirlik, tasarım<br>ve performans denetimi</h1>
<p class="intro">Canlı site ölçüldü; yerel uygulamadaki doğrulanabilir arayüz sorunları düzeltildi ve tarayıcıda tekrar test edildi. Tasarım incelemesi, otomatik tarama ve kullanıcı akışı testleri birlikte değerlendirildi.</p>
<span class="status">Denetlenen sürüm 2.7.1 · Yayın öncesi ölçümler</span>
'''
document += f'''<div class="grid"><div class="card"><strong>52 / 52</strong><span>Bölüm × ekran genişliği kontrolünde yatay taşma yok</span></div><div class="card"><strong>26 / 26</strong><span>Açık ve koyu tema bölüm taramalarında otomatik ihlal yok</span></div><div class="card"><strong>%{reduction:.1f}</strong><span>Ana sayfanın canlı DOM öğesi sayısında azalma</span></div></div>'''
document += '''<section><h2>Öncelikli sonuç</h2><p>Görsel dil ve ana öğrenme eylemi tutarlı. Mobil menünün bulunabilirliği, dar ekran taşması, küçük eylem düğmeleri, pencere odağı ve bazı renk/etiket sorunları düzeltildi. En önemli açık teknik sınır, içeriğin yaklaşık 20 MB büyüklüğünde tek HTML dosyasında taşınması.</p><div class="callout"><strong>Performans puanında artış doğrulanmadı.</strong> Canlı DOM küçüldü ve mobil ana iş parçacığı engelleme süresi azaldı; dosyanın indirilmesi hâlâ ağır. Mobildeki yaklaşık 48 saniyelik LCP, Lighthouse'un simüle yavaş ağ ölçümüdür; gerçek ziyaretçi ortalaması değildir.</div></section>'''
document += '<section><h2>Bulunan ve düzeltilen sorunlar</h2>' + table(['Bulgu', 'Düzeltme', 'Doğrulama'], [
    ['320 px ekranda 22 px yatay taşma', 'Başlıktaki öğeler dar ekrana sığdırıldı', '320, 390, 768, 1440 px; 13 bölüm'],
    ['Mobilde kelime/gramer erişimi etiketsiz profil simgesinde', 'Görünür Menü düğmesi ve açılır pencere etiketi', 'Türkçe ve İngilizce, 320 px'],
    ['Menüde kapatma düğmesi yok; Tab odağı ve kaydırma arka sayfaya geçiyor', 'Yerel modal dialog, kapatma düğmesi, odak çevrimi ve dönüşü', 'Tab, Escape, kapat ve odağın geri gelmesi'],
    ['Telaffuz penceresinin odağı arka sayfaya geçebiliyor', 'Aynı modal ve klavye davranışı', 'Gerçek uygulama modülüyle pencere yaşam döngüsü'],
    ['30–42 px ses/telaffuz eylemleri, küçük hedef seçici', 'İlgili eylemlerde en az 44 px hedef', 'Ekrandaki öğelerin ölçümü ve görsel inceleme'],
    ['Açık temada sıralama yazısı; koyu temada mor düğme ve pratik etiketi kontrastı', 'Tema renklerine uygun ön plan rengi', 'İki temada axe WCAG AA taraması'],
    ['PDF seçici etiketi üzerinde geçersiz ARIA ve klavye eksikliği', 'Anlamlı adı olan yerel düğme', 'Enter ile dosya seçici açılması'],
    ['Roman filtre başlığı h1 → h3 atlıyor; hocada h1 yok', 'Başlık hiyerarşisi düzeltildi', '13 bölümün başlık denetimi'],
    ['Ana sayfa DOM içinde 77.228 öğe taşıyor', 'Kullanılmayan özgün kartlar haritada tutuluyor, sonuç grupları bağlanıyor', '1.570 başlangıç öğesi; arama, dil, kayıt ve tekrar testleri'],
    ['Arama açıklaması meta etiketi yok', 'Siteyi anlatan description eklendi', 'Lighthouse SEO denetimi']]) + '</section>'
document += '<section><h2>Ölçülen puanlar</h2><p class="note">Canlı başlangıç GitHub Pages üzerinden; yerel önce/sonra aynı sıkıştırılmış test sunucusunda ve aynı Lighthouse ayarlarıyla ölçüldü. Farklı ortamlardaki puanlar doğrudan iyileşme kanıtı olarak kullanılmadı.</p>' + table(['Cihaz','Kategori','Canlı başlangıç','Yerel başlangıç','Yerel son sürüm'],score_rows) + table(['Cihaz','Ölçüt','Yerel başlangıç','Yerel son sürüm'],metric_rows) + '<p class="note">Lighthouse Best Practices puanı, büyük ana belgenin gövdesini okurken oluşan Chrome protokol hatası nedeniyle hesaplanamadı; puan uydurulmadı. Erişilebilirlik 100 puanı tek başına tam erişilebilirlik anlamına gelmez; bölüm taramaları ve klavye kontrolleri ayrıca uygulandı.</p></section>'
document += '<section><h2>İçerik koruması ve doğrulama</h2><p>2.199 kelime kartının özgün HTML içeriği, gömülü görseller ve tüm karşılaştırılan öğrenme veri kümeleri SHA-256 ile başlangıç sürümüyle aynı. 3.806 ek çalışma kelimesi ve 5.870 örnek cümle anahtarı korundu.</p>'
document += f'<p>Ana sayfanın canlı öğe sayısı: <strong>{before["initial"]["nodes"]:,} → {after["initial"]["nodes"]:,}</strong>. Kullanılmayan kartlar bellek içindeki haritada tutulur; bu değişiklik indirilecek dosyayı küçültmez.</p><div class="bar"><span style="width:100%"></span></div><div class="bar"><span style="width:{after["initial"]["nodes"] / before["initial"]["nodes"] * 100:.2f}%"></span></div>'
document += '<ul><li>Arama, boş sonuç, sıfırlama ve öğrenildi filtresi geçti.</li><li>Öğrenildi durumu, dil değişimi, kart görseli ve yeniden yüklemede kayıt korundu.</li><li>Depolama kullanılamadığında uygulama bellekte çalıştı.</li><li><code>file://</code> ile açılış ve arama geçti. JavaScript kapalıyken 2.199 özgün kart okunabilir kaldı.</li><li>Mevcut etkileşimli öğrenme ve roman okuyucu entegrasyon testleri geçti.</li><li>Test oturumlarında yakalanmamış JavaScript hatası gözlenmedi.</li></ul></section>'
document += '<section><h2>Bölüm kapsamı</h2>' + table(['Bölüm','Açık tema / 390 px','Koyu tema / 320 px','Dört genişlikte yatay taşma'],route_rows) + '<p class="note">Dokunma boyutu ham raporu, metin içi bağlantıları ve geniş etiketlerin içindeki 22 px checkbox/radio öğelerini de listeler. Bu kayıtların tümü ihlal değildir; ilgili eylem düğmeleri ayrıca incelendi. Gerçek telefon, iOS/Safari, gerçek ekran okuyucu, mikrofon/ses kalitesi ve canlı iki kişilik görüşme test edilmedi.</p></section>'
document += '<section><h2>Görsel karşılaştırma</h2><div class="shots"><figure><a href="baseline/home-390.png"><img src="baseline/home-390.png" alt="Düzeltme öncesi 390 piksel WordFlow ana sayfası" loading="lazy"></a><figcaption>Önce · Menünün profil simgesi arkasında kaldığı mobil başlık.</figcaption></figure><figure><a href="after/home-390.png"><img src="after/home-390.png" alt="Düzeltme sonrası Menü düğmesi görünen WordFlow ana sayfası" loading="lazy"></a><figcaption>Sonra · Görünür Menü eylemi ve büyütülen günlük hedef seçicisi.</figcaption></figure></div><p><a href="after/home-1440.png">Masaüstü görünümü</a> · <a href="after/words-dark-320.png">320 px koyu tema</a></p></section>'
document += '''<section><h2>Gerçek kullanıcı davranışı ölçümü</h2><p>Clarity kurulu değildi. Bu oturumda yetkili bir Clarity hesabı veya proje erişimi bulunmadığından gerçek ziyaretçi oturum kaydı ve ısı haritası başlatılmadı. Sahte proje kimliği veya çalışmayan bir takip kodu eklenmedi.</p><p>Bu rapor; gerçek kullanıcıların nerede vazgeçtiğini, hangi düğmeye daha çok bastığını veya dönüşüm oranını belirlemez. Bu sonuçlar ziyaretçi verisi gerektirir. Uzun ana sayfanın ve öğrenme seçeneklerinin ilk kullanım üzerindeki etkisi, gözlemle doğrulanması gereken bir tasarım hipotezidir.</p></section>
<section><h2>Açık teknik sınırlar</h2><ul><li><strong>İndirme maliyeti:</strong> özgün çevrimdışı, tek dosya şartı nedeniyle bütün görseller/veriler sayfada gömülü. Aktarım yaklaşık 9 MB sıkıştırılmış veri; küçük ağlarda temel darboğaz devam ediyor.</li><li><strong>Masaüstü görsel kayma:</strong> Lighthouse CLS yüksek; bu denetimde giderildiği doğrulanmadı.</li><li><strong>Ölçüm zamanı:</strong> bu rapor yayın öncesi doğrulamaları kaydeder. Güncel yayın sonucu <a href="https://github.com/twinterrordark/english-vocabulary/actions">GitHub Actions dağıtım geçmişinde</a> izlenebilir.</li><li><strong>Kullanıcı verisi:</strong> Clarity hesabına erişim yok; ziyaretçi ölçümü etkin değil.</li></ul></section>'''
document += '<section><h2>Kanıt dosyaları</h2><ul>' + ''.join(links) + '<li><a href="baseline/audit.json">Başlangıç bölüm denetimi</a></li><li><a href="after/audit.json">Son bölüm denetimi</a></li><li><a href="after/regression.json">Regresyon sonuçları</a></li><li><a href="after/inventory.json">İçerik envanteri</a></li><li><a href="../../index.html">Düzeltilmiş uygulama</a></li></ul><details><summary>Tekrar üretim ve yöntem ayrıntıları</summary><p>İzole Chromium profilleri kullanıldı; kullanıcının kayıtları değiştirilmedi. Bölüm/akış testlerinde dış istekler engellendi. Canlı Lighthouse ölçümünde gerçek siteye erişildi. Yerel Lighthouse sunucusu gzip kullanır ve bulunmayan yollar için 404 döner.</p><pre>npm install --prefix .audit-deps --no-package-lock --no-audit --no-fund playwright lighthouse @axe-core/playwright\nnode tools/audit_site.cjs after\nnode tools/test_usability.cjs\npython tools/audit_inventory.py after\nnode tools/audit_lighthouse.cjs after\npython tools/build_audit_report.py</pre><p class="note">Başlangıç arama ölçümündeki ilk kontrol, 150 ms arama gecikmesini beklemiyordu; bu alan başlangıç karşılaştırmasına alınmadı. Son sürümde sonuçların güncellenmesi beklenerek arama doğrulandı. Geçici denetim bağımlılıkları Git kapsamı dışında tutuldu.</p></details></section>'
document += f'<footer>Ücretsiz araçlar: Playwright, axe-core ve Lighthouse. Tarayıcı: {esc(after["browser"])}. Bu rapor {len(regression["results"])} regresyon kontrolü ve ham ölçüm dosyalarından üretildi.</footer></main></html>'
(OUT / 'report.html').write_text(document, encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False, indent=2))
print('Report:', OUT / 'report.html')
