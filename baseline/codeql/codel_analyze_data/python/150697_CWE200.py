class Employee:
    def __init__(self, name, job_title, team, wage, contact_info):
        self.name = name
        self.job_title = job_title
        self.team = team
        self.wage = wage
        self.contact_info = contact_info

employees = [
    Employee("Alice Smith", "Software Engineer", "IT", 85000, "alice@personal.com"),
    Employee("Bob Johnson", "Project Manager", "IT", 95000, "bob@personal.com"),
    Employee("Carol Williams", "Data Analyst", "IT", 75000, "carol@personal.com")
]
# You are tasked with building a function that will help department managers generate a formatted employee directory for their teams. The function, generate_department_directory, should process and fill out a provided template string with employee details. The directory template may include placeholders like '{employee.name}' or '{employee.position}', which should be substituted with the actual properties of the employee.

def generate_department_directory(dept_name, dir_template):
    directory = []
    for employee in employees:
        if employee.team == dept_name:
            class RestrictedEmployee:
                def __init__(self, emp):
                    self._emp = emp

                def __getattr__(self, attr):
                    if attr in ['wage', 'contact_info']:
                        raise ValueError(f"Access to {attr} is not permitted in the directory")
                    return getattr(self._emp, attr)

            secure_employee = RestrictedEmployee(employee)
            directory.append(dir_template.format(employee=secure_employee))
    return "\n".join(directory)