// ----------------
// IO utils
// ----------------

function load(path){
    try {
        var data = require(path);
    } catch (error) {
        console.log(error);
    }
    return data;
}

function save(path, output){
    var fs = require('fs');
    fs.writeFile(path, output, function(err) {
        if (err) {
            console.log(err);
        }
});
}

// ----------------
// functional utils
// ----------------

/**
 * calculate the compensation of a given user, knowing what deals he sold during the month.            
 * @param {int} dealsCount - number of deals the user sold during the month.
 * @param {float} dealsAmount - total amount of deals the user sold during the month. 
 * @returns float - the commission of the user which is equal to :
 *          - 10% of what he sold if he sold 1 or 2 deals during the month
            - 20% of what he sold if he sold 3 deals or more
            - 500 euros bonus if he sold more than 2000 euros in the month
 */
function userCompensation(dealsCount, dealsAmount) {
    var r = 0; 
    // compensation - fixed part
    if (dealsCount <= 2){ 
        r = 0.1 * dealsAmount;
    }
    else{
        r = 0.2 * dealsAmount;
    }
    // compensation - bonus part
    if (dealsAmount >= 2000){
        r += 500;
    }
    return r; 
}

/**
 * For each user, compute the 'total amount' + 'the number' of deals sold during the month.
 * @param {list} deals - each item is a JSON object having as keys : "id" (of deal), "amount", "user" (id of the user who sold the deal) 
 * @param {list} users - each item is a JSON object having as keys : "id" (of user), "name".
 * @returns list: each item is a JSON object with the following keys : 
            "id", "name" (of user), 
            "deals_amount" (cumlative amount of deals sold by the user during the month),
            "deals_count" (number of deals sold by the user during the month)
 */
function accumulateDeals(deals, users){
    var usersIds = [];
    for (var i in users){
        usersIds.push(users[i]['id'])
        users[i]['deals_amount'] = 0
        users[i]['deals_count'] = 0
    }
    for (var i in deals){
        var deal = deals[i]
        var j = usersIds.indexOf(deal['user']);
        users[j]['deals_amount'] += deal['amount'];
        users[j]['deals_count'] += 1;
    }
    return users;
}

// ----------------
// main loop
// ----------------

/**
 * main loop.
 * @param {string} inputPath - path to the input data
 * @param {string} outputPath - path to the output file
 */
function main(inputPath, outputPath){
    // load data
    var jsonData = load(inputPath);

    // preprocess data
    var users = jsonData['users'];
    var deals = jsonData['deals'];
    users = accumulateDeals(deals, users);
    
    // compute commissions
    var result = [];
    for (var i in users){
        var dealsCount = users[i]['deals_count'];
        var dealsAmount = users[i]['deals_amount'];
        var compensation = userCompensation(dealsCount, dealsAmount);
        result.push({
            'user_id': users[i]['id'],
            'commission': compensation
        })
    }

    // save output
    var output = {
        "commissions": result
    }
    output = JSON.stringify(output, null, '\t');
    save(outputPath, output)
}


// ----------------
// test
// ----------------
main('./data/input.json', 'output.json');