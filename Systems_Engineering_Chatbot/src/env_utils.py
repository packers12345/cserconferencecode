import os


def safe_load_dotenv(dotenv_path: str):
    """
    Load a .env file but skip variables whose value would exceed the
    Windows environment-variable length limit (32767 characters).

    This prevents ValueError: the environment variable is longer than 32767 characters
    when a .env accidentally contains huge blobs (e.g., embedded files or base64).
    """
    max_env_len = 32767
    path = dotenv_path
    if not os.path.exists(path):
        return
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('export '):
                    line = line[len('export '):]
                if '=' not in line:
                    continue
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip().strip('"\'')
                if len(val) > max_env_len:
                    print(f"Skipping environment variable '{key}': value exceeds {max_env_len} characters (Windows limit).")
                    continue
                os.environ[key] = val
    except Exception as e:
        print(f"Error loading .env file '{path}': {e}")
