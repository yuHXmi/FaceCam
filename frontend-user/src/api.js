import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
});


// Cameras
export const listCameras = () => API.get("/api/cameras");

// History
export const listHistory = () => API.get("/api/history");
