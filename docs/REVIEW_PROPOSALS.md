# Persian Eval v1.1 — review proposals

Auto-generated from `data/review_proposals.jsonl`. Total proposals: 226. Rejected: 4. Revise: 160. Accepted: 62. Parse errors: 0.

Use this file to triage what to apply. The reviewer is claude-sonnet-4-6, which is strict about Persian phrasing and constraint solvability. Take its 'reject' calls seriously; treat 'revise' as a useful suggestion to skim, not a requirement.

## Rejected (4)

### `hard_culture` — 1 items

#### `peval-hard-culture-012`

**Prompt:** اگر کسی بگوید «سرش را زیر آب کرد»، در زبان فارسی محاوره‌ای معمولا چه برداشت می‌شود؟

  - الف) حمام کرد
  - ب) شنا یاد گرفت
  - پ) زیر باران ایستاد
  - ت) خود را پنهان کرد یا غیب شد ← labelled answer

**Rubric:** clarity=3, ambiguity=3, cultural_fit=4, leakage_risk=2, difficulty=3

**Issues:**
  - معنای اصلی اصطلاح «سر کسی را زیر آب کردن» فریب دادن یا خیانت کردن به کسی است، نه پنهان شدن
  - ضمیر «ش» در «سرش» مبهم است: می‌تواند بازتابی (سر خودش) یا متعدی (سر دیگری) باشد
  - هیچ‌کدام از گزینه‌ها معنای اصلی اصطلاح (فریب دادن/زمین زدن کسی) را منعکس نمی‌کنند
  - پاسخ برچسب‌گذاری‌شده با معنای رایج این اصطلاح در فارسی محاوره‌ای مطابقت ندارد

**Proposed changes:**
```json
{
  "rewrite_prompt": "اگر کسی بگوید «سر فلانی را زیر آب کرد»، در زبان فارسی محاوره‌ای معمولاً چه برداشت می‌شود؟ با گزینه‌های: الف) او را فریب داد یا به او خیانت کرد، ب) او را به شنا یاد داد، ج) او را تنبیه کرد، د) او را نجات داد",
  "notes": "برای اصلاح این آیتم باید ضمیر مبهم برطرف شود و گزینه‌ها بازنویسی شوند تا معنای واقعی اصطلاح (فریب دادن/خیانت کردن) در پاسخ صحیح منعکس شود. در غیر این صورت آیتم باید حذف شود."
}
```

---

### `hard_reading` — 1 items

#### `peval-hard-reading-028`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: کمیته انتخاب گفت اگر کسی هم آلمانی و هم سوئدی بداند، اولویت دارد. مهتاب فقط آلمانی می‌داند. کمیته او را پذیرفت. سوال: این تصمیم با ضابطه اعلام‌شده چه تناسبی دارد؟

**Accepted answers:** ['ناسازگار با ضابطه اعلام\u200cشده', 'خلاف ضابطه اولویت']

**Rubric:** clarity=4, ambiguity=4, cultural_fit=5, leakage_risk=1, difficulty=4

**Issues:**
  - Labeled answer is logically wrong: the rule grants priority to bilingual candidates but does not exclude monolingual ones, so accepting Mahtab does NOT violate the stated rule
  - Item conflates a sufficient condition (both languages → priority) with a necessary condition (only bilingual candidates may be accepted)
  - High ambiguity: a careful reasoner would correctly conclude the decision is compatible with the rule, opposite to the expected answer
  - Question phrasing 'چه تناسبی دارد' is open-ended and invites multiple defensible interpretations

**Proposed changes:**
```json
{
  "answer_replacement": "سازگار است؛ ضابطه فقط اولویت تعیین می‌کند نه شرط لازم برای پذیرش",
  "rewrite_prompt": "اگر سناریو باید ناسازگاری واقعی نشان دهد، ضابطه باید بازنویسی شود: مثلاً 'فقط کسانی پذیرفته می‌شوند که هم آلمانی و هم سوئدی بدانند' تا پذیرش مهتاب واقعاً خلاف ضابطه باشد.",
  "notes": "The item tests logical reasoning but the expected answer is itself logically incorrect. Either the rule must be rewritten to be a necessary condition (not just a priority), or the expected answer must be changed to reflect that the decision is actually compatible with the stated rule."
}
```

---

### `hard_reasoning` — 1 items

#### `peval-hard-reasoning-014`

**Prompt:** دو دوست به نام مینا و رضا با هم آشنا هستند. مینا می‌گوید: «من از رضا بزرگ‌ترم.» رضا می‌گوید: «من از مینا کوچک‌ترم.» اگر یکی از این دو دروغ بگوید، چه نتیجه می‌گیریم؟

  - الف) رضا از مینا بزرگ‌تر است
  - ب) هر دو هم‌سن‌اند ← labelled answer
  - پ) مینا از رضا بزرگ‌تر است
  - ت) نمی‌توان نتیجه گرفت

**Rubric:** clarity=2, ambiguity=4, cultural_fit=5, leakage_risk=2, difficulty=3

**Issues:**
  - The two statements are logically equivalent (both say 'Mina is older than Reza'), so it is impossible for exactly one of them to be lying — the premise is self-contradictory.
  - The labeled answer 'هر دو هم‌سن‌اند' is incorrect; no valid conclusion follows from an impossible premise.
  - The correct answer under standard logic would be 'نمی‌توان نتیجه گرفت' but even that is debatable since the premise is vacuously true (ex falso quodlibet).
  - The puzzle appears to intend a contradiction between the two statements, but as written they are equivalent, making the question fundamentally flawed.
  - Difficulty is overstated at 4; the real challenge is noticing the statements are equivalent, which makes the question broken rather than hard.

**Proposed changes:**
```json
{
  "rewrite_prompt": "دو دوست به نام مینا و رضا با هم آشنا هستند. مینا می‌گوید: «من از رضا بزرگ‌ترم.» رضا می‌گوید: «من از مینا بزرگ‌ترم.» اگر یکی از این دو دروغ بگوید، چه نتیجه می‌گیریم؟ (با این بازنویسی، گزاره‌ها واقعاً متناقض می‌شوند و جواب 'نمی‌توان نتیجه گرفت' یا تحلیل دقیق‌تری ممکن است)",
  "notes": "The fundamental flaw is that Mina saying 'I am older than Reza' and Reza saying 'I am younger than Mina' are identical propositions — they cannot differ in truth value. The puzzle needs to be redesigned so the two statements are genuinely in tension. Even with a rewrite, the answer index and correct answer would need to change. Rejection is recommended."
}
```

---

### `short_qa` — 1 items

#### `peval-public-shortqa-027`

**Prompt:** در صفحه‌کلید استاندارد، حرف «ش» معمولا روی کدام ردیف قرار دارد؟

**Accepted answers:** ['ردیف بالا', 'ردیف بالای حروف']

**Rubric:** clarity=4, ambiguity=2, cultural_fit=4, leakage_risk=2, difficulty=2

**Issues:**
  - فاکتوئال اشتباه: حرف «ش» در صفحه‌کلید استاندارد فارسی (ISIRI 9147) روی ردیف میانی (home row) قرار دارد، نه ردیف بالا
  - «ش» معادل کلید S در QWERTY است که در ردیف اصلی/میانی قرار دارد
  - پاسخ‌های ارائه‌شده («ردیف بالا» و «ردیف بالای حروف») هر دو نادرست هستند
  - این خطای بنیادی با ویرایش قابل اصلاح نیست مگر اینکه سوال کاملاً بازنویسی شود

**Proposed changes:**
```json
{
  "answer_replacement": "ردیف میانی",
  "rewrite_prompt": "در صفحه‌کلید استاندارد فارسی، حرف «ش» روی کدام ردیف قرار دارد؟",
  "notes": "اگر بخواهیم این آیتم را نجات دهیم، باید پاسخ به «ردیف میانی» یا «ردیف اصلی» یا «home row» تغییر کند. اما از آنجا که پاسخ فعلی کاملاً غلط است و این یک خطای فاکتوئال بنیادی است، توصیه می‌شود آیتم رد شود یا با پاسخ صحیح بازنویسی شود."
}
```

---


## Revise (160)

### `culture` — 17 items

#### `peval-public-culture-005`

**Prompt:** در فرهنگ ایرانی، سفره هفت‌سین معمولا با کدام جشن همراه است؟

  - الف) نوروز ← labelled answer
  - ب) یلدا
  - پ) مهرگان
  - ت) سده

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=4, difficulty=1

**Issues:**
  - difficulty is overrated at 3; this is trivial knowledge for any Iranian adult or child
  - leakage_risk is underrated at 1; this exact question is ubiquitous in online Persian cultural quizzes and educational materials

**Proposed changes:**
```json
{
  "notes": "The answer and distractors are all correct. Only metadata needs updating: difficulty should be 1 (trivial) and leakage_risk should be 4. Optionally, the question could be made harder by asking about a specific element of the هفت‌سین (e.g., which item symbolizes what), but as a basic cultural literacy check it is acceptable."
}
```

---

#### `peval-public-culture-006`

**Prompt:** در سفره هفت‌سین، کدام مورد یکی از هفت «س» سنتی محسوب می‌شود؟

  - الف) شیرینی
  - ب) سنجد ← labelled answer
  - پ) شمع
  - ت) نان

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=4, difficulty=2

**Issues:**
  - Three of four distractors do not start with 'س', making elimination trivial by letter recognition alone
  - Difficulty is overstated at 3; effective difficulty is closer to 1–2 given weak distractors
  - High leakage risk: Haft-Sin questions are extremely common in public Persian trivia sources
  - شمع and شیرینی start with 'ش' not 'س', so they are implausible distractors for a question explicitly about 'س' items

**Proposed changes:**
```json
{
  "notes": "Replace distractors with other 'س'-initial words that are NOT part of Haft-Sin, e.g. سیب‌زمینی، ساعت، سوپ، or سیگار. This forces genuine knowledge of the canonical seven items rather than simple letter-matching. Suggested revised choices: (A) سیب‌زمینی (B) سنجد (C) ساعت (D) سوپ."
}
```

---

#### `peval-public-culture-009`

**Prompt:** کدام یک از خوراکی‌های زیر بیشتر در سفره شب یلدا دیده می‌شود؟

  - الف) انار ← labelled answer
  - ب) آناناس
  - پ) کاهو
  - ت) موز

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Difficulty is overrated at 3; the correct answer is very well-known and the distractors (pineapple, lettuce, banana) are too obviously wrong for anyone with basic Iranian cultural knowledge.
  - Distractors could be strengthened by replacing one non-Yalda food with another traditional Yalda item (e.g., هندوانه or آجیل) to create a more discriminating question.

**Proposed changes:**
```json
{
  "notes": "Consider replacing one of the weaker distractors (e.g., کاهو or موز) with هندوانه or چای to make the item slightly more challenging while remaining culturally grounded. Also update difficulty to 2 in metadata."
}
```

---

#### `peval-public-culture-012`

**Prompt:** در فرهنگ ایرانی، «عیدی» معمولا در کدام مناسبت داده می‌شود؟

  - الف) روز معلم
  - ب) روز مادر
  - پ) شب یلدا
  - ت) نوروز ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Difficulty is overrated at 3; this is trivial knowledge for any Iranian — should be 1 or 2
  - عیدی is also associated with Eid al-Fitr in some Iranian families, though this option is absent from choices so no ambiguity in practice

**Proposed changes:**
```json
{
  "notes": "The only needed change is correcting the difficulty rating from 3 to 2 (or 1). The item itself is culturally accurate and well-formed. Optionally, adding 'عید فطر' as a distractor instead of one of the weaker ones would increase difficulty and acknowledge the secondary usage of عیدی, but this is optional."
}
```

---

#### `peval-public-culture-013`

**Prompt:** کدام نوع موسیقی ایرانی بر پایه «دستگاه» سامان یافته است؟

  - الف) موسیقی سنتی ← labelled answer
  - ب) موسیقی محلی شمالی
  - پ) موسیقی پاپ
  - ت) موسیقی راک

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=2

**Issues:**
  - Two distractors (موسیقی پاپ and موسیقی راک) are trivially eliminable, reducing effective difficulty
  - Difficulty rating of 3 is inflated; should be 2
  - Leakage risk underestimated — this is a standard encyclopedic fact about Iranian music widely available online

**Proposed changes:**
```json
{
  "notes": "Replace موسیقی پاپ and موسیقی راک with more plausible distractors such as 'موسیقی مقامی' (maqam-based music) or 'موسیقی کلاسیک غربی' to increase discriminability. Also correct difficulty to 2 in metadata."
}
```

---

#### `peval-public-culture-015`

**Prompt:** در آشپزی سنتی ایرانی، کدام غذا با برنج و گوشت و سبزی پخته می‌شود؟

  - الف) پیتزا
  - ب) ماکارونی
  - پ) قورمه‌سبزی ← labelled answer
  - ت) سوشی

**Rubric:** clarity=3, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=1

**Issues:**
  - قورمه‌سبزی با برنج پخته نمی‌شود؛ برنج در کنار آن سرو می‌شود نه داخل آن — توصیف 'با برنج و گوشت و سبزی پخته می‌شود' از نظر آشپزی نادرست است
  - سه گزینه غلط (پیتزا، ماکارونی، سوشی) همگی غذاهای خارجی و کاملاً بدیهی هستند و سطح سختی را به حداقل می‌رسانند
  - سطح دشواری ۳ برای این سؤال با این گزینه‌ها بسیار بالاست؛ واقعاً سطح ۱ است
  - اگر هدف پرسش درباره قورمه‌سبزی است، توصیف باید اصلاح شود: 'کدام خورش ایرانی با گوشت، سبزی و لوبیا قرمز تهیه می‌شود و معمولاً با برنج سرو می‌شود؟'

**Proposed changes:**
```json
{
  "rewrite_prompt": "در آشپزی سنتی ایرانی، کدام خورش با گوشت، سبزی معطر و لوبیا قرمز تهیه می‌شود و معمولاً با برنج سرو می‌شود؟",
  "notes": "گزینه‌های غلط باید با غذاهای ایرانی واقعی جایگزین شوند تا سطح دشواری افزایش یابد؛ مثلاً: فسنجان، آبگوشت، کوکو سبزی. همچنین توصیف اصلی از نظر فنی نادرست بود چون قورمه‌سبزی برنج را در خود ندارد."
}
```

---

#### `peval-public-culture-017`

**Prompt:** در ادب فارسی، «دیوان» معمولا به چه چیز اشاره دارد؟

  - الف) مجموعه شعرهای یک شاعر ← labelled answer
  - ب) فقط مجموعه نامه‌های یک پادشاه
  - پ) کتاب آشپزی
  - ت) کتاب مرجع تاریخی

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=1

**Issues:**
  - Distractor 'کتاب آشپزی ' is laughably implausible and reduces item quality
  - Difficulty is overestimated at 3; this is trivial (difficulty 1) for any Persian speaker familiar with دیوان حافظ or دیوان سعدی
  - Distractor 'کتاب مرجع تاریخی' is also weak; a better distractor could exploit the administrative meaning of دیوان
  - Leakage risk slightly elevated as this is a very standard definitional question likely appearing in many educational materials

**Proposed changes:**
```json
{
  "notes": "Replace 'کتاب آشپزی' with a more plausible distractor exploiting the administrative/governmental meaning of دیوان, e.g. 'مجموعه احکام و فرامین دیوانی یک پادشاه'. Replace 'کتاب مرجع تاریخی' with something like 'مجموعه نثر ادبی یک نویسنده' to increase discriminative power. Also update difficulty to 1 or 2."
}
```

---

#### `peval-public-culture-018`

**Prompt:** در سفره ایرانی، نان «بربری» معمولا چه شکلی دارد؟

  - الف) گرد و کوچک
  - ب) بیضی و کشیده ← labelled answer
  - پ) مکعب
  - ت) مثلث

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Two distractors ('مکعب' and 'مثلث') are laughably implausible for any type of bread, making the item too easy to eliminate by process of elimination
  - Difficulty is overrated at 3; barbari is one of the most common Iranian breads and its shape is widely known
  - Replacing weak distractors with more plausible bread shapes would improve item quality

**Proposed changes:**
```json
{
  "notes": "Replace 'مکعب' and 'مثلث' with more plausible distractors such as 'دایره‌ای و پهن' (like taftoon) and 'مستطیل کوتاه و ضخیم' to make the item more discriminating. Suggested revised choices: (0) گرد و پهن, (1) بیضی و کشیده [correct], (2) دایره‌ای و کوچک, (3) مستطیل کوتاه و ضخیم. Also lower difficulty to 2."
}
```

---

#### `peval-public-culture-019`

**Prompt:** در فرهنگ گفتاری فارسی، عبارت «سلامتی شما» معمولا کجا گفته می‌شود؟

  - الف) هنگام شروع جلسه رسمی
  - ب) هنگام خداحافظی از تلفن کار
  - پ) هنگام نوشیدن چای یا نوشیدنی در جمع ← labelled answer
  - ت) هنگام شروع خواندن نماز

**Rubric:** clarity=4, ambiguity=2, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Distractor D (هنگام شروع خواندن نماز) is laughably implausible, weakening the item's discriminative power
  - «سلامتی شما» is also used in non-drinking contexts (e.g., as a general well-wish), creating mild ambiguity not addressed by the question
  - Difficulty is overrated at 3; this is straightforward for any native Iranian Persian speaker
  - Question could be sharpened by adding «به‌عنوان نوعی تست» or specifying 'most typical' to reduce ambiguity

**Proposed changes:**
```json
{
  "rewrite_prompt": "در فرهنگ گفتاری فارسی، عبارت «سلامتی» یا «سلامتی شما» بیشتر در کدام موقعیت به‌کار می‌رود؟",
  "notes": "Replace distractor D with something more plausible, e.g. «هنگام تبریک گفتن تولد» to improve discriminative power. Also consider replacing D with «هنگام دست دادن با بزرگ‌ترها» for a more realistic foil. Adjusting difficulty to 2 is recommended."
}
```

---

#### `peval-public-culture-020`

**Prompt:** در فرهنگ ایرانی، «سیزده‌بدر» معمولا به چه شکلی برگزار می‌شود؟

  - الف) ماندن در خانه و خواندن قرآن
  - ب) خرید لباس عید
  - پ) روزه گرفتن از صبح تا شب
  - ت) رفتن به طبیعت و گذراندن روز در فضای باز ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Difficulty is overrated at 3; Sizdah Bedar's outdoor tradition is universally known among Iranians, making this trivial-to-easy (difficulty 2 is more appropriate)
  - Leakage risk is slightly higher than 1 since Sizdah Bedar is a very commonly described cultural event online, though the exact phrasing appears original

**Proposed changes:**
```json
{
  "notes": "The item is fundamentally sound and the correct answer is unambiguous. Only the difficulty metadata needs adjustment from 3 to 2. The item can be accepted with this minor metadata fix."
}
```

---

#### `peval-public-culture-021`

**Prompt:** کدام یک از موارد زیر یکی از «هنرهای دستی» سنتی ایران به شمار می‌آید؟

  - الف) قالی‌بافی ← labelled answer
  - ب) برنامه‌نویسی
  - پ) دوبله فیلم
  - ت) جرنالیسم

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=1

**Issues:**
  - All three distractors are laughably wrong (modern professions/technologies), making the item trivially easy by elimination
  - Difficulty is mislabeled as 3; actual difficulty is 1
  - Distractors do not test knowledge of Iranian handicrafts specifically — any test-taker can answer without cultural knowledge

**Proposed changes:**
```json
{
  "rewrite_prompt": "کدام یک از موارد زیر یکی از «هنرهای دستی» سنتی ایران به شمار می‌آید؟",
  "notes": "Replace distractors with plausible traditional arts that are NOT handicrafts, e.g.: موسیقی کلاسیک ایرانی (traditional music, not a handicraft), خوشنویسی (calligraphy — borderline, could be argued either way), نقاشی دیواری (mural painting). Better yet, keep all options as traditional arts and crafts but only one qualifies as 'هنر دستی' per UNESCO/Iranian classification, e.g.: choices = [قالی‌بافی، موسیقی دستگاهی، شعر کلاسیک، تعزیه]. This forces genuine knowledge. Also update difficulty to 2–3 after revision."
}
```

---

#### `peval-public-culture-022`

**Prompt:** در ادب فارسی، عبارت «ای دل غافل» معمولا چه حسی را منتقل می‌کند؟

  - الف) شادی شدید
  - ب) افسوس و هشدار ← labelled answer
  - پ) خشم
  - ت) تعجب علمی

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=1, difficulty=2

**Issues:**
  - «تعجب علمی» به عنوان گزینه چهارم بسیار مصنوعی و نامتناسب با فضای ادبی سؤال است و سؤال را بیش از حد آسان می‌کند
  - با وجود گزینه‌ای مانند «تعجب علمی»، حذف گزینه‌های نادرست آسان‌تر می‌شود و سطح دشواری واقعی پایین‌تر از ۳ است

**Proposed changes:**
```json
{
  "notes": "گزینه چهارم «تعجب علمی» باید با گزینه‌ای طبیعی‌تر و ادبی‌تر جایگزین شود، مثلاً «حسرت عاشقانه» یا «شگفتی عارفانه» تا سؤال چالش‌برانگیزتر و متناسب‌تر با فضای ادب فارسی باشد."
}
```

---

#### `peval-public-culture-023`

**Prompt:** در ضرب‌المثل فارسی «از این ستون به آن ستون فرج است» منظور چیست؟

  - الف) ستون‌های بنا را باید کم کرد
  - ب) باید همیشه سرجای خود ایستاد
  - پ) گذر زمان ممکن است گشایش بیاورد ← labelled answer
  - ت) دو ستون بهتر از یکی است

**Rubric:** clarity=5, ambiguity=2, cultural_fit=5, leakage_risk=3, difficulty=2

**Issues:**
  - The labeled answer emphasizes 'passage of time' but the proverb is more precisely about changing one's situation/position bringing relief, not time per se
  - No other distractor is defensibly correct, so the item still functions, but the answer phrasing is imprecise
  - Leakage risk is moderate — this proverb and its standard interpretation appear widely in Persian educational/cultural websites
  - Difficulty is closer to 2 than 3 for native Persian speakers familiar with common proverbs

**Proposed changes:**
```json
{
  "answer_replacement": "تغییر وضعیت یا شرایط ممکن است گشایش بیاورد",
  "notes": "The answer at index 2 should be revised to better reflect the proverb's actual meaning: relief comes from a change in situation/position, not specifically from the passage of time. The answer_index remains 2. Suggested replacement: 'تغییر وضعیت یا شرایط ممکن است گشایش بیاورد'. Difficulty should be downgraded to 2."
}
```

---

#### `peval-public-culture-024`

**Prompt:** در آداب میهمانی ایرانی، رسم «تعارف» معمولا به چه معناست؟

  - الف) نوعی رقص جمعی
  - ب) نوعی موسیقی محلی
  - پ) نوعی غذای محلی
  - ت) اصرار مودبانه در پذیرایی یا گرفتن چیزی ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Answer description captures only the 'insistence' side of ta'arof, missing the full bidirectional ritual (offer + expected refusal + re-offer)
  - Difficulty rated 3 but topic is well-known; 2 is more appropriate
  - Leakage risk slightly elevated — ta'arof is a very commonly discussed topic online

**Proposed changes:**
```json
{
  "answer_replacement": "رفتار مودبانه‌ای شامل اصرار در پذیرایی یا تعارف کردن چیزی و انتظار رد کردن آن از سوی طرف مقابل",
  "rewrite_prompt": "در فرهنگ ایرانی، «تعارف» به چه نوع رفتار اجتماعی‌ای گفته می‌شود؟",
  "notes": "The answer replacement better captures the bidirectional nature of ta'arof. The prompt rewrite is slightly more precise. If the answer text is changed, the choices list must be updated accordingly. Alternatively, keep the current answer as-is since it is still the only defensible choice among the four options — in that case, status can be 'accepted'."
}
```

---

#### `peval-public-culture-028`

**Prompt:** کدام شاعر بیشتر با رباعیات خود در جهان شناخته می‌شود؟

  - الف) اوحدی
  - ب) سنایی
  - پ) هاتف
  - ت) خیام ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - هاتف به رباعیات شناخته نمی‌شود و یک گزینه گمراه‌کننده ضعیف است که حذف آن را آسان می‌کند
  - سطح دشواری ۳ اغراق‌آمیز است؛ این سؤال برای اکثر فارسی‌زبانان بسیار آسان است (سطح ۲ مناسب‌تر است)
  - جایگزینی هاتف با شاعری که به رباعیات شناخته می‌شود (مثلاً ابوسعید ابوالخیر) کیفیت گزینه‌های گمراه‌کننده را بهبود می‌بخشد

**Proposed changes:**
```json
{
  "notes": "Replace 'هاتف' with 'ابوسعید ابوالخیر' as a distractor, since ابوسعید is also associated with رباعیات and makes for a more challenging and fair distractor. Update difficulty metadata from 3 to 2."
}
```

---

#### `peval-public-culture-029`

**Prompt:** کدام بنای تاریخی در شیراز قرار دارد و آرامگاه یک شاعر بزرگ فارسی است؟

  - الف) حافظیه ← labelled answer
  - ب) تخت جمشید
  - پ) ارگ بم
  - ت) میدان نقش جهان

**Rubric:** clarity=5, ambiguity=2, cultural_fit=5, leakage_risk=3, difficulty=2

**Issues:**
  - Difficulty overrated at 3; this is trivial knowledge for any Persian speaker, closer to 1-2
  - Leakage risk underrated at 1; this is a very common Iranian quiz/educational question
  - Mild ambiguity: Shiraz also contains سعدیه (tomb of Sa'di), another great Persian poet — the question could have two correct answers if choices were different, though current MCQ is unambiguous
  - Distractor quality uneven: ارگ بم and میدان نقش جهان are from completely different cities and easily eliminated

**Proposed changes:**
```json
{
  "rewrite_prompt": "کدام بنا در شیراز قرار دارد و آرامگاه حافظ شیرازی، شاعر بزرگ ایرانی، است؟",
  "notes": "Specifying Hafez by name removes the ambiguity with سعدیه and makes the question more precise. Alternatively, keep the current phrasing but replace one of the easy distractors (e.g., ارگ بم) with سعدیه to increase difficulty and test whether test-takers know which Shirazi poet's tomb is called حافظیه vs سعدیه."
}
```

---

#### `peval-public-culture-030`

**Prompt:** در زبان فارسی، «خط نستعلیق» بیشتر برای چه کاری استفاده می‌شود؟

  - الف) نوشتن متون کامپیوتری
  - ب) خوش‌نویسی شعر و ادبیات ← labelled answer
  - پ) نقشه‌برداری مهندسی
  - ت) نوشتن فرمول ریاضی

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - distractor 'نقشه‌برداری مهندسی' is too absurd and makes correct answer easier to identify by elimination
  - difficulty overrated at 3; should be 2 for general Persian cultural knowledge
  - leakage risk slightly underrated; this is a commonly known fact that may appear in educational sources

**Proposed changes:**
```json
{
  "notes": "Replace the laughably wrong distractor 'نقشه‌برداری مهندسی' with 'نوشتن اسناد رسمی و اداری' to make the MCQ more challenging and all distractors plausible. Adjust difficulty to 2."
}
```

---

### `hard_culture` — 13 items

#### `peval-hard-culture-005`

**Prompt:** وقتی کسی در فارسی می‌گوید «دلش با ما نیست»، نزدیک‌ترین معنی محاوره‌ای کدام است؟

  - الف) از نظر فکری در جای دیگری است یا تمایلی ندارد ← labelled answer
  - ب) خانه‌اش از ما دور است
  - پ) بیمار است
  - ت) دل‌درد دارد

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - The answer phrase 'از نظر فکری' (intellectually) underweights the emotional/affective dimension of the idiom, which is equally or more central to its meaning
  - Difficulty is closer to 2 than 3 for native Persian speakers — this is a very common everyday expression

**Proposed changes:**
```json
{
  "answer_replacement": "از نظر ذهنی یا احساسی در جای دیگری است یا تمایلی ندارد",
  "notes": "The labeled answer index (0) remains correct — it is clearly the best choice. Only the wording of choice 0 needs minor refinement to include the emotional dimension alongside the cognitive one. Difficulty should be downgraded to 2 as this idiom is widely known among Persian speakers."
}
```

---

#### `peval-hard-culture-009`

**Prompt:** در زبان عامیانه فارسی، عبارت «سرت به کار خودت باشد» معمولا چه پیامی دارد؟

  - الف) خواست محترمانه برای دخالت نکردن ← labelled answer
  - ب) تشویق به یادگیری
  - پ) احوال‌پرسی
  - ت) پیشنهاد همکاری

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=1, difficulty=2

**Issues:**
  - The word 'محترمانه' (polite/respectful) in the answer mischaracterizes the register of the expression; 'سرت به کار خودت باشد' is typically blunt or even rude, not polite
  - Difficulty is overrated at 3; this is a very common colloquial phrase known to all native speakers

**Proposed changes:**
```json
{
  "answer_replacement": "خواست مستقیم (و اغلب تند) برای دخالت نکردن",
  "notes": "The core meaning of the answer is correct (mind your own business / don't interfere), but labeling it 'محترمانه' is inaccurate. The phrase is colloquially used as a blunt or dismissive rebuke. The answer text in choice 0 should drop 'محترمانه' or replace it with 'مستقیم' or 'صریح'. Difficulty should be lowered to 2."
}
```

---

#### `peval-hard-culture-010`

**Prompt:** اگر در فارسی کسی به دیگری بگوید «روی حرفش نمی‌ایستد»، نزدیک‌ترین مفهوم چیست؟

  - الف) بسیار رسمی صحبت می‌کند
  - ب) به وعده و گفته خودش پایبند نیست ← labelled answer
  - پ) پشت میز ایستاده صحبت می‌کند
  - ت) صدایش بالا نمی‌رود

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Choice C ('پشت میز ایستاده صحبت می‌کند') is too obviously absurd as a literal reading and is a weak distractor
  - Difficulty is closer to 2 than 3 — this is a fairly common and well-known idiom among Persian speakers
  - Having one laughably literal distractor reduces the discriminative power of the item

**Proposed changes:**
```json
{
  "notes": "Replace choice C with a more plausible wrong answer, e.g., 'خیلی آرام و با احتیاط صحبت می‌کند' or 'نظرش را به راحتی تغییر می‌دهد' (the latter is close but subtly different — changing opinion vs. not keeping a promise). This would make the item more discriminating. Also lower difficulty to 2."
}
```

