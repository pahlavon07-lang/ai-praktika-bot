# Python Final Exam — yechimlar

| Fayl | Nima |
|---|---|
| `Final_Exam_solution.py` | 5 ta topshiriqning to'liq kodi |
| `javoblar.txt` | Skript ishga tushirilganda chiqqan natijalar (javoblar) |
| `titanic.csv`, `customer_orders.csv` | Kerakli ma'lumot fayllari |

## Ishga tushirish

```bash
pip install pandas
python Final_Exam_solution.py                # hammasi avtomatik ishlaydi
python Final_Exam_solution.py --interactive  # Task 3 da input() so'raydi
```

## Qisqacha javoblar

- **Task 1** — `digit_sum(24) = 6`, `digit_sum(502) = 7`
- **Task 2** — `is_prime(n)`: 1 tub emas, bo'luvchilar faqat `sqrt(n)` gacha tekshiriladi
- **Task 3** — `roster.db` bazasida `Roster(Name TEXT, Species TEXT, Age INTEGER)` jadvali,
  3 ta yozuv + `input()` orqali yangisi qo'shiladi
- **Task 4** — Titanic (891 qator):
  - `SibSp > 0` **va** `Parch > 0`: **142 ta** yo'lovchi
  - yoshi `<= 15` va omon qolmagan: **34 ta** yo'lovchi
- **Task 5** — customer_orders.csv (100 qator):
  - `>= 20` ta buyurtma bergan mijozlar: **101, 102, 103, 104** (105 da 18 ta — chiqarib tashlandi)
  - o'rtacha birlik narxi `> $120`: **102 ($138.10)** va **104 ($169.75)**

> Eslatma: topshiriq matnida `Survived: 0 for yes and 1 for no` deyilgan, lekin haqiqiy
> Titanic datasetida `1 = omon qolgan`, `0 = omon qolmagan`. Kodda standart konvensiya
> ishlatilgan (`NOT_SURVIVED = 0`) — kerak bo'lsa shu konstantani o'zgartirish yetarli.
