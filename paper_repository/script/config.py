from zhipuai import ZhipuAI

client = ZhipuAI(api_key="8abc0cf3f892ad7b0163ebbb2ae2086c.neA2Jey6S4cZX7wJ")

def get_completion(prompt):
    response = client.chat.completions.create(
        model="GLM-4-Air",
        temperature=0.1,
        messages=[
                { "role": "system" , "content": "You are a professional paper analyzer." },
                { "role": "user" , "content": prompt}
                ],
        )
    return response.choices[0].message.content