---

#### `peval-hard-culture-013`

**Prompt:** وقتی در پیامی رسمی فارسی نوشته می‌شود «در صورت صلاحدید»، نزدیک‌ترین معنی آن چیست؟

  - الف) اگر مفید بدانید ← labelled answer
  - ب) حتما این کار را بکنید
  - پ) ما نمی‌دانیم چه کار کنیم
  - ت) اگر بودجه کافی داشته باشید

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - «اگر مفید بدانید» captures 'if you find it useful' but «صلاحدید» more precisely means 'at your discretion' or 'if you see fit' — a better phrasing would be «اگر صلاح بدانید» or «اگر مناسب بدانید»
  - Difficulty rated 4 but this is a moderately common formal phrase; 3 is more appropriate

**Proposed changes:**
```json
{
  "answer_replacement": "اگر صلاح بدانید",
  "notes": "Replace choice A and the answer with «اگر صلاح بدانید» to more accurately reflect the meaning of «صلاحدید» (discretion/appropriateness rather than utility). Update answer_index to 0 accordingly. Lower difficulty to 3."
}
```

---

#### `peval-hard-culture-015`

**Prompt:** در رسم تعارف ایرانی، اگر مهمان به اصرار میزبان برای پذیرایی بیشتر بگوید «سیر سیرم، واقعا»، مفهوم رایج اجتماعی این پاسخ چیست؟

  - الف) میزبان باید حتما تعارف را تمام کند
  - ب) مهمان عصبانی شده است
  - پ) میزبان معمولا یک یا دو بار دیگر تعارف می‌کند ← labelled answer
  - ت) مهمان درخواست غذا دارد

**Rubric:** clarity=4, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - Answer describes host's reaction rather than the social meaning of the guest's statement, creating a slight framing mismatch
  - Choice 1 ('مهمان عصبانی شده است') is laughably implausible, weakening the distractor set
  - Difficulty rating of 4 seems high; most Iranian adults know this taarof script well

**Proposed changes:**
```json
{
  "rewrite_prompt": "در رسم تعارف ایرانی، اگر مهمان به اصرار میزبان برای پذیرایی بیشتر بگوید «سیر سیرم، واقعا»، میزبان معمولاً چه واکنشی نشان می‌دهد؟",
  "notes": "Reframing the question to ask about the host's typical reaction (rather than the 'social meaning' of the guest's words) aligns better with the correct answer. Also recommend replacing choice 1 with a more plausible distractor such as 'میزبان می‌پذیرد که مهمان واقعاً سیر است و تعارف را متوقف می‌کند' to create a more meaningful contrast with the correct answer."
}
```

---

#### `peval-hard-culture-016`

**Prompt:** ضرب‌المثل «کوزه‌گر از کوزه شکسته آب می‌خورد» معمولا برای چه موقعیتی به کار می‌رود؟

  - الف) هنر کوزه‌گری در حال نابودی است
  - ب) کوزه‌ها همیشه می‌شکنند
  - پ) آب گرم بهتر از سرد است
  - ت) کسی که برای دیگران کاری می‌کند ولی خودش از آن بی‌بهره است ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=2

**Issues:**
  - Distractors are too obviously wrong (literal/irrelevant readings), making elimination trivial without cultural knowledge
  - Difficulty rating of 4 is inflated; effective difficulty is closer to 2 given weak distractors
  - Leakage risk underestimated — this proverb and its standard meaning are widely documented online
  - Item is placed in 'hard' split but distractors do not support that classification

**Proposed changes:**
```json
{
  "notes": "Replace weak distractors with more plausible alternatives, e.g.: (0) 'کسی که کار زیاد می‌کند ولی نتیجه‌اش ضعیف است', (1) 'صنعتگر باید از محصول خودش استفاده کند نه دیگران', (2) 'کسی که تجربه زیاد دارد اشتباه نمی‌کند'. These would make the item genuinely harder and appropriate for the hard split. Also consider lowering difficulty metadata to 3 even after revision."
}
```

---

#### `peval-hard-culture-017`

**Prompt:** وقتی فردی در فارسی می‌گوید «گرد و خاک کردن»، در گفت‌وگوی روزمره معمولا چه برداشت می‌شود؟

  - الف) ایجاد سر و صدا یا غوغا ← labelled answer
  - ب) نظافت اتاق
  - پ) گذاشتن گل و گلدان
  - ت) رفت و آمد دوستانه

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=3

**Issues:**
  - distractor 'گذاشتن گل و گلدان' is laughably wrong and has no plausible connection to the idiom, weakening the item
  - the idiom also carries a 'showing off / making a big splash' nuance that the answer phrase does not fully capture, though it remains the best option

**Proposed changes:**
```json
{
  "notes": "Replace 'گذاشتن گل و گلدان' with a more plausible distractor, e.g. 'تمیز کردن و گردگیری کردن' (dusting/cleaning) to exploit the literal meaning more effectively, or 'ایجاد ترافیک و شلوغی' to stay in the commotion domain but be distinguishable. Optionally expand the correct answer to 'ایجاد سر و صدا، غوغا یا جلب توجه' to capture the showing-off nuance."
}
```

---

#### `peval-hard-culture-019`

**Prompt:** در یک ایمیل کاری رسمی فارسی، کدام بسته شدن مودب‌تر تلقی می‌شود؟

  - الف) خداحافظ
  - ب) بای
  - پ) با احترام ← labelled answer
  - ت) تا بعد

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Item is placed in 'hard' split but difficulty is clearly 2/5 — mismatch between split and difficulty
  - Difficulty rating of 2 is inconsistent with 'hard_culture' track expectations

**Proposed changes:**
```json
{
  "notes": "The answer and distractors are well-constructed and culturally accurate. The only issue is the split/track mismatch: this item belongs in an easier track. Either move it to a standard difficulty split, or replace it with a harder formal-register question (e.g., distinguishing between 'با احترام', 'با تقدیم احترامات', and 'با سپاس فراوان' in different formal contexts)."
}
```

---

#### `peval-hard-culture-021`

**Prompt:** اگر یک سرپرست در محیط کار رسمی به کارمند بگوید «اگر زحمتی نیست، گزارش را تا فردا ببینم»، نزدیک‌ترین خوانش این جمله کدام است؟

  - الف) درخواست انجام تا فردا با لحن مودبانه ← labelled answer
  - ب) اعلام تعطیلی فردا
  - پ) اعلام عدم نیاز به گزارش
  - ت) تشکر از گزارش قبلی

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Distractors 1, 2, and 3 are laughably wrong — no native speaker would hesitate between them and the correct answer
  - Difficulty is overstated at 3; with these distractors it is closer to 2 or even 1
  - Missing a plausible foil: a distractor suggesting the request is genuinely optional would test the core pragmatic point more rigorously

**Proposed changes:**
```json
{
  "notes": "Replace at least two distractors with more plausible alternatives. Suggested replacements: (a) «درخواست اختیاری که کارمند می‌تواند رد کند» — tests whether learner knows the politeness formula is not genuinely optional; (b) «بیان نگرانی سرپرست از حجم کار کارمند» — tests whether learner misreads تعارف as genuine concern. This would raise difficulty to 3–4 and make the item genuinely discriminating."
}
```

---

#### `peval-hard-culture-024`

**Prompt:** اگر یک کارمند به مدیر بگوید «در خدمت شما هستم»، در یک گفت‌وگوی کاری معمول چه می‌رساند؟

  - الف) انکار مسئولیت
  - ب) اعلام تعلیق از کار
  - پ) اعلام مرخصی
  - ت) بیان احترام و آمادگی برای انجام کار ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty is overestimated: «در خدمت شما هستم» is one of the most common Persian politeness formulas; any native speaker would answer instantly — difficulty is closer to 1–2, not 3
  - Item is placed in 'hard' split and 'hard_culture' track, which is inconsistent with its trivial difficulty
  - Distractors are weak: none of the wrong choices are even remotely plausible for this phrase, making it too easy to eliminate by process of elimination

**Proposed changes:**
```json
{
  "notes": "Either move this item to an 'easy' or 'medium' split, or replace the phrase with a more ambiguous or context-dependent politeness expression (e.g., «قابلی ندارد» or «چشم» in a nuanced workplace context) and craft more plausible distractors to justify placement in the hard track. The answer itself is correct."
}
```

---

#### `peval-hard-culture-026`

**Prompt:** در گفت‌وگوی روزمره ایرانی، عبارت «خسته نباشید» معمولا کجا گفته می‌شود؟

  - الف) هنگام شروع روز اداری
  - ب) هنگام دیدن کسی که در حال کار است ← labelled answer
  - پ) هنگام تشویق در یک مسابقه
  - ت) هنگام آغاز سفر

**Rubric:** clarity=4, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - 'کجا' implies physical location but choices describe situations/timing; 'در چه موقعیتی' would be more precise
  - The phrase is also used when someone finishes work or is leaving, not only while actively working — the answer description is slightly narrow
  - Item is in 'hard' split but difficulty is low (2/5)

**Proposed changes:**
```json
{
  "rewrite_prompt": "در گفت‌وگوی روزمره ایرانی، عبارت «خسته نباشید» معمولاً در چه موقعیتی گفته می‌شود؟",
  "notes": "The correct answer (index 1) remains valid as the best choice among the four. Minor prompt wording fix recommended to replace 'کجا' with 'در چه موقعیتی'. Consider moving to 'medium' split given low difficulty."
}
```

---

#### `peval-hard-culture-027`

**Prompt:** وقتی کسی می‌گوید «این کار از من برمی‌آید»، نزدیک‌ترین معنی محاوره‌ای چیست؟

  - الف) این کار را امروز انجام می‌دهم
  - ب) این کار از من گرفته شد
  - پ) این کار را می‌توانم انجام دهم ← labelled answer
  - ت) این کار را بلد نیستم

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Item is placed in 'hard' split but the idiom «از من برمی‌آید» is extremely common and well-known to any Persian speaker — difficulty is closer to 1–2, not appropriate for a hard track.
  - Difficulty metadata (2) is consistent with the item being easy, but the split assignment ('hard') contradicts this.

**Proposed changes:**
```json
{
  "notes": "The answer and distractors are all correct. The only issue is the split assignment: this item belongs in a basic or intermediate track, not 'hard'. Recommend moving to a lower-difficulty split or replacing with a less common idiom (e.g., «از این ستون به آن ستون فرج است» or a more obscure expression) to justify the hard track placement."
}
```

---

#### `peval-hard-culture-029`

**Prompt:** اگر یک ایرانی در پاسخ به سوال «حال شما چطور است؟» بگوید «شکر، می‌گذرد»، نزدیک‌ترین برداشت ادب‌مند چیست؟

  - الف) بیان نسبتا مودبانه و خودداری از شکایت ← labelled answer
  - ب) نشان دادن خشم پنهان
  - پ) اعلام استعفا
  - ت) درخواست کمک فوری

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Difficulty is overrated at 4; the expression «شکر، می‌گذرد» is extremely common and any native speaker or intermediate learner would immediately recognize it as polite stoic acceptance — difficulty should be 2
  - The distractors are not very tempting; choices like «خشم پنهان» and «درخواست کمک فوری» are too obviously wrong, reducing discriminative power
  - The phrase could be enriched or made harder by asking about a more subtle or ambiguous expression

**Proposed changes:**
```json
{
  "notes": "The item is factually correct and culturally authentic, but the difficulty metadata is inflated. Recommend downgrading difficulty to 2 in metadata. Optionally, replace with a more nuanced expression (e.g., «نه بد، نه خوب» or «دست شما درد نکند» in an unusual context) to genuinely challenge test-takers. If kept as-is, it belongs in a medium rather than hard track."
}
```

---

### `hard_instruction` — 6 items

#### `peval-hard-instruction-005`

**Prompt:** یک پاسخ فارسی برای کاربری که از قطعی اینترنت شکایت دارد بنویس. باید با «درک می‌کنم» شروع شود، شامل کلمات «پیگیری» و «راهکار» باشد، علامت سوال نداشته باشد و بین ۱۲ تا ۴۰ کلمه باشد.

**Constraints:** `{"required_prefix": "درک می‌کنم", "required_keywords": ["پیگیری", "راهکار"], "forbidden": ["؟", "?"], "min_words": 12, "max_words": 40}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - max_words of 40 is very generous; combined with min_words of 12, the range is wide and reduces difficulty below the 'hard' track expectation
  - Difficulty is closer to 3 than 4 because the constraints are straightforward and non-conflicting; the forbidden question mark is the only subtle element
  - No forbidden words that could conflict with required_keywords, which is good, but also means the item lacks the tension expected in hard_instruction items

**Proposed changes:**
```json
{
  "constraint_changes": {
    "min_words": 20,
    "max_words": 30
  },
  "rewrite_prompt": "یک پاسخ فارسی برای کاربری که از قطعی اینترنت شکایت دارد بنویس. باید با «درک می‌کنم» شروع شود، شامل کلمات «پیگیری» و «راهکار» باشد، علامت سوال نداشته باشد و بین ۲۰ تا ۳۰ کلمه باشد.",
  "notes": "Tightening the word range from 12–40 to 20–30 increases difficulty meaningfully and better fits the 'hard' track. All constraints remain jointly satisfiable. The item is otherwise well-constructed."
}
```

---

#### `peval-hard-instruction-006`

**Prompt:** یک پاراگراف فارسی درباره مزایای کار تیمی بنویس. پاسخ باید شامل «بازخورد» و «هدف مشترک» باشد، نباید کلمه «خیلی» را داشته باشد و دقیقا با کلمه «همکاری» شروع شود. طول بین ۱۵ تا ۴۵ کلمه.

**Constraints:** `{"required_prefix": "همکاری", "required_keywords": ["بازخورد", "هدف مشترک"], "forbidden": ["خیلی"], "min_words": 15, "max_words": 45}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - Difficulty rated 5 (expert) but constraints are jointly satisfiable without conflict and vocabulary is common — 3 is more appropriate
  - Word range 15–45 is generous; the lower bound of 15 is tight but achievable, so no real issue there

**Proposed changes:**
```json
{
  "notes": "The item is well-formed and all constraints are jointly satisfiable. The only needed change is correcting the difficulty metadata from 5 to 3. Everything else (prompt wording, forbidden/required keywords, word bounds, cultural fit) is solid."
}
```

---

#### `peval-hard-instruction-015`

**Prompt:** یک پیام تشکر رسمی فارسی به یک استاد بعد از پایان نیمسال بنویس. باید با «استاد گرامی» شروع شود، شامل «راهنمایی» و «این نیمسال» باشد، نباید کلمه «بد» داشته باشد و با «ارادتمند شما» تمام شود. طول بین ۲۰ تا ۵۰ کلمه.

**Constraints:** `{"required_prefix": "استاد گرامی", "required_suffix": "ارادتمند شما", "required_keywords": ["راهنمایی", "این نیمسال"], "forbidden": ["بد"], "min_words": 20, "max_words": 50}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - Difficulty rated 5 (expert) but constraints are moderate; forbidden word «بد» is trivially avoidable in a formal thank-you context, reducing actual difficulty
  - Forbidden word «بد» adds almost no real constraint — a formal letter to a professor would never naturally include this word, making it a non-binding restriction

**Proposed changes:**
```json
{
  "constraint_changes": {
    "forbidden": [
      "متأسفانه",
      "ناامید"
    ],
    "notes": "Replace «بد» with a word that is more plausible to appear in a thank-you letter but should be avoided, e.g. «متأسفانه» or «ناامید», to make the forbidden constraint meaningful"
  },
  "rewrite_prompt": "یک پیام تشکر رسمی فارسی به یک استاد بعد از پایان نیمسال بنویس. باید با «استاد گرامی» شروع شود، شامل «راهنمایی» و «این نیمسال» باشد، نباید کلمه «متأسفانه» داشته باشد و با «ارادتمند شما» تمام شود. طول بین ۲۰ تا ۵۰ کلمه.",
  "notes": "Item is structurally sound and culturally appropriate. Main issue is that the forbidden word «بد» is trivially avoidable, making that constraint meaningless. Replacing it with a word like «متأسفانه» (unfortunately) that could plausibly appear in a letter but should be avoided would increase genuine difficulty. Difficulty metadata should be revised from 5 to 3."
}
```

---

#### `peval-hard-instruction-023`

**Prompt:** یک پیام کوتاه برای دعوت یک متخصص به یک گفت‌وگوی پادکست بنویس. باید با «جناب آقای» یا «سرکار خانم» شروع شود (یکی به انتخاب)، شامل «گفت‌وگو» و «پادکست» باشد، نباید علامت تعجب داشته باشد و طول بین ۱۸ تا ۴۵ کلمه.

**Constraints:** `{"required_keywords": ["گفت‌وگو", "پادکست"], "forbidden": ["!"], "min_words": 18, "max_words": 45}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - forbidden list only includes ASCII '!' but not full-width '！' which could appear in Persian digital text
  - difficulty rated 4 by original reviewer but constraints are non-conflicting and straightforward — 3 is more accurate
  - prompt does not specify whether the expert's name should be included or can be left as a placeholder, which may cause inconsistent outputs

**Proposed changes:**
```json
{
  "constraint_changes": {
    "forbidden": [
      "!",
      "！"
    ]
  },
  "rewrite_prompt": "یک پیام کوتاه برای دعوت یک متخصص (می‌توانید نام را به صورت فرضی بنویسید) به یک گفت‌وگوی پادکست بنویس. باید با «جناب آقای» یا «سرکار خانم» شروع شود (یکی به انتخاب)، شامل «گفت‌وگو» و «پادکست» باشد، نباید علامت تعجب داشته باشد و طول بین ۱۸ تا ۴۵ کلمه.",
  "notes": "Adding full-width exclamation mark to forbidden list and clarifying that a placeholder name is acceptable makes the item more robust and consistent."
}
```

---

#### `peval-hard-instruction-028`

**Prompt:** یک پاسخ فارسی به یک ایمیل که خواستار اطلاعات بیشتر از یک گزارش است بنویس. باید با «پیرو ایمیل» شروع شود، شامل «جزئیات تکمیلی» و «پیوست» باشد، نباید علامت سوال داشته باشد و طول بین ۱۵ تا ۴۵ کلمه.

**Constraints:** `{"required_prefix": "پیرو ایمیل", "required_keywords": ["جزئیات تکمیلی", "پیوست"], "forbidden": ["؟", "?"], "min_words": 15, "max_words": 45}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - difficulty rated 4 but constraints are clear and word window (15–45) is generous, making this more of a difficulty-3 item
  - prompt could clarify that the reply is *providing* the requested information (not requesting it), to avoid any misreading of the scenario direction

**Proposed changes:**
```json
{
  "rewrite_prompt": "یک پاسخ رسمی فارسی به یک ایمیل که خواستار اطلاعات بیشتر درباره یک گزارش است بنویس. در این پاسخ اطلاعات درخواست‌شده را ارائه بده. باید با «پیرو ایمیل» شروع شود، شامل «جزئیات تکمیلی» و «پیوست» باشد، نباید علامت سوال داشته باشد و طول بین ۱۵ تا ۴۵ کلمه باشد.",
  "notes": "The item is fundamentally sound. Only minor improvements needed: clarify the reply direction (providing info, not requesting it) and adjust difficulty to 3. Constraints are jointly satisfiable with no conflicts."
}
```

---

#### `peval-hard-instruction-029`

**Prompt:** یک متن کوتاه برای دعوت همکاران به یک نشست هم‌فکری درباره فرهنگ سازمانی بنویس. باید با «همکاران گرامی» شروع شود، شامل «هم‌فکری» و «فرهنگ سازمانی» باشد، نباید کلمه «اجباری» داشته باشد و طول بین ۲۰ تا ۵۰ کلمه.

**Constraints:** `{"required_prefix": "همکاران گرامی", "required_keywords": ["هم‌فکری", "فرهنگ سازمانی"], "forbidden": ["اجباری"], "min_words": 20, "max_words": 50}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - Forbidden word «اجباری» is extremely unlikely to appear in an invitation text naturally, making that constraint nearly trivial and not meaningfully testing constraint-following
  - Difficulty overrated at 4; given generous word range and non-conflicting constraints, 3 is more accurate

**Proposed changes:**
```json
{
  "constraint_changes": {
    "forbidden": [
      "اجباری",
      "الزامی"
    ],
    "max_words": 50
  },
  "rewrite_prompt": "یک متن کوتاه برای دعوت همکاران به یک نشست هم‌فکری درباره فرهنگ سازمانی بنویس. باید با «همکاران گرامی» شروع شود، شامل «هم‌فکری» و «فرهنگ سازمانی» باشد، نباید کلمه‌های «اجباری» یا «الزامی» داشته باشد و طول بین ۲۰ تا ۵۰ کلمه.",
  "notes": "Adding «الزامی» to the forbidden list makes the constraint more meaningful, as it is a word that could plausibly appear in formal workplace communications. Difficulty adjusted to 3."
}
```

---

### `hard_math` — 18 items

#### `peval-hard-math-005`

**Prompt:** یک کالا قیمت اولیه ۲۵۰ هزار تومان دارد. ابتدا ۱۰ درصد گران می‌شود و سپس از قیمت جدید ۲۰ درصد تخفیف می‌خورد. قیمت نهایی به تومان چقدر است؟

**Accepted answers:** ['۲۲۰۰۰۰', '220000', '۲۲۰ هزار', '220 هزار', 'دویست و بیست هزار']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Difficulty overrated at 3; two-step percentage problem is straightforward, difficulty 2 is more appropriate
  - Missing answer variants with thousands separators (۲۲۰،۰۰۰ and 220,000)
  - Variants with unit 'تومان' appended (e.g. 'دویست و بیست هزار تومان') should be accepted since the question asks for price 'به تومان'

**Proposed changes:**
```json
{
  "answer_additions": [
    "۲۲۰،۰۰۰",
    "220,000",
    "دویست و بیست هزار تومان",
    "۲۲۰ هزار تومان",
    "220 هزار تومان",
    "۲۲۰٬۰۰۰"
  ],
  "notes": "The mathematical answer is correct. Main issues are: (1) difficulty should be lowered to 2, (2) answer list should include variants with thousands separators and with the unit 'تومان' explicitly appended, since the prompt asks for the price 'به تومان' which may prompt models to include the unit in their response."
}
```

---

#### `peval-hard-math-006`

**Prompt:** میانگین چهار عدد ۱۵ است. اگر عدد پنجمی به‌نام x به آنها اضافه شود تا میانگین پنج عدد ۱۸ شود، x چند است؟

**Accepted answers:** ['۳۰', '30']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Problem is placed in 'hard_math' track but is a basic two-step arithmetic problem suitable for middle school, not advanced math
  - Difficulty rating of 3 in metadata is inflated; problem is closer to difficulty 2
  - Leakage risk is non-trivial: this exact problem type (4 numbers avg 15, add x to get avg 18) is extremely common in Iranian math textbooks and online resources

**Proposed changes:**
```json
{
  "notes": "The math and answer are correct. The main issue is track placement: this item belongs in a 'basic_math' or 'medium_math' track, not 'hard_math'. Consider either moving it to an easier track or increasing difficulty by adding a layer of complexity (e.g., making one of the four numbers unknown with an additional constraint)."
}
```

---

#### `peval-hard-math-007`

**Prompt:** سه نفر در ساختن یک دیوار همکاری می‌کنند. نفر اول به‌تنهایی این کار را در ۶ ساعت انجام می‌دهد، نفر دوم در ۸ ساعت و نفر سوم در ۱۲ ساعت. اگر هر سه با هم کار کنند، چند ساعت طول می‌کشد؟ پاسخ را به ساعت بنویس.

**Accepted answers:** ['۸/۳', '8/3', '۲ و ۲/۳', '2 و 2/3']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=3

**Issues:**
  - Answer list missing natural Iranian Persian phrasing '۲ ساعت و ۴۰ دقیقه'
  - Missing written-out Persian form 'دو و دو سوم'
  - Difficulty rated 4 but this is a standard middle-school work-rate problem; 3 is more appropriate
  - Decimal approximation variants (۲.۶۷) not included

**Proposed changes:**
```json
{
  "answer_additions": [
    "۲ ساعت و ۴۰ دقیقه",
    "دو و دو سوم",
    "۲.۶۷",
    "2.67",
    "۲ و ۲/۳ ساعت",
    "2 و ۲/۳"
  ],
  "notes": "The mathematical answer 8/3 is correct. The main issue is answer list incompleteness: '۲ ساعت و ۴۰ دقیقه' is a very natural way an Iranian student would express this answer. Difficulty should be downgraded to 3 as this is a standard work-rate problem from Iranian middle school curriculum (ریاضی راهنمایی)."
}
```

---

#### `peval-hard-math-008`

**Prompt:** یک قطار ۱۲۰ کیلومتر را با سرعت ۸۰ کیلومتر بر ساعت طی می‌کند و سپس ۸۰ کیلومتر را با سرعت ۴۰ کیلومتر بر ساعت. سرعت میانگین کل مسیر چند کیلومتر بر ساعت است؟

**Accepted answers:** ['۵۷.۱۴', '۵۷.۱', '57.1', '57.14', 'حدود ۵۷']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=3

**Issues:**
  - 'حدود ۵۷' is too imprecise for exact scoring and should be removed
  - Missing accepted phrasings: fraction form 400/7 and ۴۰۰/۷, and ۵۷.۱۴۳
  - Difficulty rated 4 but this is a standard high-school weighted-speed trap question; 3 is more accurate
  - Mixing approximate phrasing with exact scoring is internally inconsistent

**Proposed changes:**
```json
{
  "answer_additions": [
    "۴۰۰/۷",
    "400/7",
    "۵۷.۱۴۳",
    "57.143",
    "۵۷.۱۴۲۸"
  ],
  "notes": "Remove 'حدود ۵۷' from answer list as it is incompatible with exact scoring. Add fraction and extended decimal forms. Lower difficulty from 4 to 3."
}
```

---

#### `peval-hard-math-012`

**Prompt:** محیط یک دایره ۱۰ سانتی‌متر است. اگر شعاع آن دو برابر شود، محیط چند سانتی‌متر می‌شود؟

**Accepted answers:** ['۲۰', '20', 'بیست']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=1

**Issues:**
  - item is in 'hard_math' track and 'hard' split but the problem is trivially elementary — circumference scales linearly with radius, no real computation needed
  - self-assigned difficulty of 3 is inflated; should be 1
  - answer list missing natural full-phrase variant 'بیست سانتی‌متر'

**Proposed changes:**
```json
{
  "answer_additions": [
    "بیست سانتی‌متر",
    "۲۰ سانتی‌متر",
    "20 سانتی‌متر"
  ],
  "notes": "The math is correct and the answer list is mostly complete, but this item does not belong in the hard_math track. It should either be moved to an easy/medium geometry track or replaced with a genuinely difficult geometry problem (e.g., involving arc length, sector area, inscribed angles, or coordinate geometry). Difficulty should be corrected to 1."
}
```

---

#### `peval-hard-math-013`

**Prompt:** علی ۵ ساله است و پدرش ۳۵ ساله. چند سال دیگر سن پدر دقیقا دو برابر سن علی می‌شود؟

**Accepted answers:** ['۲۵', '25', 'بیست و پنج']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Problem is placed in 'hard_math' track but is a trivial single-variable linear equation suitable for middle school — difficulty is overestimated
  - Difficulty metadata says 3 but actual difficulty is closer to 2 (basic age problem)
  - Leakage risk is non-trivial: 5-year-old / 35-year-old age problem is one of the most canonical examples in algebra textbooks worldwide

**Proposed changes:**
```json
{
  "notes": "Move item to 'easy' or 'medium' track and update difficulty to 2. Alternatively, replace with a harder age problem (e.g., involving three people or a ratio that changes over time) to justify the 'hard_math' track placement. The answer list is complete and correct."
}
```

---

#### `peval-hard-math-014`

**Prompt:** اگر مجموع سه عدد متوالی ۴۸ باشد، عدد وسط چند است؟

**Accepted answers:** ['۱۶', '16', 'شانزده']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=1

**Issues:**
  - Item is in 'hard_math' track / 'hard' split but is elementary-level arithmetic (grade 4–5); severe track mismatch
  - Difficulty is 1, not 2 as labelled in the rubric
  - Extremely common textbook problem type with high leakage risk
  - Does not meet the difficulty bar expected for a hard math benchmark

**Proposed changes:**
```json
{
  "notes": "Either move this item to an 'easy' or 'medium' math track, or replace the prompt with a genuinely hard problem (e.g., involving arithmetic sequences with non-trivial constraints, modular arithmetic, or combinatorics). The answer and answer list are mathematically correct as-is."
}
```

---

#### `peval-hard-math-015`

**Prompt:** یک کتاب در یک فروشگاه ۲۰ درصد تخفیف خورد و قیمت آن به ۸۰ هزار تومان رسید. قیمت اصلی کتاب چقدر بود (به تومان)؟

**Accepted answers:** ['۱۰۰۰۰۰', '100000', '۱۰۰ هزار', '100 هزار', 'صد هزار']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Item is placed in 'hard_math' track and 'hard' split but the problem is elementary one-step arithmetic — not hard by any standard
  - Missing answer variants with thousands separators (۱۰۰،۰۰۰ and 100،000)
  - Difficulty rating of 3 is inflated for a single-step percentage reversal

**Proposed changes:**
```json
{
  "answer_additions": [
    "۱۰۰،۰۰۰",
    "100،000",
    "یک صد هزار"
  ],
  "notes": "The math and answer are correct. The main issue is misclassification: this belongs in a basic/easy math track, not hard_math. If it must stay in hard_math, the problem should be made more complex (e.g., compound discounts, multi-step reasoning). Recommend moving to an 'easy_math' or 'basic' track, or replacing with a harder percentage problem."
}
```

---

#### `peval-hard-math-017`

**Prompt:** نسبت سن دو نفر ۲ به ۳ است. اگر مجموع سن آن‌ها ۵۰ باشد، سن نفر بزرگ‌تر چند است؟

**Accepted answers:** ['۳۰', '30', 'سی']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=1

**Issues:**
  - Item is in 'hard_math' track but the problem is trivially easy (single-step ratio calculation, middle-school level)
  - Difficulty self-rating of 3 is inflated; actual difficulty is 1
  - Leakage risk is moderate — this exact problem (ratio 2:3, sum 50) is a canonical textbook example widely available in Persian math resources
  - Answer list missing 'سی سال' which is a natural Persian response when asked about age

