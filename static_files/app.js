document.addEventListener("DOMContentLoaded", () => {
  const kgEl = document.getElementById("kg");
  if (kgEl) {
    try {
      const data = JSON.parse(kgEl.textContent);
      console.log("KG for container:", data);
    } catch (e) {
      console.warn("Invalid KG JSON", e);
    }
  }
});
