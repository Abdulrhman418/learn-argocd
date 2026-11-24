const form = document.querySelector("#note-form");
const input = document.querySelector("#note-content");
const notes = document.querySelector("#notes");
const status = document.querySelector("#status");

async function request(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || `Request failed (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}

function renderNotes(items) {
  notes.replaceChildren();
  for (const note of items) {
    const item = document.createElement("li");
    const content = document.createElement("span");
    const remove = document.createElement("button");
    content.textContent = note.content;
    remove.type = "button";
    remove.textContent = "Delete";
    remove.addEventListener("click", async () => {
      try {
        await request(`/api/notes/${note.id}`, { method: "DELETE" });
        await loadNotes();
      } catch (error) {
        status.textContent = error.message;
      }
    });
    item.append(content, remove);
    notes.append(item);
  }
}

async function loadNotes() {
  const data = await request("/api/notes");
  renderNotes(data.notes);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  status.textContent = "";
  try {
    await request("/api/notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: input.value }),
    });
    input.value = "";
    await loadNotes();
  } catch (error) {
    status.textContent = error.message;
  }
});

loadNotes().catch((error) => {
  status.textContent = error.message;
});
