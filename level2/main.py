import json

# ----------------
# IO utils
# ----------------

def load(path):
    with open(path) as file:
        data = json.load(file)
    return data

def save(path, output):
    with open(path, "w") as file:
        json.dump(output, file, indent=4)

# ----------------
# functional utils
# ----------------

def computeCommission(objective, amount):
    """computes the commission of the user given the total amount of deals he sold during the month.

    Args:
        objective (float): the user's objective.
        amount (float): the amount of deals, that is being commissioned.

    Returns:
        float: the commission of the user which is equal to the sum of :
            - 5% of what he sold between 0% and 50% of his objective
            - 10% of what he sold between 50% and 100% of his objective
            - 15% of what he sold above his objective
    """
    if (amount >= objective):
        # commission = 0.05 * (0.5 * objective) + 0.1 * (0.5 * objective) + 0.15 * (amount - objective);
        commission = 0.15 * (0.5 * objective) + 0.15 * (amount - objective)
    
    elif (amount >= (0.5 * objective)):
        commission = 0.05 * (0.5 * objective) + 0.1 * (amount - objective)
    
    else:
        commission = 0.05 * amount

    return commission 

def accumulateDeals(deals, users):
    """For each user, computes the total amount of deals sold during the month.

    Args:
        deals (list): each item is a JSON object having as keys : "id" (of deal), "amount", "user" (id of the user who sold the deal)
        users (list): each item is a JSON object having as keys : "id" (of user), "name", "objective".

    Returns:
        list: each item is a JSON object with the following keys : 
            "id", "name" (of user), 
            "deals_amount" (cumlative amount of deals sold by the user during the month),
    """
    usersIds = []
    for i in range(len(users)):
        usersIds.append(users[i]['id'])
        users[i]['deals_amount'] = 0
    
    for i in range(len(deals)):
        j = usersIds.index(deals[i]['user'])
        users[j]['deals_amount'] += deals[i]['amount']
    
    return users

# ----------------
# main loop
# ----------------

def main(inputPath, outputPath):
    """ main function

    Args:
        inputPath (string): path to the input data
        outputPath (string): path to the output file
    """
    # load data
    jsonData = load(inputPath)

    # preprocess
    users = jsonData['users']
    deals = jsonData['deals']
    users = accumulateDeals(deals, users)

    # initialize outputs
    result = []
    
    for i in range(len(users)):
        amount = users[i]['deals_amount']
        objective = users[i]['objective']
        commission = computeCommission(objective, amount)
        result.append({
            'user_id': users[i]['id'],
            'commission': commission
        })

    # save output
    output = {
        "commissions": result
    }
    save(outputPath, output)


# ----------------
# test
# ----------------
if __name__ == "__main__":
    main('./data/input.json', 'output_py.json')