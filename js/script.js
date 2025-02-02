document.addEventListener("DOMContentLoaded", function(){
    let dataCache = [];  // Cache the fetched data

    // Event listener for opening the description box
    document.getElementById('containerContent').addEventListener("click", function(event){
        if(event.target.classList.contains("openup") || event.target.id == "close"){
            let boxId = event.target.id;  // Get the id of the clicked item
            let boxDesc = document.getElementById('descBox');
            let contentBox = document.getElementById('contentsBox');
            // Find the corresponding data based on the boxId
            let itemData = dataCache.find(item => item._id === boxId);
                // Toggle description visibility
                if(boxDesc.classList.contains('see')){
                    boxDesc.classList.replace('see', 'unsee');
                } else {
                    boxDesc.classList.replace('unsee', 'see');

                    // Populate the description box with relevant information
                    contentBox.innerHTML = `   
                            <strong>Category:</strong><p id="category">${itemData.category}</p>
                            <strong>Phone:</strong><p id="phone">${itemData.phone}</p>
                            <strong>${itemData.description.substring(0,8)}</strong><p id="desc">${itemData.description.substring(8,itemData.description.lenght)}</p>
                            `;
                }
            }
    });

    function informtionItem(data){
        dataCache = [];  //  Réinitialiser le cache
        let itemContainer = document.getElementById('contentItems');
        itemContainer.innerHTML = "";
        data.forEach(element => {
            if (!dataCache.some(item => item._id === element._id)) {  // Éviter les doublons
                dataCache.push(element);
            }
    
            itemContainer.innerHTML += `  <!-- Use innerHTML += to append, not overwrite -->
                <div class="item">
                    <div class="u${element.priority}"></div>
                    <div class="flex container">
                        <i class="fa-solid fa-exclamation orange icon openup" title="description" id="${element._id}"></i>
                    </div>
                    <p class="description">${element.title}</p>
                    <div class="flex container">
                        <i class="fa-solid fa-check green icon accept" title="accept" id="accept"></i>
                    </div>
                    <div class="flex container">
                        <i class="fa-solid fa-xmark red icon decline" title="decline" id="decline"></i>
                    </div>
                </div>
            `;
        });
    }    

    // Fetch the data from the server
    fetch("http://127.0.0.1:5000/requests")
    .then(response => response.json())
    .then(data => informtionItem(data))
    .catch(error => console.error("Error:", error));
});
