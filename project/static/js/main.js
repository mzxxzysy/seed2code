function selectBox(event) {
  let modal = document.querySelector(".modal");
  let modal_popup = document.querySelector(".modal_popup");
  let content_bg = document.querySelector(".content_bg");

  modal.style.display = "flex";
  modal_popup.style.display = "flex";
  content_bg.style.filter = "blur(10px)";

  let closeBtn = document.querySelector(".x");

  closeBtn.onclick = function () {
    modal.style.display = "none";
    modal_popup.style.display = "none";
    content_bg.style.filter = "blur(0)";
  };
}
