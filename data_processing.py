from typing import List
import dataclasses
import re
import json

FINAL_ANS = "answer is "
NUMBER_SET = [str(num) for num in range(0, 10)]


@dataclasses.dataclass
class Example:
    question: str
    answer: str
    thought: str


def remove_calculations(line: str) -> str:
    return re.sub("<<.*>>", "", line)


def parse_example_file(file: str) -> List[Example]:
    result = []
    with open(file, "r") as f:
        for line in f:
            sample = json.loads(line)
            question = remove_calculations(sample["question"])
            split_answer = sample["answer"].split("#### ")
            thought = remove_calculations(split_answer[0])
            answer = split_answer[1].replace(",", "")
            result.append(Example(question, answer, thought))

    return result


def generate_prompt(examples: List[Example]) -> str:
    prompt = ""
    for ex in examples:
        prompt += "Q: " + ex.question + "\nA: " + ex.thought + "The answer is " + ex.answer + ".\n\n"
    return prompt


def generate_question(question: Example) -> str:
    return f"Q: {question.question}\nA: "


def _is_float(s):
    try:
        float(s)
        return True
    except:
        return False


def clean_ans(ans):
    index = ans.find(".")
    if index >= 0:
        end_index = index + 1
        while end_index < len(ans) and ans[end_index] in NUMBER_SET:
            end_index += 1
        ans = ans[:end_index]
    while ans and ans.endswith("."):
        ans = ans[:-1]

    ans = ans.split("=")[-1].strip()
    for c in ["$", ",", "%", "€", '"']:
        ans = ans.replace(c, "")
    parts = ans.split(" ")
    for part in parts:
        if _is_float(part):
            return part

    ans = parts[0]  # default
    for part in parts:
        if not part.isalpha():  # take the 1st non-alpha token
            ans = part
            break
    while ans and ans[-1].isalpha():
        ans = ans[:-1]
    return ans.strip()


def get_ans(pred) -> str:
    text = pred.replace("\n", "").strip()
    if text.rfind(FINAL_ANS) >= 0:
        pred_ans = text[text.rfind(FINAL_ANS) + len(FINAL_ANS) : len(text)].strip()
        return clean_ans(pred_ans)
    else:
        return ""
