import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
});

// People
export const listPeople = () => API.get("/api/people");
export const addPerson = (formData) =>
  API.post("/api/people/add", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
export const deletePerson = (id) => API.delete(`/api/people/${id}`); 

// Cameras
export const listCameras = () => API.get("/api/cameras");
export const addCamera = (data) => API.post("/api/cameras", data);
export const deleteCamera = (id) => API.delete(`/api/cameras/${id}`);