**Proposed changes:**
```json
{
  "answer_additions": [
    "سی سال",
    "۳۰ سال",
    "30 سال"
  ],
  "rewrite_prompt": "نسبت سن سه نفر ۲ به ۳ به ۵ است. اگر مجموع سن آن‌ها ۱۲۰ باشد و سن میانی هر سال ۲ سال افزایش یابد، پس از ۵ سال سن بزرگ‌ترین نفر چند خواهد بود؟",
  "notes": "The current problem is too simple for the hard_math track. Either move it to an easy/medium track, or replace with a more complex multi-step ratio problem. The rewrite_prompt above is one possible harder variant, though it should be reviewed for clarity. Alternatively, keep the problem but reassign to a basic_math or medium track."
}
```

---

#### `peval-hard-math-018`

**Prompt:** اگر شعاع یک دایره ۷ سانتی‌متر باشد و عدد پی را ۲۲/۷ بگیریم، مساحت دایره چند سانتی‌متر مربع است؟

**Accepted answers:** ['۱۵۴', '154', 'صد و پنجاه و چهار']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=4, difficulty=1

**Issues:**
  - Track mismatch: problem is elementary-level but placed in hard_math/hard split
  - Leakage risk: r=7 with π=22/7 is the canonical Iranian school textbook example for circle area, almost certainly from standard curriculum
  - Difficulty self-rating of 3 is too high; this is a trivial plug-in calculation (difficulty 1)
  - Answer list could include unit-bearing variants for robustness

**Proposed changes:**
```json
{
  "answer_additions": [
    "۱۵۴ سانتی‌متر مربع",
    "154 سانتی‌متر مربع"
  ],
  "notes": "The mathematical answer is correct. The core problem is misclassification: this is a grade-5 level Iranian math problem and should not be in the hard split. Either replace with a genuinely difficult geometry problem (e.g., involving inscribed polygons, arc lengths, sector areas with non-trivial algebra) or move to a basic_math track. Leakage risk is high due to the iconic r=7, π=22/7 pairing used in virtually all Iranian math textbooks."
}
```

---

#### `peval-hard-math-019`

**Prompt:** احتمال اینکه با پرتاب یک تاس عددی بزرگ‌تر از ۴ بیاید چقدر است؟ پاسخ را به‌صورت کسر ساده‌شده بنویس.

**Accepted answers:** ['۱/۳', '1/3']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=4, difficulty=1

**Issues:**
  - item is in 'hard_math' track but is a trivially easy probability question (elementary level)
  - leakage risk is high — this is one of the most canonical probability examples in Persian math textbooks
  - difficulty should be rated 1, not 2
  - answer list is adequate given the 'ساده‌شده' constraint; unsimplified 2/6 correctly excluded

**Proposed changes:**
```json
{
  "rewrite_prompt": "یک تاس منصفانه شش‌وجهی را دو بار پرتاب می‌کنیم. احتمال اینکه مجموع دو عدد به‌دست‌آمده بزرگ‌تر از ۹ باشد چقدر است؟ پاسخ را به‌صورت کسر ساده‌شده بنویس.",
  "notes": "If the track must remain 'hard_math', the prompt needs to be replaced with a genuinely harder probability problem. The suggested rewrite (sum > 9 with two dice) gives P = 6/36 = 1/6, which is still not 'hard' but at least requires a sample space enumeration. For a truly hard item, consider conditional probability, combinatorics, or Bayes' theorem. Alternatively, move this item to an 'easy_math' or 'basic_math' track."
}
```

---

#### `peval-hard-math-020`

**Prompt:** تعداد مقسوم‌علیه‌های مثبت عدد ۱۲ چند تا است؟

**Accepted answers:** ['۶', '6', 'شش']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=1

**Issues:**
  - Difficulty is trivially low (grade 4–5 level); does not belong in 'hard_math' track or 'hard' split
  - Difficulty metadata is rated 3 but should be 1 — finding divisors of 12 is elementary
  - Leakage risk slightly underestimated; this is an extremely standard textbook problem

**Proposed changes:**
```json
{
  "answer_additions": [
    "٦"
  ],
  "notes": "Either move this item to an 'easy_math' or 'elementary' track/split, or replace it with a genuinely hard number theory question (e.g., counting divisors of a large number like 720 or 10^6, or asking for the number of divisors of n! for small n). The current question is appropriate for a basic math benchmark, not a hard one."
}
```

---

#### `peval-hard-math-021`

**Prompt:** اگر در یک خانواده ۳ فرزند باشد و هر فرزند به‌طور مستقل با احتمال یک‌دوم پسر یا دختر باشد، احتمال اینکه دقیقا دو پسر باشند چقدر است؟ پاسخ را به‌صورت کسر بنویس.

**Accepted answers:** ['۳/۸', '3/8']

**Rubric:** clarity=4, ambiguity=2, cultural_fit=5, leakage_risk=3, difficulty=2

**Issues:**
  - Difficulty is severely overrated (rated 4, actual ~2); this is a trivial binomial probability problem taught in introductory courses
  - Item is placed in 'hard' split but is entry-level probability
  - Extremely standard textbook problem — high leakage/contamination risk
  - Answer list missing mixed-digit variant (e.g., 3/۸ or ۳/8) and decimal form 0.375/۰٫۳۷۵
  - Prompt says 'به‌صورت کسر' but does not specify simplified form, so 6/16 is technically valid

**Proposed changes:**
```json
{
  "answer_additions": [
    "۰٫۳۷۵",
    "0.375",
    "3/۸",
    "۳/8"
  ],
  "notes": "This item should be moved to an 'easy' or 'medium' split. Consider replacing with a harder probability problem (e.g., conditional probability, Bayes' theorem, or combinatorics with constraints) to justify the 'hard_math' track. Also add a note that the fraction should be in simplified form to avoid 6/16 being accepted."
}
```

---

#### `peval-hard-math-022`

**Prompt:** میانگین ۵ عدد ۲۰ است. اگر یکی از این اعداد، که برابر ۱۵ بود، حذف شود، میانگین چهار عدد باقی‌مانده چند است؟

**Accepted answers:** ['۲۱.۲۵', '21.25', 'بیست و یک و یک\u200cچهارم']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - difficulty is overrated at 3; this is a basic two-step arithmetic problem not suitable for 'hard' split
  - answer list missing common Persian phrasing '۲۱ و یک‌چهارم' (with space)
  - split label 'hard' is inconsistent with the elementary nature of the problem

**Proposed changes:**
```json
{
  "answer_additions": [
    "۲۱ و یک‌چهارم",
    "بیست‌ویک و یک چهارم"
  ],
  "notes": "The math is correct (100-15=85, 85/4=21.25). Main issues are the difficulty mislabeling and missing answer variant. Consider moving to a standard/medium track or replacing with a harder mean problem (e.g., weighted means, missing value with constraints)."
}
```

---

#### `peval-hard-math-023`

**Prompt:** اگر x در معادله ۳x − ۷ = ۲x + ۵ صدق کند، مقدار x چند است؟

**Accepted answers:** ['۱۲', '12', 'دوازده']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=1

**Issues:**
  - Item is in 'hard_math' track and 'hard' split but is a trivially easy one-step linear equation (difficulty 1, not appropriate for a hard benchmark)
  - Difficulty metadata says 2 but should be 1; more importantly the track/split assignment is wrong
  - Leakage risk is slightly elevated — this exact equation form appears in countless textbooks worldwide

**Proposed changes:**
```json
{
  "notes": "Either move this item to an 'easy_math' or 'basic_algebra' track, or replace the equation with a genuinely hard problem (e.g., a system of nonlinear equations, a Diophantine equation, or a competition-level algebra problem) to justify placement in the hard split. The answer list is complete and correct."
}
```

---

#### `peval-hard-math-025`

**Prompt:** اگر طول یک مستطیل ۴ متر و عرض آن ۳ متر باشد، طول قطر آن چند متر است؟

**Accepted answers:** ['۵', '5', 'پنج']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=5, difficulty=1

**Issues:**
  - Item is in 'hard_math' track and 'hard' split but is trivially easy — 3-4-5 Pythagorean triple is the most elementary geometry example
  - Leakage risk is very high: this exact problem with these exact numbers appears in every Persian middle school textbook
  - Answer list missing unit-inclusive variants since the question asks 'چند متر است'

**Proposed changes:**
```json
{
  "answer_additions": [
    "۵ متر",
    "5 متر",
    "پنج متر"
  ],
  "rewrite_prompt": "اگر طول یک مستطیل ۷ متر و عرض آن ۲۴ متر باشد، طول قطر آن چند متر است؟",
  "notes": "Either move this item to an easy/medium track, or replace the numbers with a less canonical Pythagorean triple (e.g., 7-24-25) to increase difficulty and reduce leakage. The rewrite_prompt suggestion uses 7-24-25 which is less commonly memorized. Also add unit-inclusive answer variants."
}
```

---

#### `peval-hard-math-026`

**Prompt:** اگر امروز دوشنبه باشد، ۲۰۰ روز دیگر چه روزی از هفته است؟

**Accepted answers:** ['شنبه']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=3

**Issues:**
  - Labeled answer شنبه (Saturday) is mathematically incorrect
  - 200 mod 7 = 4; Monday + 4 days = Friday (جمعه), not Saturday
  - Leakage risk is moderate — 'X days from Monday' problems are very common in puzzle repositories
  - Difficulty is overrated; this is straightforward modular arithmetic, more like difficulty 3

**Proposed changes:**
```json
{
  "answer_replacement": "جمعه",
  "notes": "200 ÷ 7 = 28 remainder 4. Starting from Monday (دوشنبه) and advancing 4 days: Tuesday, Wednesday, Thursday, Friday. The correct answer is جمعه (Friday). The current answer شنبه is wrong by one day. Also consider adding 'پنج‌شنبه' as an alternative if the question is interpreted as counting today as day 1 (199 mod 7 = 3, Monday+3 = Thursday), but the most natural reading gives جمعه."
}
```

---

#### `peval-hard-math-030`

**Prompt:** احتمال اینکه با پرتاب همزمان دو تاس، مجموع برابر ۷ شود چقدر است؟ پاسخ را به‌صورت کسر ساده‌شده بنویس.

**Accepted answers:** ['۱/۶', '1/6']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=4, difficulty=1

**Issues:**
  - Track mismatch: item is in 'hard_math' track but this is an elementary probability problem (middle-school level, difficulty 1–2 not 3+)
  - Leakage risk is high: this is arguably the most canonical dice probability problem in existence, present in virtually every probability textbook and online resource
  - Difficulty rating of 3 in metadata is inflated; this is trivial for any student who has studied basic probability
  - Answer list could optionally include 'یک ششم' (Persian word form) for robustness

**Proposed changes:**
```json
{
  "answer_additions": [
    "یک ششم"
  ],
  "notes": "This item should be moved to an 'easy' or 'medium' probability track, not 'hard_math'. The difficulty metadata should be corrected to 1 or 2. If the goal is to keep it in hard_math, the problem should be substantially harder — e.g., asking for conditional probability, multiple dice, or a more complex combinatorial setup. The leakage risk is inherent to the problem's canonical nature and cannot be fixed by rewording alone."
}
```

---

### `hard_reading` — 16 items

#### `peval-hard-reading-006`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک پژوهش در میان دانش‌آموزان نشان داد کسانی که صبحانه می‌خورند نمره‌های بهتری دارند. اما بررسی دقیق‌تر نشان داد این دانش‌آموزان معمولا از خانواده‌هایی هستند که شب زود می‌خوابند و حمایت تحصیلی بیشتری دارند. ...

**Accepted answers:** ['حمایت خانوادگی و خواب کافی', 'حمایت خانواده و خواب زود']

**Rubric:** clarity=4, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - سوال از 'عامل پنهانی' (مفرد) می‌پرسد اما متن دو عامل مخدوش‌کننده دارد — ابهام در تعداد پاسخ
  - پاسخ‌های لیبل‌شده از 'حمایت خانوادگی' استفاده می‌کنند اما متن دقیقاً 'حمایت تحصیلی' دارد
  - سطح دشواری 5 اغراق‌آمیز است؛ 3 یا 4 مناسب‌تر است
  - لیست پاسخ‌های پذیرفتنی برای F1 ناقص است

**Proposed changes:**
```json
{
  "answer_additions": [
    "خواب کافی و حمایت تحصیلی",
    "حمایت تحصیلی و خواب زود",
    "حمایت تحصیلی خانواده و خواب کافی",
    "وضعیت خانوادگی و خواب",
    "حمایت تحصیلی"
  ],
  "rewrite_prompt": "متن را بخوان و پاسخ کوتاه بده: یک پژوهش در میان دانش‌آموزان نشان داد کسانی که صبحانه می‌خورند نمره‌های بهتری دارند. اما بررسی دقیق‌تر نشان داد این دانش‌آموزان معمولاً از خانواده‌هایی هستند که شب زود می‌خوابند و حمایت تحصیلی بیشتری دارند. سوال: چه عوامل پنهانی نتیجه ساده «صبحانه = نمره بهتر» را تردیدآمیز می‌کنند؟",
  "notes": "تغییر 'عامل پنهانی' به 'عوامل پنهانی' (جمع) با متن همخوانی بیشتری دارد و ابهام را برطرف می‌کند. همچنین سطح دشواری باید از 5 به 3 کاهش یابد."
}
```

---

#### `peval-hard-reading-008`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: مدیر یک رستوران دو پیشخدمت داشت. پیشخدمت اول هر روز فرم رضایت مشتریان را خودش پر می‌کرد. پیشخدمت دوم فرم را به مشتری می‌داد. در گزارش پایان ماه، رضایت پیشخدمت اول کمی بالاتر بود. مدیر نتیجه گرفت پیشخدمت اول...

**Accepted answers:** ['تعارض منافع در پر کردن فرم', 'سوگیری در جمع\u200cآوری داده توسط خود پیشخدمت']

**Rubric:** clarity=4, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - Difficulty rated 5 (expert) is inflated; the self-reporting bias is moderately transparent, not expert-level
  - Answer list is too narrow for f1 scoring; many valid Persian phrasings are missing
  - The scenario makes the flaw fairly obvious on careful reading, reducing difficulty

**Proposed changes:**
```json
{
  "answer_additions": [
    "پیشخدمت اول فرم را خودش پر کرده است",
    "عدم بی‌طرفی در جمع‌آوری داده",
    "مقایسه ناعادلانه به دلیل روش متفاوت جمع‌آوری داده",
    "نبود کنترل یکسان در روش جمع‌آوری داده",
    "خودگزارشی پیشخدمت اول",
    "داده‌های غیرقابل اعتماد به دلیل پر کردن فرم توسط خود پیشخدمت",
    "تفاوت در روش جمع‌آوری داده بین دو پیشخدمت"
  ],
  "constraint_changes": {
    "difficulty": 3
  },
  "notes": "The core concept (self-reporting bias / conflict of interest) is correct and the item is salvageable. Difficulty should be revised to 3. The f1 answer list needs expansion to capture the many natural ways a Persian speaker might express this insight."
}
```

---

#### `peval-hard-reading-009`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: مدیر مدرسه گفت اگر سرویس مدرسه به‌موقع برسد، اردو ساعت ۸ برگزار می‌شود. صبح روز اردو بچه‌ها دیدند هرچند سرویس به‌موقع رسید، اردو ساعت ۹ آغاز شد چون قفل در ورودی پارک نیم‌ساعت دیر باز شد. سوال: علت اصلی تاخی...

**Accepted answers:** ['دیر باز شدن قفل در ورودی پارک', 'تاخیر در باز شدن در پارک']

**Rubric:** clarity=3, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - ناسازگاری منطقی: قفل نیم‌ساعت دیر باز شد اما اردو یک ساعت تأخیر داشت (۸ به ۹)؛ این تناقض می‌تواند خواننده دقیق را گیج کند
  - سطح دشواری ۴ برای سؤالی که پاسخش صریحاً در متن آمده اغراق‌آمیز است
  - فهرست پاسخ‌های پذیرفتنی ناقص است

**Proposed changes:**
```json
{
  "answer_additions": [
    "قفل پارک دیر باز شد",
    "نیم‌ساعت تأخیر در باز شدن قفل در پارک",
    "باز نشدن به‌موقع قفل در ورودی پارک",
    "تأخیر در گشوده شدن در پارک"
  ],
  "rewrite_prompt": "متن را بخوان و پاسخ کوتاه بده: مدیر مدرسه گفت اگر سرویس مدرسه به‌موقع برسد، اردو ساعت ۸ برگزار می‌شود. صبح روز اردو بچه‌ها دیدند هرچند سرویس به‌موقع رسید، اردو ساعت ۹ آغاز شد چون قفل در ورودی پارک یک ساعت دیر باز شد. سوال: علت اصلی تاخیر اردو چه بود؟",
  "notes": "مهم‌ترین مشکل، ناسازگاری زمانی است: تأخیر قفل نیم‌ساعت بود اما تأخیر اردو یک ساعت. پیشنهاد می‌شود 'نیم‌ساعت' به 'یک ساعت' تغییر یابد تا متن منسجم شود. همچنین سطح دشواری به ۳ کاهش یابد."
}
```

---

#### `peval-hard-reading-010`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک شهرداری برای کاهش تصادف، در سه چهارراه دوربین نصب کرد. یک سال بعد، تعداد تصادفات در آن سه چهارراه نصف شد. اما در گزارش سراسری شهر، عدد کل تصادف فقط ۵٪ کم شد. سوال: چه احتمالی توضیح می‌دهد که چرا کاهش محل...

**Accepted answers:** ['جابه\u200cجایی تصادف به چهارراه\u200cهای دیگر', 'انتقال رفتار رانندگی به نقاط بدون دوربین']

**Rubric:** clarity=4, ambiguity=3, cultural_fit=5, leakage_risk=2, difficulty=3

**Issues:**
  - دو پاسخ موجود در واقع یک مفهوم (اثر جابه‌جایی) را با دو عبارت متفاوت بیان می‌کنند و تکراری هستند
  - پاسخ مهم 'بازگشت به میانگین' (regression to the mean) که توضیح آماری قوی‌تری است، در لیست پاسخ‌ها غایب است
  - توضیح ریاضی محض (سه چهارراه از کل شهر سهم کوچکی دارند) نیز پاسخ دفاع‌پذیر است و باید اضافه شود
  - سطح دشواری ۵ اغراق‌آمیز است؛ اثر جابه‌جایی مفهوم شناخته‌شده‌ای است
  - امتیاز ابهام باید بالاتر باشد چون چند پاسخ دفاع‌پذیر وجود دارد

**Proposed changes:**
```json
{
  "answer_additions": [
    "بازگشت به میانگین (این چهارراه‌ها به دلیل تصادف بالا انتخاب شدند و به‌طور طبیعی بهبود می‌یافتند)",
    "سهم کوچک سه چهارراه از کل شهر (کاهش ۵۰٪ در تعداد کمی از نقاط تأثیر ناچیزی بر کل دارد)",
    "رانندگان مسیرهای جایگزین بدون دوربین را انتخاب کردند"
  ],
  "notes": "پاسخ‌های فعلی هر دو اثر جابه‌جایی را توصیف می‌کنند. باید یکی حذف و پاسخ‌های 'بازگشت به میانگین' و 'تأثیر ریاضی سهم کوچک' اضافه شوند. همچنین metadata باید ambiguity=3 و difficulty=3 را منعکس کند."
}
```

---

#### `peval-hard-reading-013`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: مدیر یک سایت دید پس از تغییر رنگ دکمه خرید از آبی به نارنجی، فروش ۲٪ بالا رفت. اما همان روز یک کمپین تلویزیونی هم آغاز شده بود. سوال: چرا نمی‌توان مطمئن بود رشد فروش از تغییر رنگ دکمه است؟

**Accepted answers:** ['همزمانی با کمپین تلویزیونی', 'اثر کمپین به\u200cعنوان متغیر مزاحم']

**Rubric:** clarity=5, ambiguity=2, cultural_fit=4, leakage_risk=1, difficulty=3

**Issues:**
  - Answer list too narrow for f1 scoring — many valid Persian phrasings of the correct concept are missing
  - Difficulty is overstated at 4; the confound is explicitly named in the text, requiring minimal inference
  - Second answer phrase 'متغیر مزاحم' is technical jargon not commonly used in everyday Iranian Persian

**Proposed changes:**
```json
{
  "answer_additions": [
    "وجود متغیر مداخله‌گر",
    "کمپین تلویزیونی هم همزمان شروع شده بود",
    "همزمانی دو رویداد مختلف",
    "عدم کنترل سایر عوامل",
    "نمی‌توان رابطه علّی برقرار کرد",
    "کمپین تلویزیونی می‌توانست عامل اصلی باشد",
    "متغیر گیج‌کننده وجود داشت",
    "عامل دیگری هم در همان زمان وجود داشت"
  ],
  "notes": "The item tests a valid and important concept (confounding variables). The scenario is well-constructed. Main issue is that f1 scoring requires a broader set of accepted answers to avoid penalizing correct but differently-phrased responses. Difficulty should be revised to 3 since the confounding factor is explicitly stated in the passage."
}
```

---

#### `peval-hard-reading-014`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک شهر سه راه دارد: راه شمال، راه مرکز، راه جنوب. کارگزار شهر گفت اگر در راه شمال سد ساخته شود، آب در راه مرکز به‌حد کافی می‌رسد. ولی پس از ساخت سد، آب در راه مرکز کم شد چون تامین مرکز مستقل از شمال بود. سو...

**Accepted answers:** ['فرض غلط رابطه علی بین شمال و مرکز', 'نسبت دادن نادرست علت']

**Rubric:** clarity=3, ambiguity=3, cultural_fit=3, leakage_risk=1, difficulty=4

**Issues:**
  - هر دو پاسخ ارائه‌شده مفهوم یکسانی را بیان می‌کنند و تنوع واقعی ندارند
  - اصطلاح 'خطای نگرشی' غیرمعمول است؛ 'مغالطه منطقی' یا 'خطای شناختی' رایج‌تر است
  - فهرست پاسخ‌های پذیرفتنی برای نمره‌دهی f1 ناقص است — اصطلاحات استاندارد مانند 'مغالطه علّی کاذب' غایب‌اند
  - سناریو کمی مبهم است: استقلال تامین مرکز از شمال توضیح نمی‌دهد چرا آب کم شد، فقط می‌گوید سد تاثیری نداشته
  - سطح دشواری 5 اغراق‌آمیز است؛ 4 مناسب‌تر است

**Proposed changes:**
```json
{
  "answer_additions": [
    "مغالطه علّی کاذب",
    "خطای علّیت کاذب",
    "همبستگی را علیّت پنداشتن",
    "فرض رابطه علت و معلولی نادرست",
    "خطای شناختی در تشخیص علت",
    "مغالطه post hoc"
  ],
  "rewrite_prompt": "متن را بخوان و پاسخ کوتاه بده: یک شهر سه مسیر آبرسانی دارد: مسیر شمال، مسیر مرکز، مسیر جنوب. کارگزار شهر ادعا کرد اگر در مسیر شمال سد ساخته شود، آب در مسیر مرکز به حد کافی می‌رسد. اما پس از ساخت سد، آب در مسیر مرکز کم شد؛ زیرا تامین آب مرکز اصلاً به مسیر شمال وابسته نبود. سوال: ادعای کارگزار ناشی از کدام خطای منطقی یا شناختی بود؟",
  "notes": "اصطلاح 'خطای نگرشی' باید به 'خطای منطقی' یا 'خطای شناختی' تغییر یابد. فهرست پاسخ‌های f1 باید اصطلاحات استاندارد مغالطه علّی را شامل شود. سناریو نیاز به اندکی اصلاح دارد تا منطق کاهش آب روشن‌تر شود."
}
```

---

#### `peval-hard-reading-015`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: تیم نگه‌داری بنا گفت اگر گزارش تخلف امضا شود، آسانسور تعمیر می‌شود. ساکنان امضا کردند، ولی آسانسور تعمیر نشد چون قطعه یدکی در بازار موجود نبود. سوال: علت قطعی نقض وعده تیم چه بود؟

**Accepted answers:** ['نبود قطعه یدکی در بازار', 'موجود نبودن قطعه']

**Rubric:** clarity=4, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - Answer list is incomplete for F1 scoring — missing common Persian paraphrases like 'عدم وجود قطعه یدکی' and 'کمبود قطعه یدکی'
  - The word 'قطعی' in the question ('علت قطعی نقض وعده') is slightly awkward; 'علت اصلی' or simply 'علت' would be more natural Iranian Persian
  - Difficulty rating of 3 seems slightly high for a straightforward causal reading task where the answer is explicitly stated in the text

**Proposed changes:**
```json
{
  "answer_additions": [
    "عدم وجود قطعه یدکی",
    "کمبود قطعه یدکی",
    "قطعه یدکی پیدا نمی‌شد",
    "قطعه یدکی در دسترس نبود",
    "نبود قطعه"
  ],
  "rewrite_prompt": "متن را بخوان و پاسخ کوتاه بده: تیم نگه‌داری بنا گفت اگر گزارش تخلف امضا شود، آسانسور تعمیر می‌شود. ساکنان امضا کردند، ولی آسانسور تعمیر نشد چون قطعه یدکی در بازار موجود نبود. سوال: علت اصلی تعمیر نشدن آسانسور چه بود؟",
  "notes": "Replacing 'علت قطعی نقض وعده تیم' with 'علت اصلی تعمیر نشدن آسانسور' makes the question more natural and directly tied to the text. Also added several common Persian paraphrases to the answer list for better F1 coverage."
}
```

---

#### `peval-hard-reading-016`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک پژوهش نشان داد در یک منطقه، شهرهایی که میزان بستنی‌فروشی بیشتری دارند، آمار غرق‌شدگی بالاتری هم دارند. پژوهشگر نتیجه گرفت بستنی باعث غرق‌شدن می‌شود. سوال: چه متغیر مزاحم احتمالی توضیح بهتری می‌دهد؟

**Accepted answers:** ['گرما و فصل تابستان', 'هوای گرم و رفتن به آب']

**Rubric:** clarity=4, ambiguity=2, cultural_fit=4, leakage_risk=5, difficulty=3

**Issues:**
  - این مثال (بستنی و غرق‌شدگی) مشهورترین مثال متغیر مزاحم در آموزش آمار است و احتمال نشت از منابع عمومی بسیار بالاست
  - سطح دشواری در متادیتا ۵ ثبت شده اما برای کسی با آشنایی پایه با آمار، این سوال بسیار ساده است
  - لیست پاسخ‌های پذیرفتنی ناقص است و چندین معادل فارسی طبیعی را شامل نمی‌شود
  - به دلیل شهرت بسیار زیاد این مثال، ممکن است سوال قدرت تمایز کافی نداشته باشد

**Proposed changes:**
```json
{
  "answer_additions": [
    "فصل تابستان",
    "تابستان",
    "دمای هوا",
    "آب‌وهوای گرم",
    "فصل گرما",
    "گرمای هوا",
    "دما",
    "تابستان و گرما",
    "گرم بودن هوا"
  ],
  "notes": "توصیه می‌شود این مثال با یک سناریوی کمتر شناخته‌شده جایگزین شود تا خطر نشت کاهش یابد. همچنین سطح دشواری باید از ۵ به ۳ تصحیح شود. اگر مثال حفظ می‌شود، لیست پاسخ‌های پذیرفتنی باید گسترش یابد."
}
```

---

#### `peval-hard-reading-017`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: مدیر یک پروژه دید زمان جلسه‌های هفتگی هر هفته طولانی‌تر می‌شود. بررسی کرد و دید چون دستور جلسه نوشته نمی‌شود، بحث‌های فرعی زیاد می‌شوند. تصمیم گرفت دستور جلسه از قبل ارسال شود. سوال: ریشه ناکارآمدی جلسه‌ها ...

**Accepted answers:** ['نبود دستور جلسه از پیش', 'نداشتن دستور جلسه']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Answer list is incomplete — missing common Persian phrasings for the same concept
  - Difficulty overrated: the answer is explicitly stated in the passage, making it closer to level 2
  - 'نبود دستور جلسه از پیش' is slightly unnatural; 'نبود دستور جلسه از قبل' mirrors the source text better

**Proposed changes:**
```json
{
  "answer_additions": [
    "فقدان دستور جلسه",
    "عدم تنظیم دستور جلسه",
    "نبود دستور جلسه از قبل",
    "ننوشتن دستور جلسه",
    "عدم ارسال دستور جلسه قبل از جلسه",
    "نوشته نشدن دستور جلسه"
  ],
  "notes": "The item is fundamentally sound — clear passage, unambiguous root cause, good cultural fit. The main fix needed is expanding the answer list to cover natural Persian paraphrases for f1 scoring. Difficulty should be lowered to 2 since the answer is directly and explicitly stated in the text without requiring inference."
}
```

---

#### `peval-hard-reading-018`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک مدیر بازاریابی داده‌ها را فقط از ۲۵٪ مشتریان وفادار جمع می‌کرد، چون پاسخ‌گوتر بودند. سپس بر اساس همین داده‌ها برای کل بازار تصمیم می‌گرفت. سوال: نام این خطا چیست؟

**Accepted answers:** ['سوگیری انتخاب نمونه', 'سوگیری انتخاب']

**Rubric:** clarity=5, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - سوگیری نمونه‌گیری (sampling bias) is a common and arguably more precise Persian term for this scenario but is absent from the answer list
  - خطای انتخاب is a colloquial but defensible variant not included
  - Difficulty self-rated as 4 but concept is standard undergraduate-level material; 3 is more appropriate
  - Ambiguity is slightly higher than 1 because multiple valid technical terms exist for this phenomenon

**Proposed changes:**
```json
{
  "answer_additions": [
    "سوگیری نمونه‌گیری",
    "خطای انتخاب",
    "تعصب انتخاب"
  ],
  "notes": "The core answer is correct. The answer list needs expansion to cover the most common Persian technical synonyms. Difficulty should be adjusted to 3 in metadata. Ambiguity score of 2 reflects that multiple valid technical terms exist, though they all point to the same underlying concept."
}
```

---

#### `peval-hard-reading-019`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: کمیته آموزش گفت اگر نرخ قبولی دانش‌آموزان از ۸۰٪ بالاتر برود، معلم برتر معرفی می‌شود. در سال آینده نرخ قبولی به ۸۵٪ رسید، ولی معلم برتر معرفی نشد چون ضوابط جدیدی برای ارزیابی اضافه شد. سوال: علت معرفی نشدن ...

