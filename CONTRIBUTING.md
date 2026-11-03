# المساهمة · Contributing

## إضافة عام جديد أو تصحيح تاريخ

1. انسخ آخر ملف في `data/` باسم العام الجديد، مثل `data/1450.toml`.
2. أضف رابط المصدر في قسم `[sources]`، ويُفضّل إعلان وزارة التعليم أو واس أو الحساب الرسمي لإدارة التعليم.
3. أضف كل حدث كقسم `[[events]]`:

```toml
[[events]]
id = "1450-autumn"          # يبدأ برقم العام، ولا يتغير بعد النشر
type = "break"              # staff-return · first-day · semester-start · last-day · summer · break
                            # national-day · founding-day · eid · long-weekend · exams
start = 2028-11-17
end = 2028-11-25            # شامل لآخر يوم، ويُحذف لحدث يوم واحد
title_ar = "إجازة الخريف"
title_en = "Autumn break"
regions = ["main", "west"]  # main = معظم المناطق · west = مكة والمدينة وجدة والطائف
source = "moe"              # مفتاح من [sources] أو رابط مباشر
```

4. شغّل `python scripts/validate.py` ثم `python scripts/build.py`، وافتح Pull Request.

**الـ `id` لا يتغير بعد النشر.** تطبيقات التقويم تتعرف على الحدث به، فتصحيح التاريخ مع بقاء الـ `id` يحدّث الحدث عند المشتركين، وتغيير الـ `id` ينشئ حدثًا مكررًا.

اجعل `complete = true` حين يكتمل تقويم العام كما أعلنته الوزارة.

## English

Copy the latest file in `data/`, add an official source under `[sources]`, add each event as `[[events]]` (fields above), run `python scripts/validate.py` and `python scripts/build.py`, and open a pull request. Never change an event's `id` once published: calendar apps match events by it, so a fixed date with the same id updates in place for every subscriber, while a new id creates a duplicate. Every event needs an official source.
