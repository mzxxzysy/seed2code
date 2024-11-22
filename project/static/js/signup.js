document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const usernameInput = document.getElementById("id_username");
  const password1Input = document.getElementById("id_password1");
  const password2Input = document.getElementById("id_password2");

  function createErrorMessage(element, message) {
    const existingError = element.nextElementSibling;
    if (existingError && existingError.classList.contains("error-message")) {
      existingError.remove();
    }

    const errorMsg = document.createElement("div");
    errorMsg.className = "error-message";
    errorMsg.style.color = "red";
    errorMsg.style.fontSize = "0.8rem";
    errorMsg.textContent = message;
    element.parentNode.insertBefore(errorMsg, element.nextSibling);
  }

  usernameInput.addEventListener("input", function () {
    const username = this.value;
    const existingError = this.nextElementSibling;

    if (username.length <= 5) {
      createErrorMessage(this, "ID는 5자 이상이어야 합니다.");
    } else if (existingError && existingError.classList.contains("error-message")) {
      existingError.remove();
    }
  });

  function validatePassword() {
    const password = password1Input.value;
    const hasNumber = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    const isLongEnough = password.length >= 8;

    let errorMessage = "";
    if (!isLongEnough) {
      errorMessage += "비밀번호는 8자 이상이어야 합니다. ";
    }
    if (!hasNumber || !hasSpecialChar) {
      errorMessage += "숫자, 특수기호를 포함해야 합니다. ";
    }

    if (errorMessage) {
      createErrorMessage(password1Input, errorMessage.trim());
      return false;
    } else {
      const existingError = password1Input.nextElementSibling;
      if (existingError && existingError.classList.contains("error-message")) {
        existingError.remove();
      }
      return true;
    }
  }

  function validatePasswordConfirmation() {
    const password1 = password1Input.value;
    const password2 = password2Input.value;

    if (password1 !== password2) {
      createErrorMessage(password2Input, "비밀번호가 일치하지 않습니다.");
      return false;
    } else {
      const existingError = password2Input.nextElementSibling;
      if (existingError && existingError.classList.contains("error-message")) {
        existingError.remove();
      }
      return true;
    }
  }

  password1Input.addEventListener("input", validatePassword);
  password2Input.addEventListener("input", validatePasswordConfirmation);

  form.addEventListener("submit", function (event) {
    const isUsernameValid = usernameInput.value.length > 5;
    const isPasswordValid = validatePassword();
    const isPasswordConfirmed = validatePasswordConfirmation();

    if (!isUsernameValid || !isPasswordValid || !isPasswordConfirmed) {
      event.preventDefault();
    }
  });
});
