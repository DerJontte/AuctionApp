function updateCur(rate){
    let input = document.getElementById("starting_price");
    let output = document.getElementById("converted");
    output.innerHTML = (input.value * rate).toFixed(2);
}