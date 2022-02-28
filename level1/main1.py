import json
import pandas as pd
import datetime

# IO utils
def load(path):
    with open(path) as file:
        data = json.load(file)
    return data

def save(path, output):
    with open(path, "w") as file:
        json.dump(output, file)
        #json.dump(output, file, indent=4)


# utils
def computeCommission(row):
    dealsCount = row['deals_count']
    dealsAmount = row['deals_amount']
    r = 0
    
    # compensation - fixed part
    if dealsCount <= 2:
        r = 0.1 * dealsAmount
    else:
        r = 0.2 * dealsAmount
    
    # compensation - bonus part
    if dealsAmount >= 2000:
        r += 500
    return r


def main(inputPath, outputPath):
    # load data
    jsonData = load(inputPath)

    # preprocess deals : accumulate deals per each user.
    df = pd.DataFrame.from_dict(jsonData['deals'])
    df = df[['user', 'amount']].copy()
    df = df.groupby('user')['amount'].agg(deals_amount='sum',deals_count='count').reset_index()
    
    # compute commissions
    df['commission'] = df.apply(computeCommission, axis=1)
    
    # setup output format
    df.rename(columns={"user": "user_id"}, inplace=True)
    df = df[['user_id', 'commission']].copy()
    result = pd.DataFrame.to_json(df, orient='records', lines=True)   

    # output
    output = {
        "commissions": result
    }
    save(outputPath, output)


# test
if __name__ == "__main__":
    t0 = datetime.datetime.now()
    for i in range(1000):
        main('./data/input.json', 'output_py.json')
    print((datetime.datetime.now()-t0).total_seconds()*1000)