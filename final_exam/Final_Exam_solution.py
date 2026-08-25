# ----- Python Final Exam — YECHIMLAR (Solutions) -----
#
# Ishga tushirish / How to run:
#     cd final_exam
#     pip install pandas
#     python Final_Exam_solution.py
#
# Task 3 uchun yangi yozuv kiritish (interaktiv rejim):
#     python Final_Exam_solution.py --interactive
#
# Kerakli fayllar (shu papkada bo'lishi kerak):
#     titanic.csv, customer_orders.csv

import os
import sqlite3
import sys

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TITANIC_CSV = os.path.join(BASE_DIR, "titanic.csv")
ORDERS_CSV = os.path.join(BASE_DIR, "customer_orders.csv")
ROSTER_DB = os.path.join(BASE_DIR, "roster.db")

# Interaktiv rejim: faqat "--interactive" bayrog'i berilganda input() so'raladi.
INTERACTIVE = "--interactive" in sys.argv


def ask_int(prompt):
    """Butun son kiritilguncha qayta so'raydi (noto'g'ri kiritishda yiqilmaydi)."""
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print(f"   ! '{raw}' butun son emas, qaytadan kiriting.")


def banner(text):
    print("\n" + "=" * 90)
    print(text)
    print("=" * 90)


# ======================================================================================
# TASK 1 — digit_sum(k): sonning raqamlari yig'indisi
# ======================================================================================
def digit_sum(k):
    """k sonining raqamlari yig'indisini qaytaradi.

    Manfiy son ham qabul qilinadi (ishorasi hisobga olinmaydi).
    Misol: digit_sum(24) -> 6, digit_sum(502) -> 7
    """
    k = abs(int(k))
    total = 0
    while k > 0:
        total += k % 10   # oxirgi raqamni olamiz
        k //= 10          # oxirgi raqamni tashlab yuboramiz
    return total


# Muqobil (qisqa) variant:
def digit_sum_short(k):
    return sum(int(digit) for digit in str(abs(int(k))))


def run_task1():
    banner("TASK 1 — digit_sum(k)")
    for value in (24, 502, 0, 7, 9999, 123456, -389):
        print(f"digit_sum({value:>7}) = {digit_sum(value):>3}   "
              f"(tekshiruv: {digit_sum_short(value)})")


# ======================================================================================
# TASK 2 — is_prime(n): tub son ekanini aniqlash
# ======================================================================================
def is_prime(n):
    """n (n > 0) tub son bo'lsa True, aks holda False qaytaradi.

    1 tub son emas. 2 — yagona juft tub son.
    Bo'luvchilarni faqat sqrt(n) gacha tekshiramiz — O(sqrt(n)).
    """
    n = int(n)
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2   # faqat toq bo'luvchilar
    return True


def run_task2():
    banner("TASK 2 — is_prime(n)")
    for value in (1, 2, 3, 4, 9, 13, 17, 25, 29, 97, 100, 7919):
        print(f"is_prime({value:>5}) = {is_prime(value)}")
    print("\n2..50 oralig'idagi tub sonlar:",
          [x for x in range(2, 51) if is_prime(x)])


# ======================================================================================
# TASK 3 — SQLite: Roster jadvali (Name TEXT, Species TEXT, Age INTEGER)
# ======================================================================================
def run_task3():
    banner("TASK 3 — SQLite: Roster jadvali")

    connection = sqlite3.connect(ROSTER_DB)
    cursor = connection.cursor()

    # 1) Yangi baza va Roster jadvalini yaratamiz.
    cursor.execute("DROP TABLE IF EXISTS Roster")
    cursor.execute(
        """
        CREATE TABLE Roster (
            Name    TEXT,
            Species TEXT,
            Age     INTEGER
        )
        """
    )

    # 2) Jadvalni berilgan qiymatlar bilan to'ldiramiz.
    people = [
        ("Benjamin Sisko", "Human", 40),
        ("Jadzia Dax", "Trill", 300),
        ("Kira Nerys", "Bajoran", 29),
    ]
    cursor.executemany(
        "INSERT INTO Roster (Name, Species, Age) VALUES (?, ?, ?)", people
    )
    connection.commit()

    print("Boshlang'ich jadval:")
    for row in cursor.execute("SELECT Name, Species, Age FROM Roster"):
        print(f"   {row[0]:<16} | {row[1]:<8} | {row[2]:>3}")

    # 3) input() orqali yangi ma'lumot qo'shamiz.
    if INTERACTIVE:
        print("\nYangi yozuv kiriting:")
        name = input("   Name    : ").strip()
        species = input("   Species : ").strip()
        age = ask_int("   Age     : ")
    else:
        # Interaktiv bo'lmagan rejimda namuna yozuv ishlatiladi,
        # shunda skript avtomatik ham ishlay oladi.
        name, species, age = "Miles O'Brien", "Human", 45
        print(f"\n[demo rejim] input() o'rniga namuna yozuv qo'shildi: "
              f"{name} | {species} | {age}")
        print("   (real input uchun: python Final_Exam_solution.py --interactive)")

    cursor.execute(
        "INSERT INTO Roster (Name, Species, Age) VALUES (?, ?, ?)",
        (name, species, age),
    )
    connection.commit()

    print("\nYangilangan jadval:")
    for row in cursor.execute("SELECT Name, Species, Age FROM Roster"):
        print(f"   {row[0]:<16} | {row[1]:<8} | {row[2]:>3}")

    connection.close()
    print(f"\nBaza fayli saqlandi: {os.path.basename(ROSTER_DB)}")


