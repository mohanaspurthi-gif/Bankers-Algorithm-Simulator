def calculate_need(maximum, allocation):
    """
    Calculate the remaining resources needed by each process.

    maximum:    maximum demand matrix
    allocation: currently allocated resources matrix
    """
    if len(maximum) != len(allocation):
        raise ValueError("Maximum and Allocation must have the same number of processes.")

    need = []

    for i in range(len(maximum)):
        if len(maximum[i]) != len(allocation[i]):
            raise ValueError("Maximum and Allocation must have matching resource columns.")

        row = []
        for j in range(len(maximum[i])):
            if allocation[i][j] > maximum[i][j]:
                raise ValueError(
                    f"Allocation cannot exceed maximum demand (process P{i}, resource {j})."
                )
            row.append(maximum[i][j] - allocation[i][j])

        need.append(row)

    return need


def safety_algorithm(available, allocation, need):
    """
    Determine whether the current system state is safe.

    Returns:
        (True, safe_sequence) if every process can finish.
        (False, partial_sequence) otherwise.
    """
    process_count = len(allocation)
    resource_count = len(available)

    if len(need) != process_count:
        raise ValueError("Need and Allocation must have the same number of processes.")

    if any(len(row) != resource_count for row in allocation):
        raise ValueError("Each Allocation row must match the number of resource types.")

    if any(len(row) != resource_count for row in need):
        raise ValueError("Each Need row must match the number of resource types.")

    if any(value < 0 for value in available):
        raise ValueError("Available resources cannot be negative.")

    work = available.copy()
    finish = [False] * process_count
    safe_sequence = []

    while len(safe_sequence) < process_count:
        found_process = False

        for i in range(process_count):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(resource_count)):
                # This process can finish, so it releases its allocated resources.
                for j in range(resource_count):
                    work[j] += allocation[i][j]

                finish[i] = True
                safe_sequence.append(i)
                found_process = True

        if not found_process:
            break

    return len(safe_sequence) == process_count, safe_sequence


def check_resource_request(process_id, request, available, allocation, maximum):
    """
    Check whether a resource request can be granted safely.

    Returns a dictionary containing the decision and relevant state.
    Process IDs are zero-based: 0 means P0, 1 means P1, etc.
    """
    process_count = len(allocation)
    resource_count = len(available)

    if process_id < 0 or process_id >= process_count:
        raise ValueError("Invalid process ID.")

    if len(request) != resource_count:
        raise ValueError("Request must contain one value for each resource type.")

    need = calculate_need(maximum, allocation)

    if any(value < 0 for value in request):
        raise ValueError("A request cannot contain negative values.")

    if any(request[j] > need[process_id][j] for j in range(resource_count)):
        return {"granted": False, "message": "Request exceeds this process's remaining need."}

    if any(request[j] > available[j] for j in range(resource_count)):
        return {"granted": False, "message": "Not enough resources are currently available."}

    # Temporarily allocate the requested resources.
    new_available = [
        available[j] - request[j] for j in range(resource_count)
    ]
    new_allocation = [row.copy() for row in allocation]
    for j in range(resource_count):
        new_allocation[process_id][j] += request[j]

    new_need = calculate_need(maximum, new_allocation)
    is_safe, sequence = safety_algorithm(new_available, new_allocation, new_need)

    if is_safe:
        return {
            "granted": True,
            "message": "Request can be granted; the resulting state is safe.",
            "available": new_available,
            "allocation": new_allocation,
            "need": new_need,
            "safe_sequence": sequence,
        }

    return {
        "granted": False,
        "message": "Request cannot be granted because it would leave the system unsafe.",
        "safe_sequence": sequence,
    }
