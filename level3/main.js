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
 * returns the commission Interval given the user's objective and the progress (amount of deals) he made so far.
 *          - 0.15 if (the progress is above his objective)                     --> 15% Interval
            - 0.1  if (the progress is between 50% and 100% of his objective)   --> 10% Interval
            - 0.05 if (the progress is between 0% and 50% of his objective)     --> 5% Interval
 * @param {float} objective - the user's objective
 * @param {float} progress - the progress made by the user during the month so far (amount of deals sold) 
 * @returns the commission Interval (0.05, 0.1 or 0.15)
 */
function getCommissionInterval(objective, progress){
    var p;
    if (progress > objective){p = 0.15;}
    else if (progress > (0.5 * objective)){p = 0.1;}
    else {p = 0.05;}
    return p;
}

/**
 * computes the commission of a deal, when the deal is split between two intervals.
 * @param {float} threshold - threshold seperating the two intervals. It can be either (50% of the objective) or (the objective).
 * @param {float} progress - the cumulative sum of deals commissioned so far.
 * @param {float} amount - the amount of the current deal, that is being commissioned.
 * @param {float} currInterval - the Commissioning Interval reached so far (with 'progress')
 * @param {float} nextInterval - the Commissioning Interval to be reached after closing the current deal (with 'progress + amount')
 * @returns the commission associated to the deal.
 */
function twoSplitsCommission(threshold, progress, amount, currInterval, nextInterval){
    var amount1 = threshold - progress; 
    return amount1 * currInterval + (amount - amount1) * nextInterval;
}

/**
 * computes the commission of a deal given its amount, the user's objective and how far has he progressed towards his objective.
 * @param {*} objective - the user's objective.
 * @param {*} progress - the cumulative sum of deals commissioned so far (taken in their chronological order)
 * @param {*} amount - the amount of the current deal, that is being commissioned.
 * @returns the commission associated to the deal.
 */
function computeCommission(objective, progress, amount) {
    var currInterval = getCommissionInterval(objective, progress);
    var nextInterval = getCommissionInterval(objective, progress + amount);
    var commission;
 
    if (currInterval === nextInterval){
        // By closing this deal, the salesman will stay in the same interval of progress with respect to his objective.
        commission = amount * nextInterval;
    }
    else if (currInterval == 0.05 && nextInterval == 0.1){
        // The salesman will switch from the 5% interval to the 10% interval.
        // Therefore the deal is split into the two intervals from either side of the THRESHOLD = "50% of his objective"
        commission = twoSplitsCommission(0.5 * objective, progress, amount, currInterval, nextInterval);
    }
    else if (currInterval == 0.1 && nextInterval == 0.15){
        // The salesman will switch from the 5% interval to the 10% interval.
        // Therefore the deal is split into the two intervals from either side of the THRESHOLD = "100% of his objective"
        commission = twoSplitsCommission(objective, progress, amount, currInterval, nextInterval);
    }
    else if (currInterval == 0.05 && nextInterval == 0.15){
        // The salesman will switch from the 5% interval to the 15% interval.
        // Therefore the deal is split into the three intervals (5%, 10% and 15% interval)
        var amount1 = 0.5 * objective - progress; // amount to reach 10% interval
        var amount2 = 0.5 * objective; // amount to reach 15% interval
        var amount3 = amount - (amount1 + amount2);
        commission = amount1 * 0.05 + amount2 * 0.1 + amount3 * 0.15;
    }
    else {
        throw 'error';
    }
    return commission; 
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
    var jsonData = load(inputPath);
    var users = jsonData['users'];
    var deals = jsonData['deals'];
    
    // initialize outputs and auxiliary variables
    var outDeals = [];
    var outCommissions = []; 
    var usersIds = [];
    var monthProgress = [];
    for (var i in users){
        var id = users[i]['id'];
        outCommissions.push({"user_id": id, "commission": {}});
        outDeals.push({"user_id": id, "deals": []})
        usersIds.push(id);
        monthProgress.push(0);
    }

    // preprocess
    for (var i in deals){
        var deal = deals[i];
        var idx = usersIds.indexOf(deal['user']);
        var commissions = outCommissions[idx]['commission'];
        var objective = users[idx]['objective'];
        var amount = deal['amount'];
        var month = deal['payment_date'].substring(0,7);
        
        if (commissions.hasOwnProperty(month)){
            progress = monthProgress[idx];
            c0 = commissions[month];
        }
        else{
            progress = 0;
            c0 = 0;
        }

        c = computeCommission(objective, progress, amount)
        outCommissions[idx]['commission'][month] = c0 + c;
        monthProgress[idx] = progress + amount;

        outDeals[idx]['deals'].push({"id": deal['id'],"commission": c});
    }

    sortedDeals = [];
    for (var i in outDeals){
        sortedDeals.push(outDeals[i]['deals'])
    }
    // output
    var output = {
        "commissions": outCommissions,
        "deals": sortedDeals
    }
    output = JSON.stringify(output, null, '\t');
    save(outputPath, output);
}


// ----------------
// test
// ----------------
main('./data/input.json', 'output_js.json');