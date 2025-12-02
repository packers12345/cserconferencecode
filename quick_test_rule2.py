import sys, os
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from Systems_Engineering_Chatbot.src.hard_rules import detect_rule_2_trigger, generate_rule_2_response

prompt = "assess whether an rlc circuit can be leveraged for a verification model for a mechanical spring system"
print('Prompt:', prompt)
print('detect_rule_2_trigger ->', detect_rule_2_trigger(prompt))
resp = generate_rule_2_response()
print('\nResponse preview (first 400 chars):\n')
print(resp[:400])
