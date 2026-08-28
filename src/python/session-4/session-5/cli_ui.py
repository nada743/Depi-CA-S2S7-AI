from model import get_response
def main_bot():
    print("chatbot: Hi How can i assist you ?")
    while True:
        user_input = input("User:   ").lower()
        response = get_response(user_input)
        print("chatbot:", response)

        if user_input == "goodbye":
            break
