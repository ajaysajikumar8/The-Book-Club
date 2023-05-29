import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
from flask import url_for
from db_operations import get_books_by_author

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

with open("intents.json", "r") as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Amanda"


def get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                response = random.choice(intent["responses"])
                if "{author}" in response:
                    author = extract_variable_input(msg, intent["patterns"], "author")
                    if author:
                        books = get_books_by_author(author)
                        if books:
                            response = response.replace("{author}", author)
                            book_links = [f'<a href="{url_for("get_book", book=book)}">{book}</a>' for book in books]
                            response += "\nBooks by {author}: " + ', '.join(book_links)
                        else:
                            response = "No books found for the author."
                    else:
                        response = "Author name not provided."
                return response

    return "I do not understand..."



def extract_variable_input(user_input, patterns, variable_name):
    for pattern in patterns:
        if "{" + variable_name + "}" in pattern:
            start_index = pattern.index("{")
            end_index = pattern.index("}") + len(variable_name) + 2  # Adjusted end index to include the variable name and closing curly brace
            if start_index < end_index:
                variable_input = user_input[start_index:end_index].replace("{", "").replace("}", "").strip()
                return variable_input

    return None



if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence == "quit":
            break

        response = get_response(sentence)
        print(response)
