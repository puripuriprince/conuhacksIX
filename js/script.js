document.addEventListener("DOMContentLoaded", function(){
    let dataCache = [];  // Cache the fetched data
    function formatPhoneNumber(phoneNumberString) {
        var cleaned = ('' + phoneNumberString).replace(/\D/g, '');
        var match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
        if (match) {
          return '(' + match[1] + ') ' + match[2] + '-' + match[3];
        }
        return null;
      }
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
                            <strong>Phone:</strong><p id="phone">${formatPhoneNumber(itemData.phone)}</p>
                            <strong>${itemData.description.substring(0,8)}</strong><p id="desc">${itemData.description.substring(8,itemData.description.lenght)}</p>
                            `;
                }
            }
            if(event.target.classList.contains('accept') || event.target.classList.contains('decline')){
                deleteItem(event.target.id);
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
                <div class="item grab" id="${element._id}">
                    <div class="u${element.priority}"></div>
                    <div class="flex container">
                        <i class="fa-solid fa-exclamation orange icon openup" title="summary" id="${element._id}"></i>
                    </div>
                    <p class="description">${element.title} - ${element.category}</p>
                    <div class="flex container">
                        <i class="fa-solid fa-check green icon accept" title="accept" id="${element._id}"></i>
                    </div>
                    <div class="flex container">
                        <i class="fa-solid fa-xmark red icon decline" title="decline" id="${element._id}"></i>
                    </div>
                </div>
            `;
        });
    }    

    function fetchData() {
         // Fetch the data from the server
    fetch("http://127.0.0.1:5000/requests")
    .then(response => response.json())
    .then(data => informtionItem(data))
    .catch(error => console.error("Error:", error));

    }
     // Fetch data immediately when the page loads
     fetchData();

     // Fetch data every 5 seconds (adjust interval as needed)
     setInterval(fetchData, 5000);

     function deleteItem(itemId) {
        fetch(`http://127.0.0.1:5000/requests/${itemId}`, {
            method: "DELETE"
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.message) {
                fetchData(); // Refresh the data
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => console.error("Error:", error));
    }

        const draggable = document.getElementById('dragMe');
        const dropTarget = document.getElementById('dropTarget');

        // Event listener for when dragging starts
        draggable.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', e.target.id);
        });

        // Event listener to allow dropping
        dropTarget.addEventListener('dragover', (e) => {
            e.preventDefault(); // Allow the drop
            dropTarget.classList.add('over'); // Optional: highlight the drop target
        });
});
