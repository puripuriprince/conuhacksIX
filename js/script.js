
 
document.addEventListener("DOMContentLoaded", function(){
    let tasks = [{
        "address": "101 Main St, Downtown, Cityville",
        "phone": "555-123-4567",
        "priority": 1,
        "description": "A person has collapsed and is unresponsive. Immediate medical attention required.",
        "title": "Medical Emergency: Unresponsive Person",
        "category": "Medical 🚑"
    },
    {
        "address": "250 Oak Ave, Suburbia, Cityville",
        "phone": "555-987-6543",
        "priority": 2,
        "description": "A fire has started in a building. Evacuation in progress, but fire is not yet under control.",
        "title": "Fire Emergency: Building Evacuation",
        "category": "Fire 🚒"
    },
    {
        "address": "500 Maple St, Northside, Cityville",
        "phone": "555-246-8101",
        "priority": 3,
        "description": "Suspicious activity reported in a parking lot, but no immediate threat detected. Authorities are requested for investigation.",
        "title": "Suspicious Activity: Investigation Requested",
        "category": "Police 🚔"
    },{
        "address": "200 River Rd, Coastal City",
        "phone": "555-321-9876",
        "priority": 1,
        "description": "A car accident involving multiple vehicles with injuries. Ambulance and fire trucks urgently needed.",
        "title": "Motor Vehicle Accident: Multiple Injuries",
        "category": "Medical 🚑"
    },
    {
        "address": "75 Pine Rd, Countryside, Cityville",
        "phone": "555-654-3210",
        "priority": 2,
        "description": "A person is trapped in a house due to flooding. Help is needed to rescue the individual. Flooding is moderate but increasing.",
        "title": "Flooding Emergency: Person Trapped",
        "category": "Flood 🚒"
    },
    {
        "address": "88 Elm St, Westside, Cityville",
        "phone": "555-369-2580",
        "priority": 3,
        "description": "An abandoned vehicle blocking a minor road. No immediate danger, but requires removal for traffic flow.",
        "title": "Non-Emergency: Abandoned Vehicle",
        "category": "Police 🚔"
    }       
    ]

    function sendTasksToDatabase(tasks) {
        fetch('http://127.0.0.1:8000/add-task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(tasks)  // Convert tasks array to JSON string
        })
        .then(response => response.json())  // Parse the response as JSON
        .then(data => {
            console.log('Success:', data);  // Handle the success response
        })
        .catch((error) => {
            console.error('Error:', error);  // Handle any errors
        });
    }

    function fetchData() {
        // Fetch the data from the server
   fetch("http://127.0.0.1:8000/requests")
   .then(response => response.json())
   .then(data => informtionItem(data))
   .catch(error => console.error("Error:", error));

   }
    // Fetch data immediately when the page loads
    fetchData();

    // Fetch data every 5 seconds (adjust interval as needed)
    setInterval(fetchData, 5000);

    function deleteItem(itemId) {
       fetch(`http://127.0.0.1:8000/requests/${itemId}`, {
           method: "DELETE"
       })
       .then(response => response.json())
       .then(data => {
           if (data.message) {
               fetchData(); // Refresh the data
           } else {
               alert("Error: " + data.error);
           }
       })
       .catch(error => console.error("Error:", error));
   }
    let names = [
        "Alice Dupont",
        "Pierre Martin",
        "Sophie Lefevre",
        "Louis Bernard",
        "Claire Moreau",
        "Marc Robert",
        "Juliette Dufresne",
        "Vincent Lemoine",
        "Isabelle Lefevre",
        "Antoine Gauthier"
    ];    
    function moveNameToEnd(index) {
        if (index >= 0 && index < names.length) {  // Ensure index is within the array bounds
            let name = names.splice(index, 1)[0];  // Remove the name by index
            names.push(name);  // Add it to the end of the array
        } else {
            console.log("Invalid index");
        }
    }
    function populate(){
        console.log(names);
        let side =  document.getElementById('sidePannel');
        side.innerHTML = "";
        for(let i = 0; i < names.length;i++){
            side.innerHTML += `
            <div class="user-item">
            <i class="fa-solid fa-user icon user"></i>
            <p>${names[i]}</p>
            <input type="checkbox" id="${i}" class="check-two"/>
        </div>`;
        };
    }
    populate();
    let mapsLocation = [
    "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2795.196749225881!2d-73.59774788443732!3d45.507047479101095!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x4cc91a3f18b3a925%3A0xb3a61f7b15b3b8ef!2sMount%20Royal!5e0!3m2!1sen!2sca!4v1706900000000",
    "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2795.086144473391!2d-73.55336308443723!3d45.50300147910109!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x4cc91a44184b3f71%3A0x92fdf2c9467251d4!2sOld%20Montreal!5e0!3m2!1sen!2sca!4v1706900000001",
    "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2795.1521126033055!2d-73.55648638443731!3d45.504498479101086!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x4cc91a46f52b405b%3A0x391f9794e82d3277!2sNotre-Dame%20Basilica%20of%20Montreal!5e0!3m2!1sen!2sca!4v1706900000002",
    "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2796.314251158902!2d-73.55220068443753!3d45.559958279101074!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x4cc91a9c914d2a8d%3A0x2b3e1c29042a16a!2sMontreal%20Biodome!5e0!3m2!1sen!2sca!4v1706900000004",
    "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2795.2485426853554!2d-73.57947408443743!3d45.50338547910107!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x4cc91a5b12d2dfad%3A0x7f9b8aa6ff99c9fd!2sMontreal%20Museum%20of%20Fine%20Arts!5e0!3m2!1sen!2sca!4v1706900000005",
    "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2795.678221234785!2d-73.62059048443734!3d45.53758647910106!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x4cc91a92cbe9b7d1%3A0x7b67f021d12384cd!2sJean-Talon%20Market!5e0!3m2!1sen!2sca!4v1706900000006",
    "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2795.340048124982!2d-73.57814598443743!3d45.504790479101074!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x4cc91a4855f2f41d%3A0x4d1b4a6c8c917e5e!2sMcGill%20University!5e0!3m2!1sen!2sca!4v1706900000007",
    ]
    let mapIndex=0;
    function updateMap() {
        let mapFrame = document.getElementById("mapFrame");
        mapIndex = Math.floor(Math.random() * mapsLocation.length);
        // Construct the new Embed URL using place names
        let newSrc = mapsLocation[mapIndex];

        mapFrame.src = newSrc;
    }
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
                    updateMap();
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
    let first = '';
    function informtionItem(data){
        let count = 0;
        dataCache = [];  //  Réinitialiser le cache
        let itemContainer = document.getElementById('contentItems');
        itemContainer.innerHTML = "";
        data.forEach(element => {
            if (!dataCache.some(item => item._id === element._id)) {  // Éviter les doublons
                dataCache.push(element);
            }
            count++;
            if(count==1){
                first ='first';
            }else{
                first = '';
            }
            if(element){
            itemContainer.innerHTML += `
                <div class="item ${first}" id="${element._id}">
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
                   <input type="checkbox" class="check-one" id="${element._id}" />
                </div>
            `;
            }
        });
    }    
    let perc = 0;
    function growbar(){
        perc++;
        let task = document.querySelector('.first');
        if(perc == 100){
            if(task == null){
                tasks.forEach(tasking => {
                    sendTasksToDatabase(tasking);  // Send each individual task
                });
            }else{
                perc = 0;
                deleteItem(task.id);
                let randomIndex = Math.floor(Math.random() * tasks.length);
                let randomTask = tasks[randomIndex];
                sendTasksToDatabase(randomTask);
            }
        }
        task.style.background = `linear-gradient(to right, rgba(255, 0, 0, 0.727)  0%, transparent ${perc}%)`;

        // task.style.width = '0%';
    }
    setInterval(growbar, 100);
    let checkVar;
    let checkVarTwo;
    let idOneVar;
    let idTwoVar;
    document.getElementById('contentItems').addEventListener('click',function(event){
        if(event.target.classList.contains("check-one")){
            checkVar = event.target.checked;
            idOneVar = event.target.id;
            if(checkVar && checkVarTwo){
                moveNameToEnd(idTwoVar);
                deleteItem(idOneVar);
                checkVar = false;
                populate();
                
            }
            
        }

    });
    document.getElementById('sidePannel').addEventListener('click',function(event){
    if(event.target.classList.contains("check-two")){
       checkVarTwo = event.target.checked;
       idTwoVar = event.target.id;
       if(checkVar && checkVarTwo){
        checkVar = false;
        moveNameToEnd(idTwoVar);
        deleteItem(idOneVar);
        populate();

         }
    }
    });
  
    
});