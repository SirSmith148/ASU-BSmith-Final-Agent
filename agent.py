

API_KEY = "cse476"
API_BASE = "http://10.4.58.53:41701/v1"
MODEL = "bens_model"

import os, json, textwrap, re, time
import requests
import random

API_KEY  = os.getenv("OPENAI_API_KEY", "cse476")
API_BASE = os.getenv("API_BASE", "http://10.4.58.53:41701/v1")  
MODEL    = os.getenv("MODEL_NAME", "bens_model")    


def run_agent(input_text: str) -> str:
    mode = random.randint(0, 2)
    #Randomizer for sleceting how the agent prompts the LLM
    if mode == 0:
        answer_string = solve_simple(input_text)
    elif mode == 1:
        answer_string = solve_with_self_consistency(input_text)
    elif mode == 2:
        answer_string = solve_with_reflection(input_text)

    return answer_string

def call_llm(prompt: str, system: str = "You are a helpful assistant. Reply with only the final answer—no explanation.", model: str = MODEL,temperature: float = 0.0, timeout: int = 60) -> dict:
    # Makes a call to the LLM API and returns the response. THIS IS FROM THE TUTORIAL FILE
    url = f"{API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user",   "content": prompt}],
        "temperature": temperature,
        "max_tokens": 128,
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        status = resp.status_code
        hdrs   = dict(resp.headers)
        if status == 200:
            data = resp.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"ok": True, "text": text, "raw": data, "status": status, "error": None, "headers": hdrs}
        else:
            # try best-effort to surface error text
            err_text = None
            try:
                err_text = resp.json()
            except Exception:
                err_text = resp.text
            return {"ok": False, "text": None, "raw": None, "status": status, "error": str(err_text), "headers": hdrs}
    except requests.RequestException as e:
        return {"ok": False, "text": None, "raw": None, "status": -1, "error": str(e), "headers": {}}

def solve_simple(input_text: str) -> str:
    #Tells the LLM to only giove the answer without any explanation
    prompt = ("Answer the following question and respond with only the final answer: " + input_text)
    result = call_llm(prompt)
    #checks if the call was successful and returns the answer
    if result["ok"]:
        return (result["text"] or "").strip()
    return ""

def solve_with_self_consistency(input_text: str, num_samples: int = 5) -> str:
    #creates an answer array for all the answers the LLM will generate
    answers = []
    #generates multiple answers based on input, and stores them in the array
    for _ in range(num_samples):
        prompt = ("Answer the following question and respond with only the final answer: " + input_text)
        #calls the LLM with higher temperature to increase answer variability
        result = call_llm(prompt, temperature=0.5)
        #checks if the call was successful and stores the answer
        if result["ok"]:
            answer = (result["text"] or "").strip()
            answers.append(answer)
    if not answers:
        return ""
    #counts the frequency of each answer
    dulplicates = {}
    for answer in answers:
        dulplicates[answer] = dulplicates.get(answer, 0) + 1
    #slects the answer that was generated the most and returns it
    best_answer = max(dulplicates, key=dulplicates.get)
    return best_answer





