# this comes from https://pypi.python.org/pypi/toposort
# but that version requires dict comprehension which we do not have in python 2.6
# TODO once I upgraded amazon to 2.7 we can get rid of this and install toposort
# NOTE we are currently not using the toposort
from functools import reduce as _reduce

def toposort(data):
    if len(data) == 0:
        return
    data = data.copy()
    for k, v in data.items():
        v.discard(k)
    extra_items_in_deps = _reduce(set.union, data.values()) - set(data.keys())
    #data.update({item:set() for item in extra_items_in_deps})
    #this line changed
    data.update(dict((item,set()) for item in extra_items_in_deps))
    while True:
        ordered = set(item for item, dep in data.items() if len(dep) == 0)
        if not ordered:
            break
        yield ordered
        data = dict((item, (dep - ordered))
                for item, dep in data.items()
                    if item not in ordered)
    if len(data) != 0:
        raise ValueError('Cyclic dependencies exist among these items: {}'.format(', '.join(repr(x) for x in data.items())))

def smaller_task_than_due(tid1, tid2, tasks):
    """
    Smaller than based on due date.
    """
    task1 = tasks[tid1]
    task2 = tasks[tid2]
    # Now on due dates
    if "due" in task1 and "due" in task2:
        return task1["due"] - task2["due"]
    # if only the first one has a due, it comes indeed before the one without
    # due
    elif "due" in task1:
        return -1
    elif "due" in task2:
        return 1
    else:
        return 0


def smaller_task_than(tid1, tid2, tasks):
    task1 = tasks[tid1]
    task2 = tasks[tid2]

    if "priority" in task1 and "priority" in task2:
        diff = task1["priority"] - task2["priority"]
        if diff != 0:
            return diff
        else:
            return smaller_task_than_due(tid1, tid2, tasks)
    # anything with priority is better than anything without priority
    elif "priority" in task1:
        return -1
    elif "priority" in task2:
        return 1
    else:
        return smaller_task_than_due(tid1, tid2, tasks)

def cyclic(data):
    try:
        sorted_data = list(toposort(data))
        return True
    except ValueError:
        return False

def sort_tasks(tasks):
    task_ids = tasks.keys()

    # data will be dict of { node: deps, node: deps}
    data = {}
    no_comes_after = set([])
    for task_id, item in tasks.iteritems():
        # we want the comes_after taken into account
        if 'comes_after' in item:
            data[task_id] = set([item['comes_after']])
        else:
            no_comes_after.add(task_id)

    # first topo sort for comes_after
    try:
        sorted_data = list(toposort(data))
    except ValueError:
        return task_ids
    
    # Now remove any element from no_comes_after that would actually be present
    # in the sorted data (this means the task ids themselves might have
    # occurred in the comes_after):
    for group in sorted_data:
        # difference update
        no_comes_after -= group
    # Now add the no_comes_after to the last group:
    if sorted_data:
        sorted_data[-1].update(no_comes_after)
    else:
        sorted_data.append(no_comes_after)
        

    # then sort each group on due date and priority
    result = []
    for group in sorted_data:
        sorted_group = sorted(group, cmp=lambda tid1, tid2: smaller_task_than(tid1, tid2, tasks))
        result += sorted_group

    # finally remove any task_ids that are in the sorted list (because they
    # appear in comes_after for example), but do not appear as keys in the
    # origin task list:
    result = [task_id for task_id in result if task_id in task_ids]

    return result
           
