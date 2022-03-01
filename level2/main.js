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
 * computes the commission of the user given the total amount of deals he sold during the month.
 * @param {*} objective - the user's objective.
 * @param {*} amount - the amount of deals, that is being commissioned.
 * @returns the commission of the user which is equal to the sum of :
 *      - 5% of what he sold between 0% and 50% of his objective
        - 10% of what he sold between 50% and 100% of his objective
        - 15% of what he sold above his objective
 */
function computeCommission(objective, amount) {
    var commission;
    if (amount >= objective){
        //commission = 0.05 * (0.5 * objective) + 0.1 * (0.5 * objective) + 0.15 * (amount - objective);
        commission = 0.15 * (0.5 * objective) + 0.15 * (amount - objective);
    }
    else if (amount >= (0.5 * objective)){ 
        commission = 0.05 * (0.5 * objective) + 0.1 * (amount - objective);
    }
    else {
        commission = 0.05 * amount
    }
    return commission; 
}

/**
 * For each user, computes the total amount of deals sold during the month.
 * @param {list} deals - each item is a JSON object having as keys : "id" (of deal), "amount", "user" (id of the user who sold the deal)
 * @param {list} users - each item is a JSON object having as keys : "id" (of user), "name", "objective".
 * @returns list - each item is a JSON object with the following keys : 
            "id", "name" (of user), 
            "deals_amount" (cumlative amount of deals sold by the user during the month),
 */
function accumulateDeals(deals, users){
    let usersIds = [];
    for (var i in users){
        usersIds.push(users[i]['id'])
        users[i]['deals_amount'] = 0
    }
    for (var i in deals){
        let j = usersIds.indexOf(deals[i]['user']);
        users[j]['deals_amount'] += deals[i]['amount'];
    }
    return users;
}

// ----------------
// main loop
// ----------------

/**
 * main loop.
 * @param {string} inputPath - path to the input data.
 * @param {string} outputPath - path to the output file.
 */
function main(inputPath, outputPath){
    // load data
    let jsonData = load(inputPath);
    let users = jsonData['users'];
    let deals = jsonData['deals'];

    // initialize outputs
    let result = [];
    
    users = accumulateDeals(deals, users);

    for (var i in users){
        let amount = users[i]['deals_amount'];
        let objective = users[i]['objective'];
        let commission = computeCommission(objective, amount);
        result.push({
            'user_id': users[i]['id'],
            'commission': commission
        })
    }

    // output
    let output = {
        "commissions": result
    }
    output = JSON.stringify(output, null, '\t');
    save(outputPath, output)
}


// ----------------
// test
// ----------------
main('./data/input.json', 'output_js.json');