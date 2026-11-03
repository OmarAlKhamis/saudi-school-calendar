# التقويم الدراسي السعودي · Saudi School Calendar

أضف التقويم الدراسي الرسمي لوزارة التعليم إلى تقويم Google أو Apple أو Outlook **مرة واحدة**، وتصلك تواريخ كل عام دراسي جديد تلقائيًا: بداية الدراسة، الإجازات، الإجازات المطولة، الأعياد، اليوم الوطني ويوم التأسيس.

**👈 صفحة الاشتراك: https://omaralkhamis.github.io/saudi-school-calendar**

مجاني ومفتوح المصدر، بلا إعلانات ولا تطبيق. كل تاريخ مرفق بمصدره.

## الاشتراك

| التقويم | عربي | English |
|---|---|---|
| معظم مناطق المملكة | [`main-ar.ics`](https://omaralkhamis.github.io/saudi-school-calendar/main-ar.ics) | [`main-en.ics`](https://omaralkhamis.github.io/saudi-school-calendar/main-en.ics) |
| مكة المكرمة والمدينة المنورة وجدة والطائف | [`west-ar.ics`](https://omaralkhamis.github.io/saudi-school-calendar/west-ar.ics) | [`west-en.ics`](https://omaralkhamis.github.io/saudi-school-calendar/west-en.ics) |

- **Google Calendar:** افتح صفحة الاشتراك واضغط «Google»، أو من الكمبيوتر: الإعدادات ← إضافة تقويم ← من عنوان URL، والصق الرابط.
- **iPhone / Mac:** اضغط «Apple / iPhone» في صفحة الاشتراك، أو: الإعدادات ← التقويم ← الحسابات ← إضافة حساب ← آخر ← إضافة تقويم مشترك.
- **Outlook:** اضغط «Outlook.com» أو «Microsoft 365».

إدارات التعليم في مكة المكرمة والمدينة المنورة وجدة والطائف تعتمد تقويمًا خاصًا يبدأ بعد بقية المناطق بأسبوع، ولذلك لها رابط مستقل.

## ما المغطى

| العام | معظم المناطق | المدن الأربع |
|---|---|---|
| 1447هـ (2025–2026) | كامل | — |
| 1448هـ (2026–2027) | كامل، مع الإجازات الإضافية لإدارات التعليم | كامل، مع الإجازة الإضافية |
| 1449هـ (2027–2028) | بداية العام ونهايته؛ الإجازات عند إعلانها | بداية العام |

الإجازات الإضافية تعلنها إدارات التعليم وقد تختلف بين منطقة وأخرى، والمعتمد هو إعلان إدارة تعليم منطقتك.

## المساهمة

التواريخ في مجلد [`data/`](data/)، ملف لكل عام هجري. لإضافة عام جديد أو تصحيح تاريخ: عدّل الملف وأرفق رابط المصدر الرسمي وافتح Pull Request. التفاصيل في [CONTRIBUTING.md](CONTRIBUTING.md).

يراقب المستودع أخبار وزارة التعليم ووكالة الأنباء السعودية يوميًا، ويفتح Issue تلقائيًا عند إعلان تقويم جديد.

---

## English

Subscribe once to the official Saudi Ministry of Education school calendar in Google Calendar, Apple Calendar or Outlook, and every new school year shows up on its own: term starts, breaks, long weekends, Eid holidays, National Day and Founding Day.

**Subscribe page: https://omaralkhamis.github.io/saudi-school-calendar**

There are four feeds: most of the Kingdom, and Makkah / Madinah / Jeddah / Taif (whose education departments run a calendar one week later), each in Arabic and English. Links are in the table above.

**How it works.** Dates live in [`data/`](data/) as one TOML file per Hijri year, each event with its official source. On every push, GitHub Actions validates the data, builds the `.ics` feeds and the landing page, and publishes them to GitHub Pages. Calendar apps re-fetch subscribed feeds on their own (Google every few hours), so updates reach everyone automatically. A daily workflow watches MoE and SPA news and opens an issue when a new calendar is announced.

```bash
python scripts/validate.py   # check the data
python scripts/build.py      # build site/ (feeds + index.html)
python scripts/watch_news.py --dry-run
```

Python 3.11+, standard library only.

## License

Code: [MIT](LICENSE). Calendar data in `data/`: public domain ([CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)). Dates come from the Ministry of Education's published calendar; this project is independent and not affiliated with the Ministry.
