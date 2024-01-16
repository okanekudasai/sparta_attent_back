let my_ip = 'http://localhost:5000';
// let my_ip = 'http://152.69.225.239:8080'

let init = async () => {
    console.log("눌림");
    let kakao_id = document.querySelector("#kakao_id").value;
    let kakao_password = document.querySelector("#kakao_password").value;
    const formData = new URLSearchParams();
    formData.append('kakao_id', kakao_id);
    formData.append('kakao_password', kakao_password);
    let initiating = await axios.post(my_ip + "/initiating", formData)
    console.log(initiating)
    if(isNaN(initiating)) return;
    console.log(my_ip + "/makeSchedule/" + initiating)
    document.querySelector("#chrome_index").value = initiating;
    let make_schedule = await axios.get(my_ip + "/makeSchdule/" + initiating)
    console.log(make_schedule)
}

let confirm_login = async () => {
    let chrome_index = document.querySelector("#chrome_index").value;
    let conforming = await axios.get(my_ip + "/isOpen/" + chrome_index)
    console.log(conforming)
}

let logout = async () => {
    let chrome_index = document.querySelector("#chrome_index").value;
    let logouting = await axios.get(my_ip + "/logout/" + chrome_index).then(res => res.data)
    console.log(logouting)
}

let open_naver = async () => {
    let naverIndex = await axios.get(my_ip + "/openNaver").then(res => res.data)
    document.querySelector("#naver_index").value = naverIndex;
}

let close_naver = async () => {
    let num = document.querySelector("#naver_index").value;
    let res = await axios.get(my_ip + "/closeNaver/" + num).then(res => res.data)
    console.log(res)
}