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

def computeCommission(dealsCount, dealsAmount):
    """ calculate the compensation of a given user, knowing what deals he sold during the month.
        Users are commissioned as follow:
            - 10% of what they sold if they sold 1 or 2 deals during the month
            - 20% of what they sold if they sold 3 deals or more
            - 500 euros bonus if they sold more than 2000 euros in the month

    Args:
        dealsCount (int): number of deals the user sold during the month.
        dealsAmount (float): total amount of deals the user sold during the month.

    Returns:
        float: the commission of the user. 
    """
    if dealsCount <= 2:
        p = 0.1
    else:
        p = 0.2
    r = p * dealsAmount + (500 if dealsAmount >= 2000 else 0) 
    return r

def accumulateDeals(deals, users):
    """ For each user, compute the 'total amount' + 'the number' of deals sold during the month.

    Args:
        deals (list): each item is a JSON object having as keys : "id" (of deal), "amount", "user" (id of the user who sold the deal)
        users (list): each item is a JSON object having as keys : "id" (of user), "name".

    Returns:
        list: each item is a JSON object with the following keys : 
            "id", "name" (of user), 
            "deals_amount" (cumlative amount of deals sold by the user during the month),
            "deals_count" (number of deals sold by the user during the month)
    """
    usersIds = []
    for i in range(len(users)):
        usersIds.append(users[i]['id'])
        users[i]['deals_amount'] = 0
        users[i]['deals_count'] = 0
    
    for i in range(len(deals)):
        deal = deals[i]
        j = usersIds.index(deal['user'])
        users[j]['deals_amount'] += deal['amount']
        users[j]['deals_count'] += 1
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
    
    # preprocess data
    users = jsonData['users']
    deals = jsonData['deals']
    users = accumulateDeals(deals, users)
    
    # compute commissions
    result = []
    for i in range(len(users)):
        dealsCount = users[i]['deals_count']
        dealsAmount = users[i]['deals_amount']
        commission = computeCommission(dealsCount, dealsAmount)
        result.append({
            'user_id': users[i]['id'],
            'commission': commission
        })

    # save output
    output = {"commissions": result}
    save(outputPath, output)


# ----------------
# test
# ----------------
if __name__ == "__main__":
    main('./data/input.json', 'output_py.json')