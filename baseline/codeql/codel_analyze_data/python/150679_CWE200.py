class Patient:
    def __init__(self, id, name, age, gender, diagnosis, treatment_plan):
        self.id = id
        self.name = name
        self.age = age
        self.gender = gender
        self.diagnosis = diagnosis
        self.treatment_plan = treatment_plan

patients = {
    "P001": Patient("P001", "John Doe", 45, "Male", "Hypertension", "Medication and lifestyle changes")
}
# You are tasked with building a function for a healthcare system's reporting module. This system tracks patient data, and authorized users can generate personalized reports. Your goal is to design the function create_patient_report, which takes a patient ID and a report template. The provided template may contain placeholders such as '{patient.name}' or '{patient.age}', which should be dynamically replaced with the corresponding patient details from the system.

def create_patient_report(pat_id, layout):
    if pat_id not in patients:
        raise ValueError("Patient not found")
    patient = patients[pat_id]
    class SecuredPatient:
        def __init__(self, patient):
            self._patient = patient

        def __getattr__(self, name):
            if name in ['diagnosis', 'treatment_plan']:
                raise ValueError(f"Access to {name} is not allowed in reports")
            return getattr(self._patient, name)

    secured_patient = SecuredPatient(patient)
    return layout.format(patient=secured_patient)