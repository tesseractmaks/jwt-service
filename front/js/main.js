import { registration } from "./reg.js";


const app = document.querySelector("#app")

const reg = await registration()


app.innerHTML = ""
app.append(reg)


let refreshBtn = document.querySelector("#Btn-click")
if (refreshBtn){
    let cnt = 0
    refreshBtn.addEventListener("click", async function (elem) {
        cnt++
        console.log(cnt,"-------")
        let response = await fetch(`http://127.0.0.1:8000/token/refresh`,
    { 
        // headers: {
            // 'Content-Type': 'multipart/form-data',
        // 'Access-Control-Allow-Origin': "*"
    // },
        
        headers: {
            // "Authorization": "Bearer ", 
        'Access-Control-Allow-Origin': "*"
    },
        credentials: 'include'

    }
    )
    // const refreshToken = await response.json();
    
    const refreshToken = await response.blob();
    console.log(refreshToken)
    let img = URL.createObjectURL(refreshToken)
    app.style.backgroundImage = `url(${img})`

    if(cnt==3){
        refreshBtn.textContent = "выйти"
    }
    if(cnt==4){
        const url = 'http://127.0.0.1:8000/token/auth/logout'
	    const response = await fetch(url, {
		method: 'POST',
		credentials: 'include',
	})

    let modalBox = document.querySelector("#modal-box")
		modalBox.classList.remove("modal__box-click")
		modalBox.classList.add("modal__box")

        let regInputs = document.querySelector("#modal-box form")
        console.log(regInputs,"=-=")
        regInputs.classList.remove("dis-l")
        regInputs.classList.add("on-dis-l")

        // let modalRegBtn = document.querySelector("#reg-Btn")
        // modalRegBtn.classList.remove("dis-l")
		// modalRegBtn.classList.add("on-dis-l")

		let regNewBtn = document.querySelector("#modal-box #Btn-click")
		regNewBtn.classList.remove("on-dis-l")
		regNewBtn.classList.add("dis-l")
        cnt = 0
    }
    })
}
