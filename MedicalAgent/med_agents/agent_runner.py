import json
from MedicalAgent.models.openai_model_output import ManagementPlanOutput
from MedicalAgent.med_agents.prompt_builder import build_dynamic_prompt
from MedicalAgent.config.interview_instructions import BASE_AGENT_INSTRUCTIONS
from MedicalAgent.utils.pretty_printer import print_management_plan
from agents import Agent, Runner

async def run_medical_interview():
    history_data = ""
    current_section = "Presenting Complaint"
    asked_questions = set()

    print("------------------------------------------------------------")
    print(" STARTING MEDICAL HISTORY INTERVIEW ")
    print("------------------------------------------------------------\n")
    print("Agent: Hello. What medical issues brought you in today?")
    user_input = input("You: ")

    agent = Agent(
        name="Conversational Medical Agent",
        instructions=BASE_AGENT_INSTRUCTIONS,
        model="gpt-4o-mini",
        output_type=ManagementPlanOutput
    )

    while True:
        if current_section.strip().upper() == "DONE":
            print("\nInterview complete (forced stop).")
            break

        context_input = {
            "User_Response": user_input,
            "History_So_Far": history_data,
            "Current_Section": current_section
        }
        context_string = json.dumps(context_input)

        dynamic_prompt = build_dynamic_prompt(
            BASE_AGENT_INSTRUCTIONS,
            current_section,
            user_input,
            history_data,
            asked_questions
        )
        agent.instructions = dynamic_prompt

        try:
            result = await Runner.run(agent, context_string)
            output = result.final_output

            next_action = (output.primary_working_diagnosis or "").strip().upper()
            question_text = output.differential_diagnosis[0].strip() if output.differential_diagnosis else ""
            history_data = output.physician_note or history_data
            next_section = (output.follow_up_recommendation or "").strip()

            # Stop when done
            if next_section.upper() == "DONE" or next_action == "FINAL_DIAGNOSIS":
                print("\nInterview complete. Generating management plan...\n")

                plan_prompt = f"""
You are a senior physician generating a structured management plan
based on the following collected history:

{history_data}

Now produce a complete JSON output in the ManagementPlanOutput format.
"""
                agent.instructions = plan_prompt
                result = await Runner.run(agent, history_data)
                final_output = result.final_output

                print_management_plan(final_output)
                break

            # Handle repeated or missing questions
            if not question_text or question_text in asked_questions:
                print("\nAgent returned a repeated or invalid question. Please clarify or skip.")
                user_input = input("You: ")
                continue

            asked_questions.add(question_text)

            if next_action == "ASK_QUESTION":
                print("\n------------------------------------------------------------")
                print(f" Current Section: {current_section}")
                print("------------------------------------------------------------")
                print(f"Agent: {question_text}")
                user_input = input("You: ")
                current_section = next_section or current_section
                continue

            print("\nUnexpected agent response. Debug info:")
            print(output.model_dump_json(indent=4))
            break

        except Exception as e:
            print("\nAn error occurred during the conversation.")
            print(f"Error: {e}")
            print(f"Last Context Sent: {context_string}")
            break
