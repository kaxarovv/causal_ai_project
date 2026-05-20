import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ── Загрузка данных ──────────────────────────────────────────
df = pd.read_csv("../data/history.csv", on_bad_lines="skip")

# ── Метрики ──────────────────────────────────────────────────
saved_kwh = (df["naive_power"] - df["power"]).sum()
saved_pct = saved_kwh / df["naive_power"].sum() * 100
avg_your  = df["power"].mean()
avg_naive = df["naive_power"].mean()
avg_pue   = df["pue"].mean()

print("=" * 40)
print(f"Тиков данных:          {len(df)}")
print(f"Экономия энергии:      {saved_pct:.1f}%")
print(f"Сэкономлено кВт:       {saved_kwh:.1f}")
print(f"Ср. мощность Causal:   {avg_your:.1f} кВт")
print(f"Ср. мощность наивной:  {avg_naive:.1f} кВт")
print(f"Средний PUE:           {avg_pue:.3f}")
print("=" * 40)

# ── Агрегация в 8 точек ──────────────────────────────────────
df["group"] = pd.cut(df.index, bins=8, labels=range(8))
grouped = df.groupby("group", observed=True)[["power", "naive_power"]].mean()
t = np.arange(1, 9)

# ── Графики ──────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Энергияны үнемдеу: Causal AI және Naive Systems", fontsize=14)

# График 1: линейный — мощность во времени
ax1.plot(t, grouped["naive_power"].values, "r-o", label="Naive (fan=80%)")
ax1.plot(t, grouped["power"].values,       "g-o", label="Causal AI")
ax1.fill_between(t,
                 grouped["naive_power"].values,
                 grouped["power"].values,
                 alpha=0.15, color="green", label="Үнемдеу аймағы")
ax1.set_title("Уақыт бойынша энергия тұтыну")
ax1.set_xlabel("Уақыт кезеңі")
ax1.set_ylabel("Қуат (кВт)")
ax1.legend()
ax1.grid(True, linestyle="--", alpha=0.5)

# График 2: столбчатый — сравнение средней мощности
bars = ax2.bar(
    ["Naive\n(fan=80%)", "Causal AI"],
    [avg_naive, avg_your],
    color=["red", "green"],
    width=0.4
)
for bar, val in zip(bars, [avg_naive, avg_your]):
    ax2.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 0.3,
             f"{val:.1f} кВт",
             ha="center", fontsize=12, fontweight="bold")

ax2.set_title("Орташа қуат")
ax2.set_ylabel("кВт")
ax2.set_ylim(avg_your - 15, avg_naive + 10)
ax2.grid(axis="y", linestyle="--", alpha=0.5)
# ax2.text(0.5, 0.5,
#          f"Э\n{saved_pct:.1f}%",
#          ha="center", fontsize=13, fontweight="bold", color="green",
#          transform=ax2.transAxes)

plt.tight_layout()
plt.savefig("energy_savings_2.png", dpi=150, bbox_inches="tight")
print("\nГрафик сохранён: energy_savings.png")
plt.show()