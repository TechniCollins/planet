function toIsoString(date) {
  var tzo = -date.getTimezoneOffset(),
      dif = tzo >= 0 ? '+' : '-',
      pad = function(num) {
          return (num < 10 ? '0' : '') + num;
      };

      iso_date = date.getFullYear() +
                 '-' +
                 pad(date.getMonth() + 1) +
                 '-' +
                 pad(date.getDate()) +
                 'T' +
                 pad(date.getHours()) +
                 ':' +
                 pad(date.getMinutes())

      tz = dif + pad(Math.floor(Math.abs(tzo) / 60)) +
      ':' + pad(Math.abs(tzo) % 60)

  return [iso_date, tz];
}

var dt = toIsoString(new Date());
// Get ISO 8601 formated date and time zone
iso_date = dt[0];
tz = dt[1];
document.getElementById("order-time").value = iso_date;
document.getElementById("order-time").max = iso_date;

function disableTimeChange(){
    document.getElementById("order-time").disabled = true;
};

function changeTime(){
    document.getElementById("order-time").disabled = false;
};

function selectTable(){
    var table = document.querySelector('input[name="table"]:checked').value;
    var dt = document.getElementById("order-time").value;
    if (dt && table){
      window.location.replace("/items" + "?table=" + table + "&time=" + encodeURIComponent(dt) + encodeURIComponent(tz));
    }
    else{
      alert("Please select a table and a date");
    }
};