# import the agent module
from app.agent.agent import agent

def main():
    response = agent.invoke(
        {
            "messages":[
                {
                    "role": "user",
                    "content": "I'd like to book 2026-09-07 at 10:00 AM. My name is John Smith and my phone number is 01700000000."
                }
            ]
        }
    )

    print(response["messages"][-1].content)

    # for detailed information about the response, you can print the entire response object
    # for message in response["messages"]:
    #     print("\n==============================")
    #     print(type(message).__name__)
    #     print(message)


if __name__ == "__main__":
    main()