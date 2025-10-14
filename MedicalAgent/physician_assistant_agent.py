import json
from agents import Agent, Runner
from models.openai_model_output import ManagementPlanOutput

# ---- Base instructions for interview phase ----
BASE_AGENT_INSTRUCTIONS = """
You are a medical assistant conducting a structured patient interview.

**CRITICAL CONTROL INSTRUCTIONS:**
- Ask **only one new question** relevant to the current section.
- Use 'primary_working_diagnosis' = 'ASK_QUESTION' for ongoing interview.
- When the interview is complete, set 'primary_working_diagnosis' = 'FINAL_DIAGNOSIS'
  and 'follow_up_recommendation' = 'DONE'.

**STRUCTURE:**
- Put your next question in 'differential_diagnosis[0]'.
- Add all collected history in 'physician_note'.
- Indicate next section in 'follow_up_recommendation'.

**SECTIONS:**
Follow this order strictly:
Presenting Complaint → History of Presenting Complaint → Past Medical History → Medications → Social History → Family History → DONE

**DO NOT:**
- Repeat any previously asked questions.
- Rephrase already asked questions.
- Continue asking questions after follow_up_recommendation == "DONE".

You must generate a NEW question every time.
"""

# ---- Initialize base agent ----
agent = Agent(
    name="Conversational Medical Agent",
    instructions=BASE_AGENT_INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ManagementPlanOutput,
)


# ---- Dynamic Prompt Builder ----
def build_dynamic_prompt(
    base_instructions, current_section, user_response, history_so_far, asked_questions
):
    asked_text = "\n".join(f"- {q}" for q in asked_questions) or "None"
    return f"""
You are currently in the section: **{current_section}**

User's Last Answer:
{user_response}

Collected History So Far:
{history_so_far}

Questions already asked in any section:
{asked_text}

You MUST now generate ONE completely NEW question for the current section.
Do not rephrase or repeat any previous question.

If all sections are complete, set:
- 'primary_working_diagnosis' = 'FINAL_DIAGNOSIS'
- 'follow_up_recommendation' = 'DONE'

{base_instructions}
"""


# ---- Main Function ----
async def conversational_history_taking():
    history_data = ""
    current_section = "Presenting Complaint"
    asked_questions = set()

    print("--- Starting Medical History Interview ---")
    print("Agent: Hello. What medical issues brought you in today?")
    user_input = input("You: ")

    while True:
        # Stop condition safeguard (in case model loops)
        if current_section.strip().upper() == "DONE":
            print("\n✅ Interview complete (forced stop).")
            break

        # Build context for the agent
        context_input = {
            "User_Response": user_input,
            "History_So_Far": history_data,
            "Current_Section": current_section,
        }
        context_string = json.dumps(context_input)

        # Build dynamic prompt
        dynamic_prompt = build_dynamic_prompt(
            BASE_AGENT_INSTRUCTIONS,
            current_section,
            user_input,
            history_data,
            asked_questions,
        )
        agent.instructions = dynamic_prompt

        try:
            result = await Runner.run(agent, context_string)
            output = result.final_output

            next_action = (output.primary_working_diagnosis or "").strip().upper()
            question_text = (
                output.differential_diagnosis[0].strip()
                if output.differential_diagnosis
                else ""
            )
            history_data = output.physician_note or history_data
            next_section = (output.follow_up_recommendation or "").strip()

            # --- Stop interview when DONE ---
            if next_section.upper() == "DONE" or next_action == "FINAL_DIAGNOSIS":
                print("\n✅ Interview complete. Generating final management plan...")

                # ----- PHASE 2: MANAGEMENT PLAN GENERATION -----
                plan_prompt = f"""
                You are a senior physician generating a structured management plan
                based on the following collected history:
                
                {history_data}
                
                Now produce a complete JSON output in the **ManagementPlanOutput** format:
                - 'differential_diagnosis': 3–5 plausible causes based on history.
                - 'primary_working_diagnosis': The most likely diagnosis.
                - 'diagnostic_plan': 2–4 DiagnosticTest objects with name and rationale.
                - 'therapeutic_plan': 2–3 MedicationOrder objects with name, dose_route, and rationale.
                - 'patient_education_and_counseling': 3–5 EducationInstruction objects (topic + instruction).
                - 'follow_up_recommendation': e.g. "Follow up in 3 days" or "Refer to gastroenterologist".
                - 'physician_note': Concise summary of key findings and plan.
                
                Respond **only** with a valid JSON matching the ManagementPlanOutput schema.
                """
                agent.instructions = plan_prompt
                result = await Runner.run(agent, history_data)
                final_output = result.final_output

                print("\n--- Final Management Plan ---")
                print(final_output.model_dump_json(indent=4))
                break

            # Handle repeated or missing question edge case
            if not question_text or question_text in asked_questions:
                print("\n⚠️ Agent returned a repeated or invalid question. Skipping.")
                user_input = input("You (clarify previous answer or skip): ")
                continue

            # Track asked questions to avoid repeats
            asked_questions.add(question_text)

            if next_action == "ASK_QUESTION":
                print(f"\n[Current Section: {current_section}]")
                print(f"Agent: {question_text}")
                user_input = input("You: ")
                current_section = next_section or current_section
                continue

            # Handle any unexpected model response
            print("\n⚠️ Unexpected agent response. Dumping debug info:")
            print(output.model_dump_json(indent=4))
            break

        except Exception as e:
            print(f"\n❌ Error occurred: {e}")
            print(f"Last Context Sent: {context_string}")
            break
