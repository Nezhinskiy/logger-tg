def model_dict_or_none(model):
    if model:
        return f'{model.__dict__=}'
    return f'is {None}'
