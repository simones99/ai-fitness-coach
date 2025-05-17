import requests

def ask_local_llm(prompt):
    """
    Sends a prompt to the local LLM via /v1/chat/completions endpoint and returns the response.
    """
    url = "http://127.0.0.1:1234/v1/chat/completions"

    payload = {
        "model": "local-model",  # LM Studio ignores this
        "messages": [
            {"role": "system", "content": '''
             You are a personal fitness coach. 
                I want you to suggest a workout plan based on my personal data and workout history.
                I will provide you with my workout data, including distance, duration, heart rate, cadence, power, elevation, and calories burned.
                You will analyze this data and suggest a workout plan that is tailored to my fitness level and goals in a friendly and encouraging manner.
                You will provide the workout plan in a structured format, including the type of workout, duration, intensity, and any other relevant details.
                You will also provide a brief explanation of why this workout is suitable for me based on the data I provided.
                You will not provide any other information or suggestions outside of the workout plan.
                You will not include any disclaimers or warnings about exercise or fitness.
                You will not ask me any questions or request any additional information.
                You will not provide any information about yourself or your capabilities.
                You will not provide any information about the AI or its limitations.
                '''},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        #"max_tokens": 1012
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    except requests.exceptions.RequestException as e:
        return f"Error communicating with local LLM: {e}"

    except Exception as e:
        return f"Unexpected error: {e}"