**Accepted answers:** ['اضافه شدن ضوابط جدید ارزیابی', 'تغییر ضوابط ارزیابی']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty is overrated (labeled 4, but answer is explicitly stated in text — no inference needed, more like 2)
  - Answer list is incomplete for f1 scoring; several natural Persian phrasings are missing
  - Item is labeled 'hard_reading' but the reasoning is trivial — the cause is directly stated in the passage

**Proposed changes:**
```json
{
  "answer_additions": [
    "افزوده شدن ضوابط جدید",
    "اضافه شدن معیارهای جدید ارزیابی",
    "تغییر معیارهای ارزیابی",
    "وضع ضوابط جدید ارزیابی",
    "ضوابط ارزیابی تغییر کرد",
    "اعمال ضوابط جدید"
  ],
  "notes": "The item is factually correct and well-formed, but the difficulty is significantly overestimated. The answer is explicitly stated in the final clause of the passage ('ضوابط جدیدی برای ارزیابی اضافه شد'), requiring no inference. To justify placement in the 'hard' track, the passage could be made more complex (e.g., the reason buried in a longer text, or requiring multi-step reasoning). As-is, it belongs in a medium-difficulty track. The f1 answer list should also be expanded to capture natural Persian paraphrases."
}
```

---

#### `peval-hard-reading-020`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک معلم دید نمره‌های امتحان نهایی در کلاس دخترانه بهتر از کلاس پسرانه است. در همان مدرسه، تعداد ساعت تدریس کلاس دخترانه دو برابر بوده. سوال: چرا نمی‌توان از این آمار نتیجه گرفت دختران در آن درس قوی‌ترند؟

**Accepted answers:** ['تفاوت در ساعت تدریس', 'متغیر مزاحم ساعت تدریس']

**Rubric:** clarity=4, ambiguity=2, cultural_fit=4, leakage_risk=1, difficulty=3

**Issues:**
  - answer list too narrow for f1 scoring — only technical phrasings included, missing natural Persian expressions
  - difficulty overrated at 4; standard confounding variable scenario is closer to 3
  - 'متغیر مزاحم' is jargon unlikely to match typical respondent output, reducing f1 recall unfairly
  - other confounders (e.g., teacher quality, student selection) could also be cited as valid reasons, slightly raising ambiguity

**Proposed changes:**
```json
{
  "answer_additions": [
    "ساعت تدریس بیشتر بوده",
    "کلاس دخترانه ساعت بیشتری داشته",
    "عامل مداخله‌گر ساعت تدریس",
    "مقایسه منصفانه نیست چون ساعت تدریس متفاوت است",
    "عامل گیج‌کننده وجود دارد",
    "متغیر کنترل‌نشده ساعت تدریس",
    "تفاوت ساعت آموزش دلیل بهتر بودن نمره‌هاست نه توانایی دختران"
  ],
  "notes": "The item tests a valid and useful concept (confounding variables). The core answer is correct but the accepted answer list must be broadened significantly for f1 scoring to work fairly. Difficulty should be adjusted to 3."
}
```

---

#### `peval-hard-reading-023`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک مدیر گفت چون ده درصد کارمندان از کافه شکایت دارند، باید کافه را تعطیل کنیم. اعضای تیم گفتند بهتر است نظر ۹۰ درصد بقیه را هم پرسید. سوال: ضعف تصمیم اولیه مدیر چه بود؟

**Accepted answers:** ['بی\u200cتوجهی به نظر اکثریت', 'تصمیم بر مبنای اقلیت']

**Rubric:** clarity=5, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty is overestimated; the 10%/90% contrast is explicit in the text, making the answer quite obvious — difficulty 2 is more appropriate
  - Answer list is incomplete: several common Persian phrasings of the same concept are missing and would be penalized under F1 scoring
  - The two provided answers are near-synonyms of each other, offering little coverage diversity

**Proposed changes:**
```json
{
  "answer_additions": [
    "نادیده گرفتن نظر اکثریت",
    "تعمیم نظر اقلیت به کل",
    "تصمیم‌گیری بر اساس داده‌های ناقص",
    "نادیده گرفتن ۹۰ درصد کارمندان",
    "عدم توجه به نظر بقیه کارمندان",
    "سوگیری در جمع‌آوری نظرات"
  ],
  "notes": "The item is conceptually sound and the scenario is well-constructed. Main issues are: (1) difficulty should be lowered to 2 since the answer is nearly explicit in the text, and (2) the F1 answer list needs more paraphrase coverage to avoid penalizing valid responses. The 'base_rate' category label is acceptable but 'sampling_bias' might be more precise."
}
```

---

#### `peval-hard-reading-024`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: شهردار یک شهر گفت چون پارک سرسبزتر شد، تعداد شکایت‌های ساکنان نزدیک پارک کم شد، پس کیفیت زندگی بهتر شده. اما بررسی نشان داد خیلی از همان ساکنان قبلا اسباب‌کشی کرده‌اند. سوال: چرا نتیجه شهردار قابل اعتماد نیست؟

**Accepted answers:** ['جابه\u200cجایی ساکنان شاکی', 'خروج معترضان از منطقه']

**Rubric:** clarity=4, ambiguity=2, cultural_fit=4, leakage_risk=2, difficulty=4

**Issues:**
  - Answer list too sparse for f1 scoring — many valid Persian phrasings missing
  - Difficulty self-rated as 5 but text explicitly hints at the answer; 4 is more accurate
  - No human reviewers listed; still pending review
  - Category 'survivor_bias' is close but the mechanism is more precisely selection bias due to attrition

**Proposed changes:**
```json
{
  "answer_additions": [
    "ساکنان ناراضی قبلاً رفته بودند",
    "تغییر ترکیب ساکنان منطقه",
    "سوگیری بازماندگان",
    "کاهش شکایت به دلیل رفتن معترضان بود نه بهبود واقعی",
    "نمونه باقی‌مانده نماینده ساکنان اولیه نیست",
    "انتخاب نمونه مغرضانه",
    "ساکنان شاکی از منطقه مهاجرت کرده بودند"
  ],
  "notes": "The item tests a valid and important reasoning skill. The core answer is correct but the f1 answer list needs expansion to cover the range of natural Persian phrasings a respondent might use. Difficulty should be adjusted to 4. Consider adding at least one human reviewer before finalizing."
}
```

---

#### `peval-hard-reading-027`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک پژوهش گفت در شهرهایی که قهوه بیشتری مصرف می‌شود، آمار سکته بالاتر است. بررسی نشان داد در همان شهرها میانگین سن جمعیت هم بیشتر است. سوال: متغیر مزاحم احتمالی چیست؟

**Accepted answers:** ['میانگین سن بالاتر', 'بیشتر بودن سن جمعیت']

**Rubric:** clarity=5, ambiguity=2, cultural_fit=4, leakage_risk=2, difficulty=4

**Issues:**
  - answer list is too narrow for f1 scoring — many natural Persian phrasings for 'age' are missing
  - standalone 'سن' should be an accepted answer
  - classic coffee-stroke-age confounding example has moderate leakage risk from epidemiology textbooks

**Proposed changes:**
```json
{
  "answer_additions": [
    "سن",
    "سن جمعیت",
    "میانگین سنی بالاتر",
    "پیری جمعیت",
    "سالمندی جمعیت",
    "عامل سن",
    "بالا بودن سن"
  ],
  "notes": "The item is conceptually sound and the labelled answers are correct. The main issue is that f1 scoring requires a broader set of accepted phrasings. Age (سن) in various forms should all be accepted. Leakage risk is moderate because this is a canonical epidemiology teaching example, but the Persian framing appears original enough to keep."
}
```

---

#### `peval-hard-reading-030`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک تیم بازی، در سه ماه گذشته همه بازی‌های خانگی را برده ولی همه بازی‌های خارج از خانه را باخته. مربی نتیجه گرفت زمین خانگی برای تیم حیاتی است. سوال: چه احتمال جایگزینی، توضیحی متفاوت برای این الگو می‌دهد؟

**Accepted answers:** ['تفاوت قدرت حریفان در دو دسته', 'حریفان خارج از خانه قوی\u200cتر']

**Rubric:** clarity=4, ambiguity=5, cultural_fit=3, leakage_risk=1, difficulty=3

**Issues:**
  - ambiguity is extremely high — many equally valid alternative explanations exist (travel fatigue, crowd support, psychological factors, small sample size, scheduling bias), but only one category is in the answer list
  - the two listed answers are essentially the same phrasing of the same idea, not two distinct accepted answers
  - F1 scoring will unfairly penalize correct answers not in the list
  - auto-review rated ambiguity=1 which is incorrect for an open-ended alternative-explanation question
  - prompt phrasing 'چه احتمال جایگزینی' is slightly unnatural in Persian

**Proposed changes:**
```json
{
  "answer_additions": [
    "خستگی ناشی از سفر برای بازی‌های خارج از خانه",
    "حمایت هواداران در زمین خانگی",
    "عوامل روانشناختی و اعتماد به نفس در زمین خانگی",
    "تعداد بازی‌ها کم است و نمی‌توان نتیجه‌گیری قطعی کرد",
    "شرایط زمین یا آب‌وهوا در مکان‌های مختلف متفاوت است",
    "برنامه‌ریزی بازی‌ها به گونه‌ای بوده که حریفان قوی‌تر در خارج از خانه بازی کرده‌اند",
    "حریفان ضعیف‌تر در بازی‌های خانگی"
  ],
  "rewrite_prompt": "متن را بخوان و پاسخ کوتاه بده: یک تیم بازی، در سه ماه گذشته همه بازی‌های خانگی را برده ولی همه بازی‌های خارج از خانه را باخته. مربی نتیجه گرفت زمین خانگی برای تیم حیاتی است. سوال: چه توضیح جایگزینی می‌تواند این الگو را بدون اشاره به اهمیت زمین خانگی توضیح دهد؟",
  "notes": "The item tests a valid skill (alternative hypothesis generation) but is fundamentally open-ended. Either (a) add all major alternative explanations to the answer list and accept any of them, or (b) convert to MCQ format with one clearly best alternative explanation as the correct answer and distractors. MCQ conversion would be cleaner for reliable scoring."
}
```

---

### `hard_reasoning` — 12 items

#### `peval-hard-reasoning-005`

**Prompt:** اگر هر کارمندی که به سرور دسترسی دارد، رمز عبور دو مرحله‌ای فعال کرده باشد و علی به سرور دسترسی دارد، کدام نتیجه قطعی است؟

  - الف) علی رمز عبور دو مرحله‌ای فعال کرده است ← labelled answer
  - ب) علی رمز عبور دو مرحله‌ای ندارد
  - پ) هیچ نتیجه‌ای نمی‌توان گرفت
  - ت) علی به سرور دسترسی ندارد

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Choice index 3 ('علی به سرور دسترسی ندارد') directly contradicts an explicit premise and is laughably wrong as a distractor, reducing item quality.
  - Difficulty is closer to 2 (trivial modus ponens) than 3.

**Proposed changes:**
```json
{
  "notes": "Replace choice index 3 with a plausible non-sequitur such as 'علی باید رمز عبور خود را تغییر دهد' to make it a more meaningful distractor. Adjust difficulty metadata from 3 to 2."
}
```

---

#### `peval-hard-reasoning-006`

**Prompt:** همه پزشکان دانشگاه‌رفته‌اند. مریم دانشگاه نرفته است. کدام نتیجه قطعی است؟

  - الف) مریم پزشک است
  - ب) مریم پزشک نیست ← labelled answer
  - پ) مریم ممکن است پزشک باشد
  - ت) هیچ نتیجه‌ای نمی‌توان گرفت

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=2, difficulty=3

**Issues:**
  - Minor orthographic issue: 'دانشگاه‌رفته‌اند' in the prompt uses an unexpected zero-width non-joiner making it read as a compound adjective rather than verb phrase; should be 'دانشگاه رفته‌اند'

**Proposed changes:**
```json
{
  "rewrite_prompt": "همه پزشکان دانشگاه رفته‌اند. مریم دانشگاه نرفته است. کدام نتیجه قطعی است؟",
  "notes": "The logic and answer are correct (valid modus tollens). Only fix needed is the spacing/ZWNJ issue in the prompt. Leakage risk is slightly elevated because modus tollens with this exact structure is a canonical textbook example, but the Persian phrasing is sufficiently original."
}
```

---

#### `peval-hard-reasoning-007`

**Prompt:** چهار نفر به نام‌های نازنین، بهرام، کاوه و سارا در صف ایستاده‌اند. نازنین دقیقا قبل از بهرام است. سارا آخرین نفر صف نیست. کاوه پشت سر بهرام است. ترتیب از اول به آخر کدام است؟

  - الف) نازنین، بهرام، کاوه، سارا
  - ب) بهرام، نازنین، کاوه، سارا
  - پ) نازنین، بهرام، سارا، کاوه ← labelled answer
  - ت) نازنین، سارا، بهرام، کاوه

**Rubric:** clarity=3, ambiguity=3, cultural_fit=5, leakage_risk=2, difficulty=3

**Issues:**
  - puzzle has two valid orderings: نازنین،بهرام،سارا،کاوه AND سارا،نازنین،بهرام،کاوه — both satisfy all three constraints
  - under-constrained puzzle; only works as MCQ because the second solution happens not to appear in choices
  - difficulty is overstated at 4; with the ambiguity it is closer to 3
  - کاوه پشت سر بهرام است is slightly ambiguous (immediately behind vs. anywhere behind), though context implies anywhere behind

**Proposed changes:**
```json
{
  "rewrite_prompt": "چهار نفر به نام‌های نازنین، بهرام، کاوه و سارا در صف ایستاده‌اند. نازنین دقیقاً قبل از بهرام است. سارا آخرین نفر صف نیست. کاوه پشت سر بهرام است. نازنین اول صف است. ترتیب از اول به آخر کدام است؟",
  "notes": "افزودن قید 'نازنین اول صف است' جواب را یکتا می‌کند و ابهام منطقی را برطرف می‌سازد. بدون این قید، ترتیب سارا،نازنین،بهرام،کاوه نیز معتبر است."
}
```

---

#### `peval-hard-reasoning-009`

**Prompt:** علی می‌گوید: «اگر فردا باران ببارد، در خانه می‌مانم.» فردا علی در خانه نماند. چه نتیجه قطعی می‌توان گرفت؟

  - الف) فردا باران نبارید ← labelled answer
  - ب) فردا باران بارید
  - پ) هیچ نتیجه‌ای نمی‌توان گرفت
  - ت) علی همیشه در خانه می‌ماند

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=3

**Issues:**
  - Choice 3 ('علی همیشه در خانه می‌ماند') is a laughably weak distractor that no test-taker would seriously consider; it does not probe any real logical misconception.
  - Only three distractors effectively test reasoning; replacing choice 3 with a more plausible foil would improve discrimination.

**Proposed changes:**
```json
{
  "notes": "Replace choice 3 with a more plausible distractor such as 'علی دروغ گفته است' (Ali lied) or 'ممکن است باران باریده باشد یا نباریده باشد' to better probe the common error of thinking the conditional can be violated without consequence. The correct answer and answer_index remain unchanged."
}
```

---

#### `peval-hard-reasoning-010`

**Prompt:** گروهی شامل شش دانش‌آموز است. سه نفر فوتبال بازی می‌کنند، چهار نفر شطرنج بازی می‌کنند، و دو نفر هر دو را بازی می‌کنند. چند نفر هیچ‌کدام را بازی نمی‌کنند؟

  - الف) صفر
  - ب) یک ← labelled answer
  - پ) دو
  - ت) سه

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=3, difficulty=2

**Issues:**
  - Difficulty is overrated at 4; this is a standard middle-school inclusion-exclusion problem, more like difficulty 2
  - Track placement in 'hard_reasoning' is inappropriate for a basic Venn diagram problem
  - The specific numbers (6, 3, 4, 2) are extremely common in textbook examples, raising leakage risk

**Proposed changes:**
```json
{
  "notes": "The answer is mathematically correct (5 play at least one, so 1 plays neither). However, this item should be moved to an easier track (e.g., 'reasoning' or 'math') and the difficulty metadata corrected to 2. Alternatively, to justify 'hard_reasoning' placement, the problem could be made more complex — e.g., adding a third activity, conditional constraints, or requiring multi-step deduction. The numbers should also be changed to reduce leakage risk."
}
```

---

#### `peval-hard-reasoning-012`

**Prompt:** یک قفسه پنج کتاب دارد. کتاب آبی دقیقا کنار کتاب قرمز است. کتاب سبز سمت چپ کتاب آبی نیست. کتاب زرد دقیقا در وسط است. اگر کتاب قرمز سمت چپ کتاب آبی باشد، کدام چینش ممکن است؟

  - الف) سبز، قرمز، زرد، آبی، سفید
  - ب) سفید، قرمز، آبی، زرد، سبز
  - پ) قرمز، آبی، زرد، سبز، سفید
  - ت) سفید، سبز، زرد، قرمز، آبی ← labelled answer

**Rubric:** clarity=4, ambiguity=1, cultural_fit=4, leakage_risk=2, difficulty=4

**Issues:**
  - Labeled answer (Choice D: سفید، سبز، زرد، قرمز، آبی) is INCORRECT — Green is at position 2 and Blue is at position 5, violating constraint 2 (Green must not be to the left of Blue)
  - Correct answer is Choice C (index 2): قرمز، آبی، زرد، سبز، سفید — satisfies all four constraints
  - Choice D also has Red=4, Blue=5 which is valid for adjacency/order, but fails the Green constraint
  - Difficulty rating of 5 is slightly inflated; this is a straightforward constraint-satisfaction puzzle, more like difficulty 3-4

**Proposed changes:**
```json
{
  "answer_replacement": "قرمز، آبی، زرد، سبز، سفید",
  "answer_index_replacement": 2,
  "notes": "The correct arrangement satisfying all constraints is Red=1, Blue=2, Yellow=3, Green=4, White=5 (Choice C, index 2). The labeled answer Choice D places Green at position 2 and Blue at position 5, which directly violates the constraint that Green is not to the left of Blue. answer_index should be changed from 3 to 2, and answer field updated accordingly."
}
```

---

#### `peval-hard-reasoning-013`

**Prompt:** اگر هر کس که زبان عربی می‌داند بتواند ترجمه کند و سینا بتواند ترجمه کند، آیا می‌توان نتیجه گرفت سینا زبان عربی می‌داند؟

  - الف) خیر، این نتیجه‌گیری نادرست است ← labelled answer
  - ب) بله، حتما
  - پ) بله، فقط در صورت وجود یک ترجمه کتبی
  - ت) هیچ نتیجه‌ای نمی‌توان گرفت

**Rubric:** clarity=4, ambiguity=3, cultural_fit=5, leakage_risk=2, difficulty=4

**Issues:**
  - Choice 0 ('این نتیجه‌گیری نادرست است') implies the conclusion is false, but logically the conclusion is merely unwarranted — Sina might still know Arabic
  - Choice 3 ('هیچ نتیجه‌ای نمی‌توان گرفت') is arguably more precise and defensible than the labeled answer, creating ambiguity between two correct-ish options
  - Slight grammatical awkwardness in 'هر کس که زبان عربی می‌داند بتواند ترجمه کند'

**Proposed changes:**
```json
{
  "rewrite_prompt": "اگر هر کسی که زبان عربی می‌داند بتواند ترجمه کند، و سینا بتواند ترجمه کند، آیا می‌توان نتیجه گرفت که سینا زبان عربی می‌داند؟",
  "notes": "Rewrite choice 0 to 'خیر، این استنتاج از نظر منطقی معتبر نیست' to clarify that the inference is invalid (not that the conclusion is necessarily false). Rewrite choice 3 to something clearly wrong, e.g., 'بله، چون سینا می‌تواند ترجمه کند پس حتماً عربی می‌داند' to eliminate the competing defensible distractor."
}
```

---

#### `peval-hard-reasoning-015`

**Prompt:** در یک جعبه ۳ توپ قرمز و ۲ توپ آبی است. اگر یک توپ بدون نگاه برداریم و آن توپ آبی نباشد، کدام جمله درست است؟

  - الف) توپ‌های جعبه باقی‌مانده ۲ قرمز و ۲ آبی است
  - ب) توپ‌های جعبه باقی‌مانده ۳ قرمز و ۱ آبی است
  - پ) توپ‌های جعبه باقی‌مانده ۲ قرمز و ۱ آبی است ← labelled answer
  - ت) توپ‌های جعبه باقی‌مانده ۳ قرمز و ۲ آبی است

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - labelled answer is WRONG: removing a non-blue (i.e. red) ball leaves 2 red + 2 blue, not 2 red + 1 blue
  - answer_index should be 0, not 2
  - difficulty is overstated — this is trivial conditional reasoning, not 'hard'
  - item is misclassified in 'hard' split given its actual difficulty

**Proposed changes:**
```json
{
  "answer_replacement": "توپ‌های جعبه باقی‌مانده ۲ قرمز و ۲ آبی است",
  "answer_index_replacement": 0,
  "notes": "The drawn ball is not blue, so it must be red. Starting with 3 red + 2 blue, removing 1 red leaves 2 red + 2 blue. The correct answer is choice index 0. The difficulty rating should be lowered to 2 and the item reconsidered for the 'hard' split."
}
```

---

#### `peval-hard-reasoning-016`

**Prompt:** اگر هر سه‌گوش متساوی‌الاضلاع متساوی‌الزاویه باشد و یک سه‌گوش متساوی‌الزاویه نباشد، آن سه‌گوش چه ویژگی قطعی دارد؟

  - الف) قائم‌الزاویه است
  - ب) متساوی‌الاضلاع هست
  - پ) نمی‌توان نتیجه گرفت
  - ت) متساوی‌الاضلاع نیست ← labelled answer

**Rubric:** clarity=4, ambiguity=1, cultural_fit=3, leakage_risk=2, difficulty=3

**Issues:**
  - استفاده از 'سه‌گوش' به جای 'مثلث' که در فارسی ریاضی ایران رایج‌تر است؛ این انتخاب واژگانی کمی غیرطبیعی به نظر می‌رسد
  - جمله‌بندی 'هر سه‌گوش متساوی‌الاضلاع متساوی‌الزاویه باشد' کمی ناهموار است و می‌توان آن را روان‌تر نوشت

**Proposed changes:**
```json
{
  "rewrite_prompt": "اگر هر مثلث متساوی‌الاضلاع، متساوی‌الزاویه باشد و یک مثلث متساوی‌الزاویه نباشد، آن مثلث چه ویژگی قطعی دارد؟",
  "notes": "جایگزینی 'سه‌گوش' با 'مثلث' برای انطباق با اصطلاح رایج در کتب درسی ریاضی ایران. منطق و پاسخ صحیح است (modus tollens). گزینه‌ها نیز باید با 'مثلث' به‌روزرسانی شوند."
}
```

---

#### `peval-hard-reasoning-020`

**Prompt:** اگر گزاره «هر کارمندی که آموزش امنیت دیده، می‌تواند به سامانه وصل شود» درست باشد، و حسن نتواند به سامانه وصل شود، چه نتیجه قطعی می‌گیریم؟

  - الف) نمی‌توان نتیجه گرفت
  - ب) حسن آموزش امنیت دیده ولی فراموش کرده
  - پ) حسن کارمند نیست
  - ت) حسن آموزش امنیت ندیده است ← labelled answer

**Rubric:** clarity=3, ambiguity=3, cultural_fit=5, leakage_risk=2, difficulty=3

**Issues:**
  - Labeled answer is logically incomplete: modus tollens yields ¬Employee(Hassan) ∨ ¬Trained(Hassan), not ¬Trained(Hassan) alone
  - Choice A ('نمی‌توان نتیجه گرفت') is arguably the most defensible answer under strict logic
  - Choice C ('حسن کارمند نیست') is equally defensible as Choice D
  - Missing premise: the question does not establish that Hassan is an employee

**Proposed changes:**
```json
{
  "rewrite_prompt": "اگر گزاره «هر کارمندی که آموزش امنیت دیده، می‌تواند به سامانه وصل شود» درست باشد، و حسن یک کارمند است ولی نمی‌تواند به سامانه وصل شود، چه نتیجه قطعی می‌گیریم؟",
  "notes": "Adding 'حسن یک کارمند است' as a premise makes the modus tollens unambiguous and Choice D (answer_index 3) the sole correct answer. Without this premise, the item is logically flawed and Choice A is defensible."
}
```

---

#### `peval-hard-reasoning-021`

**Prompt:** علی، بابک و سارا هر کدام یا فقط راست‌گو یا فقط دروغ‌گو هستند. علی می‌گوید: «بابک دروغ‌گوست.» بابک می‌گوید: «سارا راست‌گوست.» سارا می‌گوید: «من دروغ‌گو نیستم.» اگر دقیقا یک نفر دروغ‌گو باشد، چه کسی است؟

  - الف) بابک ← labelled answer
  - ب) علی
  - پ) سارا
  - ت) نمی‌توان تعیین کرد

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=4

**Issues:**
  - Labeled answer is WRONG: 'بابک' (index 0) is incorrect. Case analysis shows Babak as liar leads to contradiction (Babak's lie would make Sara a liar, giving two liars).
  - Correct answer is 'علی' (index 1): Ali as liar is the only self-consistent assignment under the exactly-one-liar constraint.
  - Difficulty rating of 5 is inflated; this is a standard 3-person liar puzzle, more appropriate at difficulty 4.

**Proposed changes:**
```json
{
  "answer_replacement": "علی",
  "answer_index_replacement": 1,
  "notes": "Full case analysis: (1) Ali=liar → consistent; (2) Babak=liar → Babak's statement 'Sara is truth-teller' is false → Sara is liar → two liars, contradiction; (3) Sara=liar → Ali's statement 'Babak is liar' must be true → Babak is liar → two liars, contradiction. Only Case 1 works. The answer and answer_index must be changed to علی and 1 respectively."
}
```

---

#### `peval-hard-reasoning-025`

**Prompt:** در یک کلاس ۲۰ نفری، حداقل هر دانش‌آموز یک ورزش دوست دارد. ۱۲ نفر فوتبال، ۹ نفر والیبال و ۵ نفر هر دو را دوست دارند. چند نفر فقط یکی از این دو ورزش را دوست دارند؟

  - الف) یازده ← labelled answer
  - ب) شانزده
  - پ) هفده
  - ت) نوزده

**Rubric:** clarity=3, ambiguity=2, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Internal inconsistency: 12 + 9 - 5 = 16, not 20, so the premise that all 20 students like at least one sport is violated
  - The 'حداقل هر دانش‌آموز یک ورزش دوست دارد' clause is either erroneous or misleading decoration
  - Distractors 'هفده' and 'نوزده' have no clear mathematical derivation, making them implausible
  - Difficulty is overrated at 4; this is a basic inclusion-exclusion problem (difficulty 2-3)
  - Answer is arithmetically correct (7+4=11) despite the inconsistent premise

**Proposed changes:**
```json
{
  "rewrite_prompt": "در یک کلاس، ۱۲ نفر فوتبال، ۹ نفر والیبال و ۵ نفر هر دو را دوست دارند. چند نفر فقط یکی از این دو ورزش را دوست دارند؟",
  "notes": "Remove the contradictory '20-student / at least one sport' premise since the numbers only support 16 students liking at least one sport. Alternatively, fix the numbers so they are consistent with 20 students (e.g., football=13, volleyball=11, both=4 → only one = 16, total = 20). Also replace 'هفده' and 'نوزده' with more mathematically motivated distractors such as 'شش' (football only) or 'چهار' (volleyball only). Reduce difficulty rating to 2."
}
```

---

### `instruction` — 9 items

#### `peval-public-instruction-007`

**Prompt:** یک جمله کوتاه فارسی بنویس که با «اگر» شروع شود و کلمه «تمرین» را داشته باشد. طول بین ۶ تا ۲۵ کلمه.

