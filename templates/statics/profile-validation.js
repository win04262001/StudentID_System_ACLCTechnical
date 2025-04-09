/**
 * Client-side validation for profile photos
 * Uses the trainable validator API
 */

document.addEventListener("DOMContentLoaded", () => {
  const profileInput = document.getElementById("profile_picture")
  const validateBtn = document.getElementById("validate_profile")
  const profileLoading = document.getElementById("profile_loading")
  const profileError = document.getElementById("profile_error")
  const profileSuccess = document.getElementById("profile_success")
  const submitButton = document.getElementById("submit_button")

  let profileValid = false
  const signatureValid = false

  // Validate profile picture when the validate button is clicked
  if (validateBtn) {
    validateBtn.addEventListener("click", () => {
      const file = profileInput.files[0]
      if (!file) {
        profileError.textContent = "Please select a file first"
        profileError.classList.remove("d-none")
        profileSuccess.classList.add("d-none")
        return
      }

      // Show loading indicator
      profileLoading.classList.remove("d-none")
      profileError.classList.add("d-none")
      profileSuccess.classList.add("d-none")

      // Create form data
      const formData = new FormData()
      formData.append("profile", file)

      // Send to server for validation
      fetch("/validate_image/profile", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          profileLoading.classList.add("d-none")

          if (data.valid) {
            profileSuccess.textContent =
              "✅ Photo meets all requirements" +
              (data.confidence ? ` (${(data.confidence * 100).toFixed(1)}% confidence)` : "")
            profileSuccess.classList.remove("d-none")
            profileError.classList.add("d-none")
            profileValid = true
          } else {
            profileError.textContent = "❌ " + (data.error || "Validation failed")
            profileError.classList.remove("d-none")
            profileSuccess.classList.add("d-none")
            profileValid = false
          }

          updateSubmitButton()
        })
        .catch((error) => {
          profileLoading.classList.add("d-none")
          profileError.textContent = "Error: " + error.message
          profileError.classList.remove("d-none")
          profileValid = false
          updateSubmitButton()
        })
    })
  }

  // Update submit button state based on validation status
  function updateSubmitButton() {
    if (submitButton) {
      submitButton.disabled = !(profileValid && signatureValid)
    }
  }
})

