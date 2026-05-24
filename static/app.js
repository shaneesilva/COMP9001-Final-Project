const loginScreen = document.querySelector("#login-screen");
const appScreen = document.querySelector("#app-screen");
const loginForm = document.querySelector("#login-form");
const nameInput = document.querySelector("#name-input");
const taskForm = document.querySelector("#task-form");
const taskInput = document.querySelector("#task-input");
const taskList = document.querySelector("#task-list");
const emptyState = document.querySelector("#empty-state");
const goalTrack = document.querySelector("#goal-track");
const goalCopy = document.querySelector("#goal-copy");
const todayLabel = document.querySelector("#today-label");
const welcomeName = document.querySelector("#welcome-name");
const catSprite = document.querySelector("#cat-sprite");
const catName = document.querySelector("#cat-name");
const catMessage = document.querySelector("#cat-message");
const bowlFill = document.querySelector("#bowl-fill");
const bowlLabel = document.querySelector("#bowl-label");
const completedCount = document.querySelector("#completed-count");
const pendingCount = document.querySelector("#pending-count");
const energyCount = document.querySelector("#energy-count");
const refreshButton = document.querySelector("#refresh-button");
const logoutButton = document.querySelector("#logout-button");
const clearCompletedButton = document.querySelector("#clear-completed");

let activeUser = localStorage.getItem("pixelPetUser");
let catAnimationTimer = null;

const SPRITE_COLUMNS = 11;
const SPRITE_ROWS = 53;

const CAT_ANIMATIONS = {
  idle: {
    frames: [0, 0, 4, 5, 4, 0],
    speed: 320,
  },
  hungry: {
    frames: [319, 320, 321, 320],
    speed: 260,
  },
  sleepy: {
    frames: [187, 188, 198, 199, 209, 210, 220, 221],
    speed: 460,
  },
  happy: {
    frames: [308, 309, 310, 309, 308, 308],
    speed: 190,
  },
  full: {
    frames: [198, 199, 198, 199],
    speed: 520,
  },
};

async function api(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Something went wrong.");
  }
  return data;
}

async function loadState() {
  if (!activeUser) return;
  const response = await fetch(`/api/state?user=${encodeURIComponent(activeUser)}`);
  const data = await response.json();
  renderApp(data);
}

function showApp() {
  loginScreen.classList.add("hidden");
  appScreen.classList.remove("hidden");
}

function showLogin() {
  appScreen.classList.add("hidden");
  loginScreen.classList.remove("hidden");
  nameInput.focus();
}

function renderGoal(cat) {
  goalTrack.innerHTML = "";
  for (let index = 0; index < cat.daily_goal; index += 1) {
    const tile = document.createElement("span");
    tile.className = "goal-tile";
    if (index < cat.completed_today) {
      tile.classList.add("filled");
    }
    goalTrack.appendChild(tile);
  }

  const remaining = Math.max(0, cat.daily_goal - cat.completed_today);
  goalCopy.textContent =
    remaining === 0
      ? "Goal reached. The bowl is full for today."
      : `${remaining} more task${remaining === 1 ? "" : "s"} to fully feed the cat.`;
}

function renderTasks(tasks) {
  taskList.innerHTML = "";
  emptyState.classList.toggle("hidden", tasks.length > 0);

  tasks.forEach((task) => {
    const item = document.createElement("li");
    item.className = `task-item${task.completed ? " done" : ""}`;

    const completeButton = document.createElement("button");
    completeButton.type = "button";
    completeButton.className = "task-button complete";
    completeButton.textContent = task.completed ? "OK" : "[ ]";
    completeButton.setAttribute(
      "aria-label",
      task.completed ? `Mark ${task.text} incomplete` : `Complete ${task.text}`,
    );
    completeButton.addEventListener("click", () => toggleTask(task.id));

    const text = document.createElement("span");
    text.className = "task-text";
    text.textContent = task.text;

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "task-button delete";
    deleteButton.textContent = "X";
    deleteButton.setAttribute("aria-label", `Delete ${task.text}`);
    deleteButton.addEventListener("click", () => deleteTask(task.id));

    item.append(completeButton, text, deleteButton);
    taskList.appendChild(item);
  });
}

function renderCat(cat) {
  catName.textContent = cat.name;
  catMessage.textContent = cat.message;
  bowlFill.style.height = `${cat.bowl_percent}%`;
  bowlLabel.textContent = `${cat.bowl_percent}%`;
  completedCount.textContent = cat.completed_today;
  pendingCount.textContent = cat.pending_today;
  energyCount.textContent = cat.energy;
  startCatAnimation(cat.pose);
}

function showCatFrame(frameIndex) {
  const column = frameIndex % SPRITE_COLUMNS;
  const row = Math.floor(frameIndex / SPRITE_COLUMNS);
  const xPercent = (column / (SPRITE_COLUMNS - 1)) * 100;
  const yPercent = (row / (SPRITE_ROWS - 1)) * 100;
  catSprite.style.backgroundPosition = `${xPercent}% ${yPercent}%`;
}

function startCatAnimation(pose) {
  const animation = CAT_ANIMATIONS[pose] || CAT_ANIMATIONS.idle;
  let frameCursor = 0;

  window.clearInterval(catAnimationTimer);
  catSprite.dataset.pose = pose;

  function nextFrame() {
    showCatFrame(animation.frames[frameCursor]);
    frameCursor = (frameCursor + 1) % animation.frames.length;
  }

  nextFrame();
  catAnimationTimer = window.setInterval(nextFrame, animation.speed);
}

function renderApp(data) {
  activeUser = data.username;
  localStorage.setItem("pixelPetUser", activeUser);
  welcomeName.textContent = data.display_name;
  todayLabel.textContent = data.today;
  renderGoal(data.cat);
  renderTasks(data.tasks);
  renderCat(data.cat);
  showApp();
}

async function login(displayName) {
  const data = await api("/api/login", { display_name: displayName });
  renderApp(data);
}

async function addTask(text) {
  const data = await api("/api/tasks", { user: activeUser, text });
  renderApp(data);
}

async function toggleTask(taskId) {
  const data = await api("/api/tasks/toggle", { user: activeUser, task_id: taskId });
  renderApp(data);
}

async function deleteTask(taskId) {
  const data = await api("/api/tasks/delete", { user: activeUser, task_id: taskId });
  renderApp(data);
}

async function clearCompleted() {
  const data = await api("/api/tasks/clear-completed", { user: activeUser });
  renderApp(data);
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await login(nameInput.value || "Guest");
});

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = taskInput.value.trim();
  if (!text) return;
  taskInput.value = "";
  await addTask(text);
  taskInput.focus();
});

refreshButton.addEventListener("click", loadState);

logoutButton.addEventListener("click", () => {
  activeUser = null;
  localStorage.removeItem("pixelPetUser");
  showLogin();
});

clearCompletedButton.addEventListener("click", clearCompleted);

if (activeUser) {
  loadState();
} else {
  showLogin();
}