**Constraints:** `{"required_prefix": "اگر", "required_keywords": ["تمرین"], "min_words": 6, "max_words": 25}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty is overrated at 3; the task is trivial for any Persian speaker — a simple conditional sentence with one required word.
  - Scoring should clarify whether morphological variants of «تمرین» (e.g., «تمرین‌ها», «تمرین‌کردن») satisfy the keyword requirement.
  - min_words=6 is very low for a meaningful conditional sentence; could be raised to 7 or 8 to ensure non-trivial output.

**Proposed changes:**
```json
{
  "constraint_changes": {
    "min_words": 7
  },
  "notes": "The item is fundamentally sound. Difficulty should be corrected to 2. A minor tweak to min_words (6→7) ensures the output is a proper conditional clause rather than a fragment. Clarifying morphological variant acceptance for 'تمرین' in scoring notes would improve robustness."
}
```

---

#### `peval-public-instruction-015`

**Prompt:** یک متن سه‌جمله‌ای کوتاه برای معرفی یک کتاب موردعلاقه بنویس که شامل کلمه «داستان» باشد. طول بین ۱۵ تا ۴۵ کلمه.

**Constraints:** `{"required_keywords": ["داستان"], "min_words": 15, "max_words": 45}`

**Rubric:** clarity=4, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - The three-sentence requirement is stated in the prompt but not encoded as a metadata constraint (e.g., sentence_count: 3), so automated scoring cannot verify it.
  - Difficulty is overrated at 3; this is a simple creative task with loose constraints — 2 is more appropriate.
  - Ambiguity is slightly higher than 1 because the open topic ('یک کتاب موردعلاقه') means many valid outputs exist, though for instruction-following this is expected.

**Proposed changes:**
```json
{
  "constraint_changes": {
    "sentence_count": 3
  },
  "notes": "Add a sentence_count: 3 field to the answer/constraints block so automated scoring can verify the three-sentence requirement. Lower difficulty to 2. The rest of the item is well-formed and culturally natural."
}
```

---

#### `peval-public-instruction-016`

**Prompt:** یک پیام کوتاه برای رزرو یک قرار ملاقات کاری بنویس. پاسخ باید شامل «جلسه» و یک ساعت مشخص (مثل «ساعت ۱۰») باشد. از کلمه «شاید» استفاده نکن. حداکثر ۳۰ کلمه.

**Constraints:** `{"required_keywords": ["جلسه", "ساعت"], "forbidden": ["شاید"], "min_words": 8, "max_words": 30}`

**Rubric:** clarity=4, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - required_keywords includes 'ساعت' but the prompt requires a specific time expression (e.g., 'ساعت ۱۰'); a response with bare 'ساعت' would pass keyword check but not fully satisfy the prompt's intent
  - difficulty is overrated at 3; this is a simple, low-stakes instruction-following task closer to 2
  - The prompt mentions 'یک ساعت مشخص' but the keyword check cannot verify the digit/number following 'ساعت' — consider adding a note or adjusting the required_keywords to better capture this

**Proposed changes:**
```json
{
  "rewrite_prompt": "یک پیام کوتاه برای رزرو یک قرار ملاقات کاری بنویس. پاسخ باید شامل کلمه «جلسه» و یک ساعت مشخص (مثل «ساعت ۱۰» یا «ساعت ۱۴:۳۰») باشد. از کلمه «شاید» استفاده نکن. حداکثر ۳۰ کلمه.",
  "notes": "The core constraint structure is sound and jointly satisfiable. The main issue is that 'ساعت' as a standalone keyword cannot enforce that a specific time number follows it. Since automated keyword-matching cannot easily check for a numeral after 'ساعت', the item should either accept this limitation explicitly or add a note for human reviewers to verify the time specificity. Difficulty should be lowered to 2."
}
```

---

#### `peval-public-instruction-018`

**Prompt:** یک پیام تبریک کوتاه برای موفقیت یک دوست بنویس که با «تبریک» شروع شود و با «است» تمام شود. حداکثر ۲۰ کلمه.

**Constraints:** `{"required_prefix": "تبریک", "required_suffix": "است", "min_words": 5, "max_words": 20}`

**Rubric:** clarity=4, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - min_words=5 is not mentioned in the prompt; the model is not told there is a minimum word count
  - difficulty is overrated at 3; this is a straightforward task for any fluent Persian speaker, closer to 2
  - ambiguity is slightly underrated at 1; while constraints are clear, the open-ended creative nature means many valid outputs exist (expected for instruction tasks, but worth noting)

**Proposed changes:**
```json
{
  "rewrite_prompt": "یک پیام تبریک کوتاه برای موفقیت یک دوست بنویس که با «تبریک» شروع شود و با «است» تمام شود. حداقل ۵ کلمه و حداکثر ۲۰ کلمه.",
  "notes": "The only concrete fix needed is adding the minimum word count to the prompt so the model is aware of all constraints. Difficulty should be lowered to 2. The item is otherwise well-formed and the constraints are jointly satisfiable in natural Persian."
}
```

---

#### `peval-public-instruction-019`

**Prompt:** یک یادداشت کوتاه برای آشپز خانه بنویس که سفارش غذای فردا را توضیح می‌دهد. باید کلمه «ناهار» و کلمه «ساعت» را داشته باشد. طول بین ۱۰ تا ۳۰ کلمه.

**Constraints:** `{"required_keywords": ["ناهار", "ساعت"], "min_words": 10, "max_words": 30}`

**Rubric:** clarity=4, ambiguity=1, cultural_fit=4, leakage_risk=1, difficulty=2

**Issues:**
  - 'آشپز خانه' is ambiguous — with a space it could mean 'home cook' rather than 'kitchen' (آشپزخانه) or 'cook/chef' (آشپز); the intended recipient is unclear
  - Difficulty rated 3 but the task is straightforward (two common keywords, generous word range); difficulty 2 is more appropriate
  - Cultural fit slightly reduced due to the orthographic ambiguity in 'آشپز خانه'

**Proposed changes:**
```json
{
  "rewrite_prompt": "یک یادداشت کوتاه برای آشپز بنویس که سفارش غذای فردا را توضیح می‌دهد. باید کلمه «ناهار» و کلمه «ساعت» را داشته باشد. طول بین ۱۰ تا ۳۰ کلمه.",
  "notes": "Changed 'آشپز خانه' to 'آشپز' to remove orthographic and semantic ambiguity. The difficulty metadata should be updated to 2."
}
```

---

#### `peval-public-instruction-020`

**Prompt:** یک جمله درباره فایده زود خوابیدن بنویس که با «اگر» شروع شود و با «بهتر است» پایان یابد. حداکثر ۲۰ کلمه.

**Constraints:** `{"required_prefix": "اگر", "required_suffix": "بهتر است", "min_words": 6, "max_words": 20}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty rating of 3 is inflated; this is a simple sentence-construction task, difficulty 2 is more appropriate
  - required_suffix «بهتر است» may fail if model appends punctuation (e.g., «بهتر است.»); scoring logic should strip trailing punctuation
  - min_words of 6 is very low relative to the topic; could be raised to 8 for more meaningful sentences

**Proposed changes:**
```json
{
  "constraint_changes": {
    "min_words": 8
  },
  "notes": "Item is fundamentally sound and constraints are jointly satisfiable. Main issues are: (1) difficulty should be 2 not 3; (2) scoring system must normalize trailing punctuation before checking required_suffix; (3) min_words could be raised slightly to 8 to ensure non-trivial responses. No fundamental problems."
}
```

---

#### `peval-public-instruction-022`

**Prompt:** یک متن کوتاه راهنما برای استفاده از یک نان‌توستر بنویس. باید مرحله‌ای باشد و حداقل سه فعل امری داشته باشد. طول بین ۱۵ تا ۴۵ کلمه. از کلمه «خطر» استفاده نکن.

