document.addEventListener("DOMContentLoaded", function(){
    document.getElementById('containerContent').addEventListener("click", function(event){
        if(event.target.id == "openUp" || event.target.id == "close"){
            let boxDesc = document.getElementById('descBox');
            if(boxDesc.classList.contains('see')){
                boxDesc.classList.replace('see', 'unsee');
            }else{
                boxDesc.classList.replace('unsee', 'see');
            }
        }
    });
});