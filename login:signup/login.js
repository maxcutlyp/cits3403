function passconfirm(){
    var pass1 = document.getElementById("pass1");
    var pass2 = document.getElementById("pass2");
    const passmatch = document.createTextNode("Passwords do not match");
    if(pass1.length != pass2.length){
        document.appendChild(passmatch);
    }
    else{
        for(let i = 0; i < pass1.clientHeight; i++){
            if(pass1[i] != pass2[i]){
                document.appendChild(passmatch);
                break;
            }
        }
    }
    
}