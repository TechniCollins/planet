function modifyOrder(food_object, action){
    var item = food_object.getAttribute("item");
    var price = parseInt(food_object.getAttribute("price"));
    var cart = JSON.parse(document.getElementById("cart").getAttribute("items"));

    var num_items = parseInt(document.getElementById(item).innerHTML);
    var total = parseInt(document.getElementById("total").innerHTML);

    if (action == 0){
        if (num_items < 1){
            // Ignore removal
        }
        else{
           // remove food
           cart[item] = cart[item] - 1; // remove 1
           document.getElementById(item).innerHTML = num_items - 1;
           document.getElementById("total").innerHTML = total - price;
        }
    }
    else {
        // Add food
        cart[item] = (cart[item] || 0) + 1; // Add 1 or initialize to 0 then add 1
        document.getElementById(item).innerHTML = num_items + 1;
        document.getElementById("total").innerHTML = total + price;
    }

    document.getElementById("cart").setAttribute("items", JSON.stringify(cart));

    // Check if cart has anything in it, enable button if it does, disable if it doesn't
    for(var i in cart){
        if(cart[i]){
            document.getElementById("cart").setAttribute("class", "btn btn-primary");
            return; // At least 1 item is needed
        }
    }
    document.getElementById("cart").setAttribute("class", "btn btn-primary disabled");
}

const get = async (url, params) => {
    const response = await fetch(url + '?' + new URLSearchParams(params))
    const data = await response.json()

    return data
}

function submitOrder(object){
    var url = new URL(window.location);
    var time = url.searchParams.get("time");
    var table = url.searchParams.get("table");
    var items = encodeURIComponent(object.getAttribute("items"));

    // Call it with async:
    (async () => {
        const data = await get('/add-order', {
            time: time,
            table: table,
            items: items
        })

        if (data["id"]){
            window.location.replace("/confirm-payment?order_id=" + data["id"]);
        }
        else{
            alert("Something went wrong");
        }
    })()
}