**Constraints:** `{"required_keywords": ["نان"], "forbidden": ["خطر"], "min_words": 15, "max_words": 45}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - The `answer` metadata does not encode the '≥3 imperative verbs' constraint or the 'step-by-step' requirement — automated scoring will miss these key structural requirements.
  - Difficulty is slightly lower than rated (2 rather than 3) since the task is straightforward for a competent Persian writer.
  - No mechanism in the scoring schema to verify imperative verb count; evaluator must handle this manually or via LLM judge.

**Proposed changes:**
```json
{
  "notes": "The item is functionally sound and the constraints are satisfiable, but the scoring metadata is incomplete: 'min_imperative_verbs: 3' and a 'step_by_step: true' flag (or equivalent) should be added to the answer object so automated/LLM evaluators have explicit criteria to check. Without this, the two most important constraints in the prompt are invisible to the scorer. A simple fix is to add these as additional fields or document them in a 'notes' field within the answer schema. No rewrite of the prompt itself is needed."
}
```

---

#### `peval-public-instruction-025`

**Prompt:** یک جمله کوتاه درباره فایده یادگیری زبان دوم بنویس که شامل کلمه «فرصت» باشد. از کلمه «همیشه» استفاده نکن. حداکثر ۳۰ کلمه.

**Constraints:** `{"required_keywords": ["فرصت"], "forbidden": ["همیشه"], "min_words": 7, "max_words": 30}`

**Rubric:** clarity=4, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - min_words: 7 is not stated in the prompt — the model is unaware of this constraint, creating a hidden evaluation criterion
  - difficulty is overrated at 3; constraints are minimal and non-conflicting, making this a trivially easy task
  - prompt says 'یک جمله کوتاه' (one short sentence) but max_words is 30, which could allow multi-sentence responses — slight ambiguity

**Proposed changes:**
```json
{
  "constraint_changes": {
    "min_words": null
  },
  "rewrite_prompt": "یک جمله کوتاه (حداقل ۷ کلمه) درباره فایده یادگیری زبان دوم بنویس که شامل کلمه «فرصت» باشد. از کلمه «همیشه» استفاده نکن. حداکثر ۳۰ کلمه.",
  "notes": "Adding the min_words constraint explicitly to the prompt removes the hidden evaluation criterion. Difficulty should be lowered to 2. Alternatively, if min_words is removed from the answer spec entirely (since any valid sentence will exceed 7 words), the prompt can remain as-is."
}
```

---

#### `peval-public-instruction-026`

**Prompt:** یک پاسخ کوتاه و مودب برای رد یک دعوت ناهار بنویس. باید شامل «ممنون» و یک علت کوتاه باشد. حداکثر ۲۰ کلمه.

**Constraints:** `{"required_keywords": ["ممنون"], "min_words": 6, "max_words": 20}`

**Rubric:** clarity=5, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - The prompt requires 'یک علت کوتاه' (a short reason) but this constraint is not captured in required_keywords or any formal scoring field — a response with only 'ممنون' + filler could pass automated checks without providing a reason.
  - Difficulty is overrated at 3; this is a simple everyday social task, more like 2.
  - No 'forbidden' list, which is fine, but the gap between prose constraints and formal scoring constraints may cause inconsistent evaluation.

**Proposed changes:**
```json
{
  "constraint_changes": {
    "max_words": 20,
    "min_words": 8
  },
  "rewrite_prompt": "یک پاسخ کوتاه و مودب برای رد یک دعوت ناهار بنویس. باید شامل «ممنون» و یک علت کوتاه (مثلاً کار، قرار قبلی، یا مشغله) باشد. حداکثر ۲۰ کلمه.",
  "notes": "Consider adding a second required keyword such as 'متأسفانه' or 'نمی‌تونم' to better enforce the 'reason' requirement in automated scoring. Raising min_words to 8 also nudges responses toward including a reason. Difficulty adjusted to 2."
}
```

---

### `knowledge` — 18 items

#### `peval-public-knowledge-006`

**Prompt:** کدام کشور همسایه شرقی ایران است؟

  - الف) ترکیه
  - ب) افغانستان ← labelled answer
  - پ) ارمنستان
  - ت) آذربایجان

**Rubric:** clarity=4, ambiguity=2, cultural_fit=5, leakage_risk=4, difficulty=2

**Issues:**
  - Pakistan is also an eastern neighbor of Iran, making the question technically ambiguous outside the MCQ context
  - Difficulty rated 3 but this is basic school-level geography, should be 1–2
  - Leakage risk rated 1 but this is a very common textbook/quiz question, should be 3–4
  - Question phrasing implies a unique answer; better to frame as 'which of the following'

**Proposed changes:**
```json
{
  "rewrite_prompt": "کدام یک از گزینه‌های زیر همسایه شرقی ایران است؟",
  "notes": "Answer (افغانستان) is correct among the given choices. Main issues are difficulty and leakage_risk metadata values being miscalibrated, and minor phrasing ambiguity since Pakistan is also an eastern neighbor but not listed as a choice."
}
```

---

#### `peval-public-knowledge-008`

**Prompt:** دریاچه ارومیه در کدام منطقه ایران قرار دارد؟

  - الف) مرکز
  - ب) جنوب
  - پ) شرق
  - ت) شمال‌غرب ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Difficulty overestimated at 3; Lake Urmia is one of Iran's most famous landmarks and its northwestern location is widely known, especially given extensive media coverage of its environmental crisis
  - Slight leakage risk as this is a classic Iranian school geography exam question

**Proposed changes:**
```json
{
  "notes": "The item is factually correct and well-constructed. Only metadata adjustment needed: lower difficulty from 3 to 2. Leakage risk bumped to 2 due to its prevalence in school exams. All other aspects are solid."
}
```

---

#### `peval-public-knowledge-009`

**Prompt:** کوه دماوند در کدام رشته‌کوه قرار دارد؟

  - الف) البرز ← labelled answer
  - ب) زاگرس
  - پ) هندوکش
  - ت) کپه‌داغ

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Difficulty overrated at 3; this is elementary-school knowledge in Iran, should be 2
  - Leakage risk slightly elevated — this exact question appears commonly in Iranian school curricula and online quizzes

**Proposed changes:**
```json
{
  "notes": "Only metadata adjustment needed: lower difficulty from 3 to 2. The item itself is factually correct and well-formed. Consider whether a more nuanced geography question about Damavand (e.g., its geological type, height ranking, or location within the Alborz sub-ranges) would better suit difficulty level 3."
}
```

---

#### `peval-public-knowledge-010`

**Prompt:** ماه پایانی فصل تابستان در تقویم هجری شمسی چیست؟

  - الف) مرداد
  - ب) شهریور ← labelled answer
  - پ) مهر
  - ت) تیر

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty is rated 3 in metadata but this is trivial elementary-school knowledge; should be 2

**Proposed changes:**
```json
{
  "notes": "The answer (شهریور) is correct and all distractors are legitimate. Only change needed is lowering the difficulty rating from 3 to 2 in the metadata rubric."
}
```

---

#### `peval-public-knowledge-011`

**Prompt:** آذر چندمین ماه تقویم هجری شمسی است؟

  - الف) هشتم
  - ب) دهم
  - پ) نهم ← labelled answer
  - ت) یازدهم

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - difficulty rated 3 but this is basic calendar knowledge known to virtually all Persian speakers; 2 is more appropriate

**Proposed changes:**
```json
{
  "notes": "The answer and distractors are correct. Only the difficulty metadata needs adjustment from 3 to 2. All distractors are plausible adjacent months, which is good design."
}
```

---

#### `peval-public-knowledge-012`

**Prompt:** اولین روز فصل پاییز در تقویم هجری شمسی معمولا در کدام ماه است؟

  - الف) شهریور
  - ب) آذر
  - پ) آبان
  - ت) مهر ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - The word 'معمولاً' is inaccurate — the first day of autumn is always (not 'usually') the first of Mehr in the Shamsi calendar
  - Difficulty is overrated at 3; this is basic common knowledge for Iranian adults

**Proposed changes:**
```json
{
  "rewrite_prompt": "اولین روز فصل پاییز در تقویم هجری شمسی در کدام ماه است؟",
  "notes": "Removing 'معمولاً' makes the question factually precise. Difficulty should be lowered to 2. The answer and answer_index remain correct."
}
```

---

#### `peval-public-knowledge-014`

**Prompt:** نماد شیمیایی Au به کدام عنصر اشاره دارد؟

  - الف) نقره
  - ب) طلا ← labelled answer
  - پ) مس
  - ت) آهن

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=4, difficulty=2

**Issues:**
  - Leakage risk is underestimated — Au=Gold is one of the most classic chemistry trivia questions and this exact format appears widely in Persian educational/quiz content
  - Difficulty overestimated at 3; Au→Gold is among the most commonly known chemical symbols and should be rated 2

**Proposed changes:**
```json
{
  "rewrite_prompt": "عنصر شیمیایی با نماد Au و عدد اتمی ۷۹ چه نام دارد و در کدام گروه جدول تناوبی قرار می‌گیرد؟",
  "notes": "If leakage is a concern, the prompt could be made more specific (e.g., referencing atomic number or group) to reduce overlap with scraped quiz content. Alternatively, the item can be accepted as-is if the benchmark tolerates well-known factual questions, but leakage_risk and difficulty metadata should be corrected."
}
```

---

#### `peval-public-knowledge-016`

**Prompt:** سرعت نور در خلا تقریبا چقدر است؟

  - الف) سیصد کیلومتر بر ثانیه
  - ب) سه‌هزار کیلومتر بر ثانیه
  - پ) سی‌میلیون کیلومتر بر ثانیه
  - ت) سیصد هزار کیلومتر بر ثانیه ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=2

**Issues:**
  - Difficulty is overrated at 3; this is basic middle-school science knowledge, more appropriate at 2.
  - Leakage risk is non-trivial: speed-of-light MCQ questions are extremely common on Persian educational websites.

**Proposed changes:**
```json
{
  "notes": "The answer and distractors are correct. Only metadata adjustments needed: difficulty should be lowered to 2, and leakage_risk should be raised to 3. The item is otherwise acceptable."
}
```

---

#### `peval-public-knowledge-017`

**Prompt:** کدام پروتکل پایه‌ای انتقال صفحه‌های وب در اینترنت است؟

  - الف) HTTP ← labelled answer
  - ب) FTP
  - پ) SMTP
  - ت) IMAP

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=1

**Issues:**
  - Difficulty is overrated at 3; this is basic/trivial knowledge (HTTP for web pages is taught at introductory level)
  - Leakage risk is higher than 1 — this exact question format is extremely common in Persian tech quizzes and educational materials
  - Item is too easy to provide meaningful discrimination among test-takers with any tech background

**Proposed changes:**
```json
{
  "rewrite_prompt": "کدام پروتکل برای انتقال امن صفحه‌های وب (HTTPS) به‌عنوان نسخه رمزنگاری‌شده HTTP استفاده می‌شود و از کدام لایه امنیتی بهره می‌برد؟",
  "notes": "The current item is too trivial for a benchmark. Either increase difficulty by asking about HTTPS/TLS, HTTP versions (HTTP/2 vs HTTP/3), or status codes, or accept the item as-is but correct the difficulty metadata to 1. The rewrite_prompt suggestion is optional — at minimum, difficulty should be corrected to 1 in metadata."
}
```

---

#### `peval-public-knowledge-018`

**Prompt:** زبان نشانه‌گذاری اصلی برای ساخت ساختار صفحه‌های وب کدام است؟

  - الف) CSS
  - ب) HTML ← labelled answer
  - پ) JSON
  - ت) XML

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=3, difficulty=1

**Issues:**
  - Difficulty is rated 3 but the question is trivially easy — HTML as the web markup language is among the most basic tech facts known even to non-developers
  - Leakage risk is underestimated; this exact question type is ubiquitous in online quizzes and introductory web courses

**Proposed changes:**
```json
{
  "notes": "The item is factually correct and well-formed. Only metadata needs updating: difficulty should be lowered to 1 (trivial) and leakage_risk raised to 3. Consider replacing with a harder web-technology question (e.g., about semantic HTML5 elements, ARIA roles, or the DOM) to add more value to the benchmark."
}
```

---

#### `peval-public-knowledge-020`

**Prompt:** کدام واحد ذخیره‌سازی از کیلوبایت کوچک‌تر است؟

  - الف) مگابایت
  - ب) گیگابایت
  - پ) ترابایت
  - ت) بایت ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=1

**Issues:**
  - difficulty is trivially easy (1), not 3 as marked in existing rubric
  - leakage risk is slightly elevated as this is a very standard textbook question

**Proposed changes:**
```json
{
  "notes": "The answer and distractors are all correct. The only issue is the difficulty metadata is overrated — this is a level-1 trivial question. Consider replacing with a harder storage-unit question (e.g., involving bits, nibbles, or conversion calculations) to make it more useful as a benchmark item."
}
```

---

#### `peval-public-knowledge-023`

**Prompt:** شاهنامه اثر کدام شاعر است؟

  - الف) سعدی
  - ب) نظامی
  - پ) فردوسی ← labelled answer
  - ت) خاقانی

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=4, difficulty=1

**Issues:**
  - difficulty is severely overrated — this is the most elementary fact in Persian literary education, known by every schoolchild
  - leakage_risk is severely underrated — this exact question appears verbatim in countless Persian educational quizzes and textbooks online
  - item has very low discriminative value for a benchmark; nearly all respondents (human or model) will answer correctly

**Proposed changes:**
```json
{
  "rewrite_prompt": "فردوسی در شاهنامه برای سرودن کدام بخش از داستان‌های حماسی بیشترین تعداد بیت را اختصاص داده است؟",
  "notes": "The current item is factually correct but trivially easy and highly likely to be contaminated from public sources. If the goal is to test Persian literary knowledge at a meaningful difficulty level, the prompt should be revised to ask something less universally known — for example, about the content, structure, or specific episodes of the Shahnameh. The proposed rewrite increases difficulty while staying on topic. Alternatively, the item could be kept as a warm-up/anchor item if the benchmark intentionally includes easy items, but difficulty metadata must be corrected to 1."
}
```

---

#### `peval-public-knowledge-024`

**Prompt:** مثنوی معنوی اثر کدام شاعر است؟

  - الف) هاتف
  - ب) عطار
  - پ) رودکی
  - ت) مولوی ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=4, difficulty=1

**Issues:**
  - Difficulty is vastly overrated at 3; this is one of the most elementary facts in Persian literature education (difficulty 1).
  - Leakage risk is high — this exact question appears in countless public Persian literature quizzes and school exam banks.
  - هاتف is a weak distractor with no plausible connection to Masnavi Ma'navi; a stronger distractor (e.g., سنایی or نظامی) would improve item quality.
  - The question is trivially easy for any Persian speaker with basic schooling, reducing its discriminative value.

**Proposed changes:**
```json
{
  "notes": "Replace هاتف with a stronger distractor such as سنایی (who also wrote masnavis with mystical themes) to improve item quality. Update difficulty to 1. Consider rewriting the prompt with slightly different wording to reduce leakage risk, e.g., 'کدام شاعر سراینده مثنوی معنوی است؟' — though this alone won't substantially reduce leakage for such a canonical fact."
}
```

---

#### `peval-public-knowledge-026`

**Prompt:** رود کارون عمدتا در کدام استان جریان دارد؟

  - الف) گلستان
  - ب) خوزستان ← labelled answer
  - پ) گیلان
  - ت) همدان

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - difficulty is overrated — Karun/Khuzestan association is well-known general knowledge, not medium difficulty
  - leakage_risk slightly underrated — basic geography MCQs of this form are common in Iranian school exams and online quizzes

**Proposed changes:**
```json
{
  "notes": "The answer is correct and distractors are all valid. Only metadata adjustments needed: lower difficulty to 2 and raise leakage_risk to 2. The question is otherwise well-formed and idiomatic."
}
```

---

#### `peval-public-knowledge-027`

**Prompt:** یک ربع ساعت چند دقیقه است؟

  - الف) پنج
  - ب) ده
  - پ) پانزده ← labelled answer
  - ت) بیست

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=1

**Issues:**
  - Difficulty is overrated at 3; this is a trivially easy primary-school fact and should be rated 1.
  - Leakage risk is slightly higher than 1 since this exact phrasing is a very common textbook question.

**Proposed changes:**
```json
{
  "notes": "The answer and distractors are correct. Only the difficulty metadata needs correction from 3 to 1. The item is otherwise acceptable."
}
```

---

#### `peval-public-knowledge-028`

**Prompt:** کدام جانور پستاندار است؟

  - الف) مار
  - ب) قورباغه
  - پ) تمساح
  - ت) نهنگ ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=4, difficulty=1

**Issues:**
  - Difficulty is trivially low (elementary school level), not a 3 as rated
  - High leakage risk — this exact question format is ubiquitous in Persian educational materials and online quizzes
  - As a benchmark item, it provides little discriminative power for evaluating model knowledge

**Proposed changes:**
```json
{
  "rewrite_prompt": "کدام یک از جانوران زیر پستاندار دریایی محسوب می‌شود و برای تنفس باید به سطح آب بیاید؟",
  "notes": "Either increase difficulty by replacing distractors with more confusing options (e.g., خفاش دریایی، دلفین، فک vs. نهنگ — though all are mammals, so that won't work), or replace the entire question with a harder biology question. Alternatively, keep the question but adjust difficulty metadata to 1–2 and accept the low difficulty as intentional for coverage purposes."
}
```

---

#### `peval-public-knowledge-029`

**Prompt:** در کدام عنصر، پیشوند «اکسی» به‌طور غالب در نام ترکیب‌ها دیده می‌شود؟

  - الف) اکسیژن ← labelled answer
  - ب) کربن
  - پ) نیتروژن
  - ت) گوگرد

**Rubric:** clarity=3, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - سوال تقریباً دوری (tautological) است: پیشوند «اکسی» مستقیماً از «اکسیژن» گرفته شده، پس پاسخ بدیهی است
  - سطح دشواری بیش از حد ارزیابی شده؛ واقعاً سطح ۱-۲ است نه ۳
  - عبارت «به‌طور غالب» مبهم است — آیا منظور فراوانی ترکیبات است یا ریشه‌شناسی نام؟
  - سوال می‌تواند با بازنویسی به چیز آموزنده‌تری تبدیل شود

**Proposed changes:**
```json
{
  "rewrite_prompt": "پیشوند «اکسی» در نام‌گذاری ترکیبات شیمیایی معمولاً نشان‌دهنده حضور کدام عنصر در ساختار مولکول است؟",
  "notes": "بازنویسی پیشنهادی سوال را کمتر دوری می‌کند و به جای تکیه بر ریشه‌شناسی واضح، بر مفهوم شیمیایی تمرکز می‌کند. همچنین سطح دشواری باید به ۲ تصحیح شود."
}
```

---

#### `peval-public-knowledge-030`

**Prompt:** آیا گزاره زیر درست است؟ «خط استوا از داخل خاک ایران می‌گذرد.»

  - الف) درست است
  - ب) نادرست است ← labelled answer
  - پ) تنها از جزیره‌های جنوبی می‌گذرد
  - ت) تنها از خلیج فارس می‌گذرد

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty is rated 3 but the fact that Iran is in the Northern Hemisphere far from the equator is basic geography, warranting a difficulty of 2

**Proposed changes:**
```json
{
  "notes": "Only change needed is lowering difficulty from 3 to 2 in the metadata rubric. The answer, distractors, and phrasing are all correct and appropriate."
}
```

---

### `reading` — 26 items

#### `peval-public-reading-005`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: نسرین صبح به آزمایشگاه رفت تا نمونه‌ی آبی را که از رودخانه گرفته بود بررسی کند. او می‌خواست بفهمد چرا ماهی‌های منطقه کم شده‌اند. بعد از چند ساعت آزمایش، نتیجه نشان داد که اکسیژن محلول در آب پایین است. نسرین...

**Accepted answers:** ['شهرداری', 'برای شهرداری']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty is overrated at 3; this is a direct verbatim lookup with no inference, more appropriate at 1–2
  - Answer list missing 'به شهرداری' as a natural alternative phrasing in Persian

**Proposed changes:**
```json
{
  "answer_additions": [
    "به شهرداری",
    "شهرداری شهر"
  ],
  "notes": "The item is otherwise well-formed. The only substantive fix needed is adding 'به شهرداری' to the accepted answers list and correcting the difficulty metadata from 3 to 2 (or even 1), since the answer is a direct copy from the last sentence of the passage with no inference required."
}
```

---

#### `peval-public-reading-006`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: کیان هر شب پیش از خواب کمی کتاب می‌خواند تا ذهنش از کارهای روز فاصله بگیرد. او متوجه شد در روزهایی که این کار را انجام می‌دهد، صبح راحت‌تر بیدار می‌شود. سوال: کیان متوجه چه نتیجه‌ای از خواندن شبانه شد؟

**Accepted answers:** ['راحت\u200cتر بیدار شدن صبح', 'بیدار شدن آسان\u200cتر در صبح']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty is overrated at 3; this is a direct recall question where the answer is nearly verbatim in the text — should be 1 or 2
  - Answer list is missing the near-verbatim phrase from the passage ('صبح راحت‌تر بیدار می‌شود') and other natural Persian variants
  - Answer list missing 'بیدار شدن راحت‌تر در صبح' and 'راحت‌تر بیدار شدن در صبح' as valid F1 targets

**Proposed changes:**
```json
{
  "answer_additions": [
    "صبح راحت‌تر بیدار می‌شود",
    "بیدار شدن راحت‌تر در صبح",
    "راحت‌تر بیدار شدن در صبح",
    "در صبح راحت‌تر بیدار می‌شود"
  ],
  "notes": "The item is fundamentally sound but the difficulty metadata should be corrected to 2 (trivial-to-easy), and the answer list should include the near-verbatim phrase from the source text to ensure fair F1 scoring for responses that quote the passage directly."
}
```

---

#### `peval-public-reading-007`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: روستای پیرانه چند سال پیش بدون آب لوله‌کشی بود. اهالی با کمک گروهی داوطلب، چاه عمیقی حفر کردند و لوله‌ها را تا خانه‌ها رساندند. حالا همه به آب سالم دسترسی دارند. سوال: مشکل اصلی روستا پیش از این کار چه بود؟

**Accepted answers:** ['نبود آب لوله\u200cکشی', 'نداشتن آب لوله\u200cکشی']

**Rubric:** clarity=5, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty overrated at 3; answer is nearly verbatim in the text, should be 1–2
  - answer list incomplete — several natural Persian phrasings missing
  - mild ambiguity: 'نداشتن آب سالم' is also defensible from the passage's closing sentence and should be accepted
  - 'نداشتن آب' (simplified) is a plausible short answer that F1 scoring might penalize unfairly if not listed

**Proposed changes:**
```json
{
  "answer_additions": [
    "فقدان آب لوله‌کشی",
    "نداشتن آب سالم",
    "نبود آب سالم",
    "دسترسی نداشتن به آب لوله‌کشی",
    "نداشتن آب"
  ],
  "notes": "Item is fundamentally sound and the passage is well-written. Main fixes needed: (1) lower difficulty to 2, (2) expand answer list to cover natural paraphrases including 'نداشتن آب سالم' which is implied by the text's final sentence. Ambiguity bumped to 2 because of this secondary defensible answer."
}
```

---

#### `peval-public-reading-008`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: مهسا یک کارگاه کوچک سفال دارد. او ابتدا گل را ورز می‌دهد، بعد آن را روی چرخ شکل می‌دهد و در نهایت ظرف‌ها را در کوره می‌پزد. سوال: گام پایانی در کار مهسا چیست؟

**Accepted answers:** ['پختن ظرف\u200cها در کوره', 'پختن در کوره']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty overestimated — answer is directly signalled by 'در نهایت', making this trivial extraction
  - answer list missing common short-form and nominal variants

**Proposed changes:**
```json
{
  "answer_additions": [
    "پختن ظرف‌ها",
    "پخت ظرف‌ها در کوره",
    "پخت در کوره",
    "قرار دادن ظرف‌ها در کوره"
  ],
  "notes": "Item is otherwise well-formed. The passage is clean and culturally natural. Difficulty should be lowered to 2 since the final step is explicitly flagged with 'در نهایت'. Adding nominal form 'پخت' variants improves F1 scoring robustness."
}
```

---

#### `peval-public-reading-009`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک باغبان جوان متوجه شد در گوشه‌ای از باغ، گل‌ها زودتر از بقیه پژمرده می‌شوند. او بررسی کرد و دید آن گوشه آفتاب کمتری می‌گیرد. سوال: علت پژمرده شدن زودتر گل‌ها چه بود؟

**Accepted answers:** ['کم بودن آفتاب', 'نور آفتاب کم']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Answer list is too narrow for F1 scoring — many natural Persian phrasings are missing
  - Difficulty rated 3 but the answer is explicitly stated in the text with zero inference required; should be 1 or 2
  - F1 scoring requires broader coverage of synonymous expressions to avoid penalizing correct but differently-phrased answers

**Proposed changes:**
```json
{
  "answer_additions": [
    "کمبود نور آفتاب",
    "کمبود آفتاب",
    "نگرفتن آفتاب کافی",
    "آفتاب کافی نگرفتن",
    "دریافت نکردن آفتاب کافی",
    "نور کم",
    "کم بودن نور",
    "آفتاب کم"
  ],
  "notes": "The item is fundamentally sound but needs a richer answer set for F1 evaluation. Difficulty should be lowered to 1 or 2 since the cause is directly and explicitly stated in the passage — no inference or reasoning is needed."
}
```

---

#### `peval-public-reading-010`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک شرکت کوچک تصمیم گرفت برای کاهش هزینه‌ها، جلسه‌های هفتگی را به صورت آنلاین برگزار کند. بعد از سه ماه، هزینه ایاب و ذهاب به نصف رسید. سوال: تصمیم شرکت چه اثری بر هزینه‌ها داشت؟

**Accepted answers:** ['نصف شدن هزینه ایاب و ذهاب', 'نصف شدن هزینه\u200cهای جابه\u200cجایی']

**Rubric:** clarity=5, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Answer list is incomplete — many natural Persian phrasings of the same answer are missing
  - Difficulty is overrated at 3; the answer is nearly verbatim in the text, making this trivial (should be 1–2)
  - Mild ambiguity: question asks about 'هزینه‌ها' broadly, but text only specifies travel costs; a general answer like 'هزینه‌ها کاهش یافت' could be considered partially correct
  - Direct quote from text ('هزینه ایاب و ذهاب به نصف رسید') is not in the answer list but should be accepted

**Proposed changes:**
```json
{
  "answer_additions": [
    "هزینه ایاب و ذهاب به نصف رسید",
    "هزینه‌های رفت و آمد نصف شد",
    "کاهش ۵۰ درصدی هزینه ایاب و ذهاب",
    "هزینه‌های سفر نصف شد",
    "هزینه رفت و آمد به نصف کاهش یافت",
    "هزینه‌های ایاب و ذهاب کاهش یافت"
  ],
  "notes": "The answer list needs expansion to cover natural paraphrases. Difficulty should be lowered to 2 since the answer is almost directly quoted from the passage. The question wording 'چه اثری بر هزینه‌ها داشت' is slightly broader than what the text supports (only travel costs are mentioned), which introduces minor ambiguity."
}
```

---

#### `peval-public-reading-011`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: ساسان همیشه دیر به مدرسه می‌رسید. معلمش پیشنهاد کرد لباس‌های روز بعد را شب قبل آماده کند. ساسان این کار را انجام داد و از هفته بعد به‌موقع به کلاس رسید. سوال: راه‌حلی که معلم پیشنهاد کرد چه بود؟

**Accepted answers:** ['آماده کردن لباس شب قبل', 'آماده کردن لباس\u200cها در شب پیش']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Answer list is incomplete — several natural Persian paraphrases of the correct answer are missing
  - Difficulty is overrated at 3; the answer is directly stated in the text with no inference required, making this a 2

**Proposed changes:**
```json
{
  "answer_additions": [
    "لباس‌های روز بعد را شب قبل آماده کردن",
    "شب قبل لباس‌ها را آماده کردن",
    "آماده کردن لباس برای روز بعد در شب قبل",
    "آماده کردن لباس‌های فردا در شب",
    "شب قبل لباس آماده کردن"
  ],
  "notes": "The item is fundamentally sound but the F1 answer set needs expansion to cover natural paraphrases. Difficulty should be lowered to 2 since the answer is verbatim in the passage."
}
```

---

#### `peval-public-reading-012`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک پژوهشگر دید که در خانه‌هایی که گیاه آپارتمانی وجود دارد، رطوبت هوا کمی بیشتر است. او این موضوع را در یک مقاله کوتاه گزارش کرد. سوال: یافته اصلی پژوهشگر چه بود؟

**Accepted answers:** ['بالاتر بودن رطوبت در خانه\u200cهای دارای گیاه', 'افزایش رطوبت در خانه\u200cهای با گیاه']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty is overrated at 3; the answer is directly stated in the passage, making this trivially easy (difficulty 1–2)
  - Answer list is incomplete — missing common Persian paraphrases of the finding
  - Neither answer preserves the 'کمی' (slightly) qualifier from the original text, which could affect F1 matching

**Proposed changes:**
```json
{
  "answer_additions": [
    "خانه‌هایی که گیاه آپارتمانی دارند رطوبت هوای کمی بیشتری دارند",
    "رطوبت هوا در خانه‌های دارای گیاه آپارتمانی کمی بالاتر است",
    "خانه‌هایی با گیاه رطوبت بیشتری دارند",
    "وجود گیاه در خانه با رطوبت بیشتر هوا همراه است"
  ],
  "notes": "The item is fundamentally sound but the difficulty should be lowered to 2 since the answer is a near-verbatim restatement of the passage. The answer list should be expanded to include phrasings that retain the 'کمی' qualifier and other natural Persian variants to improve F1 scoring robustness."
}
```

---

#### `peval-public-reading-013`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: تیم توسعه نرم‌افزار متوجه شد بیشتر گزارش‌های خطا از یک صفحه خاص می‌آید. آن‌ها آن صفحه را بازنویسی کردند و تعداد گزارش‌ها به یک‌سوم رسید. سوال: نتیجه بازنویسی صفحه چه بود؟

**Accepted answers:** ['کاهش گزارش خطا به یک\u200cسوم', 'یک\u200cسوم شدن گزارش\u200cهای خطا']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=1, difficulty=2

**Issues:**
  - اولین پاسخ ('کاهش گزارش خطا به یک‌سوم') فاقد نشانه جمع است؛ باید 'گزارش‌های خطا' باشد
  - سطح دشواری 3 برای سوالی که پاسخ آن مستقیماً در متن آمده بیش از حد بالاست؛ 2 مناسب‌تر است
  - لیست پاسخ‌های پذیرفتنی ناقص است و چند عبارت طبیعی فارسی را پوشش نمی‌دهد

**Proposed changes:**
```json
{
  "answer_additions": [
    "کاهش گزارش‌های خطا به یک‌سوم",
    "تعداد گزارش‌های خطا به یک‌سوم کاهش یافت",
    "گزارش‌های خطا به یک‌سوم کاهش پیدا کرد",
    "خطاها به یک‌سوم رسید",
    "تعداد خطاها سه برابر کمتر شد"
  ],
  "notes": "سوال از نظر محتوا درست است اما پاسخ اول دارای اشکال دستوری جزئی است و لیست پاسخ‌ها باید گسترش یابد. سطح دشواری نیز باید به 2 تغییر کند چون پاسخ کلمه‌به‌کلمه در متن موجود است."
}
```

---

#### `peval-public-reading-014`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: در یک مدرسه روستایی، دانش‌آموزان با کمک معلم خود یک کتابخانه کوچک ساختند. کتاب‌ها از اهالی روستا هدیه گرفته شد. حالا هر بچه می‌تواند هفته‌ای یک کتاب امانت بگیرد. سوال: کتاب‌های کتابخانه از کجا تامین شدند؟

**Accepted answers:** ['از اهالی روستا', 'هدیه اهالی روستا']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty rated 3 but this is a direct-extraction question with no inference; difficulty 2 is more accurate
  - Answer list missing common synonym variants like 'از مردم روستا' and 'اهدای اهالی روستا'
  - Question uses 'تامین شدند' while passage uses 'هدیه گرفته شد' — minor lexical mismatch that could trip up F1 scoring if model uses passage wording

**Proposed changes:**
```json
{
  "answer_additions": [
    "اهالی روستا",
    "از مردم روستا",
    "مردم روستا",
    "اهدای اهالی روستا",
    "توسط اهالی روستا"
  ],
  "notes": "Item is fundamentally sound. Main fixes: lower difficulty to 2, expand answer list with synonym variants to improve F1 scoring robustness. The lexical gap between 'تامین' (question) and 'هدیه' (passage) is minor but worth noting for scoring purposes."
}
```

---

#### `peval-public-reading-015`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک کارمند بانک دید که اگر صبح‌ها به‌جای فهرست بلند، فقط سه کار مهم را یادداشت کند، تا ظهر آن‌ها را تمام می‌کند. این روش به بقیه همکارانش هم پیشنهاد داد. سوال: روش کارمند چه بود؟

**Accepted answers:** ['یادداشت سه کار مهم در صبح', 'نوشتن سه کار مهم در آغاز روز']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty is rated 3 but the answer is explicitly stated in the text — more appropriate as 1 or 2
  - answer list lacks additional natural Persian phrasings that F1 scoring should accept
  - both existing answers are near-identical paraphrases; more diverse phrasings would improve F1 coverage

**Proposed changes:**
```json
{
  "answer_additions": [
    "نوشتن فقط سه کار مهم در ابتدای روز",
    "انتخاب سه کار مهم در صبح به‌جای فهرست بلند",
    "محدود کردن کارها به سه مورد مهم در صبح",
    "ثبت سه وظیفه مهم در آغاز روز کاری",
    "هر صبح فقط سه کار مهم یادداشت کردن"
  ],
  "constraint_changes": {
    "difficulty": 2
  },
  "notes": "The item is fundamentally sound — passage is clear, answer is unambiguous, and cultural fit is good. The main issues are the inflated difficulty score and insufficient answer variants for robust F1 evaluation. Lowering difficulty to 2 and adding more accepted phrasings would make this a solid item."
}
```

---

#### `peval-public-reading-016`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: در یک محله، مردم برای کاهش مصرف آب، شیرهای آب خانه‌ها را با شیرهای جدیدی عوض کردند که هوا را با آب مخلوط می‌کنند. مصرف آب در سه ماه اول حدود ده درصد کم شد. سوال: علت کاهش مصرف چه بود؟

**Accepted answers:** ['تعویض شیرها با شیرهای مخلوط\u200cکن هوا', 'نصب شیرهای جدید مخلوط\u200cکننده هوا']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=1, difficulty=2

**Issues:**
  - Answer list is thin for F1 scoring — missing natural paraphrase variants
  - شیرهای هوادار is the more idiomatic Iranian Persian term for aerator faucets and is absent from accepted answers
  - Difficulty overrated at 3; answer is directly stated in text, closer to 2
  - No variant covering the concept of 'جایگزینی' or 'استفاده از' phrasing

**Proposed changes:**
```json
{
  "answer_additions": [
    "استفاده از شیرهای هوادار",
    "جایگزینی شیرهای قدیمی با شیرهای هوادار",
    "نصب شیرهایی که هوا را با آب مخلوط می‌کنند",
    "تعویض شیرهای آب با شیرهای هوادار",
    "نصب شیرهای هوادار در خانه‌ها"
  ],
  "notes": "The item is fundamentally sound but needs a richer answer list for F1 evaluation. The term شیرهای هوادار (aerator faucets) is standard in Iranian Persian and should be included. Difficulty should be lowered to 2 since the answer is explicitly stated in the passage with no inference required."
}
```

---

#### `peval-public-reading-017`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک کافه کوچک تصمیم گرفت لیوان‌های یک‌بار مصرف را بردارد و به مشتری‌های همیشگی لیوان شخصی بدهد. بعد از شش ماه، هزینه خرید لیوان کاغذی به یک‌چهارم رسید. سوال: تغییر چه اثری بر هزینه داشت؟

**Accepted answers:** ['یک\u200cچهارم شدن هزینه لیوان کاغذی', 'کاهش هزینه لیوان کاغذی به یک\u200cچهارم']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty overrated at 3; answer is directly stated in the text with no inference needed — should be 2
  - answer list is incomplete; several natural Persian paraphrases are missing
  - numeric equivalents (75% reduction) not included in accepted answers

**Proposed changes:**
```json
{
  "answer_additions": [
    "هزینه به یک‌چهارم قبل رسید",
    "هزینه لیوان‌های کاغذی چهار برابر کمتر شد",
    "هزینه لیوان کاغذی ۷۵ درصد کاهش یافت",
    "هزینه لیوان کاغذی کاهش یافت و به یک‌چهارم رسید",
    "هزینه خرید لیوان کاغذی به یک‌چهارم رسید"
  ],
  "notes": "The item is fundamentally sound — a clean, original reading comprehension passage with a clear factual question. The main fix needed is expanding the accepted answer list to cover natural Persian paraphrases and correcting the difficulty rating from 3 to 2, since the answer is explicitly present in the text without requiring inference."
}
```

---

#### `peval-public-reading-018`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک کشاورز دید زمینش در یک گوشه نمک بالایی دارد و گندم در آن قسمت رشد نمی‌کند. او در آن گوشه به‌جای گندم گیاه مقاوم به شوری کاشت. سوال: کشاورز در آن گوشه چه نوع گیاهی کاشت؟

**Accepted answers:** ['گیاه مقاوم به شوری', 'مقاوم به شوری']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=1, difficulty=1

**Issues:**
  - Difficulty is overrated at 3; the answer is verbatim in the passage, making this a trivial direct-lookup task (difficulty 1).
  - Answer list is minimal; additional Persian synonyms for salt-tolerant plants should be accepted.
  - Item tests rote recall rather than reading comprehension — no inference required.

**Proposed changes:**
```json
{
  "answer_additions": [
    "گیاه متحمل به شوری",
    "گیاه شورپسند",
    "گیاه مقاوم به نمک",
    "گیاه شوری‌پسند"
  ],
  "notes": "The item is factually correct and well-formed, but the difficulty metadata should be corrected to 1. The answer list should be expanded with synonymous Persian phrasings. Optionally, the passage could be made slightly more complex to require inference rather than direct extraction, which would justify a higher difficulty rating."
}
```

---

#### `peval-public-reading-019`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: مدیر یک کتابفروشی متوجه شد بیشتر مشتری‌ها صبح زود می‌آیند. او تصمیم گرفت ساعت کاری را زودتر آغاز کند. سوال: تصمیم مدیر بر چه پایه‌ای گرفته شد؟

**Accepted answers:** ['زمان حضور بیشتر مشتری\u200cها', 'آمدن مشتری\u200cها در صبح زود']

**Rubric:** clarity=4, ambiguity=2, cultural_fit=4, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty overrated at 3; answer is directly stated in text, making this trivial (difficulty 2)
  - f1 answer list incomplete — missing direct paraphrase of passage and other natural Persian phrasings
  - question phrasing 'بر چه پایه‌ای' is slightly formal; 'به چه دلیل' or 'بر اساس چه چیزی' would be more colloquial and natural

**Proposed changes:**
```json
{
  "answer_additions": [
    "بیشتر مشتری‌ها صبح زود می‌آیند",
    "مشاهده زمان مراجعه مشتری‌ها",
    "الگوی حضور مشتری‌ها در صبح زود",
    "مشاهده رفتار مشتری‌ها",
    "بر اساس مشاهده حضور مشتری‌ها در صبح"
  ],
  "rewrite_prompt": "متن را بخوان و پاسخ کوتاه بده: مدیر یک کتابفروشی متوجه شد بیشتر مشتری‌ها صبح زود می‌آیند. او تصمیم گرفت ساعت کاری را زودتر آغاز کند. سوال: مدیر بر اساس چه چیزی این تصمیم را گرفت؟",
  "notes": "Item is salvageable. Main issues are incomplete answer list for f1 scoring and slight overrating of difficulty. Prompt rewrite makes question more colloquial. Adding direct text paraphrase and natural variants to answer list is essential for fair f1 evaluation."
}
```

---

#### `peval-public-reading-020`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: گروهی از همسایه‌ها هر هفته به‌نوبت زباله بازیافتی ساختمان را به مرکز بازیافت می‌برند. این کار باعث شده زباله‌ای که در سطل عمومی می‌رود نصف شود. سوال: نوبت‌بندی همسایه‌ها چه نتیجه‌ای داده است؟

**Accepted answers:** ['نصف شدن زباله سطل عمومی', 'کاهش نصف زباله عمومی ساختمان']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty overrated at 3; answer is directly and explicitly stated in the text, making this a trivial extraction task (should be 1-2)
  - answer list is too narrow for robust F1 scoring; several natural Persian paraphrases are missing
  - second answer phrase 'کاهش نصف زباله عمومی ساختمان' is slightly unnatural Persian

**Proposed changes:**
```json
{
  "answer_additions": [
    "زباله‌های سطل عمومی نصف شد",
    "میزان زباله عمومی به نصف رسید",
    "زباله سطل عمومی ساختمان نصف شده است",
    "کاهش نصف زباله در سطل عمومی",
    "زباله‌ای که به سطل عمومی می‌رود نصف شده"
  ],
  "notes": "The item is fundamentally sound but needs a richer answer set for F1 evaluation. Difficulty should be lowered to 2 since the answer is a direct quote from the passage. The second provided answer ('کاهش نصف زباله عمومی ساختمان') reads slightly awkwardly; keeping it is acceptable but the additions above are more natural."
}
```

---

#### `peval-public-reading-021`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک پزشک به بیمارش گفت که دلیل سردرد مکرر، کم‌خوابی و کم‌نوشیدن آب است. بیمار سعی کرد هر شب هفت ساعت بخوابد و روزی شش لیوان آب بنوشد. بعد از یک ماه سردردها کم شد. سوال: پزشک چه دو علتی برای سردرد بیمار ذکر کرد؟

**Accepted answers:** ['کم\u200cخوابی و کم\u200cنوشیدن آب', 'کم خوابیدن و کم آب نوشیدن']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty rated 3 but answer is verbatim in the text — trivial literal retrieval, should be 1–2
  - answer list lacks common Persian paraphrases that F1 scoring should accept (e.g. کمبود خواب و کمبود آب، بی‌خوابی و کم‌آبی)

**Proposed changes:**
```json
{
  "answer_additions": [
    "کمبود خواب و کمبود آب",
    "بی‌خوابی و کم‌آبی",
    "خواب کم و آب کم",
    "نخوابیدن کافی و ننوشیدن آب کافی",
    "کم‌خوابی و کمبود آب"
  ],
  "notes": "The item is fundamentally sound but difficulty should be corrected to 2 (or even 1) since the answer is directly stated in the passage with no inference required. F1 scoring benefits from a broader set of accepted paraphrases to avoid penalising valid Persian reformulations."
}
```

---

#### `peval-public-reading-022`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: در یک کارخانه، خط تولید قبلا با ۱۲ نفر کار می‌کرد. بعد از خرید یک دستگاه جدید بسته‌بندی، با ۸ نفر هم کار خط انجام می‌شود. سوال: تعداد نفرات لازم برای کار خط بعد از تغییر چقدر شده است؟

**Accepted answers:** ['هشت نفر', '۸ نفر', '8 نفر']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=1

**Issues:**
  - Difficulty is overrated at 3; the answer is explicitly stated verbatim in the passage, making this a trivial lookup (difficulty should be 1)
  - Answer list is missing some natural Persian phrasings a model might produce
  - The passage is so short and the answer so explicit that this barely tests reading comprehension — more of a copy-paste task

**Proposed changes:**
```json
{
  "answer_additions": [
    "هشت",
    "۸",
    "8",
    "هشت (۸) نفر",
    "۸ (هشت) نفر"
  ],
  "notes": "The item is functionally correct but trivially easy. Consider adding a mild inference step (e.g., asking how many workers were reduced, or what percentage of workers remain) to raise difficulty to at least 2. Also update difficulty metadata to 1 if kept as-is. Answer list should include bare digit forms since F1 scoring may encounter them."
}
```

---

#### `peval-public-reading-023`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک معلم تصمیم گرفت در کلاس به‌جای امتحان نهایی کتبی، از هر دانش‌آموز یک پروژه عملی بخواهد. والدین گفتند بچه‌ها انگیزه بیشتری گرفته‌اند. سوال: معلم به‌جای امتحان نهایی چه چیزی خواست؟

**Accepted answers:** ['پروژه عملی', 'یک پروژه عملی از هر دانش\u200cآموز']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty rated 3 by auto-reviewer but this is a trivial direct-retrieval question — answer is verbatim in the passage.
  - Answer list is incomplete for F1 scoring; common paraphrases like 'پروژه' alone or 'کار عملی' are missing.
  - Persian digit variants not applicable here, but short-form answers should be included.

**Proposed changes:**
```json
{
  "answer_additions": [
    "پروژه",
    "کار عملی",
    "یک پروژه عملی",
    "پروژه‌ی عملی",
    "یک پروژه‌ی عملی"
  ],
  "notes": "The item is fundamentally sound but difficulty should be corrected to 2 (trivial direct retrieval). The F1 answer list should include shorter and slightly varied Persian phrasings to avoid penalizing correct but differently-phrased responses."
}
```

---

#### `peval-public-reading-024`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک رستوران کوچک سفارش‌ها را از طریق پیامک می‌گرفت. بعد از راه‌اندازی یک اپلیکیشن ساده، تعداد سفارش‌ها در روز دو برابر شد. سوال: تغییر چه اثری بر سفارش‌ها داشت؟

**Accepted answers:** ['دو برابر شدن تعداد سفارش روزانه', 'افزایش دو برابری سفارش روزانه']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Answer list is incomplete for F1 scoring — several natural Persian phrasings of 'orders doubled' are missing
  - Difficulty is overrated at 3; this is a direct literal recall question, difficulty 2 is more appropriate

**Proposed changes:**
```json
{
  "answer_additions": [
    "سفارش‌ها دو برابر شد",
    "تعداد سفارش‌ها دو برابر شد",
    "سفارش‌های روزانه دو برابر شدند",
    "دو برابر شدن سفارش‌ها",
    "۲ برابر شدن سفارش‌های روزانه",
    "افزایش دو برابری سفارش‌ها",
    "سفارش‌ها دو برابر شدند"
  ],
  "notes": "The item is fundamentally sound — clear passage, unambiguous answer, good cultural fit. The main issue is that F1 scoring requires broader answer coverage. Also recommend lowering difficulty from 3 to 2 since the answer is explicitly stated verbatim in the text with no inference required."
}
```

---

#### `peval-public-reading-025`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: شهرداری یک شهر کوچک تصمیم گرفت در پارک‌ها چراغ‌های خورشیدی نصب کند. هزینه برق روشنایی پارک‌ها در سال اول حدود ۳۰ درصد کاهش یافت. سوال: نصب چراغ خورشیدی چه اثری بر هزینه برق پارک‌ها داشت؟

**Accepted answers:** ['حدود ۳۰ درصد کاهش', 'کاهش حدود سی درصد', 'کاهش حدود 30 درصد']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty rated 3 but question is a direct text lookup requiring no inference — should be 1 or 2
  - Answer list missing several natural Persian phrasings that F1 scoring should accept
  - No distractor or inference element; trivially answered by copying from text

**Proposed changes:**
```json
{
  "answer_additions": [
    "کاهش ۳۰ درصدی",
    "کاهش سی‌درصدی",
    "هزینه برق حدود ۳۰ درصد کاهش یافت",
    "سی درصد کاهش",
    "۳۰ درصد کاهش یافت",
    "هزینه برق کاهش یافت"
  ],
  "notes": "The item is fundamentally sound but difficulty is overestimated — the answer is verbatim in the passage. Consider adding a mild inference layer (e.g., asking whether this was a good investment, or asking about long-term implications) to raise difficulty. At minimum, correct the difficulty metadata to 2 and expand the answer list with natural Persian variants."
}
```

---

#### `peval-public-reading-026`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک شرکت حمل‌ونقل، مسیر روزانه کامیون‌ها را با یک نرم‌افزار جدید بهینه کرد. زمان رسیدن به انبار به‌طور میانگین یک ساعت کم شد. سوال: کاهش زمان رسیدن چقدر بود؟

**Accepted answers:** ['یک ساعت', '۱ ساعت', '1 ساعت', 'میانگین یک ساعت']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=1

**Issues:**
  - Difficulty rated 3 but this is a direct-lookup question requiring zero inference — should be 1
  - Answer list missing 'به‌طور میانگین یک ساعت' which is the exact phrase from the passage
  - Reordered variant '۱ ساعت به‌طور میانگین' not covered

**Proposed changes:**
```json
{
  "answer_additions": [
    "به‌طور میانگین یک ساعت",
    "۱ ساعت به‌طور میانگین",
    "1 ساعت به‌طور میانگین"
  ],
  "notes": "The item is otherwise sound. The difficulty metadata should be corrected to 1 since the answer is a verbatim copy from the passage. A few additional answer phrasings should be added to improve F1 coverage."
}
```

---

#### `peval-public-reading-027`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک خبرنگار از معلمی گزارش گرفت که سال‌هاست در روستایی دورافتاده درس می‌دهد. معلم گفت تنها انگیزه‌اش دیدن پیشرفت بچه‌هاست. سوال: انگیزه معلم برای ادامه کار چیست؟

**Accepted answers:** ['دیدن پیشرفت بچه\u200cها', 'پیشرفت بچه\u200cها']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty rated 3 but answer is verbatim in the text — should be 1 or 2
  - Answer list missing synonym variants using دانش‌آموزان and شاگردان instead of بچه‌ها
  - Answer list missing phrasing 'پیشرفت بچه‌های روستا' which is also defensible

**Proposed changes:**
```json
{
  "answer_additions": [
    "دیدن پیشرفت دانش‌آموزان",
    "پیشرفت دانش‌آموزان",
    "دیدن پیشرفت شاگردان",
    "پیشرفت شاگردان",
    "پیشرفت بچه‌های روستا"
  ],
  "notes": "The item is fundamentally sound but the difficulty metadata is inflated — the answer is a near-verbatim copy of a sentence in the passage, making this trivially easy (difficulty 1-2). The answer list should also include synonym variants where بچه‌ها is replaced by دانش‌آموزان or شاگردان, as these are natural substitutions a respondent might use."
}
```

---

#### `peval-public-reading-028`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک گروه پژوهشی از دانش‌آموزان دبیرستانی خواست هر روز سی دقیقه پیاده‌روی کنند. بعد از دو ماه، نمره‌های درس‌های نظری در میانگین کلاس اندکی بهتر شد. سوال: پژوهشگران از دانش‌آموزان چه چیزی خواستند؟

**Accepted answers:** ['پیاده\u200cروی روزانه سی دقیقه', 'روزی سی دقیقه پیاده\u200cروی']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty is overrated at 3; the answer is a direct verbatim lookup from the passage, making it trivially easy (1-2).
  - Answer list is incomplete for F1 scoring — missing the verbatim phrasing from the text and other natural Persian equivalents.
  - For F1 scoring, both Persian and Arabic digit forms of '30' should be included.

**Proposed changes:**
```json
{
  "answer_additions": [
    "هر روز سی دقیقه پیاده‌روی کنند",
    "سی دقیقه پیاده‌روی در روز",
    "پیاده‌روی سی‌دقیقه‌ای روزانه",
    "پیاده‌روی روزانه ۳۰ دقیقه",
    "روزی ۳۰ دقیقه پیاده‌روی",
    "۳۰ دقیقه پیاده‌روی در روز"
  ],
  "notes": "The item is fundamentally sound but needs a more complete answer list for robust F1 evaluation. Difficulty should be lowered to 2 since the answer is directly stated in the passage with no inference required."
}
```

---

#### `peval-public-reading-029`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: یک مغازه‌دار محله، خرید نسیه را برای مشتری‌های همیشگی محدود به مبلغ مشخصی کرد. این کار از بدهی‌های معوق او در یک سال جلوگیری کرد. سوال: تصمیم مغازه‌دار چه بود؟

**Accepted answers:** ['محدود کردن خرید نسیه به مبلغ مشخص', 'تعیین سقف برای خرید نسیه']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty is rated 3 but the answer is directly and explicitly stated in the passage with no inference needed — closer to 1-2
  - answer list is incomplete; several natural Persian paraphrases are missing
  - passage is very short and synthetic, making this more of a paraphrase task than genuine comprehension

**Proposed changes:**
```json
{
  "answer_additions": [
    "محدود کردن نسیه برای مشتریان دائمی",
    "گذاشتن سقف برای خرید نسیه",
    "تعیین حد مشخص برای نسیه",
    "محدود کردن مبلغ نسیه",
    "محدود کردن خرید نسیه مشتریان به سقف معین"
  ],
  "notes": "The item is fundamentally sound and culturally appropriate. The main issues are: (1) difficulty should be lowered to 2 since the answer is a near-verbatim copy from the passage, and (2) the accepted answer list should be expanded to cover common Persian paraphrases. No structural changes needed."
}
```

---

#### `peval-public-reading-030`

**Prompt:** متن را بخوان و پاسخ کوتاه بده: گروهی از داوطلبان یک پل چوبی قدیمی روستا را تعمیر کردند. حالا بچه‌های روستا برای رفتن به مدرسه دیگر مجبور به دور زدن از مسیر طولانی نیستند. سوال: نتیجه تعمیر پل برای بچه‌های روستا چه شد؟

**Accepted answers:** ['نیاز نداشتن به دور زدن از مسیر طولانی', 'حذف دور زدن از مسیر طولانی']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=1, difficulty=2

**Issues:**
  - پاسخ‌های موجود از نظر دستوری کمی ناطبیعی هستند (مصدر مرخم به عنوان پاسخ مستقل)
  - فهرست پاسخ‌های پذیرفتنی ناقص است؛ معادل‌های طبیعی‌تر فارسی باید اضافه شوند
  - سطح دشواری ۳ بالاتر از حد واقعی است؛ پاسخ تقریباً مستقیماً در متن آمده است
  - پاسخ مستقیم متن ('دیگر مجبور به دور زدن از مسیر طولانی نیستند') در فهرست نیست

**Proposed changes:**
```json
{
  "answer_additions": [
    "دیگر مجبور به دور زدن از مسیر طولانی نیستند",
    "مسیر رفتن به مدرسه کوتاه‌تر شد",
    "راحت‌تر به مدرسه می‌روند",
    "مسیر طولانی دور زدن حذف شد",
    "دیگر لازم نیست مسیر طولانی بروند"
  ],
  "notes": "سطح دشواری باید به ۲ کاهش یابد چون پاسخ مستقیماً در متن بیان شده است. همچنین پاسخ‌های طبیعی‌تر فارسی باید به فهرست اضافه شوند."
}
```

---

### `short_qa` — 25 items

#### `peval-public-shortqa-005`

**Prompt:** بلندترین قله رشته‌کوه البرز چه نام دارد؟

**Accepted answers:** ['دماوند', 'قله دماوند']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Difficulty rated 3 but this is basic geography for most Iranians — should be 2
  - Missing common answer variant 'کوه دماوند' from accepted answers
  - Missing ezafe variant 'قله‌ی دماوند' from accepted answers

**Proposed changes:**
```json
{
  "answer_additions": [
    "کوه دماوند",
    "قله‌ی دماوند",
    "کوه‌دماوند"
  ],
  "notes": "The answer is correct. Add 'کوه دماوند' and 'قله‌ی دماوند' as accepted variants since these are very natural ways to refer to the peak in Iranian Persian. Adjust difficulty to 2 as this is common knowledge for most Persian speakers."
}
```

---

#### `peval-public-shortqa-006`

**Prompt:** پایتخت استان خراسان رضوی چه نام دارد؟

**Accepted answers:** ['مشهد']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Difficulty rated 3 by author but this is a trivial fact known to virtually all Iranians; should be 1 or 2.
  - Answer list could optionally include 'مشهد مقدس' as an accepted alternate phrasing used in everyday Persian.
  - Leakage risk is slightly elevated since this is a well-known geographic fact likely appearing in many public Persian texts, though the exact question wording may be original.

**Proposed changes:**
```json
{
  "answer_additions": [
    "مشهد مقدس"
  ],
  "notes": "The core answer is correct. The only changes needed are: (1) lower the difficulty rating from 3 to 2 (or even 1), and (2) optionally add 'مشهد مقدس' as an accepted answer variant. The item is otherwise sound."
}
```

---

#### `peval-public-shortqa-007`

**Prompt:** نام دیگر آبراهی که خلیج فارس را به دریای عمان متصل می‌کند چیست؟

**Accepted answers:** ['تنگه هرمز']

**Rubric:** clarity=3, ambiguity=2, cultural_fit=5, leakage_risk=4, difficulty=2

**Issues:**
  - عبارت 'نام دیگر' گمراه‌کننده است؛ تنگه هرمز نام اصلی این آبراه است نه نام دیگر آن
  - برای scoring از نوع exact، باید اشکال مختلف نوشتاری فارسی مانند 'تنگهٔ هرمز' و 'تنگه‌ی هرمز' نیز در لیست پاسخ‌ها باشند
  - leakage_risk پایین‌تر از واقعیت تعیین شده؛ این سوال در منابع عمومی بسیار رایج است
  - سطح دشواری ۳ برای این سوال جغرافیایی پایه بالاتر از حد معقول است

**Proposed changes:**
```json
{
  "answer_additions": [
    "تنگهٔ هرمز",
    "تنگه‌ی هرمز",
    "Strait of Hormuz"
  ],
  "rewrite_prompt": "نام آبراهی که خلیج فارس را به دریای عمان متصل می‌کند چیست؟",
  "notes": "حذف 'نام دیگر' از سوال چون تنگه هرمز نام اصلی این آبراه است. همچنین اشکال نوشتاری مختلف باید در لیست پاسخ‌های قابل قبول گنجانده شوند تا سیستم exact matching به درستی کار کند."
}
```

---

#### `peval-public-shortqa-008`

**Prompt:** بزرگ‌ترین جزیره ایران در خلیج فارس چه نام دارد؟

**Accepted answers:** ['قشم', 'جزیره قشم']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=2

**Issues:**
  - leakage_risk rated 1 but this is a standard geography question appearing in countless Persian textbooks and websites — should be higher
  - difficulty rated 3 but this is common general knowledge in Iran, more appropriate at 2
  - missing accepted variant 'جزیره‌ی قشم' (with ezafe marker)

**Proposed changes:**
```json
{
  "answer_additions": [
    "جزیره‌ی قشم"
  ],
  "notes": "The factual answer is correct. Minor additions needed: one more accepted phrasing with ezafe, and metadata rubric scores for leakage_risk and difficulty should be adjusted to better reflect reality."
}
```

---

#### `peval-public-shortqa-009`

**Prompt:** در کدام شهر ایران میدان نقش جهان واقع شده است؟

**Accepted answers:** ['اصفهان']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=1

**Issues:**
  - Difficulty is overrated at 3; Naqsh-e Jahan Square in Isfahan is one of the most famous landmarks in Iran, making this trivial (difficulty 1) for any Iranian.
  - Leakage risk is slightly higher than 1 since this is a universally known fact, though the exact wording may be original.

**Proposed changes:**
```json
{
  "notes": "The only change needed is correcting the difficulty metadata from 3 to 1. The answer 'اصفهان' is correct and complete. No additional accepted phrasings are needed for exact match."
}
```

---

#### `peval-public-shortqa-010`

**Prompt:** نخستین ماه تقویم هجری شمسی چه نام دارد؟

**Accepted answers:** ['فروردین']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=1

**Issues:**
  - Difficulty rated 3/5 but this is trivial knowledge for any Persian speaker — should be 1/5
  - Answer list missing common idiomatic variant 'فروردین‌ماه'
  - Leakage risk underestimated; this fact appears on countless public Persian sources

**Proposed changes:**
```json
{
  "answer_additions": [
    "فروردین‌ماه"
  ],
  "notes": "Correct answer confirmed. Adjust difficulty to 1 and leakage_risk to 3. Add 'فروردین‌ماه' as an accepted alternate phrasing since it is commonly used in Iranian Persian when referring to months."
}
```

---

#### `peval-public-shortqa-011`

**Prompt:** چندمین روز فروردین معمولا با سیزده‌بدر شناخته می‌شود؟

**Accepted answers:** ['سیزدهم', '۱۳', '13']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=1

**Issues:**
  - difficulty is overrated at 3 — the answer is literally embedded in the word 'سیزده‌بدر', making this trivial (difficulty 1)
  - answer list missing bare form 'سیزده' without ordinal suffix ـم, which many respondents will write

**Proposed changes:**
```json
{
  "answer_additions": [
    "سیزده"
  ],
  "notes": "Difficulty should be 1, not 3. The question is self-answering since 'سیزده' means thirteen. Also add 'سیزده' (without ordinal suffix) to accepted answers."
}
```

---

#### `peval-public-shortqa-012`

**Prompt:** نام مرکز استان آذربایجان شرقی چیست؟

**Accepted answers:** ['تبریز']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=2

**Issues:**
  - Difficulty is overrated at 3; Tabriz as capital of East Azerbaijan is trivially known to any Iranian adult or student — difficulty 1 or 2 is more appropriate
  - Leakage risk is underrated at 1; this exact question phrasing is a standard geography quiz question widely found in Persian educational websites and textbooks

**Proposed changes:**
```json
{
  "notes": "The answer is correct and complete. Only metadata adjustments needed: lower difficulty from 3 to 2, raise leakage_risk from 1 to 3. The item is otherwise sound and can be accepted after metadata correction."
}
```

---

#### `peval-public-shortqa-013`

**Prompt:** در فارسی، گرم‌ترین فصل سال چه نامیده می‌شود؟

**Accepted answers:** ['تابستان']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=1

**Issues:**
  - Difficulty is rated 3 but the question is trivially easy (kindergarten-level knowledge); should be 1
  - Answer list missing colloquial Persian variant 'تابستون'
  - Question is too simple to meaningfully discriminate model capability; consider replacing with a harder general-knowledge item

**Proposed changes:**
```json
{
  "answer_additions": [
    "تابستون"
  ],
  "notes": "The factual answer is correct. The main issues are the inflated difficulty score and the trivial nature of the question. If kept, difficulty should be corrected to 1 and the colloquial form 'تابستون' added to accepted answers. Ideally, this item should be replaced with a more discriminating question."
}
```

---

#### `peval-public-shortqa-014`

**Prompt:** کدام رنگ معمولا در میانه پرچم سه‌رنگ ایران قرار دارد؟

**Accepted answers:** ['سفید']

**Rubric:** clarity=4, ambiguity=1, cultural_fit=5, leakage_risk=4, difficulty=1

**Issues:**
  - کلمه «معمولاً» در سوال نادرست است؛ رنگ میانه پرچم ایران همیشه سفید است، نه «معمولاً»
  - سطح دشواری بسیار پایین‌تر از ۳ است — این دانش عمومی بسیار ابتدایی است
  - خطر نشت (leakage) بالاست؛ این سوال در منابع عمومی فراوان یافت می‌شود
  - لیست پاسخ‌های پذیرفتنی می‌تواند «رنگ سفید» را نیز شامل شود

**Proposed changes:**
```json
{
  "answer_additions": [
    "رنگ سفید",
    "white"
  ],
  "rewrite_prompt": "کدام رنگ در میانه پرچم سه‌رنگ ایران قرار دارد؟",
  "notes": "حذف «معمولاً» از متن سوال ضروری است. همچنین سطح دشواری باید به ۱ تغییر یابد. خطر نشت از منابع عمومی نسبتاً بالاست."
}
```

---

#### `peval-public-shortqa-015`

**Prompt:** یک کیلومتر چند متر است؟

**Accepted answers:** ['هزار', 'هزار متر', '۱۰۰۰', '1000']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=1

**Issues:**
  - Difficulty rated 3 but this is elementary-school knowledge — should be 1
  - Leakage risk rated 1 but this is a universal basic fact Q&A pair found everywhere
  - Missing answer variant '۱۰۰۰ متر' which is a very natural Persian response
  - Missing variant 'یک هزار متر' as a natural Persian phrasing
  - Exact scoring may cause false negatives for responses like 'هزار متر است' — consider f1 or adding more variants
  - Thousands-separator form '۱٬۰۰۰' not included

**Proposed changes:**
```json
{
  "answer_additions": [
    "۱۰۰۰ متر",
    "یک هزار متر",
    "۱٬۰۰۰",
    "1,000"
  ],
  "notes": "Difficulty should be corrected to 1. Leakage risk should be at least 3 given this is a universal basic fact. The answer list needs '۱۰۰۰ متر' at minimum as it is the most natural complete answer. Consider switching scoring to f1 to handle natural sentence-form answers."
}
```

---

#### `peval-public-shortqa-016`

**Prompt:** قطب جنوب در کدام نیم‌کره زمین قرار دارد؟

**Accepted answers:** ['نیم\u200cکره جنوبی', 'جنوبی']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=1

**Issues:**
  - Difficulty is rated 3 but the question is trivially easy (difficulty 1) — the answer 'جنوبی' is literally contained within the question term 'قطب جنوب'
  - Answer list missing orthographic variants of 'نیم‌کره': 'نیمکره جنوبی' (no half-space) and 'نیم کره جنوبی' (full space) are common in Persian writing
  - Leakage risk slightly elevated — this exact phrasing appears in countless Persian geography textbooks and Q&A sites

**Proposed changes:**
```json
{
  "answer_additions": [
    "نیمکره جنوبی",
    "نیم کره جنوبی"
  ],
  "notes": "Correct the difficulty metadata from 3 to 1. The question is near-tautological. Consider replacing with a less obvious geography question to improve benchmark utility."
}
```

---

#### `peval-public-shortqa-017`

**Prompt:** بزرگ‌ترین سیاره منظومه شمسی چه نام دارد؟

**Accepted answers:** ['مشتری', 'سیاره مشتری']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=4, difficulty=1

**Issues:**
  - Difficulty rated 3 but this is elementary-school level knowledge — should be 1
  - Leakage risk rated 1 but this exact question appears verbatim on countless Persian educational sites — should be 4
  - Answer list missing 'ژوپیتر' (transliteration used in some Persian scientific texts) and 'Jupiter' as possible responses
  - For exact scoring, Persian digit variants are not applicable here, but the answer set could be slightly more complete

**Proposed changes:**
```json
{
  "answer_additions": [
    "ژوپیتر",
    "Jupiter",
    "مشتری (Jupiter)"
  ],
  "notes": "The item is factually correct and culturally appropriate, but the difficulty and leakage_risk metadata scores need correction. 'ژوپیتر' is occasionally used in Persian scientific writing as a transliteration of Jupiter and should be an accepted answer. The question is trivially easy (difficulty=1) and is a canonical question widely found on Persian quiz sites (leakage_risk=4)."
}
```

---

#### `peval-public-shortqa-018`

**Prompt:** در زبان فارسی، مخالف کلمه «روز» چیست؟

**Accepted answers:** ['شب']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=1

**Issues:**
  - Difficulty is severely overrated (marked 3, should be 1) — antonym of روز is first-grade level knowledge
  - Leakage risk is underrated (marked 1, should be ~3) — this exact question type is ubiquitous in public Persian language learning materials
  - Question is too trivial to provide meaningful benchmark discrimination

**Proposed changes:**
```json
{
  "notes": "The answer 'شب' is correct and complete. The main issues are metadata inaccuracies (difficulty and leakage_risk scores) and the overall low value of such a trivial item in a benchmark. Consider replacing with a more challenging antonym/language question, e.g., asking for a less obvious antonym or a nuanced semantic distinction in Persian vocabulary."
}
```

---

#### `peval-public-shortqa-019`

**Prompt:** چه عددی را اگر در صفر ضرب کنیم، حاصل صفر می‌شود؟

**Accepted answers:** ['هر عدد', 'همه اعداد', 'هر عددی']

**Rubric:** clarity=4, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=1

**Issues:**
  - Difficulty metadata is overrated at 3; this is elementary-level knowledge (should be 1)
  - Answer list incomplete for exact scoring — missing natural Persian phrasings like 'تمام اعداد' and 'هر عدد دلخواه'
  - Singular 'چه عددی' framing slightly misleads toward expecting a specific number, though this may be intentional
  - Exact scoring is risky here given the variety of natural ways to express 'any number' in Persian

**Proposed changes:**
```json
{
  "answer_additions": [
    "تمام اعداد",
    "هر عدد دلخواه",
    "هر عدد حقیقی",
    "هر عددی را",
    "همه‌ی اعداد"
  ],
  "notes": "Difficulty should be corrected to 1. The answer list needs expansion to reduce false negatives under exact scoring. Consider switching to f1 scoring to handle paraphrase variation more gracefully."
}
```

---

#### `peval-public-shortqa-020`

**Prompt:** نام مرکز استان گیلان چیست؟

**Accepted answers:** ['رشت']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - difficulty is overrated at 3; this is basic common knowledge in Iran, difficulty 2 is more appropriate
  - leakage risk is slightly higher than 1 since this is a standard factual question likely appearing in many educational sources

**Proposed changes:**
```json
{
  "notes": "The answer is correct and complete. Only metadata adjustment needed: difficulty should be lowered from 3 to 2, as Rasht being the capital of Gilan is extremely well-known basic geography among Iranian Persian speakers."
}
```

---

#### `peval-public-shortqa-021`

**Prompt:** کدام رنگ از ترکیب آبی و زرد به دست می‌آید؟

**Accepted answers:** ['سبز']

**Rubric:** clarity=5, ambiguity=2, cultural_fit=5, leakage_risk=4, difficulty=1

**Issues:**
  - Difficulty rated 3 but this is primary-school trivial knowledge — should be 1
  - Leakage risk rated 1 but this exact question appears in countless online educational resources
  - Ambiguity slightly non-zero: in additive (light) color mixing blue+yellow does not simply yield green; question should specify pigment/paint context to be fully unambiguous
  - Answer list missing alternative phrasing 'رنگ سبز'

**Proposed changes:**
```json
{
  "answer_additions": [
    "رنگ سبز"
  ],
  "rewrite_prompt": "کدام رنگ از ترکیب رنگ‌دانه‌های آبی و زرد (مثلاً در نقاشی) به دست می‌آید؟",
  "notes": "Metadata difficulty should be corrected to 1 and leakage_risk to 4. The rewrite adds 'رنگ‌دانه' context to eliminate the additive vs. subtractive mixing ambiguity."
}
```

---

#### `peval-public-shortqa-022`

**Prompt:** در دستگاه گردش خون انسان، خون پاک از کدام بطن قلب به آئورت می‌رود؟

**Accepted answers:** ['بطن چپ', 'چپ']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=2

**Issues:**
  - Difficulty overrated at 3; standard Iranian high school biology, should be 2
  - Leakage risk underrated at 1; this is a textbook-standard question with high likelihood of appearing verbatim in public sources
  - Answer list missing 'بطن چپ قلب' as a natural extended form

**Proposed changes:**
```json
{
  "answer_additions": [
    "بطن چپ قلب"
  ],
  "notes": "The factual answer is correct. Metadata rubric values for difficulty and leakage_risk should be adjusted. One additional answer variant added for completeness."
}
```

---

#### `peval-public-shortqa-023`

**Prompt:** نام پل قدیمی معروف اصفهان روی زاینده‌رود که از دوره صفویه به‌جا مانده چیست؟

**Accepted answers:** ['سی و سه پل', 'سی\u200cو\u200cسه پل', 'پل سی و سه پل']

**Rubric:** clarity=3, ambiguity=3, cultural_fit=5, leakage_risk=3, difficulty=2

**Issues:**
  - پل خواجو نیز یک پل معروف صفوی روی زاینده‌رود است و می‌تواند پاسخ دفاع‌پذیر دیگری باشد
  - نام رسمی تاریخی پل سی‌وسه‌پل (پل الله‌وردی‌خان) در لیست پاسخ‌ها غایب است
  - صورت‌بندی مفرد معرفه ('پل قدیمی معروف') ابهام ایجاد می‌کند چون دو پل مشهور صفوی وجود دارد
  - ریسک نشت متوسط — سوال رایج در متون گردشگری و آموزشی

**Proposed changes:**
```json
{
  "answer_additions": [
    "پل الله‌وردی‌خان",
    "پل الله وردی خان",
    "سی‌وسه‌پل",
    "۳۳ پل"
  ],
  "rewrite_prompt": "نام پل صفوی معروف اصفهان روی زاینده‌رود که الله‌وردی‌خان آن را ساخت و به خاطر تعداد دهانه‌هایش شناخته می‌شود چیست؟",
  "notes": "بازنویسی پیشنهادی با اشاره به سازنده و ویژگی متمایز پل، ابهام را برطرف می‌کند و پل خواجو را از دایره پاسخ‌های احتمالی خارج می‌سازد. همچنین پاسخ 'پل الله‌وردی‌خان' باید به لیست پاسخ‌های پذیرفتنی اضافه شود."
}
```

---

#### `peval-public-shortqa-024`

**Prompt:** جشن چهارشنبه‌سوری در آستانه کدام جشن بزرگ ایرانی برگزار می‌شود؟

**Accepted answers:** ['نوروز', 'عید نوروز']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Difficulty overrated at 3; this is basic cultural knowledge known to virtually all Iranians
  - Missing accepted phrasing 'جشن نوروز' which is a natural Iranian Persian variant

**Proposed changes:**
```json
{
  "answer_additions": [
    "جشن نوروز"
  ],
  "notes": "Item is otherwise solid. Difficulty should be lowered to 2. Adding 'جشن نوروز' as a third accepted answer improves coverage for exact-match scoring."
}
```

---

#### `peval-public-shortqa-025`

**Prompt:** در ایران، روز معلم در کدام ماه شمسی است؟

**Accepted answers:** ['اردیبهشت']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - answer list is incomplete: 'اردیبهشت‌ماه' and 'ماه اردیبهشت' are natural Persian phrasings that should be accepted
  - difficulty rated 3 by author but this is common knowledge for most Iranians; 2 is more appropriate
  - leakage_risk slightly elevated as this is a well-known public calendar fact

**Proposed changes:**
```json
{
  "answer_additions": [
    "اردیبهشت‌ماه",
    "ماه اردیبهشت"
  ],
  "notes": "The answer 'اردیبهشت' is correct (Teacher's Day is 12 Ordibehesht). Add natural Persian variants to the accepted answer list. Difficulty should be lowered to 2 as this is widely known among Iranians."
}
```

---

#### `peval-public-shortqa-026`

**Prompt:** در کدام استان ایران، شهر کیش قرار دارد؟

**Accepted answers:** ['هرمزگان']

**Rubric:** clarity=4, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - کیش جزیره است نه شهر؛ استفاده از 'شهر کیش' کمی نادقیق است، هرچند از نظر اداری قابل قبول است
  - لیست پاسخ‌های قابل قبول ناقص است — 'استان هرمزگان' نیز باید پذیرفته شود
  - سطح دشواری ۳ برای این سؤال بالاست؛ کیش یک مقصد گردشگری بسیار مشهور است و اکثر ایرانیان استان آن را می‌دانند

**Proposed changes:**
```json
{
  "answer_additions": [
    "استان هرمزگان",
    "هرمزگان"
  ],
  "rewrite_prompt": "جزیره کیش در کدام استان ایران قرار دارد؟",
  "notes": "تغییر 'شهر کیش' به 'جزیره کیش' دقیق‌تر و طبیعی‌تر است. افزودن 'استان هرمزگان' به لیست پاسخ‌های قابل قبول برای سیستم exact scoring ضروری است. سطح دشواری به ۲ کاهش یابد."
}
```

---

#### `peval-public-shortqa-028`

**Prompt:** نام بزرگ‌ترین اقیانوس جهان چیست؟

**Accepted answers:** ['اقیانوس آرام', 'آرام']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=1

**Issues:**
  - difficulty rated 3 but this is a trivial geography fact known to elementary school students — should be 1
  - leakage_risk rated 1 but this is an extremely common question widely available in Persian online sources — should be 3
  - alternative Persian name 'اقیانوس کبیر' missing from accepted answers
  - colloquial transliteration 'پاسیفیک' sometimes used in Persian and should be considered

**Proposed changes:**
```json
{
  "answer_additions": [
    "اقیانوس کبیر",
    "پاسیفیک",
    "اقیانوس پاسیفیک"
  ],
  "notes": "The answer set should include 'اقیانوس کبیر' as it is a well-known classical Persian name for the Pacific Ocean. Difficulty should be corrected to 1 (trivial). Leakage risk should be raised to 3 given how commonly this question appears in Persian educational content online."
}
```

---

#### `peval-public-shortqa-029`

**Prompt:** در زبان فارسی، فعل «رفتن» در زمان حال ساده اول‌شخص مفرد چیست؟

**Accepted answers:** ['می\u200cروم', 'میروم']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=1

**Issues:**
  - difficulty rated 3 but this is trivially easy for any Persian speaker or basic learner
  - leakage_risk rated 1 but basic conjugation questions are ubiquitous in grammar resources online
  - term 'حال ساده' is slightly informal/ambiguous in formal Persian grammar (vs. مضارع اخباری), though answer remains correct

**Proposed changes:**
```json
{
  "rewrite_prompt": "در زبان فارسی، فعل «رفتن» در زمان مضارع اخباری (حال ساده) اول‌شخص مفرد چیست؟",
  "notes": "The answer is correct and the two orthographic variants are sufficient. Main issues are metadata: difficulty should be 1 (trivial), leakage_risk should be 2-3. The prompt could optionally clarify 'مضارع اخباری' to avoid any ambiguity around 'حال ساده' terminology in formal grammar."
}
```

---

#### `peval-public-shortqa-030`

**Prompt:** کدام فلز در دمای اتاق به حالت مایع است؟

**Accepted answers:** ['جیوه']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=4, difficulty=2

**Issues:**
  - leakage risk is high — this is one of the most commonly cited science trivia questions in Persian and other languages
  - difficulty overrated at 3; this is basic general knowledge known to most educated adults
  - answer list missing alternative phrasings such as chemical symbol Hg or compound forms like 'جیوه (Hg)'

**Proposed changes:**
```json
{
  "answer_additions": [
    "Hg",
    "جیوه (Hg)",
    "mercury"
  ],
  "notes": "Gallium melts at ~29.76°C and could technically qualify depending on room temperature definition, but in Iranian science education mercury is the unambiguous expected answer. Difficulty should be lowered to 2. Leakage risk should be raised to 4."
}
```

---


## Accepted (62)

### `culture` — 9 items

#### `peval-public-culture-007`

**Prompt:** چهارشنبه‌سوری معمولا در شب آخرین چهارشنبه کدام ماه برگزار می‌شود؟

  - الف) دی
  - ب) بهمن
  - پ) اسفند ← labelled answer
  - ت) فروردین

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - difficulty is overrated at 3; this is basic cultural knowledge for any Iranian adult, more like 2

---

#### `peval-public-culture-008`

**Prompt:** در فرهنگ عامه ایرانی، خواندن دیوان حافظ برای فال گرفتن بیشتر در کدام شب رواج دارد؟

  - الف) شب نوروز
  - ب) شب چهارشنبه‌سوری
  - پ) شب جمعه
  - ت) شب یلدا ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - difficulty slightly overrated at 3; this is a well-known cultural fact among Iranians, more appropriate at 2
  - شب جمعه has a minor cultural association with Hafez recitation but 'بیشتر' qualifier adequately handles this

---

#### `peval-public-culture-010`

**Prompt:** کدام شاعر ایرانی به «شیخ اجل» معروف است؟

  - الف) حافظ
  - ب) سعدی ← labelled answer
  - پ) رودکی
  - ت) نظامی

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=2

**Issues:**
  - leakage_risk underestimated — this is a classic school-level trivia question widely found in Persian educational materials
  - difficulty slightly overestimated; this is common knowledge for most educated Iranians

---

#### `peval-public-culture-011`

**Prompt:** کدام شاعر ایرانی با لقب «لسان‌الغیب» شناخته می‌شود؟

  - الف) مولوی
  - ب) خیام
  - پ) حافظ ← labelled answer
  - ت) فردوسی

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - difficulty overrated at 3; this is common knowledge in Iranian culture and schools, 2 is more appropriate
  - leakage_risk slightly underrated; this exact question form is very common in Persian educational materials

---

#### `peval-public-culture-014`

**Prompt:** کدام ساز ایرانی با چوب نازکی به نام «مضراب» نواخته می‌شود و بدنه‌ای ذوزنقه‌ای دارد؟

  - الف) تار
  - ب) سنتور ← labelled answer
  - پ) دف
  - ت) نی

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=3

**Issues:**
  - مضراب is also used for the plectrum of تار/سه‌تار, but the additional clue of trapezoidal body makes the answer unambiguous — no real problem.
  - Leakage risk slightly elevated as santur description is standard encyclopedic content, but wording appears original.

---

#### `peval-public-culture-016`

**Prompt:** آش رشته معمولا در کدام مناسبت‌ها بیشتر پخته می‌شود؟

  - الف) صبحانه
  - ب) تولد
  - پ) مهمانی شام رسمی
  - ت) نوروز و نذر ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty is slightly overrated at 3; this is fairly common cultural knowledge for most Iranians, closer to 2

**Proposed changes:**
```json
{
  "notes": "Item is solid. The correct answer 'نوروز و نذر' is unambiguously the best choice. Distractors are reasonable. Only minor suggestion is to lower difficulty rating from 3 to 2."
}
```

---

#### `peval-public-culture-025`

**Prompt:** کدام یک از این جشن‌ها ریشه پیشااسلامی در فرهنگ ایرانی دارد؟

  - الف) مهرگان ← labelled answer
  - ب) روز مادر
  - پ) روز کارگر
  - ت) روز پزشک

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - difficulty is overrated at 3; the item is fairly easy since Mehregan is the only obviously ancient festival among modern holidays
  - leakage risk slightly higher than rated given how commonly Mehregan appears in Persian cultural quizzes

---

#### `peval-public-culture-026`

**Prompt:** در فرهنگ گفتاری ایرانی، گفتن «قابل شما را ندارد» معمولا کجا به‌کار می‌رود؟

  - الف) هنگام عذرخواهی در محل کار
  - ب) هنگام تعارف در فروش یا هدیه دادن ← labelled answer
  - پ) هنگام تبریک گفتن
  - ت) هنگام پایان سخنرانی رسمی

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty slightly overrated; any Iranian adult would know this phrase
  - answer could theoretically also cover hospitality contexts, but 'تعارف' is broad enough to include them

---

#### `peval-public-culture-027`

**Prompt:** در ادبیات فارسی، «رباعی» قالب شعری با چند مصراع است؟

  - الف) دو
  - ب) سه
  - پ) چهار ← labelled answer
  - ت) پنج

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=2

**Issues:**
  - difficulty overrated at 3 — this is elementary knowledge for any educated Iranian
  - leakage risk underrated; this Q&A is ubiquitous in Persian educational materials

---

### `hard_culture` — 4 items

#### `peval-hard-culture-006`

**Prompt:** عبارت «خاک تو سرم» در گفت‌وگوی روزمره فارسی معمولا چه حسی را منتقل می‌کند؟

  - الف) تشویق و تحسین
  - ب) افسوس یا سرزنش خود ← labelled answer
  - پ) سلام و خوش‌آمد
  - ت) تشکر

**Rubric:** clarity=5, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Expression can occasionally be directed at others (not purely self-directed), but self-reproach/regret is the dominant everyday usage and the answer is correct
  - Difficulty may be slightly overrated at 3 — any native Persian speaker would find this trivial; 2 is more appropriate

---

#### `peval-hard-culture-007`

**Prompt:** وقتی میزبان ایرانی پس از غذا می‌گوید «نوش جان»، پاسخ ادب‌مند رایج چه می‌تواند باشد؟

  - الف) خواهش می‌کنم، شما هم نوش جان
  - ب) خدا حافظ
  - پ) دست شما درد نکند ← labelled answer
  - ت) ممنون از وقت‌تان

**Rubric:** clarity=5, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - Choice A ('خواهش می‌کنم، شما هم نوش جان') is mildly defensible as an alternative polite response, slightly raising ambiguity, but 'دست شما درد نکند' is clearly the most conventional answer in Iranian etiquette.
  - Choice B ('خدا حافظ') is laughably wrong and may make the item too easy by elimination.

---

#### `peval-hard-culture-011`

**Prompt:** در فرهنگ کاری ایران، اگر همکاری بگوید «در خدمتم»، چه برداشت محتمل‌تری دارد؟

  - الف) اعلام انتقال به شعبه دیگر
  - ب) خداحافظی نهایی از سازمان
  - پ) بیان آمادگی برای کمک یا گفت‌وگو ← labelled answer
  - ت) اعلام بازنشستگی

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty is labeled 3 but the phrase «در خدمتم» is extremely common and the answer is near-trivial for native Persian speakers; 2 is more accurate

---

#### `peval-hard-culture-023`

**Prompt:** در فارسی محاوره‌ای، اگر کسی بگوید «دستش به دهنش می‌رسد»، نزدیک‌ترین معنی چیست؟

  - الف) خیلی قد بلند است
  - ب) بسیار گرسنه است
  - پ) از نظر مالی نسبتا تامین است ← labelled answer
  - ت) نمی‌تواند غذا بخورد

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=3

---

### `hard_instruction` — 10 items

#### `peval-hard-instruction-010`

**Prompt:** یک پیام پشتیبانی برای کاربری که شکایت دارد سفارشش دیر رسیده بنویس. باید با «درست می‌فرمایید» شروع شود، شامل «جبران» باشد، علامت تعجب نداشته باشد، و طول بین ۱۰ تا ۳۵ کلمه.

**Constraints:** `{"required_prefix": "درست می‌فرمایید", "required_keywords": ["جبران"], "forbidden": ["!"], "min_words": 10, "max_words": 35}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - Difficulty may be slightly overrated at 4; constraints are satisfiable with a single well-formed sentence
  - Forbidden list only bans ASCII '!' — Persian/Unicode variants (e.g., '‼') are not explicitly excluded, though this is a minor edge case

