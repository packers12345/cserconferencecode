import importlib.util, sys, os

# Ensure parent workspace directory is on sys.path so absolute imports like
# 'Systems_Engineering_Chatbot.src.*' resolve correctly when loading the module directly.
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, workspace_root)

p = r'c:\Users\adiiy\OneDrive\Desktop\Code_Folder2\Systems_Engineering_Chatbot\src\synthesis_engine.py'
spec = importlib.util.spec_from_file_location('synthesis_engine', p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SynthesisEngine = mod.SynthesisEngine

# Instantiate with no AI client to ensure special-case is used
engine = SynthesisEngine(pdf_path='', gemini_client=None)

prompts = [
    "create a system design for a mechanical spring system",
    "mechanical spring system model",
    "design the spring system",
    "give the system model for a mechanical system"
]

for i, pr in enumerate(prompts, 1):
    out = engine.generate_response(pr, {"system_topic": "mechanical spring system"})
    print(f"--- Prompt {i}: {pr}\n")
    print(out)
    print('\n')
