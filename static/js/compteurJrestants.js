window.onload = function (){
        var mtn = new Date();
    var chiffre = mtn.getUTCDate();
    for(var i=1;i<chiffre+1;i++){
        let heure = document.getElementById(i.toString())
        heure.className = "mx-auto flex h-8 w-8 items-center justify-center rounded-full bg-lime-600 font-semibold text-white";}

    setInterval(diminuerTemps, 100)
}

function diminuerTemps() {
    var now = new Date();
    let timerHour = document.getElementById("hour")
    var heure   = ('0'+now.getHours()  ).slice(-2);
    var minute  = ('0'+now.getMinutes()).slice(-2);
    var seconde = ('0'+now.getSeconds()).slice(-2);
    timerHour.innerText = ('0'+ (23-heure).toString()  ).slice(-2) + " : "+('0'+ (59 - minute).toString() ).slice(-2)   +" : "+('0'+ (59 - seconde).toString() ).slice(-2)

}


