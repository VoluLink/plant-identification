// -------------------------- chat box -------------------------------
const chatMessages = document.getElementById("chatMessages");

/*
function sendMessage(text, images = []) {
  if (!text && images.length === 0) return;

  // 1. add user message (right)
  addMessage(text, "user", images);

  // 2. simulate bot response (left)
  setTimeout(() => {
    const response = generateResponse(text);
    addMessage(response, "bot");
  }, 500);
}
  */

async function sendMessage(text, images = []) {
  if (!text && images.length === 0) return;

  if (images.length > 0) {
    try {
      const result = await identifyPlant(text, images[0]);
    } catch (err) {
      console.error(err);
      addMessage("Plant identification failed.", "bot");
    }
  }
}
// change the image to a workable blop type
async function blobUrlToBlob(blobUrl) {
  const response = await fetch(blobUrl);

  if (!response.ok) {
    throw new Error("Failed to convert blob URL");
  }

  return await response.blob();
}

// blurring and identification
async function identifyPlant(text, imageFile) {
  const imageBlob = imageFile instanceof Blob ? imageFile : await blobUrlToBlob(imageFile);

  // Blur image
  const blurForm = new FormData();
  blurForm.append("file", imageBlob, imageFile?.name || "image.png");

  const blurResponse = await fetch("/blur", {
    method: "POST",
    body: blurForm,
  });

  if (!blurResponse.ok) {
    throw new Error("Blur service failed");
  }

  const blurredBlob = await blurResponse.blob();

  // Show blurred image in chat
  const blurredUrl = URL.createObjectURL(blurredBlob);

  addMessage(text, "user", [blurredUrl]);

  // Send blurred image to PlantID
  const plantForm = new FormData();
  plantForm.append("file", blurredBlob, imageFile?.name || "image.png");

  const plantResponse = await fetch("/ident/plant_classification", {
    method: "POST",
    body: plantForm,
  });

  if (!plantResponse.ok) {
    throw new Error("PlantID failed");
  }

  const result = await plantResponse.json();
  console.log(result);
  // FIXED: use result
  const plant = result?.response?.result?.classification?.suggestions?.[0];

  if (plant) {
    addMessage(`I think this is ${plant.name} (${Math.round(plant.probability * 100)}%)`, "bot");
  }

  return result;
}
// create message bubble
function addMessage(text, type, images = []) {
  // text

  // images
  if (images.length > 0) {
    const imgContainer = document.createElement("div");
    imgContainer.className = "message-images";

    images.forEach((src) => {
      const img = document.createElement("img");
      img.src = src;

      img.className = "message-img";
      imgContainer.appendChild(img);
    });

    chatMessages.appendChild(imgContainer);
  }
  if (text) {
    const textEl = document.createElement("div");
    textEl.textContent = text;
    textEl.className = "message " + type;
    chatMessages.appendChild(textEl);
  }
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// fake response
function generateResponse(input) {
  return "You said: " + input;
}

// -------------------------- textarea behaviour -------------------------------
const box = document.getElementById("chatBox");
const textarea = box.querySelector("textarea");
const submButton = document.getElementById("submitBtn");
const dropdown = document.getElementById("myDropdown");
const triggerBtn = dropdown.querySelector(".dropdown-trigger button");

// submit text
function handleSubmit() {
  const text = textarea.value.trim();
  // collect images
  const images = [];
  previewBar.querySelectorAll("img").forEach((img) => {
    images.push(img.src);
  });

  if (!text && images.length === 0) return;

  sendMessage(text, images);

  // clear textarea
  textarea.value = "";
  submButton.disabled = true;
  // adjust chat box size
  autoResize();

  // remove images
  previewBar.replaceChildren();
  updatePreviewVisibility();
}

// Enable/disable submit button based on fill
textarea.addEventListener("input", () => {
  submButton.disabled = textarea.value.trim() === "";
  autoResize();
});

// submit Button click
submButton.addEventListener("click", handleSubmit);

// Enter key (but allow Shift+Enter for new line)
textarea.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSubmit();
  }
});

