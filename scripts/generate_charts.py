import os
import matplotlib.pyplot as plt
import numpy as np

# Ensure assets directory exists
os.makedirs("assets", exist_ok=True)

# 1. Total Annual Operational Cost
plt.figure(figsize=(8, 6))
bars = plt.bar(
    ["Manual Process\n(Old)", "Automated Process\n(New)"],
    [19.5, 6.4],
    width=0.5,
    color=["#ff9999", "#99ff99"],
    edgecolor="black",
)
plt.bar(
    ["Automated Process\n(New)"], [3.9], width=0.5, color="#ff9999", edgecolor="black"
)  # Stacked base

plt.title("Total Annual Operational Cost", fontsize=14, fontweight="bold")
plt.ylabel("Annual Cost (₹ Lakhs)", fontsize=12)
plt.ylim(0, 25)

plt.text(0, 20.2, "₹19.5L", ha="center", fontsize=12, fontweight="bold")
plt.text(
    1, 7.1, "₹6.4L\n(-67%)", ha="center", fontsize=12, fontweight="bold", color="green"
)

# Adding legend manually
from matplotlib.patches import Patch

legend_elements = [
    Patch(facecolor="#ff9999", edgecolor="black", label="Labor Cost"),
    Patch(facecolor="#99ff99", edgecolor="black", label="Software/Maintenance Cost"),
]
plt.legend(handles=legend_elements, loc="upper right")
plt.tight_layout()
plt.savefig("assets/operational_cost.png", dpi=300)
plt.close()

# 2. Year 1 Financial Flow & Payback
plt.figure(figsize=(10, 6))
months = np.arange(0, 13)
# Straight line from -7.5 to 8.1 (Total delta 15.6)
cash_flow = -7.5 + (15.6 / 12) * months

plt.plot(months, cash_flow, marker="o", color="#2ca02c", linewidth=2.5)
plt.axhline(0, color="black", linestyle="--")
plt.fill_between(
    months, cash_flow, 0, where=(cash_flow < 0), color="#eadddd", interpolate=True
)
plt.fill_between(
    months, cash_flow, 0, where=(cash_flow > 0), color="#d4e6d4", interpolate=True
)

plt.title("Year 1 Financial Flow & Payback", fontsize=14, fontweight="bold")
plt.xlabel("Months (Year 1)", fontsize=12)
plt.ylabel("Cumulative Cash Flow (₹ Lakhs)", fontsize=12)
plt.xticks(months)

# Break even annotation
plt.axvline(7.5 / (15.6 / 12), color="red", linestyle=":")
plt.annotate(
    "Break-even\n(4.6 Months)",
    xy=(4.6, -0.1),
    xytext=(5.5, -2.5),
    arrowprops=dict(facecolor="black", width=1.5, headwidth=6),
    fontsize=10,
    fontweight="bold",
    color="red",
)

# Net profit annotation
plt.annotate(
    "Net Profit:\n₹8.1L",
    xy=(12, 8.1),
    xytext=(9.5, 4.5),
    arrowprops=dict(facecolor="black", width=1.5, headwidth=6),
    fontsize=10,
    fontweight="bold",
    color="green",
)

plt.tight_layout()
plt.savefig("assets/payback_period.png", dpi=300)
plt.close()

# 3. Annual EBITDA Transformation
plt.figure(figsize=(8, 6))
categories = ["Gross Labor Savings", "Software OPEX", "Net EBITDA Uplift"]
values = [15.6, -2.5, 13.1]
colors = ["#2ca02c", "#d62728", "#2ca02c"]

bars = plt.bar(categories, values, width=0.5, color=colors, edgecolor="black")
plt.axhline(0, color="black", linewidth=1)

plt.title("Annual EBITDA Transformation", fontsize=14, fontweight="bold")
plt.ylabel("Impact (₹ Lakhs)", fontsize=12)
plt.ylim(-4, 18)

plt.text(0, 16.3, "₹15.6L", ha="center", fontsize=12, fontweight="bold")
plt.text(1, -4.3, "₹-2.5L", ha="center", fontsize=12, fontweight="bold")
plt.text(2, 13.8, "₹13.1L", ha="center", fontsize=12, fontweight="bold")

plt.tight_layout()
plt.savefig("assets/ebitda_impact.png", dpi=300)
plt.close()

# 4. Year 1 Investment vs. Net Profit
plt.figure(figsize=(8, 6))
labels = ["Total Y1 Investment", "Y1 Net Profit"]
values = [7.5, 8.1]
colors = ["#1f77b4", "#2ca02c"]

plt.bar(labels, values, width=0.5, color=colors, edgecolor="black")
plt.title("Year 1 Investment vs. Net Profit", fontsize=14, fontweight="bold")
plt.ylabel("Value (₹ Lakhs)", fontsize=12)
plt.ylim(0, 12)

plt.text(0, 7.9, "₹7.5L", ha="center", fontsize=12, fontweight="bold")
plt.text(1, 8.5, "₹8.1L", ha="center", fontsize=12, fontweight="bold")

bbox_props = dict(boxstyle="round,pad=0.3", fc="yellow", ec="orange", lw=2)
plt.text(
    0.5,
    10.5,
    "Year 1 ROI: 108%",
    ha="center",
    va="center",
    size=15,
    bbox=bbox_props,
    fontweight="bold",
)

plt.tight_layout()
plt.savefig("assets/roi_summary.png", dpi=300)
plt.close()

print("Charts generated successfully.")
