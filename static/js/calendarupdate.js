window.onload = function (){
    var mtn = new Date();
    var chiffre = mtn.getUTCDate();
    console.log(chiffre);
    for(var i=1;i<chiffre+1;i++){
        let heure = document.getElementById(i.toString())
        heure.className = "mx-auto flex h-8 w-8 items-center justify-center rounded-full bg-gray-900 font-semibold text-white";
    }

}