---

#### `peval-hard-instruction-014`

**Prompt:** یک خلاصه فارسی برای پروفایل لینکدین یک مهندس نرم‌افزار جوان بنویس. باید با «مهندس» شروع شود، شامل «بک‌اند» و «همکاری تیمی» باشد، علامت تعجب نداشته باشد و طول بین ۲۰ تا ۵۰ کلمه.

**Constraints:** `{"required_prefix": "مهندس", "required_keywords": ["بک‌اند", "همکاری تیمی"], "forbidden": ["!"], "min_words": 20, "max_words": 50}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=4

**Issues:**
  - forbidden list only covers ASCII '!' and not full-width '！', though this is a minor edge case unlikely to affect evaluation

---

#### `peval-hard-instruction-016`

**Prompt:** یک هشدار فارسی برای یک کاربر که از مرورگر قدیمی استفاده می‌کند بنویس. باید با «برای امنیت بیشتر» شروع شود، شامل «به‌روزرسانی» و «مرورگر» باشد، نباید کلمه «حتما» داشته باشد و طول بین ۱۰ تا ۳۵ کلمه.

**Constraints:** `{"required_prefix": "برای امنیت بیشتر", "required_keywords": ["به‌روزرسانی", "مرورگر"], "forbidden": ["حتما"], "min_words": 10, "max_words": 35}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - difficulty rating of 4 seems slightly inflated; constraints are clear and non-conflicting, making this a moderate rather than hard instruction task

