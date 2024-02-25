def model_dict_or_none(model: object | None) -> str:
    if model:
        return f'{model.__dict__=}'
    return f'is {None}'
