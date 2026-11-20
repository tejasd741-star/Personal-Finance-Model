import csv
import os
import random
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd

DATA_FILE = "expenses.csv"
FIELDNAMES: List[str] = ["id", "date", "category", "payment_mode", "amount", "notes"]

# Tuple data structure: immutable allowed values
VALID_CATEGORIES: Tuple[str, ...] = (
    "Food & Dining",
    "Rent & Hostel",
    "Transport",
    "Groceries",
    "Utilities",
    "Education",
    "Entertainment",
    "Healthcare",
)
VALID_PAYMENT_MODES: Tuple[str, ...] = (
    "UPI",
    "Debit Card",
    "Credit Card",
    "Cash",
    "NetBanking",
)


def print_banner(title: str) -> None:
    """Display a clean section banner in the terminal."""
    line = "=" * 72
    print(f"\n{line}\n{title.center(72)}\n{line}")


def print_subbanner(subtitle: str) -> None:
    """Display a sub-section header."""
    print(f"\n--- {subtitle} ---")


def print_records_table(records: List[Dict[str, object]], max_rows: int = 60) -> None:
    """Print expense records in a readable terminal table."""
    if not records:
        print("No records found.")
        return

    header = (
        f"{'ID':<6} {'Date':<12} {'Category':<15} "
        f"{'Payment':<12} {'Amount (INR)':>13} {'Notes':<22}"
    )
    print(header)
    print("-" * len(header))

    for rec in records[:max_rows]:
        note_str = str(rec.get("notes", ""))[:20]
        print(
            f"{str(rec['id']):<6} "
            f"{str(rec['date']):<12} "
            f"{str(rec['category']):<15} "
            f"{str(rec['payment_mode']):<12} "
            f"{float(rec['amount']):>13.2f} "
            f"{note_str:<22}"
        )

    if len(records) > max_rows:
        print(f"... ({len(records) - max_rows} more records not shown; showing first {max_rows})")


def seed_dataset_if_missing(filepath: str = DATA_FILE, num_records: int = 55) -> None:
    """Generate a realistic 55-record personal finance CSV dataset if it does not exist."""
    if os.path.exists(filepath):
        return

    random.seed(42)
    sample_notes: Dict[str, List[str]] = {
        "Food & Dining": ["Lunch mess/cafe", "Evening snacks", "Coffee & bite", "Dinner with friends"],
        "Rent & Hostel": ["Monthly accommodation", "Maintenance fee", "Room deposit share"],
        "Transport": ["Metro card recharge", "Auto commute", "Bus ticket", "Cab ride"],
        "Groceries": ["Fruits & veggies", "Dairy & eggs", "Pulses & grains", "Weekly provisions"],
        "Utilities": ["Electricity bill", "Mobile data plan", "Broadband share", "Water charge"],
        "Education": ["Reference book", "Exam registration", "Lab printouts", "Online course"],
        "Entertainment": ["Movie ticket", "Streaming subscription", "Weekend outing"],
        "Healthcare": ["Pharmacy medicine", "Doctor consultation", "Health checkup"],
    }

    amount_ranges: Dict[str, Tuple[float, float]] = {
        "Food & Dining": (80.0, 650.0),
        "Rent & Hostel": (3500.0, 9500.0),
        "Transport": (40.0, 550.0),
        "Groceries": (250.0, 1800.0),
        "Utilities": (200.0, 1600.0),
        "Education": (150.0, 2500.0),
        "Entertainment": (199.0, 1200.0),
        "Healthcare": (120.0, 1500.0),
    }

    records: List[Dict[str, object]] = []
    for i in range(1, num_records + 1):
        month = 9 + ((i - 1) % 3)  # Sep, Oct, Nov 2026
        day = 1 + ((i * 3) % 28)
        date_str = f"2026-{month:02d}-{day:02d}"

        category = VALID_CATEGORIES[i % len(VALID_CATEGORIES)]
        payment_mode = VALID_PAYMENT_MODES[(i * 2) % len(VALID_PAYMENT_MODES)]
        low, high = amount_ranges[category]
        amount = round(random.uniform(low, high), 2)

        # Intentionally leave two blank notes to demonstrate missing-value handling
        note = "" if i in (12, 37) else random.choice(sample_notes[category])

        record: Dict[str, object] = {
            "id": f"EXP{i:03d}",
            "date": date_str,
            "category": category,
            "payment_mode": payment_mode,
            "amount": amount,
            "notes": note,
        }
        records.append(record)  # List method: .append()

    save_records(records, filepath)


