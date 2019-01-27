function updateCur(rate){
    let input = document.getElementById("starting_price");
    let output = document.getElementById("converted");
    output.innerHTML = (input.value * rate).toFixed(2);
}

function validateForm(current_price) {
    let input = document.getElementById("starting_price")
    let bid = input.value;
    if (bid <= current_price) {
        alert("New bid must be higher than the current bid.");
        return false;
    }
    if (isNaN(bid)){
        alert("Please input a number.")
        return false;
    }
    if (bid.includes(".") && bid.split(".")[1].length > 2) {
        alert("Please use numbers with two decimal places or less.")
        return false;
    }
}
