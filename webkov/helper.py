from webkov.tarjan import tarjan


# take a model of order 1, returning the largest strongly connected
# component. This will be used as a filter for the model, rejecting
# all applicants not connected
def helper(model, order=1, tarjan=tarjan):
    if not order == 1:
        # still thinking about how to implement this for any order
        # and I can't catch NotImplemented.
        raise ValueError
    return max(
        tarjan({key[0]: list(value.keys()) for key, value in model.items()}),
        key=len)


def filtered_model(model, order=1):
    filt = helper(model, order)
    return {key: value for key, value in model if key in filt}
