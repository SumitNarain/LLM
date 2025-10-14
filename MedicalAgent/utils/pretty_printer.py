from MedicalAgent.models.openai_model_output import ManagementPlanOutput

def print_management_plan(plan: ManagementPlanOutput):
    print("------------------------------------------------------------")
    print(" FINAL MANAGEMENT PLAN ")
    print("------------------------------------------------------------\n")

    if plan.differential_diagnosis:
        print("DIFFERENTIAL DIAGNOSIS:")
        for i, dx in enumerate(plan.differential_diagnosis, 1):
            print(f"  {i}. {dx}")
        print()

    if plan.primary_working_diagnosis:
        print("PRIMARY WORKING DIAGNOSIS:")
        print(f"  {plan.primary_working_diagnosis}\n")

    if plan.diagnostic_plan:
        print("DIAGNOSTIC PLAN:")
        for test in plan.diagnostic_plan:
            name = getattr(test, 'name', None) or test.get('name', '')
            rationale = getattr(test, 'rationale', None) or test.get('rationale', '')
            print(f"  - {name}: {rationale}")
        print()

    if plan.therapeutic_plan:
        print("THERAPEUTIC PLAN:")
        for med in plan.therapeutic_plan:
            name = getattr(med, 'name', None) or med.get('name', '')
            dose = getattr(med, 'dose_route', None) or med.get('dose_route', '')
            rationale = getattr(med, 'rationale', None) or med.get('rationale', '')
            print(f"  - {name} ({dose}) — {rationale}")
        print()

    if plan.patient_education_and_counseling:
        print("PATIENT EDUCATION AND COUNSELING:")
        for edu in plan.patient_education_and_counseling:
            topic = getattr(edu, 'topic', None) or edu.get('topic', '')
            instruction = getattr(edu, 'instruction', None) or edu.get('instruction', '')
            print(f"  - {topic}: {instruction}")
        print()

    if plan.follow_up_recommendation:
        print("FOLLOW-UP RECOMMENDATION:")
        print(f"  {plan.follow_up_recommendation}\n")

    if plan.physician_note:
        print("PHYSICIAN NOTE:")
        print(f"  {plan.physician_note}\n")

    print("------------------------------------------------------------")
    print(" END OF SESSION ")
    print("------------------------------------------------------------\n")
