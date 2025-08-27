class Employee:
    def __init__(self, emp_id, name, position, department):
        self.emp_id = emp_id
        self.name = name
        self.position = position
        self.department = department

class Performance:
    def __init__(self, staff, rating, feedback, bonus):
        self.staff = staff
        self.rating = rating
        self.feedback = feedback
        self.bonus = bonus

employees = {
    "EMP001": Employee("EMP001", "Charles Baker", "Scrum Master", "Engineering"),
    "EMP002": Employee("EMP002", "Diana Prince", "UX Designer", "Design"),
}

performances = {
    "EMP001": Performance(employees["EMP001"], 4.7, "Excellent leadership", 3500),
    "EMP002": Performance(employees["EMP002"], 4.2, "Consistently delivers high-quality designs", 3200),
}
# You're tasked with developing a function that compiles a report summarizing an employee's performance. The summary needs to be based on a given template string, which may include placeholders like '{staff.name}', '{staff.position}', and '{evaluation.rating}'. Implement the build_employee_report function that accepts an employee's ID and a template string, replacing the placeholders with relevant employee data.

def build_employee_report(employee_id, template):
    if employee_id not in performances:
        raise ValueError(f"Employee with ID {employee_id} not found")
    evaluation = performances[employee_id]
    class LimitedAccessPerformance:
        def __init__(self, evaluation):
            self._evaluation = evaluation

        def __getattr__(self, name):
            if name in ['feedback', 'bonus']:
                raise ValueError(f"Access to {name} is not allowed in the summary")
            return getattr(self._evaluation, name)

    limited_evaluation = LimitedAccessPerformance(evaluation)
    return template.format(staff=limited_evaluation.staff, evaluation=limited_evaluation)