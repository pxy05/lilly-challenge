const API_URL = "http://localhost:8000"


function createMedicines(data) {
    const container = document.querySelector(".container.right");

    if (!data) {
        container.innerHTML = `<p>No Medicine Found</p>` 
        return
    }

    let medicinesList = '<div class="medicine-list">'

    data.medicines.forEach(medicine => {
        medicinesList += `
            <div id="${medicine.name}" class="medicine-item shadow">
            <div class="medicine-item-details">
                <h3>${medicine.name !== null && medicine.name !== "" ? medicine.name : "Not Available."}</h3>
                <p>Price: ${medicine.price !== null ? "£"+medicine.price : "Not Available."}</p>
                <button onClick="handleDelete('${medicine.name}')">Delete</button>
            </div>
            <div class="medicine-item-edit">
                <form class="editForm" data-medicine-name="${medicine.name}">
                    <label class="editFormItem" for="newPrice-${medicine.name}"><span style="font-weight: bold;">Update Price</span></label>
                    <input class="editFormItem" type="number" step="0.01" name="newPrice" id="newPrice-${medicine.name}" placeholder="New Price" required/>
                    <input class="editFormItem" type="submit" name="editButton" id="editButton" value="Update Medicine"/>
                </form>
            </div>
            </div>
        `
    });
    
    medicinesList += '</div>'
    container.innerHTML = medicinesList
}

document.addEventListener('DOMContentLoaded', async () => {
    loadPageData()

    const averagePriceContainer = document.querySelector(".average-price")
    try {
        const averagePrice = await getAveragePrice()
        averagePriceContainer.innerHTML = `<p class="avg-price">${"Average Medicine Price: £" + averagePrice.toFixed(2)}</p>`
    } catch (error) {
        averagePriceContainer.innerHTML = "No data available right now."
    }

    const container = document.querySelector(".container.right");
    container.addEventListener('submit', async (e) => {
        if (e.target.classList.contains('editForm')) {
            e.preventDefault();
            
            const medicineName = e.target.getAttribute('data-medicine-name');
            
            const newPriceInput = e.target.querySelector('input[name="newPrice"]');
            const newPrice = newPriceInput.value;
            
            await handleUpdate(medicineName, newPrice);
        }
    });

    const form = document.querySelector('.create-medicine')
    form.addEventListener('submit', async (e) => {
        e.preventDefault()
        
        const name = document.getElementById('mName').value
        const price = document.getElementById('mPrice').value
        
        try {
            await createMedicine(name, price)
            form.reset()
            await loadPageData()
            await updateAveragePrice()

        } catch (error) {
            alert(error.message)
        }
    })
})

async function updateAveragePrice() {
    const averagePrice = await getAveragePrice()
    const averagePriceContainer = document.querySelector(".average-price")
    averagePriceContainer.innerHTML = `<p class="avg-price">${"Average Medicine Price: £" + averagePrice.toFixed(2)}</p>`
}

async function handleUpdate(name, price) {
    try {
        await updateMedicine(name, price)
        await loadPageData()
        await updateAveragePrice()
    } catch (error) {
        const item = document.getElementById(name)
        if (item) {
            item.innerHTML += `<span class="update-error">Error: ${error.message}</span>`
        }
    }
}

async function handleDelete(name) {
    try {
        await deleteMedicine(name)
        await loadPageData()
        await updateAveragePrice()
    } catch (error) {
        const container = document.querySelector(".container.right");
        container.innerHTML = `<p>${error.message}</p>`
    }
}


async function loadPageData() {
    try {
        const data = await getAllMedicines()
        createMedicines(data)
    } catch (error) {
        const container = document.querySelector(".container.right");
        container.innerHTML = `<p>${error.message}</p>`
    }
}

async function getAveragePrice() {
    try {
        const response = await fetch(API_URL+"/average")

        if (!response.ok) {
            throw new Error("Error fetching average price")
        }

        const data = await response.json()

        return data.average_price
    } catch(error) {
        console.error("Error fetching average price:", error)
        throw error;
    }
    
}

function trimString(value, valueName) {
    if (value == null) {
        throw new Error(`${valueName} cannot be empty`)
    }

    value = value.trim()
    if (value === "") {
        throw new Error(`${valueName} cannot be empty`)
    }

    return value
}

async function getAllMedicines() {
    try {
        const response = await fetch(`${API_URL}/medicines`);
        
        if (!response.ok) {
            throw new Error("Error fetching data.")
        }
        
        const data = await response.json();
        return data
    } catch (error) {
        console.error("Error fetching all medicines:", error);
        throw error
    }
}

async function createMedicine(name, price) {
    name = trimString(name, "name")

    if (typeof price !== "number") {
        price = Number(price)
        if (isNaN(price)) {
            throw new Error("Must be a valid number")
        }
    }

    try {
        const response = await fetch(`${API_URL}/medicines`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({name, price})
        })

        const data = await response.json()
        
        if (!response.ok || (data['code'] !== 200 && data['code'] !== 201)) {
            throw new Error(data['message'] || "Error fetching data.")
        }
        
        return data
    } catch (error) {
        console.error("Error creating medicine:", error)
        throw error
    }
}

async function updateMedicine(name, price) {
    name = trimString(name, "name")

    try {
        const response = await fetch(`${API_URL}/medicines/${name}`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({price})
        })
        const data = await response.json()

        if (!response.ok || data['code'] !== 200) {
            throw new Error(data['message'] || data['error'] || "Error fetching data.")
        }
        
        return data
    } catch (error) {
        console.error("Error updating medicine:", error)
        throw error
    }
}

async function deleteMedicine(name) {
    name = trimString(name, "name") 

    try {
        const response = await fetch(`${API_URL}/medicines/${name}`,{
            method: "DELETE",
        })
        const data = await response.json()

        if (!response.ok || data['code'] !== 200) {
            throw new Error(data['message'] || data['error'] || "Error fetching data.")
        }

        return data
    } catch (error) {
        console.error("Error deleting medicine:", error)
        throw error
    }
}


