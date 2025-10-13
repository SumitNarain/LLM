import json
from agents import Agent, Runner
from models.openai_model_output import ManagementPlanOutput  # Import the model

# --- Agent Instructions ---
AGENT_INSTRUCTIONS = """
    You are a medical assistant conducting a structured patient interview. Your final output must strictly adhere to the ManagementPlanOutput JSON schema.

    **CRITICAL FLOW CONTROL INSTRUCTION:**
    1.  For every interview step, the 'primary_working_diagnosis' field MUST contain the single string **'ASK_QUESTION'**.
    2.  When the interview is complete (i.e., when Current_Section is 'DONE'), the 'primary_working_diagnosis' MUST contain the final diagnosis (e.g., 'Acute Heart Failure Exacerbation').

    **RULES OF THE INTERVIEW:**
    - **Current Section Tracking:** The 'follow_up_recommendation' field MUST contain the string for the **NEXT** section to be covered. Use the sequence: Presenting Complaint -> History of Presenting Complaint -> Past Medical History -> Medications -> Social History -> Family History -> DONE.

    **--- SEPARATED QUESTION AND HISTORY ---**
    - **Question:** The question for the user MUST be placed in the **FIRST element of the 'differential_diagnosis' list**. Do NOT put any other content there during the interview phase.
    - **History Collection:** The full, running narrative history collected so far MUST be placed and updated in the **'physician_note' field**. Do NOT include the question in this field.

    - **Sequencing:** Follow the sequence: Presenting Complaint -> History of Presenting Complaint -> Past Medical History -> Medications -> Social History -> Family History. When Family History is complete, change the next section to 'DONE'.

    **State based on input:** User_Response='{{User_Response}}', History_So_Far='{{History_So_Far}}', Current_Section='{{Current_Section}}'

    **Action:** If Current_Section is not 'DONE' and the section is incomplete, ask one question for the current section and set 'primary_working_diagnosis' to 'ASK_QUESTION'.
    **Action:** If Current_Section is 'DONE', fill ALL fields of the ManagementPlanOutput based on the final history in 'physician_note', and set 'primary_working_diagnosis' to the final diagnosis.
"""

# Initialize the Agent
agent = Agent(
    name="Conversational Medical Agent",
    instructions=AGENT_INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ManagementPlanOutput
)


async def conversational_history_taking():
    history_data = ""
    current_section = "Presenting Complaint (PC)"

    print("--- Starting Medical History Interview ---")
    print("Agent: Hello. What medical issues brought you in today?")
    user_input = input("You: ")

    while True:
        contextual_input = {
            "User_Response": user_input,
            "History_So_Far": history_data,
            "Current_Section": current_section
        }
        context_string = json.dumps(contextual_input)

        try:
            # 2. Run the agent for one turn (expecting a structured output)
            result = await Runner.run(agent, context_string)
            output = result.final_output

            # 3. Extract conversational fields from the final model output
            next_action_str = output.primary_working_diagnosis.upper().strip()

            # History is extracted from the physician_note field
            history_data = output.physician_note or ""

            # Question is extracted from the differential_diagnosis list (first element)
            question_text = output.differential_diagnosis[0] if output.differential_diagnosis else ""

            # The agent is responsible for setting the *next* section
            next_section = output.follow_up_recommendation.strip()
            current_section = next_section

            if next_action_str == "ASK_QUESTION":
                if not question_text:
                    print("\n!!! Agent returned no question. Continuing with default flow. !!!")
                    user_input = input("You: ")
                    continue

                print(f"\n[Current Section: {current_section}]")
                print(f"Agent: {question_text}")

                user_input = input("You: ")

            elif current_section == "DONE" or next_action_str != "ASK_QUESTION":
                # Final plan logic
                print("\n--- History Complete. Final Plan Generated. ---")
                print(f"Final History Collected (from Agent):\n{history_data}")

                print("\n--- GENERATED MANAGEMENT PLAN (ManagementPlanOutput Model) ---")
                print(output.model_dump_json(indent=4))
                print("---------------------------------------------------------")
                break

            else:
                # Fallback for unexpected model output
                print("\n------------------- DEBUG INFORMATION -------------------")
                print(f"Agent returned UNKNOWN ACTION/STATE. primary_working_diagnosis: {next_action_str}")
                print(f"Full Output Received:\n{output.model_dump_json(indent=2)}")
                print("---------------------------------------------------------")
                print("Stopping.")
                break

        except Exception as e:
            print(f"\n!!! An error occurred during the agent run: {e} !!!")
            print(f"Last Context Sent: {context_string}")
            break