# ======================================================================================
# TASK 4 — Titanic (pandas)
# ======================================================================================
# DIQQAT: topshiriq matnida "Survived: 0 for yes and 1 for no" deb yozilgan, lekin
# haqiqiy Titanic datasetida aksincha: 1 = omon qolgan, 0 = omon qolmagan.
# Quyida standart (haqiqiy) konvensiya ishlatilgan: NOT_SURVIVED = 0.
# Agar topshiriq matnidagi izoh bo'yicha hisoblash kerak bo'lsa, 1 ga o'zgartiring.
NOT_SURVIVED = 0


def run_task4():
    banner("TASK 4 — Titanic")

    df = pd.read_csv(TITANIC_CSV)
    print(f"Dataset o'lchami: {df.shape[0]} qator, {df.shape[1]} ustun")

    # 4.1) Ham aka-uka/turmush o'rtog'i, ham ota-ona/farzandi bo'lgan yo'lovchilar.
    with_family = df[(df["SibSp"] > 0) & (df["Parch"] > 0)]
    print(f"\n4.1) SibSp > 0 VA Parch > 0 bo'lgan yo'lovchilar: "
          f"{len(with_family)} ta")
    print(with_family[["PassengerId", "Name", "Sex", "Age",
                       "SibSp", "Parch", "Survived"]].head(10).to_string(index=False))

    # 4.2) Yoshi 15 va undan kichik, omon qolmagan yo'lovchilar.
    young_not_survived = df[(df["Age"] <= 15) & (df["Survived"] == NOT_SURVIVED)]
    print(f"\n4.2) Yoshi <= 15 va omon qolmagan yo'lovchilar: "
          f"{len(young_not_survived)} ta")
    print(young_not_survived[["PassengerId", "Name", "Sex", "Age",
                              "Pclass", "Survived"]].head(10).to_string(index=False))

    return with_family, young_not_survived


# ======================================================================================
# TASK 5 — customer_orders.csv (pandas groupby / filter)
# ======================================================================================
def run_task5():
    banner("TASK 5 — customer_orders.csv")

    df = pd.read_csv(ORDERS_CSV)
    print(f"Dataset o'lchami: {df.shape[0]} qator, {df.shape[1]} ustun")

    # 5.1) CustomerID bo'yicha guruhlash va 20 tadan kam buyurtma bergan
    #      mijozlarni chiqarib tashlash.
    orders_per_customer = df.groupby("CustomerID")["OrderID"].count()
    print("\nHar bir mijozdagi buyurtmalar soni:")
    print(orders_per_customer.to_string())

    active_customers = df.groupby("CustomerID").filter(lambda g: len(g) >= 20)
    kept_ids = sorted(int(cid) for cid in active_customers["CustomerID"].unique())
    print(f"\n5.1) >= 20 ta buyurtma bergan mijozlar: {kept_ids}")
    print(f"     Qolgan qatorlar soni: {len(active_customers)} "
          f"(boshlang'ich: {len(df)})")

    # 5.2) Birlik narxining o'rtachasi $120 dan yuqori bo'lgan mijozlar.
    avg_price = df.groupby("CustomerID")["Price"].mean()
    expensive = avg_price[avg_price > 120]
    print("\nHar bir mijozning o'rtacha birlik narxi:")
    print(avg_price.round(2).to_string())
    print(f"\n5.2) O'rtacha birlik narxi > $120 bo'lgan mijozlar: "
          f"{sorted(int(cid) for cid in expensive.index)}")
    print(expensive.round(2).to_string() if len(expensive) else "     (yo'q)")

    return active_customers, expensive


def main():
    run_task1()
    run_task2()
    run_task3()
    run_task4()
    run_task5()
    banner("Barcha topshiriqlar bajarildi.")


if __name__ == "__main__":
    main()
