import requests

def ask_local_llm(prompt):
    """
    Sends a prompt to the local LLM via /v1/chat/completions endpoint and returns the response.
    """
    url = "http://127.0.0.1:1234/v1/chat/completions"

    payload = {
        "model": "local-model",  # LM Studio ignores this
        "messages": [
            {"role": "system", "content": "You are a personal fitness coach."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 512
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    except requests.exceptions.RequestException as e:
        return f"Error communicating with local LLM: {e}"

    except Exception as e:
        return f"Unexpected error: {e}"