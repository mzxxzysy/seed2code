// function selectBox(event) {
//   console.log(event.target);
//   var inputId = event.target.id;
//   var box = document.querySelector(`label[for='${inputId}']`);
//   box.style.backgroundColor = "#ffffff";
//   box.style.color = "#c06a89";
//   box.style.border = "1px solid #c06a89";
//   box.style.boxShadow = "0 0 0 6px #fffffd";
// }

function selectBox(event) {
  // 모든 label에서 'selected' 클래스 제거
  document.querySelectorAll("label").forEach((label) => {
    label.classList.remove("selected");
  });

  // 클릭된 input 요소의 id
  const inputId = event.target.id;

  // input에 연결된 label 선택
  const label = document.querySelector(`label[for='${inputId}']`);

  // 클릭된 label에 'selected' 클래스 추가
  if (label) {
    label.classList.add("selected");
  }
}
