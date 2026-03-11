async function uploadContract(){

const fileInput=document.getElementById("fileInput")

if(fileInput.files.length===0){
alert("Select contract")
return
}

document.getElementById("loader").style.display="block"

const formData=new FormData()
formData.append("file",fileInput.files[0])

const response=await fetch("http://127.0.0.1:5000/upload",{
method:"POST",
body:formData
})

const data=await response.json()

localStorage.setItem("analysisResult",JSON.stringify(data))

window.location="dashboard.html"

}



window.onload=function(){
// show summary
const summaryBox = document.getElementById("summaryBox")

if(summaryBox && data.summary){
summaryBox.innerText = data.summary
}

const stored=localStorage.getItem("analysisResult")
if(!stored) return

const data=JSON.parse(stored)

document.getElementById("riskLevel").innerText=data.risk_level
document.getElementById("riskScore").innerText=data.risk_score


if(data.risk_level.includes("HIGH")){
riskLevel.classList.add("high-risk")
}
else if(data.risk_level.includes("MEDIUM")){
riskLevel.classList.add("medium-risk")
}
else{
riskLevel.classList.add("low-risk")
}


// bar chart
new Chart(document.getElementById("riskChart"),{
type:"bar",
data:{
labels:["Risk Score"],
datasets:[{
data:[data.risk_score],
backgroundColor:"#38bdf8"
}]
}
})


// pie chart
const clauses=data.clauses_detected

const labels=Object.keys(clauses)
const values=Object.values(clauses).map(v=>v?1:0)

new Chart(document.getElementById("clauseChart"),{
type:"pie",
data:{
labels:labels,
datasets:[{
data:values
}]
}
})


// explanation
let explanation=""

if(clauses.payment_terms)
explanation+="Payment Clause → Financial obligations detected<br>"

if(clauses.termination_clause)
explanation+="Termination Clause → Contract termination conditions found<br>"

if(clauses.data_privacy_clause)
explanation+="Privacy Clause → Data protection requirement detected<br>"

document.getElementById("explanation").innerHTML=explanation


// highlight text
let text=data.text

const keywords=["payment","termination","privacy"]

keywords.forEach(word=>{
const regex=new RegExp(word,"gi")
text=text.replace(regex,`<span class="highlight">${word}</span>`)
})

document.getElementById("contractText").innerHTML=text

}