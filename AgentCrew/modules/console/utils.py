def agent_evaluation_remove(data: str) -> str:
    if "<agent_evaluation>" in data and "</agent_evaluation>" in data:
        data = (
            data[: data.find("<agent_evaluation>")]
            + data[data.find("</agent_evaluation>") + 19 :]
        )
    return data