def save_records(records: List[Dict[str, object]], filepath: str = DATA_FILE) -> None:
    """Write expense records back to CSV."""
    with open(filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        for rec in records:
            writer.writerow({col: rec.get(col, "") for col in FIELDNAMES})


def load_records(filepath: str = DATA_FILE) -> List[Dict[str, object]]:
    """Read expense records from CSV into a list of dictionaries."""
    seed_dataset_if_missing(filepath)
    records: List[Dict[str, object]] = []

    with open(filepath, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                amt = float(row["amount"])
            except (ValueError, TypeError):
                amt = 0.0
            records.append(
                {
                    "id": row["id"].strip(),
                    "date": row["date"].strip(),
                    "category": row["category"].strip(),
                    "payment_mode": row["payment_mode"].strip(),
                    "amount": amt,
                    "notes": row.get("notes", "").strip(),
                }
            )
    return records


def get_unique_metadata(records: List[Dict[str, object]]) -> Tuple[Set[str], Set[str]]:
    """Use set data structures to extract unique categories and payment modes."""
    unique_categories: Set[str] = set()
    unique_modes: Set[str] = set()

    for rec in records:
        unique_categories.add(str(rec["category"]))
        unique_modes.add(str(rec["payment_mode"]))

    return unique_categories, unique_modes


def add_record(
    records: List[Dict[str, object]],
    date: str,
    category: str,
    payment_mode: str,
    amount: float,
    notes: str = "",
) -> Dict[str, object]:
    """Add a new expense record to the list and save to CSV."""
    next_num = len(records) + 1
    existing_ids = {str(r["id"]) for r in records}
    new_id = f"EXP{next_num:03d}"
    while new_id in existing_ids:
        next_num += 1
        new_id = f"EXP{next_num:03d}"

    new_record: Dict[str, object] = {
        "id": new_id,
        "date": date.strip(),
        "category": category.strip(),
        "payment_mode": payment_mode.strip(),
        "amount": round(float(amount), 2),
        "notes": notes.strip(),
    }
    records.append(new_record)
    save_records(records)
    return new_record


def search_records(records: List[Dict[str, object]], keyword: str) -> List[Dict[str, object]]:
    """Search records by ID, category, payment mode, date, or notes."""
    term = keyword.strip().lower()
    if not term:
        return []

    matches: List[Dict[str, object]] = []
    for rec in records:
        combined = " ".join(str(val).lower() for _, val in rec.items())  # dict.items()
        if term in combined:
            matches.append(rec)
    return matches


def update_record(
    records: List[Dict[str, object]],
    record_id: str,
    updates: Dict[str, object],
) -> Optional[Dict[str, object]]:
    """Update an existing record matched by ID and persist to CSV."""
    target_id = record_id.strip().upper()
    for rec in records:
        if str(rec["id"]).upper() == target_id:
            for field in updates.keys():  # dict.keys()
                if field in FIELDNAMES and field != "id":
                    if field == "amount":
                        rec[field] = round(float(updates[field]), 2)
                    else:
                        rec[field] = str(updates[field]).strip()
            save_records(records)
            return rec
    return None


def delete_record(records: List[Dict[str, object]], record_id: str) -> Optional[Dict[str, object]]:
    """Delete a record by ID using list.pop() and persist to CSV."""
    target_id = record_id.strip().upper()
    for idx, rec in enumerate(records):
        if str(rec["id"]).upper() == target_id:
            removed = records.pop(idx)  # List method: .pop()
            save_records(records)
            return removed
    return None


def run_numpy_analysis(df: pd.DataFrame) -> Dict[str, object]:
    """Perform 1D/2D NumPy array operations, indexing, slicing, and statistics."""
    amounts_1d: np.ndarray = df["amount"].to_numpy(dtype=np.float64)

    total_spend = float(np.sum(amounts_1d))
    avg_spend = float(np.mean(amounts_1d))
    max_spend = float(np.max(amounts_1d))
    min_spend = float(np.min(amounts_1d))
    std_spend = float(np.std(amounts_1d, ddof=1))

    first_five_slice = amounts_1d[:5]
    tenth_element = float(amounts_1d[9]) if len(amounts_1d) > 9 else float(amounts_1d[0])

    matrix_2d: np.ndarray = np.column_stack((amounts_1d, np.square(amounts_1d)))
    second_col_slice = matrix_2d[0:4, 1]

    return {
        "total": total_spend,
        "mean": avg_spend,
        "max": max_spend,
        "min": min_spend,
        "std": std_spend,
        "shape_1d": amounts_1d.shape,
        "shape_2d": matrix_2d.shape,
        "first_five_slice": first_five_slice,
        "tenth_element": tenth_element,
        "second_col_slice": second_col_slice,
    }


def generate_summary_report(filepath: str = DATA_FILE) -> None:
    """Read CSV with Pandas, clean missing values, analyze with NumPy & Pandas, and print report."""
    if not os.path.exists(filepath):
        print("Dataset file not found.")
        return

    df = pd.read_csv(filepath)

    # Handle missing values
    df["notes"] = df["notes"].fillna("No note provided").replace("", "No note provided")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    mean_amt = df["amount"].mean()
    df["amount"] = df["amount"].fillna(mean_amt if pd.notna(mean_amt) else 0.0)
    df["month"] = pd.to_datetime(df["date"], errors="coerce").dt.to_period("M").astype(str)

    if df.empty:
        print("No records available to generate a report.")
        return

    print("\n" + "=" * 72)
    print("PERSONAL FINANCE & EXPENSE SUMMARY REPORT".center(72))
    print("=" * 72)

    # Selected rows and columns
    print("\n[1] Selected Rows & Columns (First 5 Rows):")
    print(df[["id", "date", "category", "amount"]].head(5).to_string(index=False))

    # NumPy metrics
    np_stats = run_numpy_analysis(df)
    print("\n[2] NumPy Analysis (1D & 2D Arrays, Indexing, Slicing & Stats):")
    print(f"    1D Array Shape      : {np_stats['shape_1d']} | 2D Array Shape: {np_stats['shape_2d']}")
    print(f"    Total Expenditure   : INR {np_stats['total']:,.2f}")
    print(f"    Mean Expense        : INR {np_stats['mean']:,.2f}")
    print(f"    Median Expense      : INR {float(np.median(df['amount'])):,.2f}")
    print(f"    Std. Deviation (s)  : INR {np_stats['std']:,.2f}")
    print(f"    Max / Min Expense   : INR {np_stats['max']:,.2f} / INR {np_stats['min']:,.2f}")
    print(f"    1D Slice [:5]       : {np.round(np_stats['first_five_slice'], 2)}")
    print(f"    1D Index [9]        : INR {np_stats['tenth_element']:,.2f}")
    print(f"    2D Slice [0:4, 1]   : {np.round(np_stats['second_col_slice'], 2)}")

    # Pandas statistical summary
    print("\n[3] Pandas Statistical Summary (.describe() on Amount):")
    print(df["amount"].describe().to_string())

    # GroupBy category + sort
    cat_summary = (
        df.groupby("category", as_index=False)["amount"]
        .agg(Count="count", Total="sum", Average="mean")
        .sort_values(by="Total", ascending=False)
    )
    print("\n[4] Spending by Category (GroupBy + Sorted Descending):")
    print(cat_summary.to_string(index=False))

    # GroupBy payment mode
    mode_summary = (
        df.groupby("payment_mode", as_index=False)["amount"]
        .agg(Transactions="count", Total="sum")
        .sort_values(by="Total", ascending=False)
    )
    print("\n[5] Spending by Payment Mode:")
    print(mode_summary.to_string(index=False))

    # GroupBy month
    month_summary = (
        df.groupby("month", as_index=False)["amount"]
        .agg(Records="count", Monthly_Total="sum")
        .sort_values(by="month")
    )
    print("\n[6] Monthly Expense Trend:")
    print(month_summary.to_string(index=False))

    # Filtered high-value expenses
    high_spend = df[df["amount"] > np_stats["mean"]].sort_values(by="amount", ascending=False)
    print(f"\n[7] High-Value Expenses Above Mean (INR {np_stats['mean']:,.2f}) — Top 5:")
    print(high_spend[["id", "date", "category", "amount", "notes"]].head(5).to_string(index=False))

    top_cat = cat_summary.iloc[0]
    print("\n[8] Key Insight:")
    print(
        f"    '{top_cat['category']}' is the highest spending category at "
        f"INR {top_cat['Total']:,.2f} across {int(top_cat['Count'])} records."
    )
    print("=" * 72)


def prompt_choice(prompt_text: str, options: tuple) -> str:
    """Prompt user to pick from a tuple of valid options or enter custom text."""
    for idx, opt in enumerate(options, start=1):
        print(f"  {idx}. {opt}")
    raw = input(f"{prompt_text} (enter number or exact name): ").strip()
    if raw.isdigit():
        pos = int(raw) - 1
        if 0 <= pos < len(options):
            return options[pos]
    for opt in options:
        if raw.lower() == opt.lower():
            return opt
    return raw if raw else options[0]


def handle_add(records: List[Dict[str, object]]) -> None:
    print_subbanner("Add New Expense Record")
    date_val = input("Date (YYYY-MM-DD, e.g., 2026-11-20): ").strip() or "2026-11-20"
    category_val = prompt_choice("Select Category", VALID_CATEGORIES)
    mode_val = prompt_choice("Select Payment Mode", VALID_PAYMENT_MODES)

    try:
        amount_val = float(input("Amount (INR): ").strip())
        if amount_val < 0:
            print("Amount cannot be negative. Operation cancelled.")
            return
    except ValueError:
        print("Invalid amount entered. Operation cancelled.")
        return

    notes_val = input("Notes (optional): ").strip()
    created = add_record(records, date_val, category_val, mode_val, amount_val, notes_val)
    print(f"Added record {created['id']} (INR {created['amount']:.2f} under {created['category']}).")


def handle_search(records: List[Dict[str, object]]) -> None:
    print_subbanner("Search Expense Records")
    query = input("Enter ID, category, payment mode, date, or keyword: ").strip()
    results = search_records(records, query)
    print(f"Found {len(results)} matching record(s):")
    print_records_table(results)


def handle_update(records: List[Dict[str, object]]) -> None:
    print_subbanner("Update Existing Expense Record")
    rec_id = input("Enter Record ID to update (e.g., EXP001): ").strip()
    new_amount_raw = input("New Amount in INR (press Enter to skip): ").strip()
    new_category_raw = input("New Category (press Enter to skip): ").strip()
    new_notes_raw = input("New Notes (press Enter to skip): ").strip()

    updates: Dict[str, object] = {}
    if new_amount_raw:
        try:
            updates["amount"] = float(new_amount_raw)
        except ValueError:
            print("Invalid amount. Skipping amount update.")
    if new_category_raw:
        updates["category"] = new_category_raw
    if new_notes_raw:
        updates["notes"] = new_notes_raw

    if not updates:
        print("No fields provided to update.")
        return

    updated = update_record(records, rec_id, updates)
    if updated:
        print(f"Updated record {updated['id']} successfully.")
        print_records_table([updated], max_rows=1)
    else:
        print(f"Record ID '{rec_id}' not found.")


def handle_delete(records: List[Dict[str, object]]) -> None:
    print_subbanner("Delete Expense Record")
    rec_id = input("Enter Record ID to delete (e.g., EXP001): ").strip()
    removed = delete_record(records, rec_id)
    if removed:
        print(f"Deleted record {removed['id']} ({removed['category']} - INR {removed['amount']:.2f}).")
    else:
        print(f"Record ID '{rec_id}' not found.")


def main() -> None:
    print_banner("PERSONAL FINANCE & EXPENSES ANALYSIS MODEL")
    records = load_records()
    cats, modes = get_unique_metadata(records)
    print(f"Loaded {len(records)} records | Categories: {len(cats)} | Payment Modes: {len(modes)}")

    while True:
        print("\nChoose an operation:")
        print("  1. Display all records")
        print("  2. Add a new record")
        print("  3. Search for a record")
        print("  4. Update an existing record")
        print("  5. Delete a record")
        print("  6. Generate summary report (NumPy & Pandas)")
        print("  7. Exit")

        choice = input("\nEnter choice (1-7): ").strip()
        if choice == "1":
            print_subbanner("All Expense Records")
            print_records_table(records)
        elif choice == "2":
            handle_add(records)
        elif choice == "3":
            handle_search(records)
        elif choice == "4":
            handle_update(records)
        elif choice == "5":
            handle_delete(records)
        elif choice == "6":
            generate_summary_report()
        elif choice == "7":
            print("Exiting Personal Finance & Expenses Analysis Model. Goodbye!")
            break
        else:
            print("Invalid selection. Please enter a number from 1 to 7.")


if __name__ == "__main__":
    main()