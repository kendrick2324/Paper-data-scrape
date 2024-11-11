from zhipuai import ZhipuAI

client = ZhipuAI(api_key="")

def get_completion(prompt):
    response = client.chat.completions.create(
        model="glm-4-air",
        temperature=0.1,
        messages=[
                { "role": "system" , "content": "You are a professional paper analyzer." },
                { "role": "user" , "content": prompt}
                ],
        )
    return response.choices[0].message.content