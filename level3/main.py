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

def getCommissionInterval(objective, progress):
    """ returns the commission Interval given the 'objective' of the user and the 'progress' (amount of deals) he made so far.
            - 0.15 if (the progress is above his objective)                     --> 15% Interval
            - 0.1  if (the progress is between 50% and 100% of his objective)   --> 10% Interval
            - 0.05 if (the progress is between 0% and 50% of his objective)     --> 5% Interval

    Args:
        objective (float): the user's objective
        progress (float): the amount of deals he sold so far. (How far has he progressed towards his objective)

    Returns:
        float: the corresponding interval (0.05, 0.1 or 0.15)
    """
    if (progress > objective):
        p = 0.15
    elif (progress > (0.5 * objective)):
        p = 0.1
    else:
        p = 0.05
    return p

def twoSplitsCommission(threshold, progress, amount, currInterval, nextInterval):
    """ computes the commission of a deal, when the deal is split between two intervals.

    Args:
        threshold (float): threshold seperating the two intervals. It can be either (50% of the objective) or (the objective).
        progress (float): the cumulative sum of deals commissioned so far.
        amount (float): the amount of the current deal, that is being commissioned.
        currInterval (float): the Commissioning Interval reached so far (with 'progress')
        nextInterval (float): the Commissioning Interval to be reached after closing the current deal (with 'progress + amount')

    Returns:
        float: the commission associated to the deal.
    """
    amount1 = threshold - progress
    return amount1 * currInterval + (amount - amount1) * nextInterval

def computeCommission(objective, progress, amount):
    """ computes the commission of a deal given its amount, the user's objective and how far has he progressed towards his objective.

    Args:
        objective (float): the user's objective
        progress (float): the cumulative sum of deals commissioned so far.
        amount (float): the amount of the current deal, that is being commissioned.

    Raises:
        ValueError: 

    Returns:
        float: the commission associated to the deal.
    """
    currInterval = getCommissionInterval(objective, progress)
    nextInterval = getCommissionInterval(objective, progress + amount)
 
    if (currInterval == nextInterval):
        # By closing this deal, the salesman will stay in the same interval of progress with respect to his objective.
        commission = amount * nextInterval

    elif (currInterval == 0.05 and nextInterval == 0.1):
        # The salesman will switch from the 5% interval to the 10% interval.
        # Therefore the deal is split into the two intervals from either side of the THRESHOLD = "50% of his objective"
        commission = twoSplitsCommission(0.5 * objective, progress, amount, currInterval, nextInterval)
    
    elif (currInterval == 0.1 and nextInterval == 0.15):
        # The salesman will switch from the 5% interval to the 10% interval.
        # Therefore the deal is split into the two intervals from either side of the THRESHOLD = "100% of his objective"
        commission = twoSplitsCommission(objective, progress, amount, currInterval, nextInterval)
    
    elif (currInterval == 0.05 and nextInterval == 0.15):
        # The salesman will switch from the 5% interval to the 15% interval.
        # Therefore the deal is split into the three intervals (5%, 10% and 15% interval)
        amount1 = 0.5 * objective - progress; # amount to reach 10% interval
        amount2 = 0.5 * objective; # amount to reach 15% interval
        amount3 = amount - (amount1 + amount2)
        commission = amount1 * 0.05 + amount2 * 0.1 + amount3 * 0.15
    
    else:
        raise ValueError
    return commission

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
    users = jsonData['users']
    deals = jsonData['deals']

    
    # initialize outputs and auxiliary variables
    outDeals = []
    outCommissions = []
    usersIds = []
    monthProgress = []
    for i in range(len(users)):
        id = users[i]['id']
        outCommissions.append({"user_id": id, "commission": {}})
        outDeals.append({"user_id": id, "deals": []})
        usersIds.append(id)
        monthProgress.append(0)
    

    # process deals
    for i in range(len(deals)):
        deal = deals[i]
        idx = usersIds.index(deal['user'])
        commissions = outCommissions[idx]['commission']
        objective = users[idx]['objective']
        amount = deal['amount']
        month = deal['payment_date'][:7]

        # compute the commission associated to the deal
        if (month in commissions):
            progress = monthProgress[idx]
            c0 = commissions[month]
        else:
            progress = 0
            c0 = 0
        c = computeCommission(objective, progress, amount)

        # update output and auxiliary variables
        outCommissions[idx]['commission'][month] = c0 + c
        outDeals[idx]['deals'].append({"id": deal['id'],"commission": c})
        monthProgress[idx] = progress + amount

    # sort deals (and their associated commissions) by users 
    sortedDeals = []
    for i in range(len(outDeals)):
        sortedDeals.append(outDeals[i]['deals'])

    # save output
    output = {
        "commissions": outCommissions,
        "deals": sortedDeals
    }
    save(outputPath, output)


# ----------------
# test
# ----------------
if __name__ == "__main__":
    main('./data/input.json', 'output_py.json')