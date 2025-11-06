#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import datetime

DATA_FILE = "expenses.json"
BUDGET_FILE = "budget.json"

def load_expenses():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_expenses(expenses):
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=2)

def load_budget():
    if not os.path.exists(BUDGET_FILE):
        return {}
    with open(BUDGET_FILE, "r") as f:
        return json.load(f)

def save_budget(budget):
    with open(BUDGET_FILE, "w") as f:
        json.dump(budget, f, indent=2)

def generate_new_id(expenses):
    if not expenses:
        return 1
    return max(e['id'] for e in expenses) + 1

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

def add_expense(args):
    expenses = load_expenses()
    if args.amount <= 0:
        print("Error: Amount must be a positive number.")
        return
    expense = {
        "id": generate_new_id(expenses),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": args.description,
        "amount": round(args.amount, 2),
        "category": args.category if args.category else ""
    }
    expenses.append(expense)
    save_expenses(expenses)

    # Budget warning
    warn_budget_if_needed(expense["amount"], expense["date"], expenses)

    print(f"Expense added successfully (ID: {expense['id']})")

def update_expense(args):
    expenses = load_expenses()
    updated = False
    for expense in expenses:
        if expense['id'] == args.id:
            if args.description:
                expense['description'] = args.description
            if args.amount is not None:
                if args.amount <= 0:
                    print("Error: Amount must be positive.")
                    return
                expense['amount'] = round(args.amount, 2)
            if args.category:
                expense['category'] = args.category
            updated = True
            save_expenses(expenses)
            print("Expense updated successfully")
            break
    if not updated:
        print(f"Error: Expense with ID {args.id} not found.")

def delete_expense(args):
    expenses = load_expenses()
    prev_count = len(expenses)
    expenses = [e for e in expenses if e['id'] != args.id]
    if len(expenses) != prev_count:
        save_expenses(expenses)
        print("Expense deleted successfully")
    else:
        print(f"Error: Expense with ID {args.id} not found.")

def list_expenses(args):
    expenses = load_expenses()
    if args.category:
        expenses = [e for e in expenses if e.get("category", "") == args.category]
    if not expenses:
        print("No expenses found.")
        return
    print("ID  Date        Description      Amount   Category")
    print("-" * 50)
    for e in expenses:
        cat = e.get("category", "")
        print(f"{e['id']: <3} {e['date']}  {e['description'][:12]: <14} ${e['amount']: <7.2f} {cat}")

def summary_expenses(args):
    expenses = load_expenses()
    now = datetime.now()
    filtered = expenses
    if args.month:
        filtered = [
            e for e in expenses
            if datetime.strptime(e["date"], "%Y-%m-%d").month == args.month
                and datetime.strptime(e["date"], "%Y-%m-%d").year == now.year
        ]
        total = sum(e["amount"] for e in filtered)
        print(f"Total expenses for {datetime(now.year, args.month, 1).strftime('%B')}: ${total:.2f}")
        show_budget_warning_if_exceeded(args.month, total)
    else:
        total = sum(e["amount"] for e in filtered)
        print(f"Total expenses: ${total:.2f}")

def warn_budget_if_needed(additional, date_str, all_expenses):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    budget = load_budget()
    m = str(dt.month)
    if m in budget:
        month_expenses = [
            e["amount"] for e in all_expenses
            if datetime.strptime(e["date"], "%Y-%m-%d").month == dt.month
                and datetime.strptime(e["date"], "%Y-%m-%d").year == dt.year
        ]
        total = sum(month_expenses)
        budget_amt = budget[m]
        if total > budget_amt:
            print(f"Warning: You have exceeded your budget (${budget_amt:.2f}) for {dt.strftime('%B')}.")

def show_budget_warning_if_exceeded(month, month_total):
    budget = load_budget()
    if str(month) in budget:
        budget_amt = budget[str(month)]
        if month_total > budget_amt:
            print(f"Warning: Total expenses exceed the set budget (${budget_amt:.2f}) for this month.")

def set_budget(args):
    if args.amount <= 0:
        print("Error: Budget amount must be positive.")
        return
    budget = load_budget()
    budget[str(args.month)] = round(args.amount, 2)
    save_budget(budget)
    print(f"Budget of ${args.amount:.2f} set for month {datetime(2022, args.month, 1).strftime('%B')}.")

def export_csv(args):
    import csv
    expenses = load_expenses()
    if args.category:
        expenses = [e for e in expenses if e.get("category", "") == args.category]
    if not expenses:
        print("No expenses to export.")
        return
    with open(args.filename, "w", newline='') as csvfile:
        fieldnames = ["id", "date", "description", "amount", "category"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for e in expenses:
            writer.writerow(e)
    print(f"Exported expenses to {args.filename}")

def main():
    parser = argparse.ArgumentParser(prog="expense-tracker", description="Expense Tracker Application")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add expense
    p_add = subparsers.add_parser("add", help="Add an expense")
    p_add.add_argument("--description", type=str, required=True, help="Description of the expense")
    p_add.add_argument("--amount", type=float, required=True, help="Amount spent")
    p_add.add_argument("--category", type=str, help="Category (optional)")
    p_add.set_defaults(func=add_expense)

    # Update expense
    p_update = subparsers.add_parser("update", help="Update an expense")
    p_update.add_argument("--id", type=int, required=True, help="ID of expense to update")
    p_update.add_argument("--description", type=str, help="New description")
    p_update.add_argument("--amount", type=float, help="New amount")
    p_update.add_argument("--category", type=str, help="New category")
    p_update.set_defaults(func=update_expense)

    # Delete expense
    p_delete = subparsers.add_parser("delete", help="Delete an expense")
    p_delete.add_argument("--id", type=int, required=True, help="ID of the expense to delete")
    p_delete.set_defaults(func=delete_expense)

    # List expenses
    p_list = subparsers.add_parser("list", help="View all expenses")
    p_list.add_argument("--category", type=str, help="Filter expenses by category")
    p_list.set_defaults(func=list_expenses)

    # Summary
    p_summary = subparsers.add_parser("summary", help="View summary of expenses")
    p_summary.add_argument("--month", type=int, choices=range(1,13), help="Summary for specific month (1-12)")
    p_summary.set_defaults(func=summary_expenses)

    # Set budget
    p_budget = subparsers.add_parser("set-budget", help="Set monthly budget")
    p_budget.add_argument("--month", type=int, choices=range(1,13), required=True, help="Month (1-12)")
    p_budget.add_argument("--amount", type=float, required=True, help="Budget amount")
    p_budget.set_defaults(func=set_budget)

    # Export to CSV
    p_export = subparsers.add_parser("export-csv", help="Export expenses to CSV")
    p_export.add_argument("filename", type=str, help="Output CSV filename")
    p_export.add_argument("--category", type=str, help="Filter by category")
    p_export.set_defaults(func=export_csv)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
