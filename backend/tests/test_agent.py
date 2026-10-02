from app.agent.agent import agent


def get_last_message(response):
    return response["messages"][-1].content


def test_multiturn_booking():
    config = {
        "configurable": {
            "thread_id": "stage7-booking-test"
        }
    }

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "I want to book an appointment with Dr. Rahman."
                }
            ]
        },
        config=config,
    )

    print("\nAI:", get_last_message(response))

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "October 1, 2026."
                }
            ]
        },
        config=config,
    )

    print("\nAI:", get_last_message(response))

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "John Doe."
                }
            ]
        },
        config=config,
    )

    print("\nAI:", get_last_message(response))

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "017XXXXXXXX"
                }
            ]
        },
        config=config,
    )

    print("\nFINAL AI:", get_last_message(response))

    assert response is not None