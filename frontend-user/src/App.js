import React, { useEffect, useState } from "react";
import { Row, Col, Card, Select, List } from "antd";
import { listCameras, listHistory } from "./api";
import "./index.css";

const { Option } = Select;

export default function UserPage() {
  const [cameras, setCameras] = useState([]);
  const [selectedCam, setSelectedCam] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchAll();
    // refresh history every 10s
    const t = setInterval(() => fetchHistory(), 10000);
    return () => clearInterval(t);
  }, []);

  async function fetchAll() {
    try {
      const [cRes, hRes] = await Promise.all([listCameras(), listHistory()]);
      setCameras(cRes.data || []);
      setHistory(hRes.data || []);
      if ((cRes.data || []).length > 0 && !selectedCam) {
        setSelectedCam(cRes.data[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  }

  async function fetchHistory() {
    try {
      const hRes = await listHistory();
      setHistory(hRes.data || []);
    } catch (err) {
      console.error(err);
    }
  }

  function snapshotUrl(snapshot_path) {
    if (!snapshot_path) return "";
    const parts = snapshot_path.split(/[\\/]/);
    const fname = parts[parts.length - 1];
    return `/uploads/snapshots/${fname}`;
  }

  return (
    <div className="app-container">
      <h2 style={{ marginBottom: 20 }}>📹 User — Live & Events</h2>
      <Row gutter={16}>
        {/* Live Stream */}
        <Col span={12}>
          <Card title="Live Stream">
            {selectedCam ? (
              <img
                alt="live"
                className="img-live"
                src={`http://localhost:8000/api/stream/${selectedCam}`}
                onError={(e) => {
                  e.currentTarget.src =
                    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='600' height='400'><rect width='100%' height='100%' fill='%23eee'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='%23666'>Stream not available</text></svg>";
                }}
              />
            ) : (
              <div>No camera</div>
            )}
            <div style={{ marginTop: 8 }}>
              <Select
                value={selectedCam}
                onChange={(v) => setSelectedCam(v)}
                style={{ width: 240 }}
                placeholder="Select camera"
              >
                {cameras.map((c) => (
                  <Option key={c.id} value={c.id}>
                    {c.name}
                  </Option>
                ))}
              </Select>
            </div>
          </Card>
        </Col>

        {/* Recent Events */}
        <Col span={12}>
          <Card title="Recent Events">
            <div style={{ maxHeight: "540px", overflowY: "auto", paddingRight: "8px" }}>
              <List
                dataSource={history}
                renderItem={(item) => (
                  <List.Item key={item.id}>
                    <List.Item.Meta
                      title={
                        item.person_id ? (
                          <span className="person-tag">
                            Person ID: {item.person_id}
                          </span>
                        ) : (
                          "Unknown"
                        )
                      }
                      description={`Camera: ${item.camera_id} — ${new Date(
                        item.timestamp
                      ).toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" })}`}
                    />
                    <img
                      src={snapshotUrl(item.snapshot_path)}
                      alt="snap"
                      className="snapshot-img"
                    />
                  </List.Item>
                )}
              />
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
}