**Proposed changes:**
```json
{
  "notes": "All constraints are jointly satisfiable in Persian within the word bounds. No conflict between required_keywords and forbidden list. The prefix 'برای امنیت بیشتر' is idiomatic. Difficulty is more accurately 3 than 4, but this is a minor issue that does not affect item validity."
}
```

---

#### `peval-hard-instruction-018`

**Prompt:** یک متن فارسی برای فراخوان یک مسابقه عکاسی بنویس. باید با «مسابقه عکاسی» شروع شود، شامل «داوری» و «جایزه» باشد، نباید نقطه‌ویرگول داشته باشد و طول بین ۲۰ تا ۵۰ کلمه.

**Constraints:** `{"required_prefix": "مسابقه عکاسی", "required_keywords": ["داوری", "جایزه"], "forbidden": ["؛"], "min_words": 20, "max_words": 50}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - Forbidden character '؛' (Persian semicolon) is rarely used in natural Persian writing, making this constraint trivially easy and reducing effective difficulty
  - Difficulty rating of 4 seems slightly inflated; 3 is more appropriate given the generous word range and weak forbidden constraint

---

#### `peval-hard-instruction-021`

**Prompt:** یک متن فارسی درباره فایده پشتیبان‌گیری منظم از داده‌ها بنویس. باید با «پشتیبان‌گیری» شروع شود، شامل «از دست رفتن» و «بازیابی» باشد، نباید کلمه «همیشه» داشته باشد و طول بین ۱۵ تا ۴۵ کلمه.

**Constraints:** `{"required_prefix": "پشتیبان‌گیری", "required_keywords": ["از دست رفتن", "بازیابی"], "forbidden": ["همیشه"], "min_words": 15, "max_words": 45}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - Difficulty labeled as 4 but constraints are jointly satisfiable with moderate effort; 3 is more accurate
  - Forbidden word «همیشه» is naturally tempting in this context, which is a good design choice but doesn't push difficulty to expert level

---

#### `peval-hard-instruction-022`

**Prompt:** یک پاسخ فارسی به یک خبرنگار درباره علت رشد فروش شرکت بنویس. باید با «رشد فروش» شروع شود، شامل «بازار جدید» و «خدمات پس از فروش» باشد، نباید کلمه «صرفا» داشته باشد و طول بین ۱۸ تا ۵۰ کلمه.

**Constraints:** `{"required_prefix": "رشد فروش", "required_keywords": ["بازار جدید", "خدمات پس از فروش"], "forbidden": ["صرفا"], "min_words": 18, "max_words": 50}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - Difficulty rated 4 by author but constraints are jointly easy to satisfy; 3 is more accurate
  - Forbidden word «صرفا» is trivially avoidable in this business context and adds little challenge

---

#### `peval-hard-instruction-024`

**Prompt:** یک پاسخ فارسی برای یک کاربر که شکایت دارد فاکتورش با مبلغ سفارش نمی‌خواند بنویس. باید با «از تماس شما» شروع شود، شامل «بررسی فاکتور» و «پیگیری» باشد، نباید کلمه «قطعا» داشته باشد و طول بین ۱۵ تا ۴۵ کلمه.

**Constraints:** `{"required_prefix": "از تماس شما", "required_keywords": ["بررسی فاکتور", "پیگیری"], "forbidden": ["قطعا"], "min_words": 15, "max_words": 45}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - difficulty is rated 4 but constraints are jointly easy to satisfy; 3 is more accurate
  - forbidden word «قطعا» is trivially easy to avoid in a support-response context, reducing actual difficulty

---

#### `peval-hard-instruction-025`

**Prompt:** یک متن فارسی برای راهنمای کاربری ساده برای جست‌وجو در یک وب‌سایت بنویس. باید با «برای جست‌وجو» شروع شود، شامل «کادر بالا» و «دکمه جست‌وجو» باشد، علامت سوال نداشته باشد و طول بین ۱۵ تا ۴۰ کلمه.

**Constraints:** `{"required_prefix": "برای جست‌وجو", "required_keywords": ["کادر بالا", "دکمه جست‌وجو"], "forbidden": ["؟", "?"], "min_words": 15, "max_words": 40}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - Difficulty rated 4 by claude-review but constraints are comfortably satisfiable; 3 is more accurate

---

#### `peval-hard-instruction-026`

**Prompt:** یک هشدار فارسی برای کاربری که قصد ارسال اطلاعات حساس از طریق ایمیل دارد بنویس. باید با «هشدار» شروع شود، شامل «اطلاعات حساس» و «رمزنگاری» باشد، نباید کلمه «هرگز» داشته باشد و طول بین ۱۲ تا ۴۰ کلمه.

**Constraints:** `{"required_prefix": "هشدار", "required_keywords": ["اطلاعات حساس", "رمزنگاری"], "forbidden": ["هرگز"], "min_words": 12, "max_words": 40}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - difficulty slightly overrated at 4; constraints are clear and non-conflicting, making this more of a moderate task

**Proposed changes:**
```json
{
  "notes": "All constraints are jointly satisfiable and natural in Persian. The forbidden word «هرگز» does not conflict with required keywords. Word range 12–40 is realistic. Only minor concern is difficulty rating; 3 is more appropriate than 4 since the task is straightforward for a capable model."
}
```

---

#### `peval-hard-instruction-030`

**Prompt:** یک پاسخ کوتاه و دیپلماتیک به یک پیام انتقادی از یک مشتری بنویس. باید با «انتقاد شما» شروع شود، شامل «بازنگری» و «بهبود» باشد، نباید کلمه «اشتباه» داشته باشد و طول بین ۱۵ تا ۴۰ کلمه.

**Constraints:** `{"required_prefix": "انتقاد شما", "required_keywords": ["بازنگری", "بهبود"], "forbidden": ["اشتباه"], "min_words": 15, "max_words": 40}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=4

**Issues:**
  - No critical issues found; constraints are jointly satisfiable and realistic
  - Minor: prompt does not explicitly state the response language must be Persian, but this is strongly implied by context

---

### `hard_math` — 1 items

#### `peval-hard-math-009`

**Prompt:** اگر سه ضلع یک مثلث ۳، ۴ و ۵ سانتی‌متر باشد، مساحت آن مثلث چند سانتی‌متر مربع است؟

**Accepted answers:** ['۶', '6', 'شش']

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

---

### `hard_reasoning` — 13 items

#### `peval-hard-reasoning-008`

**Prompt:** اگر هیچ ماشین برقی به بنزین نیاز ندارد و خودروی شرکت ما برقی نیست، چه نتیجه قطعی می‌توان گرفت؟

  - الف) خودروی شرکت ما به بنزین نیاز دارد
  - ب) خودروی شرکت ما به بنزین نیاز ندارد
  - پ) هیچ خودرویی به بنزین نیاز ندارد
  - ت) نمی‌توان قطعا تصمیم گرفت ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=3

**Issues:**
  - Difficulty is overrated at 4; this is a standard syllogism trap, more like 3 for anyone with basic logic training
  - Leakage risk is slightly elevated because this syllogism pattern (electric car/gasoline) is a common logic exercise template
  - Choice A is tempting but not logically entailed — this is intentional and well-designed

---

#### `peval-hard-reasoning-011`

**Prompt:** اگر گزاره «هر دانشجوی فلسفه کتاب کانت را خوانده» درست باشد، کدام گزاره معادل آن است؟

  - الف) هر کس کتاب کانت را خوانده، دانشجوی فلسفه است
  - ب) هیچ دانشجوی فلسفه‌ای کتاب کانت را نخوانده
  - پ) هر کس کتاب کانت را نخوانده، دانشجوی فلسفه نیست ← labelled answer
  - ت) هیچ‌کس به‌جز دانشجویان فلسفه کانت را نمی‌خواند

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=4

---

#### `peval-hard-reasoning-017`

**Prompt:** در یک شرکت، هیچ کارمند جدیدی به اطلاعات حسابداری دسترسی ندارد. آرش به اطلاعات حسابداری دسترسی دارد. کدام نتیجه قطعی است؟

  - الف) آرش کارمند جدید نیست ← labelled answer
  - ب) آرش حسابدار است
  - پ) آرش رئیس شرکت است
  - ت) نمی‌توان نتیجه گرفت

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

---

#### `peval-hard-reasoning-018`

**Prompt:** اگر هر کس که در جلسه دیروز بوده دستور جلسه را گرفته باشد و سارا دستور جلسه را نگرفته، چه نتیجه قطعی می‌گیریم؟

  - الف) سارا در جلسه دیروز بوده ولی دستور را گم کرده
  - ب) سارا در جلسه دیروز نبوده است ← labelled answer
  - پ) سارا دستور را به‌زودی می‌گیرد
  - ت) نمی‌توان نتیجه گرفت

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=3

---

#### `peval-hard-reasoning-019`

**Prompt:** گروهی متشکل از هفت نفر است. حداقل چهار نفر زبان فرانسه می‌دانند و حداقل پنج نفر زبان انگلیسی می‌دانند. حداقل چند نفر هر دو زبان را می‌دانند؟

  - الف) یک نفر
  - ب) سه نفر
  - پ) دو نفر ← labelled answer
  - ت) چهار نفر

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=3

**Issues:**
  - Difficulty overrated at 4; this is a standard inclusion-exclusion problem, 3 is more appropriate
  - Leakage risk underrated at 1; classic pigeonhole/inclusion-exclusion problem type widely found in textbooks

---

#### `peval-hard-reasoning-022`

**Prompt:** اگر هر روز که جلسه برگزار می‌شود، گزارش جلسه در همان روز ارسال می‌شود، و پنجشنبه هیچ گزارشی ارسال نشد، چه نتیجه قطعی می‌گیریم؟

  - الف) پنجشنبه جلسه برگزار شد ولی گزارش به فردا موکول شد
  - ب) پنجشنبه جلسه‌ای برگزار نشد ← labelled answer
  - پ) هیچ‌گاه پنجشنبه جلسه برگزار نمی‌شود
  - ت) نمی‌توان نتیجه گرفت

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

---

#### `peval-hard-reasoning-023`

**Prompt:** گزاره‌های زیر با هم سازگارند یا ناسازگار؟ ۱) همه طوطی‌ها سخن می‌گویند. ۲) تونی یک طوطی است. ۳) تونی سخن نمی‌گوید.

  - الف) گزاره‌ها با هم سازگارند
  - ب) گزاره ۲ بی‌اثر است
  - پ) گزاره‌ها با هم ناسازگارند ← labelled answer
  - ت) تنها در صورت دانستن گونه طوطی می‌توان قضاوت کرد

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

---

#### `peval-hard-reasoning-024`

**Prompt:** اگر هر مدیر فروش باید گزارش هفتگی بدهد و تقی گزارش هفتگی نداده، چه نتیجه قطعی می‌گیریم؟

  - الف) نمی‌توان نتیجه گرفت
  - ب) تقی مدیر فروش است ولی گزارش گم شده
  - پ) تقی هفته آینده گزارش می‌دهد
  - ت) تقی مدیر فروش نیست ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=3

**Issues:**
  - Choice 1 ('گزارش گم شده') is a somewhat contrived distractor that introduces an unsupported premise, making it too obviously wrong
  - Choice 2 ('هفته آینده گزارش می‌دهد') is a weak distractor that doesn't engage with the logical structure, reducing item quality slightly

---

#### `peval-hard-reasoning-026`

**Prompt:** اگر بدانیم «بعضی پزشکان دانشمندند» و «همه دانشمندان مقاله می‌نویسند»، کدام نتیجه قطعی است؟

  - الف) همه پزشکان مقاله می‌نویسند
  - ب) بعضی پزشکان مقاله می‌نویسند ← labelled answer
  - پ) هیچ پزشکی مقاله نمی‌نویسد
  - ت) نمی‌توان نتیجه گرفت

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=3

**Issues:**
  - Classic syllogism form common in Persian logic textbooks — minor leakage risk

---

#### `peval-hard-reasoning-027`

**Prompt:** سه برادر به ترتیب سن از بزرگ به کوچک نام دارند: امیر، علی، آرش. اگر امیر بیست و هشت ساله و آرش بیست‌وچهار ساله باشد، سن علی می‌تواند کدام عدد نباشد؟

  - الف) بیست و پنج
  - ب) بیست و شش
  - پ) بیست و سه ← labelled answer
  - ت) بیست و هفت

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty may be slightly overestimated for 'hard' track — this is a straightforward bounded inference with no real complexity

---

#### `peval-hard-reasoning-028`

**Prompt:** اگر هر نشست بدون دستور کار به اضافه‌کار منجر شود و امروز اضافه‌کاری نشد، چه نتیجه قطعی می‌گیریم؟

  - الف) نشست با دستور کار برگزار شد
  - ب) هر نشست با دستور کار خوب پیش می‌رود
  - پ) نشستی برگزار نشد
  - ت) نشست امروز دستور کار داشت یا نشستی برگزار نشد ← labelled answer

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=1, difficulty=4

---

#### `peval-hard-reasoning-029`

**Prompt:** گفته شده «اگر بازاریابی تکمیل شود، فروش ماه آینده افزایش می‌یابد.» همچنین گفته شده «اگر فروش افزایش یابد، شرکت پاداش می‌دهد.» اگر شرکت پاداش نداد، چه نتیجه می‌گیریم؟

  - الف) بازاریابی حتما تکمیل نشده ← labelled answer
  - ب) فروش حتما افزایش یافته
  - پ) هر دو گزاره نقض می‌شوند
  - ت) نمی‌توان نتیجه گرفت

**Rubric:** clarity=5, ambiguity=1, cultural_fit=4, leakage_risk=2, difficulty=4

**Issues:**
  - Choice index 1 ('فروش حتما افزایش یافته') is not merely wrong but the logical opposite of what follows (¬R → ¬Q implies sales did NOT increase), making it a weak distractor for logically trained readers
  - The item is otherwise logically sound and the correct answer is unambiguous

---

#### `peval-hard-reasoning-030`

**Prompt:** اگر هر کاربر با اشتراک طلایی به بخش پیشرفته دسترسی دارد و هیچ مهمانی به بخش پیشرفته دسترسی ندارد، چه نتیجه قطعی می‌گیریم؟

  - الف) هر مهمان اشتراک طلایی دارد
  - ب) هیچ مهمانی اشتراک طلایی ندارد ← labelled answer
  - پ) هر کاربر طلایی مهمان است
  - ت) نمی‌توان نتیجه گرفت

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=4

---

### `instruction` — 17 items

#### `peval-public-instruction-005`

**Prompt:** یک پیام کوتاه فارسی برای دعوت دوستت به یک پیاده‌روی صبحگاهی بنویس که شامل کلمات «صبح» و «پارک» باشد و بین ۸ تا ۲۵ کلمه طول داشته باشد.

**Constraints:** `{"required_keywords": ["صبح", "پارک"], "min_words": 8, "max_words": 25}`

**Rubric:** clarity=5, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty is rated 3 in existing rubric but the task is quite simple (2 is more appropriate)

**Proposed changes:**
```json
{
  "notes": "All constraints are jointly satisfiable in Persian within the word bounds. Required keywords are natural and common. No forbidden list conflicts. The only minor issue is that difficulty 3 slightly overstates the challenge; 2 is more accurate for this simple invitation task."
}
```

---

#### `peval-public-instruction-006`

**Prompt:** یک توصیه کوتاه برای صرفه‌جویی در برق بنویس. پاسخ نباید شامل کلمه «همیشه» باشد و باید کلمه «لامپ» را داشته باشد. طول پاسخ بین ۶ تا ۳۰ کلمه.

**Constraints:** `{"required_keywords": ["لامپ"], "forbidden": ["همیشه"], "min_words": 6, "max_words": 30}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty is rated 3 but constraints are trivially satisfiable; 2 is more appropriate

---

#### `peval-public-instruction-008`

**Prompt:** یک جمله فارسی درباره فایده مطالعه بنویس که با «کتاب» پایان یابد و کلمه «دانش» را داشته باشد. حداکثر ۲۰ کلمه.

**Constraints:** `{"required_suffix": "کتاب", "required_keywords": ["دانش"], "min_words": 5, "max_words": 20}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty rated 3 but constraints are easily satisfiable; 2 is more accurate
  - Ending a Persian sentence naturally with the noun «کتاب» requires aphoristic/nominal sentence style, but this is achievable and common in Persian proverb-like writing

**Proposed changes:**
```json
{
  "notes": "Item is well-formed. Constraints are jointly satisfiable: a nominal/aphoristic Persian sentence such as «بهترین منبع دانش، کتاب» satisfies all conditions. The difficulty is slightly overestimated at 3; 2 is more appropriate. No other issues."
}
```

---

#### `peval-public-instruction-009`

**Prompt:** در یک پاراگراف کوتاه درباره صرفه‌جویی در آب بنویس. پاسخ باید شامل کلمات «آب» و «شیر» باشد و علامت سوال نداشته باشد. طول بین ۱۲ تا ۴۰ کلمه.

**Constraints:** `{"required_keywords": ["آب", "شیر"], "forbidden": ["؟", "?"], "min_words": 12, "max_words": 40}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty rating of 3 seems slightly high; constraints are straightforward and the task is simple for a fluent Persian speaker
  - «شیر» is polysemous but unambiguous in context — evaluators should accept any usage of the word

---

#### `peval-public-instruction-010`

**Prompt:** یک پیام کوتاه برای تشکر از یک همکار بنویس که شامل کلمه «همکاری» باشد و طول آن بین ۸ تا ۲۵ کلمه باشد. از کلمه «خیلی» استفاده نکن.

**Constraints:** `{"required_keywords": ["همکاری"], "forbidden": ["خیلی"], "min_words": 8, "max_words": 25}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty slightly overrated at 3; constraints are mild and easily satisfiable, closer to 2

---

#### `peval-public-instruction-011`

**Prompt:** یک توضیح کوتاه برای یک کودک هفت ساله درباره چرخه آب بنویس. باید کلمات «ابر» و «باران» را داشته باشد و طول بین ۱۰ تا ۳۵ کلمه.

**Constraints:** `{"required_keywords": ["ابر", "باران"], "min_words": 10, "max_words": 35}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty is rated 3 by author but task is relatively simple; 2 is more appropriate

---

#### `peval-public-instruction-012`

**Prompt:** یک معرفی کوتاه از خودت برای یک کلاس آنلاین فارسی بنویس که با «سلام» شروع شود و کلمه «هدف» را داشته باشد. طول بین ۱۰ تا ۳۰ کلمه.

**Constraints:** `{"required_prefix": "سلام", "required_keywords": ["هدف"], "min_words": 10, "max_words": 30}`

**Rubric:** clarity=5, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty rated 3 by original reviewer; more accurately 2 given the simple constraints and everyday topic.
  - reviewers list is empty and status is pending_review — administrative note only, not a content issue.

---

#### `peval-public-instruction-013`

**Prompt:** یک جمله انگیزشی برای یک دوست که در حال درس خواندن است بنویس. باید کلمه «امروز» را داشته باشد و کوتاه باشد. حداکثر ۱۸ کلمه.

**Constraints:** `{"required_keywords": ["امروز"], "min_words": 5, "max_words": 18}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty may be slightly overrated at 3; the task is simple with easy-to-satisfy constraints

---

#### `peval-public-instruction-014`

**Prompt:** یک توضیح کوتاه درباره فایده پیاده‌روی روزانه بنویس. پاسخ باید شامل کلمه «سلامت» باشد، نباید کلمه «همیشه» داشته باشد و طول بین ۸ تا ۳۰ کلمه باشد.

**Constraints:** `{"required_keywords": ["سلامت"], "forbidden": ["همیشه"], "min_words": 8, "max_words": 30}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Difficulty is slightly overrated at 3; the forbidden word 'همیشه' is unlikely to appear naturally in a walking-benefits text, making constraint satisfaction nearly trivial
  - Leakage risk is marginally higher than 1 since the topic is generic and the prompt structure is simple

---

#### `peval-public-instruction-017`

**Prompt:** یک توضیح کوتاه درباره کاربرد ایمیل در محیط کار بنویس که با «ایمیل» شروع شود و کلمه «ارتباط» را داشته باشد. طول بین ۸ تا ۲۸ کلمه.

**Constraints:** `{"required_prefix": "ایمیل", "required_keywords": ["ارتباط"], "min_words": 8, "max_words": 28}`

**Rubric:** clarity=5, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty is rated 3 by the author but the constraints are mild and non-conflicting, making this closer to a difficulty-2 item

---

#### `peval-public-instruction-021`

**Prompt:** یک توضیح کوتاه درباره مفهوم «تیم‌ورک» در محیط اداری بنویس. باید شامل «همکار» و «هدف مشترک» باشد. حداکثر ۳۵ کلمه.

**Constraints:** `{"required_keywords": ["همکار", "هدف مشترک"], "min_words": 10, "max_words": 35}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty slightly overrated at 3; task is straightforward with natural keywords and generous word limit

**Proposed changes:**
```json
{
  "notes": "Item is well-formed. Constraints are jointly satisfiable: both required keywords fit naturally in a teamwork description within 35 words. Only minor concern is difficulty rating — 2 is more appropriate than 3 given the simplicity of the topic and naturalness of the keywords."
}
```

---

#### `peval-public-instruction-023`

**Prompt:** یک یادداشت کوتاه برای یک همکار بنویس که توضیح می‌دهد امروز چرا دیر آمده‌ای. باید شامل کلمه «ترافیک» باشد و علامت تعجب نداشته باشد. حداکثر ۲۵ کلمه.

**Constraints:** `{"required_keywords": ["ترافیک"], "forbidden": ["!"], "min_words": 6, "max_words": 25}`

**Rubric:** clarity=5, ambiguity=2, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - Difficulty is slightly overrated at 3; constraints are simple and non-conflicting, making this closer to difficulty 2.
  - The forbidden list only includes ASCII '!' — consider whether the full-width or Arabic exclamation mark variants need to be listed, though in practice Persian writers use ASCII '!' so this is a minor point.

---

#### `peval-public-instruction-024`

**Prompt:** یک پیام کوتاه برای دعوت به یک نشست خانوادگی بنویس که با «خانواده» شروع شود و کلمه «جمعه» را داشته باشد. حداکثر ۲۵ کلمه.

**Constraints:** `{"required_prefix": "خانواده", "required_keywords": ["جمعه"], "min_words": 6, "max_words": 25}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty is rated 3 but the task is quite simple with minimal constraints — 2 is more accurate

**Proposed changes:**
```json
{
  "notes": "All constraints are jointly satisfiable and culturally natural. Friday (جمعه) is the Iranian weekend day, making it an ideal day for family gatherings. The only minor issue is a slight overestimate of difficulty."
}
```

---

#### `peval-public-instruction-027`

**Prompt:** یک یادداشت کوتاه برای معلم فرزندت بنویس که توضیح می‌دهد فردا فرزندت غایب است. باید با «سلام» شروع شود و کلمه «بیمار» را داشته باشد. حداکثر ۳۰ کلمه.

**Constraints:** `{"required_prefix": "سلام", "required_keywords": ["بیمار"], "min_words": 8, "max_words": 30}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty is slightly overrated at 3; task is simple with minimal constraints, more like a 2

---

#### `peval-public-instruction-028`

**Prompt:** یک پیام تشکر کوتاه از پزشک خانوادگی بنویس که شامل کلمه «صبر» باشد. حداکثر ۲۵ کلمه. نباید علامت سوال داشته باشد.

**Constraints:** `{"required_keywords": ["صبر"], "forbidden": ["؟", "?"], "min_words": 6, "max_words": 25}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty is arguably closer to 2 than 3 — the task is straightforward with generous word bounds

---

#### `peval-public-instruction-029`

**Prompt:** یک جمله درباره فایده ورزش صبحگاهی بنویس که با «ورزش» شروع شود و کلمه «انرژی» را داشته باشد. حداکثر ۲۵ کلمه.

**Constraints:** `{"required_prefix": "ورزش", "required_keywords": ["انرژی"], "min_words": 6, "max_words": 25}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty is slightly overrated at 3; the task is straightforward for any Persian speaker and 2 is more appropriate

---

#### `peval-public-instruction-030`

**Prompt:** یک پیام کوتاه برای راهنمایی نشانی به یک تاکسی‌اینترنتی بنویس. پاسخ باید شامل کلمه «خیابان» و «پلاک» باشد. حداکثر ۳۰ کلمه.

**Constraints:** `{"required_keywords": ["خیابان", "پلاک"], "min_words": 8, "max_words": 30}`

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=1, difficulty=2

**Issues:**
  - difficulty slightly overrated at 3; task is straightforward for any competent Persian speaker

---

### `knowledge` — 8 items

#### `peval-public-knowledge-005`

**Prompt:** دومین شهر پرجمعیت ایران بعد از تهران معمولا کدام شهر است؟

  - الف) مشهد ← labelled answer
  - ب) اصفهان
  - پ) شیراز
  - ت) تبریز

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - difficulty is slightly overrated at 3; this is common knowledge for most Iranians and should be 2
  - leakage_risk of 1 seems too low for a well-known geographic fact, though the specific phrasing appears original

---

#### `peval-public-knowledge-007`

**Prompt:** مرکز استان فارس کدام شهر است؟

  - الف) یزد
  - ب) اهواز
  - پ) شیراز ← labelled answer
  - ت) کرمان

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=2

**Issues:**
  - difficulty overrated at 3; this is basic Iranian geography known to most Persian speakers, 2 is more appropriate
  - leakage_risk underrated at 1; standard geography question likely appears in many public quiz sources

---

#### `peval-public-knowledge-013`

**Prompt:** در سیستم بین‌المللی یکاها، یکای پایه برای دما کدام است؟

  - الف) کلوین ← labelled answer
  - ب) فارنهایت
  - پ) سلسیوس
  - ت) رانکین

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=4, difficulty=2

**Issues:**
  - Difficulty overrated at 3; this is standard middle-school science knowledge, more like 2
  - Leakage risk underrated at 1; this is a classic textbook question widely available in Persian physics resources
  - Rankine (رانکین) is an obscure distractor that most test-takers will never have encountered, slightly weakening the distractor set

---

#### `peval-public-knowledge-015`

**Prompt:** بخش عمده جرم خورشید را کدام عنصر تشکیل می‌دهد؟

  - الف) هلیوم
  - ب) اکسیژن
  - پ) هیدروژن ← labelled answer
  - ت) کربن

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - difficulty is overrated at 3; this is basic middle-school science knowledge, more appropriate at 2

---

#### `peval-public-knowledge-019`

**Prompt:** سیستم‌عامل اوبونتو بر پایه کدام خانواده ساخته شده است؟

  - الف) مک‌اواس
  - ب) ویندوز
  - پ) لینوکس ← labelled answer
  - ت) بی‌اس‌دی

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=4, difficulty=2

**Issues:**
  - Difficulty is overrated at 3; this is basic tech knowledge, closer to 2
  - Leakage risk is underrated at 1; this exact question appears in many Persian tech quizzes online

---

#### `peval-public-knowledge-021`

**Prompt:** جنبش مشروطه در ایران رسما در دوره کدام سلسله اعلام شد؟

  - الف) قاجاریه ← labelled answer
  - ب) افشاریه
  - پ) زندیه
  - ت) صفویه

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - Difficulty slightly overrated at 3; this is basic Iranian history knowledge, more appropriate at 2
  - Leakage risk slightly elevated as this is a standard textbook question

---

#### `peval-public-knowledge-022`

**Prompt:** کوروش بزرگ بنیان‌گذار کدام سلسله ایرانی شناخته می‌شود؟

  - الف) ساسانی
  - ب) هخامنشی ← labelled answer
  - پ) اشکانی
  - ت) ماد

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=3, difficulty=2

**Issues:**
  - Difficulty slightly overrated — this is elementary-school-level Iranian history
  - Leakage risk is moderate; exact phrasing likely appears in Persian textbooks

---

#### `peval-public-knowledge-025`

**Prompt:** رودکی معمولا با کدام عنوان شناخته می‌شود؟

  - الف) پدر شعر فارسی ← labelled answer
  - ب) لسان‌الغیب
  - پ) خداوندگار غزل
  - ت) حکیم طوس

**Rubric:** clarity=5, ambiguity=1, cultural_fit=5, leakage_risk=2, difficulty=2

**Issues:**
  - difficulty slightly overrated at 3; this is a basic fact from Iranian middle-school literature curriculum
  - distractor 'خداوندگار غزل' is not a well-known epithet for any specific poet, making it a weaker distractor compared to the others

---


