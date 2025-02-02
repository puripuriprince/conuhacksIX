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
    fetch("http://127.0.0.1:5000/requests")
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error("Error:", error));
});