// adjust textarea length based on input amount
function autoResize() {
  textarea.style.height = "auto"; // reset first
  textarea.style.height = textarea.scrollHeight + "px";
}
autoResize();

// Toggle dropdown
triggerBtn.addEventListener("click", () => {
  dropdown.classList.toggle("is-active");
});

// Close dropdown when clicking outside
document.addEventListener("click", (e) => {
  if (!dropdown.contains(e.target)) {
    dropdown.classList.remove("is-active");
  }
});

// toggle light and dark mode
const toggleBtn = document.getElementById("themeToggle");
if (localStorage.getItem("theme") === "dark") {
  document.body.classList.add("dark-mode");
  toggleBtn.textContent = "☀️";
}

// toggle dark/light mode
toggleBtn.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");

  const isDark = document.body.classList.contains("dark-mode");
  localStorage.setItem("theme", isDark ? "dark" : "light");

  toggleBtn.textContent = isDark ? "☀️" : "🌙";
});

// open the camera
let stream;
async function openCamera() {
  document.getElementById("cameraBox").style.display = "block";

  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    document.getElementById("video").srcObject = stream;
  } catch (err) {
    alert("Camera access denied or not supported.");
  }
}
// take a photo with webcam
function takePhoto() {
  const video = document.getElementById("video");

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0);

  const image = canvas.toDataURL("image/png");
  addImage(image);
  stopCamera();
}

// close camera function
function stopCamera() {
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
  }
  document.getElementById("cameraBox").style.display = "none";
}
// add preview image
const previewBar = document.getElementById("previewBar");
function addImage(src) {
  const wrapper = document.createElement("div");
  wrapper.className = "preview-item";

  const img = document.createElement("img");
  img.src = src;

  const btn = document.createElement("button");
  btn.className = "remove-btn";
  btn.innerText = "×";
  btn.onclick = () => {
    URL.revokeObjectURL(img.src);
    wrapper.remove();
    updatePreviewVisibility();
  };

  wrapper.appendChild(img);
  wrapper.appendChild(btn);
  console.log(wrapper);
  // some kind of image sticking/handling here
  previewBar.appendChild(wrapper);
  updatePreviewVisibility();
}

// drag and drop function
const dropZone = document.querySelector(".chat-input-wrapper");

// prevent browser from opening the file
["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (e) => {
    e.preventDefault();
    e.stopPropagation();
  });
});

// highlight when dragging over
["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, () => {
    dropZone.classList.add("drag-active");
  });
});

// remove highlight
["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, () => {
    dropZone.classList.remove("drag-active");
  });
});

// handle drop
dropZone.addEventListener("drop", (e) => {
  const files = e.dataTransfer.files;

  for (let file of files) {
    if (file.type.startsWith("image/")) {
      const url = URL.createObjectURL(file);
      addImage(url);
    }
  }
});
// file upload
const fileInput = document.getElementById("fileInput");

if (fileInput) {
  fileInput.addEventListener("change", function (e) {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    for (const file of files) {
      const url = URL.createObjectURL(file);
      addImage(url);
    }

    this.value = "";
  });
}

// toggle of the preview bar shootingg it
function updatePreviewVisibility() {
  previewBar.style.display = previewBar.children.length ? "flex" : "none";
}

// sound toggle
let soundEnabled = localStorage.getItem("soundEnabled") !== "false";

// update icon on load
updateSoundIcon();

function toggleSound() {
  soundEnabled = !soundEnabled;
  localStorage.setItem("soundEnabled", soundEnabled);
  updateSoundIcon();
}

function updateSoundIcon() {
  const icon = document.getElementById("soundIcon");

  if (soundEnabled) {
    icon.className = "fas fa-volume-up";
  } else {
    icon.className = "fas fa-volume-mute";
  }
}

function playSendSound() {
  if (!soundEnabled) return;

  const audio = new Audio("send.mp3"); // your sound file
  audio.play();
}
