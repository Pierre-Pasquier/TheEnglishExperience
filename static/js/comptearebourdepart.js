window.onload = function (){

    setInterval(diminuerTemps, 100)
}
function diminuerTemps() {
    var now = new Date();
    let timerHour = document.getElementById("hour")
    var jour = now.getDate()
    var heure   = ('0'+now.getHours()  ).slice(-2);
    var minute  = ('0'+now.getMinutes()).slice(-2);
    var seconde = ('0'+now.getSeconds()).slice(-2);
    timerHour.innerText = (30-jour).toString() + " jours "+(+"0"+ (23-heure).toString()  ).slice(-2) + " heures " +('0'+ (59 - minute).toString() ).slice(-2)   +" minutes "+('0'+ (59 - seconde).toString() ).slice(-2)+" secondes "

}