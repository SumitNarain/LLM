def build_dynamic_prompt(
    base_instructions, current_section, user_response, history_so_far, asked_questions
):
    asked_text = "\n".join(f"- {q}" for q in asked_questions) or "None"
    return f"""
            You are currently in the section: {current_section}
            
            User's Last Answer:
            {user_response}
            
            Collected History So Far:
            {history_so_far}
            
            Questions already asked in any section:
            {asked_text}
            
            You must now generate ONE completely NEW question for the current section.
            Do not rephrase or repeat any previous question.
            
            If all sections are complete, set:
            - 'primary_working_diagnosis' = 'FINAL_DIAGNOSIS'
            - 'follow_up_recommendation' = 'DONE'
            
            {base_instructions}
            """
