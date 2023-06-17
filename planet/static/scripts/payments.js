const get = async (url, params) => {
    const response = await fetch(url + '?' + new URLSearchParams(params))
    const data = await response.json()

    return data
}

function validatePayment(object){
    var url = new URL(window.location);
    var order_id = url.searchParams.get("order_id");

    var action = "confirm-payment";
    var mpesa = document.getElementById("mpesa").value;
    var cash = document.getElementById("cash").value;

    // Call it with async:
    (async () => {
        const data = await get('', {
            action: action,
            order_id: order_id,
            mpesa: mpesa,
            cash: cash
        })

        if (data["status"]){
            alert(data["message"])
            window.location.replace("/");
        }
        else{
            alert(data["message"]);
        }
    })()
}