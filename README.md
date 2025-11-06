Expense Tracker application for basic purposes. 
Add, update, delete, view, and summarize your expenses. 
Update or delete existing expenses by ID. 
View total expenses or monthly summaries. 
Set monthly budgets and receive warnings when exceeded. 
Export expenses to CSV for external use. 

The list of commands and their expected output is shown below:

$ expense-tracker add --description "Lunch" --amount 20
# Expense added successfully (ID: 1)

$ expense-tracker add --description "Dinner" --amount 10
# Expense added successfully (ID: 2)

$ expense-tracker list
# ID  Date       Description  Amount
# 1   2024-08-06  Lunch        $20
# 2   2024-08-06  Dinner       $10

$ expense-tracker summary
# Total expenses: $30

$ expense-tracker delete --id 2
# Expense deleted successfully

$ expense-tracker summary
# Total expenses: $20

$ expense-tracker summary --month 8
# Total expenses for August: $20<img width="671" height="646" alt="image" src="https://github.com/user-attachments/assets/36a741a9-5d88-464e-b310-94c17f1dd60d" />

